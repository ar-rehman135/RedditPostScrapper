import json
from sqlalchemy import Column, Integer, String, DateTime, Text
from src.database.db import Base


class Posts(Base):
    __tablename__ = 'Posts'
    id = Column(Integer, primary_key=True, autoincrement=True)
    logo = Column(String(350))
    industry = Column(String(350))
    sector = Column(String(350))
    market_cap = Column(String(350))
    employees = Column(String(350))
    url = Column(String(350))
    description = Column(Text)
    company_name = Column(String(350))
    stock_ticker = Column(String(350), unique=True)
    similiar_companies = Column(String(350))
    volume = Column(String(350))
    week_high = Column(String(350))
    week_low = Column(String(350))
    dateTime = Column(String(350))
    def __init__(self,
            logo=None,
            industry = None,
            sector = None,
            market_cap = None,
            employees = None,
            url = None,
            description = None,
            company_name = None,
            stock_ticker = None,
            similiar_companies = None,
            volume = None,
            week_high = None,
            week_low = None,
                 dateTime = None,
                 ):
        self.logo = logo
        self.industry = industry
        self.sector = sector
        self.market_cap = market_cap
        self.employees = employees
        self.url = url
        self.description = description
        self.company_name = company_name
        self.stock_ticker = stock_ticker
        self.similiar_companies = similiar_companies
        self.volume = volume
        self.week_high = week_high
        self.week_low = week_low
        self.dateTime = dateTime

    def __repr__(self):
        return '<Post %r>' % (self.stock_ticker)

    def toDict(self):
        return json.dumps(self)


class Scores(Base):
    __tablename__ = 'StockScoresPerDay'
    id = Column(Integer, primary_key=True, autoincrement=True)
    stock_ticker = Column(String(350))
    date = Column(DateTime(350))
    sub_reddit = Column(String(350))
    mention = Column(String(350))
    score = Column(String(350))
    def __init__(self, stock_ticker = None, date = None, sub_reddit = None, mention =None, score = None):
        self.stock_ticker = stock_ticker
        self.date = date
        self.sub_reddit = sub_reddit
        self.mention = mention
        self.score = score

    def __repr__(self):
        return '<StockScoresPerDay %r>' % (self.stock_ticker)

    def toDict(self):
        return json.dumps(self)