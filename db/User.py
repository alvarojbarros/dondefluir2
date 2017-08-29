# -*- coding: utf-8 -*-

from flask_login import UserMixin
from sqlalchemy import Table, Column, Integer, String, ForeignKey, Time, DateTime, Index, or_, Date, Boolean
from tools.dbconnect import engine,MediumText,Session
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from flask_login import current_user
from db.Company import Company
import tools.DBTools
from tools.Record import Record,DetailRecord
from sqlalchemy.ext.declarative import declarative_base
from tools.Tools import *
import enum

Base = declarative_base()

class User(Base,Record,UserMixin):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True,autoincrement=True)
    Email = Column(String(50))
    Password = Column(String(20))
    Active = Column(Boolean)
    UserType = Column(Integer)
    CompanyId = Column(Integer, ForeignKey(Company.id))
    Name = Column(String(40))
    Title = Column(String(40))
    FindMe = Column(Boolean)
    EditSchedule = Column(Integer)
    FixedSchedule = Column(Boolean)
    MinTime = Column(Integer)
    MaxTime = Column(Integer)
    ShowDays = Column(Integer)
    Phone = Column(String(40))
    Comment = Column(MediumText())
    City = Column(String(100))
    Address = Column(String(100))
    ImageProfile = Column(String(100))
    NtfActivityCancel = Column(Boolean)
    NtfActivityNew = Column(Boolean)
    NtfActivityChange = Column(Boolean)
    NtfActivityReminder = Column(Boolean)
    NtfReminderDays = Column(Integer)
    NtfReminderHours = Column(Integer)
    ShowFromDays = Column(Integer)
    NtfActivityConfirm = Column(Boolean)
    NtfActivityNewCust = Column(Boolean)
    Closed = Column(Boolean)
    CreatedDate = Column(Date)

    Schedules = relationship('UserSchedule', cascade="all, delete-orphan")

    #def __repr__(self):
    #    return "<User(Active='%s', AcessGroup='%s', Password='%s')>" % (self.Active, self.AcessGroup, self.Password)

    SUPER = 0
    ADMIN = 1
    PROF = 2
    CUST = 3

    def filterFields(self,fields):
        #filtro de campo por tipo de usuario
        filters = {3:['Title','FindMe','FixedSchedule','MinTime','MaxTime','EditSchedule','Schedules','ShowDays','ShowFromDays','Comment']}
        if self.UserType in filters:
            filters = filters[self.UserType]
            for fn in filters:
                if fn in fields:
                    del fields[fn]
        if (current_user.id==self.id) and (self.EditSchedule):
            del fields['Schedules']
        if self.id and current_user.UserType!=0:
            del fields['Password']

    @classmethod
    def getUserFromDataBase(cls,id):
        user = cls.getRecordById(id)
        if user:
            return user

    @classmethod
    def getUserIdByEmail(cls,email):
        session = Session()
        record = session.query(cls).filter_by(Email=email).first()
        if not record:
            return
        id = record.id
        session.close()
        return id

    def defaults(self):
        self.syncVersion = 0
        self.UserType = 3
        self.Closed = 0
        self.NtfActivityConfirm = 1
        self.NtfActivityCancel = 1
        self.NtfActivityChange = 1
        self.NtfActivityNew = 1
        self.CreatedDate = today()

    @classmethod
    def addNewUser(cls,email,password,name):
        session = Session()
        new_user = User(Password=password)
        new_user.syncVersion = 0
        new_user.UserType = 3
        new_user.Closed = 0
        new_user.NtfActivityConfirm = 1
        new_user.NtfActivityCancel = 1
        new_user.NtfActivityChange = 1
        new_user.NtfActivityNew = 1
        new_user.Name = name
        new_user.Email = email
        new_user.CreatedDate = today()
        session.add(new_user)
        try:
            session.commit()
            from tools.MailTools import sendNewUserMail
            sendNewUserMail(email,name,password)
        except Exception as e:
            session.rollback()
            session.close()
            return Error(str(e))
        user = session.query(User).filter_by(Email=email).first()
        session.close()
        if user:
            return User(user.id,user.Password,user.Active,user.UserType,user.CompanyId)

    @classmethod
    def get(cls,username):
        user_data = cls.getUserFromDataBase(username)
        return user_data

    def __init__(self, id=None, Password=None, Active=0, UserType=3, CompanyId=None, EditSchedule=None):
        self.id = id
        self.Password = Password
        self.Active = Active
        self.UserType = UserType
        self.CompanyId = CompanyId
        self.EditSchedule = EditSchedule

    def check(self):
        if self.UserType==3:
            self.CompanyId = None
        if current_user.UserType in (1,2) and self.UserType in (1,2,3):
            self.CompanyId = current_user.CompanyId
        if current_user.UserType in (1,2) and not self.CompanyId: return Error("Completar Empresa")
        return True

    @classmethod
    def getRecordList(cls,TableClass,limit=None,order_by=None,desc=None):
        session = Session()
        records = session.query(cls)
        if current_user.UserType==1:
            records = records.filter(cls.CompanyId==current_user.CompanyId,cls.UserType>=1)
        elif current_user.UserType==2:
            records = records.filter(cls.CompanyId==current_user.CompanyId, \
                or_(cls.UserType==3,cls.id==current_user.id))
        session.close()
        return records

    @classmethod
    def canUserCreate(self):
        if current_user.UserType in (0,1,2):
            return True

    @classmethod
    def canUserDelete(self):
        if current_user.UserType == 0:
            return True

    @classmethod
    def canUserEdit(self,record):
        if current_user.id==record.id:
            return True
        elif record.UserType==None:
            return True
        elif current_user.UserType<record.UserType:
            return True
            return False

    @classmethod
    def getUserFieldsReadOnly(cls,record,fieldname):
        if fieldname=="Favorite":
            return
        if record and record.id==current_user.id:
            return
        if current_user.UserType==1:
            if record and record.UserType==3:
                return 1 #solo insertar nuevos
        if current_user.UserType==2:
            if record and record.UserType in (0,1,2):
                return 2 #nunca
            if record and record.UserType==3:
                return 1 #solo insertar nuevos

    @classmethod
    def customGetFieldsDefinition(cls,record,res):
        if record and record.id==current_user.id:
            res['UserType']['Hidde'] = True
        return res

    def getFavorite(self):
        from db.UserFavorite import UserFavorite
        session = Session()
        record = session.query(UserFavorite).filter_by(UserId=current_user.id,FavoriteId=self.id).first()
        if record and record.Checked:
            session.close()
            return 1
        session.close()
        return 0

    @classmethod
    def getRecordTitle(self):
        return ['Name']

    @classmethod
    def getLinksTo(self):
        res = {}
        res['UserType'] = {self.CUST: ['Cliente',0]}
        if current_user.UserType==0:
            res['UserType'][self.SUPER] = ['Super',0]
            res['UserType'][self.ADMIN] = ['Administrador',0]
            res['UserType'][self.PROF] = ['Profesional', 0]
        if current_user.UserType==1:
            res['UserType'][self.ADMIN] = ['Administrador',0]
            res['UserType'][self.PROF] = ['Profesional',0]
        res['CompanyId'] = {}
        session = Session()
        records = session.query(Company)
        for record in records:
            res['CompanyId'][record.id] = [record.Name,record.Closed]
        session.close()

        return res

class UserSchedule(Base,DetailRecord):
    __tablename__ = 'userschedule'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    StartTime = Column(Time)
    EndTime = Column(Time)
    d1 = Column(Boolean)
    d2 = Column(Boolean)
    d3 = Column(Boolean)
    d4 = Column(Boolean)
    d5 = Column(Boolean)
    d6 = Column(Boolean)
    d7 = Column(Boolean)

Index('Email', User.Email, unique=True)

Base.metadata.create_all(engine)
