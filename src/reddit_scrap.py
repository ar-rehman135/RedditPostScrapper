import math
import os
import sys
import re
import locale
from datetime import datetime, timedelta
from psaw import PushshiftAPI
import praw
from requests import request
import pandas as pd
import json
import time
from sqlalchemy import MetaData, Table
from src.database.db import engine, Base

# dictionary of possible subreddits to search in with their respective column name
subreddit_dict = {'pennystocks': 'pnnystks',
                  'RobinHoodPennyStocks': 'RHPnnyStck',
                  'Daytrading': 'daytrade',
                  'StockMarket': 'stkmrkt',
                  'stocks': 'stocks',
                  'investing': 'investng',
                  'wallstreetbets': 'WSB'}

# x base point of for a ticker that appears on a subreddit title or text body that fits the search criteria
base_points = 4

# x bonus points for each flair matching 'DD' or 'Catalyst' of for a ticker that appears on the subreddit
bonus_points = 2

# every x upvotes on the thread counts for 1 point (rounded down)
upvote_factor = 2

# rocket emoji
rocket = '🚀'

# praw credentials
CLIENT_ID = "3RbFQX8O9UqDCA"
CLIENT_SECRET = "NalOX_ZQqGWP4eYKZv6bPlAb2aWOcA"
USER_AGENT = "subreddit_scraper"
POLYGON_API_KEY = 'oSJ9pLSFOHYzNvPUuGUmwXNC0nx4_VLB'

def get_submission_praw(n, sub_dict):

    # datetime.today() produces UTC time now :)
    mid_interval = datetime.today() - timedelta(hours=n)
    timestamp_mid = int(mid_interval.timestamp())
    timestamp_start = int((mid_interval - timedelta(hours=n)).timestamp())
    timestamp_end = int(datetime.today().timestamp())

    reddit = praw.Reddit(client_id=CLIENT_ID, client_secret=CLIENT_SECRET, user_agent=USER_AGENT)

    recent = {}
    prev = {}
    for key in sub_dict:
        subreddit = reddit.subreddit(key)
        all_results = []
        # praw limitation gets only 1000 posts
        for post in subreddit.new(limit=1000):
            all_results.append([post.title, post.link_flair_text, post.selftext, post.score, post.created_utc])

        recent[key] = [posts for posts in all_results if posts[4] >= timestamp_mid and posts[4] <= timestamp_end]
        prev[key] = [posts for posts in all_results if posts[4] >= timestamp_start and posts[4] < timestamp_mid]

    return recent, prev

def get_submission_psaw(n, sub_dict):

    api = PushshiftAPI()

    mid_interval = datetime.today() - timedelta(hours=n)
    timestamp_mid = int(mid_interval.timestamp())
    timestamp_start = int((mid_interval - timedelta(hours=n)).timestamp())
    timestamp_end = int(datetime.today().timestamp())

    recent = {}
    prev = {}
    for key in sub_dict:
        # results from the last n hours
        recent[key] = api.search_submissions(after=timestamp_mid,
                                     before=timestamp_end,
                                     subreddit=key,
                                     filter=['title', 'link_flair_text', 'selftext', 'score'])

        # results from the last 2n hours until n hours ago
        prev[key] = api.search_submissions(after=timestamp_start,
                                     before=timestamp_mid,
                                     subreddit=key,
                                     filter=['title', 'link_flair_text', 'selftext', 'score'])

    return recent, prev

def get_submission_generators(n, sub, allsub, use_psaw):

    if sub not in subreddit_dict:
        subreddit_dict[sub] = sub

    sub_dict = {sub:subreddit_dict[sub]}
    if allsub:
        sub_dict = subreddit_dict

    if use_psaw:
        recent, prev = get_submission_psaw(n, sub_dict)

        print("Searching for tickers...")
        current_scores, current_rocket_scores = get_ticker_scores_psaw(recent)
        prev_scores, prev_rocket_scores = get_ticker_scores_psaw(prev)
    else:
        recent, prev = get_submission_praw(n, sub_dict)
        if recent and not prev:
            print('submission results were not found for the previous time period. This may be a popular subreddit with lots of submissions. Try reducing the time interval with the --interval parameter')
        elif not recent and not prev:
            print("praw did not fetch any results for the sub: ")
            print(sub)
            print("try switching to psaw")
        else: 
            print("Searching for tickers...")
            current_scores, current_rocket_scores = get_ticker_scores_praw(recent)
            prev_scores, prev_rocket_scores = get_ticker_scores_praw(prev)  

    return current_scores, current_rocket_scores, prev_scores, prev_rocket_scores

