from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

engine = create_engine('mysql+pymysql://root:n0NyF7PF2ii2wA1P@35.203.46.140/stocks_fundamental_data', convert_unicode=True)

db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=True,
                                         bind=engine))
Base = declarative_base()
Base.query = db_session.query_property()

def init_db():
    from src.models.post import Posts
    from src.models.post import Scores
    Base.metadata.create_all(bind=engine)