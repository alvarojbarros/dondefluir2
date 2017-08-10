# -*- coding: utf-8 -*-

from sqlalchemy import Table, Column, Integer, String, ForeignKey, DateTime
from tools.dbconnect import engine,MediumText,Session
from tools.Record import Record
from sqlalchemy.ext.declarative import declarative_base
from tools.Tools import *
from dondefluir.db.User import User
from dondefluir.db.Company import Company
from flask_login import current_user

Base = declarative_base()

class UserNote(Base,Record):

    __tablename__ = 'usernote'
    id = Column(Integer, primary_key=True)
    UserId = Column(Integer, ForeignKey(User.id), nullable=False)
    ProfId = Column(Integer, ForeignKey(User.id), nullable=False)
    CompanyId = Column(Integer, ForeignKey(Company.id))
    TransDate = Column(DateTime)
    Note = Column(MediumText())

    @classmethod
    def fieldsDefinition(cls):
        res = Record.fieldsDefinition()
        res['id'] = {'Type': 'integer','Hidde': True}
        res['UserId'] = {'Type': 'integer','Hidde': True}
        res['ProfId'] = {'Type': 'integer', 'Hidde': True}
        res['CompanyId'] = {'Type': 'text', 'Hidde': True}
        res['TransDate'] = {'Type': 'datetime', 'Hidde': True}
        res['Note'] = {'Type': 'text', 'Label': 'Nota','Input':'textarea','rows':'4','cols':'50'}
        return res

    @classmethod
    def getRecordList(cls,TableClass,custId=None,limit=None,order_by=None,desc=None):
        session = Session()
        if current_user.UserType==3:
            records = session.query(cls).filter_by(UserId=current_user.id)\
                .join(User,User.id==cls.ProfId)\
                .with_entities(User.Name,cls.TransDate,cls.Note)\
                .order_by(UserNote.TransDate.desc())
        elif current_user.UserType in (0,1):
            records = session.query(cls).filter_by(CompanyId=current_user.CompanyId,UserId=custId)\
                .join(User,User.id==cls.ProfId)\
                .with_entities(User.Name,cls.TransDate,cls.Note)\
                .order_by(UserNote.TransDate.desc())
        elif current_user.UserType==2:
            records = session.query(cls).filter_by(CompanyId=current_user.CompanyId,UserId=custId,ProfId=current_user.id)\
                .join(User,User.id==cls.ProfId)\
                .with_entities(User.Name,cls.TransDate,cls.Note)\
                .order_by(UserNote.TransDate.desc())
        session.close()
        return records

    @classmethod
    def getUserFieldsReadOnly(cls,record,fieldname):
        if current_user.UserType in (1,2):
            if fieldname in ('ProfId','TransDate','CompanyId'):
                return 2 #solo insertar nuevos

    def defaults(self):
        self.TransDate = now()
        self.ProfId = current_user.id
        self.CompanyId = current_user.CompanyId

    @classmethod
    def canUserDelete(self):
        return False

Base.metadata.create_all(engine)
