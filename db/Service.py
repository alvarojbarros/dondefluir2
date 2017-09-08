# -*- coding: utf-8 -*-

from sqlalchemy import Column, Integer, String, ForeignKey, Float, Boolean
from tools.dbconnect import engine,Session
from flask_login import current_user
from db.Company import Company
from tools.Record import Record
from sqlalchemy.ext.declarative import declarative_base
from tools.Tools import *

Base = declarative_base()

class Service(Base,Record):
    __tablename__ = 'service'
    id = Column(Integer, primary_key=True)
    Name = Column(String(100))
    CompanyId = Column(Integer, ForeignKey(Company.id), nullable=False)
    OnlinePayment = Column(Boolean)
    Price = Column(Float)

    def beforeInsert(self):
        self.CompanyId = current_user.CompanyId
        return True

    def check(self):
        if not self.Name: return Error("Debe Completar el Nombre")
        return True

    @classmethod
    def getRecordList(cls,TableClass,limit=None,order_by=None,desc=None):
        if current_user.UserType==(1,2):
            session = Session()
            records = session.query(TableClass).filter_by(CompanyId=current_user.CompanyId)
            session.close()
        elif current_user.UserType==1:
            session = Session()
            records = session.query(TableClass).filter_by(CompanyId=current_user.CompanyId)
            session.close()
        else:
            records = Record.getRecordList(TableClass)
        return records

    @classmethod
    def getRecordTitle(self):
        return ['Name']

    @classmethod
    def getLinksTo(self,record_list):
        res = {}
        res['CompanyId'] = {}
        session = Session()
        records = session.query(Company)
        for record in records:
            res['CompanyId'][record.id] = [record.Name,0]
        session.close()
        return res


Base.metadata.create_all(engine)
