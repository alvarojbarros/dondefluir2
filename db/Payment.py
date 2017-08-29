# -*- coding: utf-8 -*-

from sqlalchemy import Table, Column, Integer, String, ForeignKey, Float, DateTime
from tools.dbconnect import engine,Session
from flask_login import current_user
from db.Company import Company
from db.Activity import Activity
from db.User import User
from tools.Record import Record
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Payment(Base,Record):
    __tablename__ = 'payment'
    id = Column(Integer, primary_key=True)
    UserId = Column(Integer, ForeignKey(User.id), nullable=True)
    CompanyId = Column(Integer, ForeignKey(Company.id), nullable=False)
    ActivityId = Column(Integer, ForeignKey(Activity.id), nullable=False)
    ResponseCode = Column(Integer)
    Response = Column(String(30))
    Amount = Column(Float)
    TransDate = Column(DateTime)
    Reference = Column(String(30))
    Reason = Column(String(30))
    TransactionId = Column(String(30))
    Currency = Column(String(10))
    BankName = Column(String(100))
    AutorizationCode = Column(String(20))

    @classmethod
    def canUserCreate(self):
        return False

    @classmethod
    def canUserDelete(cls):
        return False

    @classmethod
    def canUserEdit(cls,record):
        return False

    @classmethod
    def getRecordList(cls,TableClass,limit=None,order_by=None,desc=None):
        session = Session()
        records = session.query(TableClass)
        if current_user.UserType==1:
            records = records.filter_by(CompanyId=current_user.CompanyId)
        elif current_user.UserType==3:
            records = records.filter_by(UserId=current_user.id)
        if order_by and desc: records = records.order_by(TableClass.c[order_by].desc())
        elif order_by: records = records.order_by(TableClass.c[order_by])
        if limit: records = records.limit(limit)
        session.close()
        return records


Base.metadata.create_all(engine)