def get_ticker_scores_praw(sub_gen_dict):
    # Python regex pattern for stocks codes
    pattern = '(?<=\$)?\\b[A-Z]{3,5}\\b(?:\.[A-Z]{1,2})?'

    # Dictionaries containing the summaries
    sub_scores_dict = {}

    # Dictionaries containing the rocket count
    rocket_scores_dict = {}

    for sub, submission_list in sub_gen_dict.items():

        sub_scores_dict[sub] = {}

        for submission in submission_list:
            # every ticker in the title will earn this base points
            increment = base_points

            # flair is worth bonus points
            if submission[1] is not None:
                if 'DD' in submission[1]:
                    increment += bonus_points
                elif 'Catalyst' in submission[1]:
                    increment += bonus_points
                elif 'technical analysis' in submission[1]:
                    increment += bonus_points

            # every 2 upvotes are worth 1 extra point
            if upvote_factor > 0 and submission[3] is not None:
                increment += math.ceil(submission[3]/upvote_factor)

            # search the title for the ticker/tickers
            title = ' ' + submission[0] + ' '
            title_extracted = set(re.findall(pattern, title))

            # search the text body for the ticker/tickers
            selftext_extracted = set()
            if submission[2] is not None:
                selftext = ' ' + submission[2] + ' '
                selftext_extracted = set(re.findall(pattern, selftext))

            extracted_tickers = selftext_extracted.union(title_extracted)
            extracted_tickers = {ticker.replace('.', '-') for ticker in extracted_tickers}

            count_rocket = title.count(rocket) + selftext.count(rocket)
            for ticker in extracted_tickers:
                rocket_scores_dict[ticker] = rocket_scores_dict.get(ticker, 0) + count_rocket

            # title_extracted is a set, duplicate tickers from the same title counted once only
            for ticker in extracted_tickers:
                sub_scores_dict[sub][ticker] = sub_scores_dict[sub].get(ticker, 0) + increment

    return sub_scores_dict, rocket_scores_dict

def get_ticker_scores_psaw(sub_gen_dict):

    pattern = '(?<=\$)?\\b[A-Z]{3,5}\\b(?:\.[A-Z]{1,2})?'

    sub_scores_dict = {}

    rocket_scores_dict = {}

    for sub, submission_gen in sub_gen_dict.items():

        sub_scores_dict[sub] = {}

        for submission in submission_gen:

            increment = base_points

            if hasattr(submission, 'link_flair_text'):
                if 'DD' in submission.link_flair_text:
                    increment += bonus_points
                elif 'Catalyst' in submission.link_flair_text:
                    increment += bonus_points
                elif 'technical analysis' in submission.link_flair_text:
                    increment += bonus_points

            # every 2 upvotes are worth 1 extra point
            if hasattr(submission, 'score') and upvote_factor > 0:
                increment += math.ceil(submission.score / upvote_factor)

            # search the title for the ticker/tickers
            if hasattr(submission, 'title'):
                title = ' ' + submission.title + ' '
                title_extracted = set(re.findall(pattern, title))

            # search the text body for the ticker/tickers
            selftext_extracted = set()
            if hasattr(submission, 'selftext'):
                selftext = ' ' + submission.selftext + ' '
                selftext_extracted = set(re.findall(pattern, selftext))

            extracted_tickers = selftext_extracted.union(title_extracted)
            extracted_tickers = {ticker.replace('.', '-') for ticker in extracted_tickers}

            count_rocket = title.count(rocket) + selftext.count(rocket)
            for ticker in extracted_tickers:
                rocket_scores_dict[ticker] = rocket_scores_dict.get(ticker, 0) + count_rocket

            # title_extracted is a set, duplicate tickers from the same title counted once only
            for ticker in extracted_tickers:
                sub_scores_dict[sub][ticker] = sub_scores_dict[sub].get(ticker, 0) + increment

    return sub_scores_dict, rocket_scores_dict

