from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

engine = create_engine('mysql+pymysql://root1:webdiR123@R@167.172.146.92/stocks_data', convert_unicode=True)
# engine = create_engine('mysql+pymysql://root:root@123@localhost/stock_fundamental_data', convert_unicode=True)

db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=True,
                                         bind=engine))
Base = declarative_base()
Base.query = db_session.query_property()

def init_db():
    from src.models.post import Posts
    from src.models.post import Scores1
    Base.metadata.create_all(bind=engine)
