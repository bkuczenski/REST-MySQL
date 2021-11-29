from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

SQLALCHEMY_DATABASE_URL = "mysql+pymysql://{}:{}@{}/{}".format(os.getenv('MYSQL_ROOT_USER'), os.getenv('MYSQL_ROOT_PASSWORD'), 
                                                                    os.getenv('MYSQL_HOST'), db=os.getenv('MYSQL_DB_NAME'))

engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()