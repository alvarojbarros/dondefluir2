# -*- coding: utf-8 -*-

from sqlalchemy import Table, Column, Integer, String, DateTime, ForeignKey
from tools.dbconnect import engine,Session,MediumText
from tools.Record import Record
from sqlalchemy.ext.declarative import declarative_base
from tools.Tools import *
from dondefluir.db.User import User
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

    @classmethod
    def fieldsDefinition(cls):
        res = Record.fieldsDefinition()
        res['id'] = {'Type': 'integer','Hidde': True}
        res['UserId'] = {'Type': 'integer','Hidde': True }
        res['Comment'] = {'Type': 'text', 'Label': 'Comentario', 'Input':'text','Readonly':1}
        res['Action'] = {'Type': 'text','Hidde': True}
        res['Status'] = {'Type': 'integer', 'Label': 'Estado', 'Input': 'combo','Values': {0: 'No Leída',1: 'Leída'}}
        res['TransDate'] = {'Type': 'datetime','Label':'Fecha', 'Input':'datetime','Readonly':1}
        res['Description'] = {'Type': 'text', 'Label': 'Descripción','Input':'textarea','rows':'4','Readonly':1}
        return res

    @classmethod
    def htmlView(cls):
        Tabs = {}
        Tabs[0] = {"Fields": [[0,["Comment"]],[1,["Status"]],[2,["Fecha"]],[3,["Description"]]]}
        return Tabs

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

Base.metadata.create_all(engine)
