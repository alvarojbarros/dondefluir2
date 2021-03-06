# -*- coding: utf-8 -*-

from sqlalchemy import Table, Column, Integer, String, ForeignKey, Time, Index
from tools.dbconnect import engine
from flask_login import current_user
from db.Service import Service
from db.Company import Company
from db.User import User
from tools.Record import Record
from sqlalchemy.ext.declarative import declarative_base
from tools.dbconnect import Session
from tools.Tools import *

Base = declarative_base()

class UserService(Base,Record):
    __tablename__ = 'userservice'
    id = Column(Integer, primary_key=True)
    UserId = Column(Integer, ForeignKey(User.id), nullable=False)
    CompanyId = Column(Integer, ForeignKey(Company.id), nullable=False)
    ServiceId = Column(Integer, ForeignKey(Service.id), nullable=False)

    def beforeInsert(self):
        self.CompanyId = current_user.CompanyId
        return True

    def check(self):
        if not self.UserId: return Error("Completar Usuario")
        if not self.ServiceId: return Error("Completar Servicio")
        return True

    @classmethod
    def getRecordList(cls,TableClass,limit=None,order_by=None,desc=None):
        session = Session()
        records = session.query(cls)
        if current_user.UserType == 1:
            records = records.filter_by(CompanyId=current_user.CompanyId)
        session.close()
        return records

    @classmethod
    def getRecordTitle(self):
        return ['UserId','ServiceId']

    @classmethod
    def getLinksTo(self,record_list):
        res = {}
        res['ServiceId'] = {}
        session = Session()
        records = session.query(Service)
        if current_user.UserType>0:
            records = records.filter_by(CompanyId=current_user.CompanyId)
        for record in records:
            res['ServiceId'][record.id] = [record.Name,0]
        session.close()

        res['UserId'] = {}
        records = session.query(User).filter(User.UserType<3)
        if current_user.UserType>0:
            records = records.filter_by(CompanyId=current_user.CompanyId)
        for record in records:
            res['UserId'][record.id] = [record.Name,0]
        session.close()
        return res


Index('UserService', UserService.UserId, UserService.ServiceId, unique=True)

Base.metadata.create_all(engine)
