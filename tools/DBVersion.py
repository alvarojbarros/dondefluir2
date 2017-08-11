from sqlalchemy import Table, Column, Integer, String
from tools.dbconnect import engine,Session
from sqlalchemy.ext.declarative import declarative_base
import settings

Base = declarative_base()

class DBVersion(Base):
    __tablename__ = 'dbversion'
    id = Column(Integer, primary_key=True)
    Version = Column(Integer)

Base.metadata.create_all(engine)

session = Session()
record = session.query(DBVersion).first()
if not record:
    record = DBVersion()
    try:
        record.Version = max(settings.versions.keys())
    except:
        record.Version = 1
    session.add(record)
    session.commit()
session.close()