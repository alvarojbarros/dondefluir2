# -*- coding: utf-8 -*-

from sqlalchemy import Table, Column, Integer, String, ForeignKey, Time
from tools.dbconnect import engine,MediumText,Session
from tools.Record import Record
from sqlalchemy.ext.declarative import declarative_base
from tools.Tools import *
from flask_login import current_user

Base = declarative_base()

class Company(Base,Record):
    __tablename__ = 'company'
    id = Column(Integer, primary_key=True)
    Active = Column(Integer)
    Name = Column(String(40))
    Phone = Column(String(40))
    Email = Column(String(40))
    WebSite = Column(String(40))
    Comment = Column(MediumText())
    City = Column(String(100))
    Address = Column(String(100))
    ImageProfile = Column(String(100))
    OnlinePayment = Column(Integer)
    KeyPayco = Column(String(50))
    Closed = Column(Integer)

    def defaults(self):
        self.Closed = 0

    def check(self):
        if not self.Name: return Error("Debe Completar el Nombre")
        return True

    @classmethod
    def canUserDelete(self):
        if current_user.UserType == 0:
            return True
        else:
            return False

    @classmethod
    def getRecordTitle(self):
        return ['Name']

    @classmethod
    def canUserEdit(cls,record):
        if current_user.UserType==3:
            return False
        return True

    @classmethod
    def getUserFieldsReadOnly(cls,record,fieldname):
        if current_user.UserType==3:
            return 2
        return 0

Base.metadata.create_all(engine)
