import configparser
import pathlib

from fastapi import HTTPException, status
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError

from src.conf.config import settings

# file_config = pathlib.Path(__file__).parent.parent.joinpath('conf/config.ini')
# config = configparser.ConfigParser()
# config.read(file_config)
#
# username = config.get('DB', 'user')
# password = config.get('DB', 'password')
# db_name = config.get('DB', 'db_name')
# domain = config.get('DB', 'domain')
# port = config.get('DB', 'port')

SQLALCHEMY_DATABASE_URL = settings.sqlalchemy_database_url

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    except SQLAlchemyError as err:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(err))
    finally:
        db.close()
