# -*- coding: utf-8 -*-

from sqlalchemy import Table, Column, Integer, String, DateTime, ForeignKey
from tools.dbconnect import engine,Session,MediumText
from tools.Record import Record
from sqlalchemy.ext.declarative import declarative_base
from tools.Tools import *
from db.User import User
from flask_login import current_user

Base = declarative_base()

class Notification(Base,Record):

    __tablename__ = 'notification'
    id = Column(Integer, primary_key=True)
    UserId = Column(Integer, ForeignKey(User.id), nullable=True)
    Status = Column(Integer)
    Comment = Column(String(255))
    Action = Column(String(255))
    TransDate = Column(DateTime)
    Description = Column(MediumText())

    def __init__(self):
        super(self.__class__,self).__init__()
        #super().__init__()

    def defaults(self):
        self.TransDate = now()
        self.Status = 0

    @classmethod
    def canUserCreate(self):
        return False

    @classmethod
    def canUserDelete(cls):
        return False

    @classmethod
    def getRecordList(cls,TableClass,limit=None,order_by=None,desc=None):
        session = Session()
        records = session.query(cls).filter_by(UserId=current_user.id).order_by(Notification.TransDate.desc())
        session.close()
        return records

    def afterSaveJS(self):
        return 'getNotifications()'

    @classmethod
    def getLinksTo(cls):
        res = {'Status': {}}
        res['Status'][0] = ['No Leída',0]
        res['Status'][1] = ['Leída',0]
        return res

Base.metadata.create_all(engine)
