import json
from sqlalchemy import Column, Integer, String
from src.database.db import Base


class Posts(Base):
    __tablename__ = 'Posts'
    id = Column(Integer, primary_key=True, autoincrement=True)
    logo = Column(String(250))
    industry = Column(String(250))
    sector = Column(String(250))
    market_cap = Column(String(250))
    employees = Column(String(250))
    url = Column(String(250))
    description = Column(String(1000))
    company_name = Column(String(50))
    stock_ticker = Column(String(120))
    similiar_companies = Column(String(250))
    volume = Column(String(250))
    week_high = Column(String(250))
    week_low = Column(String(250))

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
            week_low = None):
        self.logo = logo,
        self.industry = industry,
        self.sector = sector,
        self.market_cap = market_cap,
        self.employees = employees,
        self.url = url,
        self.description = description,
        self.company_name = company_name,
        self.stock_ticker = stock_ticker,
        self.similiar_companies = similiar_companies,
        self.volume = volume,
        self.week_high = week_high,
        self.week_low = week_low

    def __repr__(self):
        return '<Post %r>' % (self.stock_ticker)

    def toDict(self):
        return json.dumps(self)