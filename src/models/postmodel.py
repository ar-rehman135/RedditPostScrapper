import json
from sqlalchemy import Column, Integer, String, Boolean
from src.database.db import Base


class Posts(Base):
    __tablename__ = 'Stock_Data'
    id = Column(Integer, primary_key=True, autoincrement=True)
    logo = Column(String(250))
    listDate = Column(String(250))
    cik = Column(String(250))
    boomberg = Column(String(250))
    figi = Column(String(250))
    lei = Column(String(250))
    sci = Column(String(250))
    industry = Column(String(250))
    sector = Column(String(250))
    market_cap = Column(String(250))
    employees = Column(String(250))
    phone = Column(String(250))
    ceo = Column(String(250))
    url = Column(String(250))
    description = Column(String(1000))
    exchange = Column(String(1000))
    company_name = Column(String(50))
    stock_ticker = Column(String(120))
    exchange_symbol = Column(String(120))
    hq_address = Column(String(120))
    hq_state = Column(String(120))
    hq_country = Column(String(120))
    type = Column(String(120))
    updated = Column(String(120))
    tags = Column(String(120))
    similiar_companies = Column(String(250))
    active = Column(Boolean)
    volume = Column(String(250))
    week_high = Column(String(250))
    week_low = Column(String(250))

    def __init__(self,
            logo=None,
            listdate=None,
            cik=None,
            bloomberg=None,
            figi = None,
            lei = None,
            sic = None,
            country = None,
            industry = None,
            sector = None,
            market_cap = None,
            employees = None,
            phone = None,
            ceo = None,
            url = None,
            description = None,
            exchange = None,
            company_name = None,
            stock_ticker = None,
            exchange_symbol = None,
            hq_address = None,
            hq_state = None,
            hq_country = None,
            type = None,
            updated = None,
            tags = None,
            similiar_companies = None,
            volume = None,
            week_high = None,
            week_low = None):
        self.logo = logo,
        self.listdate = listdate,
        self.cik = cik,
        self.bloomberg = bloomberg,
        self.figi = figi,
        self.lei = lei,
        self.sic = sic,
        self.country = country,
        self.industry = industry,
        self.sector = sector,
        self.market_cap = market_cap,
        self.employees = employees,
        self.phone = phone,
        self.ceo = ceo,
        self.url = url,
        self.description = description,
        self.exchange = exchange,
        self.company_name = company_name,
        self.stock_ticker = stock_ticker,
        self.exchange_symbol = exchange_symbol,
        self.hq_address = hq_address,
        self.hq_state = hq_state,
        self.hq_country = hq_country,
        self.type = type,
        self.updated = updated,
        self.tags = tags,
        self.similiar_companies = similiar_companies,
        self.volume = volume,
        self.week_high = week_high,
        self.week_low = week_low

    def __repr__(self):
        return '<Post %r>' % (self.stock_ticker)

    def toDict(self):
        return json.dumps(self)