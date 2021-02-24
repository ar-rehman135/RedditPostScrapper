from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

engine = create_engine('mysql+pymysql://root:root@123@localhost/stock_fundamentals_data', convert_unicode=True)
Base = declarative_base()

def init_db():
    from src.models.post import Posts
    Base.metadata.create_all(bind=engine)