def populate_df(current_scores_dict, prev_scores_dict, interval):
    """
    Combine two score dictionaries, one from the current time interval, and one from the past time interval
    :returns: the populated dataframe
    """
    dict_result = {}
    total_sub_scores = {}

    for sub, current_sub_scores_dict in current_scores_dict.items():
        total_sub_scores[sub] = {}
        for symbol, current_score in current_sub_scores_dict.items():
            if symbol in dict_result.keys():
                dict_result[symbol][0] += current_score
                dict_result[symbol][1] += current_score
                dict_result[symbol][3] += current_score
            else:
                dict_result[symbol] = [current_score, current_score, 0, current_score]
            total_sub_scores[sub][symbol] = total_sub_scores[sub].get(symbol, 0) + current_score

    for sub, prev_sub_scores_dict in prev_scores_dict.items():
        for symbol, prev_score in prev_sub_scores_dict.items():
            if symbol in dict_result.keys():
                dict_result[symbol][0] += prev_score
                dict_result[symbol][2] += prev_score
                dict_result[symbol][3] -= prev_score
            else:
                dict_result[symbol] = [prev_score, 0, prev_score, -prev_score]
            total_sub_scores[sub][symbol] = total_sub_scores[sub].get(symbol, 0) + prev_score

    first_col = str(interval) + 'H Total'
    columns = [first_col, 'Recent', 'Prev', 'Change']
    df = pd.DataFrame.from_dict(dict_result, orient='index', columns=columns)

    if len(current_scores_dict) > 1:
        dtype_dict = {}
        for sub, total_score_dict in total_sub_scores.items():
            # add each total score dict as new column of df
            df[sub] = pd.Series(total_score_dict)
            # pandas will insert NaN for missing symbols, which converts entire column to float
            # will use the below dict to convert these columns back to int
            dtype_dict[sub] = 'int32'
        df = df.fillna(value=0).astype(dtype_dict)

    return df

def filter_df(df, min_val):
    """
    Filter the score dataframe

    :param dataframe df: the dataframe to be filtered
    :param int min_val: the minimum total score
    :returns: the filtered dataframe
    """
    BANNED_WORDS = [
        'THE', 'FUCK', 'ING', 'CEO', 'USD', 'WSB', 'FDA', 'NEWS', 'FOR', 'YOU', 'AMTES', 'WILL', 'CDT', 'SUPPO',
        'MERGE', 'BUY', 'HIGH', 'ADS', 'FOMO', 'THIS', 'OTC', 'ELI', 'IMO', 'TLDR', 'SHIT', 'ETF', 'BOOM', 'THANK',
        'PPP', 'REIT', 'HOT', 'MAYBE', 'AKA', 'CBS', 'SEC', 'NOW', 'OVER', 'ROPE', 'MOON', 'SSR', 'HOLD', 'SELL',
        'COVID', 'GROUP', 'MONDA', 'USA', 'YOLO', 'MUSK', 'AND', 'STONK', 'ELON', 'CAD', 'WIN', 'GET', 'BETS', 'INTO',
        'JUST', 'MAKE', 'NEED', 'BIG', 'STONK', 'ELON', 'CAD', 'OUT', 'TOP', 'ALL', 'ATH', 'ANY', 'AIM', 'IPO', 'EDIT',
        'NEW', 'NYC', 'CAN', 'TWO', 'BEST', 'DROP', 'MOST', 'ONE', 'CFO', 'EST', 'CSM', 'KNOW', 'EPS', 'INC', 'TERM', 'ITA',
        'PLC', 'UGL', 'CAGR'
    ]

    # compares the first column, which is the total score to the min val
    df = df[df.iloc[:, 0] >= min_val]
    drop_index = pd.Index(BANNED_WORDS).intersection(df.index)
    df = df.drop(index=drop_index)
    return df


