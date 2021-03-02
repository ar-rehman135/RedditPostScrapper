
import argparse
from src.reddit_scrap import *
from collections import Counter
from src.database.db import init_db
def main():
    # Instantiate the parser
    parser = argparse.ArgumentParser(description='AutoDD Optional Parameters')

    parser.add_argument('--interval', nargs='?', const=24, type=int, default=24,
                    help='Choose a time interval in hours to filter the results, default is 24 hours')

    parser.add_argument('--sub', nargs='?', const='pennystocks', type=str, default='pennystocks',
                    help='Choose a different subreddit to search for tickers in, default is pennystocks')

    parser.add_argument('--min', nargs='?', const=10, type=int, default=10,
                    help='Filter out results that have less than the min score, default is 10')

    parser.add_argument('--minprice', nargs='?', const=0, type=int, default=0,
                    help='Filter out results less than the min price set, default is 0')

    parser.add_argument('--maxprice', nargs='?', const=9999999, type=int, default=9999999,
                    help='Filter out results more than the max price set, default is 9999999')

    parser.add_argument('--advanced', default=False, action='store_true',
                    help='Using this parameter shows advanced yahoo finance information on the ticker')

    parser.add_argument('--sort', nargs='?', const=1, type=int, default=1,
                    help='Sort the results table by descending order of score, 1 = sort by total score, 2 = sort by recent score, 3 = sort by previous score, 4 = sort by change in score, 5 = sort by # of rocket emojis')

    parser.add_argument('--allsub', default=True, action='store_true',
                    help='Using this parameter searchs from one subreddit only, default subreddit is r/pennystocks.')

    parser.add_argument('--psaw', default=False, action='store_true',
                    help='Using this parameter selects psaw (push-shift) as the reddit scraper over praw (reddit-api)')

    parser.add_argument('--no-threads', action='store_false', dest='threads',
                    help='Disable multi-tasking (enabled by default). Multi-tasking speeds up downloading of data.')

    parser.add_argument('--csv', default=False, action='store_true',
                    help='Using this parameter produces a table_records.csv file, rather than a .txt file')

    parser.add_argument('--filename', nargs='?', const='table_records', type=str, default='table_records',
                    help='Change the file name from table_records to whatever you wish')

    args = parser.parse_args()

    print("Getting Tickers from Polygon")
    get_all_tickers_data()

    print("Getting submissions...")
    # call reddit api to get results
    current_scores, current_rocket_scores, prev_scores, prev_rocket_scores = get_submission_generators(args.interval, args.sub, args.allsub, args.psaw)

    print("Populating results...")
    results_df = populate_df(current_scores, prev_scores, args.interval)
    filter_df(results_df, args.min)

    # print("Counting rockets...")
    # rockets = Counter(current_rocket_scores) + Counter(prev_rocket_scores)
    # results_df.insert(loc=4, column='Rockets', value=pd.Series(rockets))
    # results_df = results_df.fillna(value=0).astype({'Rockets': 'int32'})


if __name__ == '__main__':
    init_db()
    main()
