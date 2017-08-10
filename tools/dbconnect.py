from sqlalchemy import create_engine, Text
import getsettings
settings = getsettings.getSettings()
from sqlalchemy.orm import sessionmaker
from sqlalchemy.dialects.mysql import MEDIUMTEXT

engine = create_engine('mysql+pymysql://%s?charset=utf8' % settings.mysqldata, pool_recycle=3600)
Session = sessionmaker(bind=engine)

def MediumText():
    return Text().with_variant(MEDIUMTEXT(), 'mysql')