def listToString(s):
    str1 = " "
    return (str1.join(s).join(","))


def get_all_tickers_data():
    all_tickers = []
    i=1
    count = 1
    result = None
    result2 = None
    logo = ''
    industry = ''
    sector = ''
    market_cap = ''
    employees = ''
    url = ''
    description = ''
    company_name = ''
    stock_ticker = ''
    similiar_companies = ''
    volume = ''
    week_high = ''
    week_low = ''
    processed_stats_data_list = []

    while i<=count and i<2:
        url = "https://api.polygon.io/v2/reference/tickers?sort=ticker&perpage=50&page="+str(i)+"&apiKey="+POLYGON_API_KEY
        resp = request(method="GET", url= url)
        tickers_data = json.loads(resp.text)
        count = math.ceil(tickers_data['count']/50)
        if 'tickers' in tickers_data:
            tickers = tickers_data['tickers']

        for ticker in tickers:
            all_tickers.append(ticker['ticker'])
        time.sleep(30)
        i+=1

    for ticker in all_tickers:
        url = "https://api.polygon.io/v1/meta/symbols/"+ticker+"/company?&apiKey="+POLYGON_API_KEY
        print(url)
        response = request(method="GET", url=url)
        result = json.loads(response.text)
        todayDate = datetime.today()
        toDate = todayDate.strftime("%Y-%m-%d")
        fromDate = str(todayDate.year - 1) + "-" + str(todayDate.month).zfill(2) + "-" + str(todayDate.day).zfill(2)

        if not 'error' in result:
            volume_url = "https://api.polygon.io/v2/aggs/ticker/"+ticker+"/range/1/year/"+fromDate+"/"+toDate+"?unadjusted=true&sort=asc&limit=120&apiKey="+POLYGON_API_KEY;
            response2 = request(method="GET", url=volume_url)
            result2 = json.loads(response2.text)
            processed_stats_data = {}
            if 'logo' in result:
                logo = result['logo'] if result['logo'] else ''
            if 'industry' in result:
                industry = result['industry'] if result['industry'] else ''
            if 'sector' in result:
                sector = result['sector'] if result['sector'] else ''
            if 'marketcap' in result:
                market_cap = result['marketcap'] if result['marketcap'] else ''
            if 'employees' in result:
                employees = result['employees'] if result['employees'] else ''
            if 'url' in result:
                url = result['url'] if result['url'] else ''
            if 'description' in result:
                description = result['description'] if result['description'] else ''
            if 'name' in result:
                company_name = result['name'] if result['name'] else ''
            if 'symbol' in result:
                stock_ticker = result['symbol'] if result['symbol'] else ''
            if 'similar' in result:
                similiar_companies = listToString(result['similar']) if result['similar'] else ''
            if 'results' in result2 and len(result2['results'])>0:
                volume = result2['results'][0]["v"]
                week_high = result2['results'][0]["h"]
                week_low = result2['results'][0]["l"]
            processed_stats_data['logo'] = logo
            processed_stats_data['industry'] = industry
            processed_stats_data['sector'] = sector
            processed_stats_data['market_cap'] = market_cap
            processed_stats_data['employees'] = employees
            processed_stats_data['url'] = url
            processed_stats_data['description'] = description
            processed_stats_data['company_name'] = company_name
            processed_stats_data['stock_ticker'] = stock_ticker
            processed_stats_data['similiar_companies'] = similiar_companies
            processed_stats_data['volume'] = volume
            processed_stats_data['week_high'] = week_high
            processed_stats_data['week_low'] = week_low
            processed_stats_data_list.append(processed_stats_data)
        else:
            print(ticker)
            break
        time.sleep(60)
    return processed_stats_data_list

def save_to_database(processed_stats_data_list):
    table = Table('Posts', autoload=True, autoload_with=engine)
    engine.execute(table.insert(), processed_stats_data_list)

    print("Data Saved to Database successfully: ")
