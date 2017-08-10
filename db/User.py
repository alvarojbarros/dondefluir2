# -*- coding: utf-8 -*-

from flask_login import UserMixin
from sqlalchemy import Table, Column, Integer, String, ForeignKey, Time, DateTime
from tools.dbconnect import engine,MediumText
from sqlalchemy.orm import relationship
from flask_login import current_user
import tools.DBTools
from tools.Record import Record,DetailRecord
from sqlalchemy.ext.declarative import declarative_base
from tools.dbconnect import Session
from tools.Tools import *

Base = declarative_base()

class User(Base,Record,UserMixin):
    __tablename__ = 'user'
    id = Column(String(20), primary_key=True)
    Password = Column(String(20))
    Active = Column(Integer)
    UserType = Column(Integer)
    Name = Column(String(40))

    @classmethod
    def fieldsDefinition(cls):
        res = Record.fieldsDefinition()
        res['id'] = {'Type': 'text', 'Label': 'Email','Input':'text','Readonly':1}
        res['Password'] = {'Type': 'text', 'Label': 'Password','Input':'password'}
        res['Active'] = {'Type': 'integer', 'Label': 'Activo', 'Input': 'checkbox','Level':[0]}
        res['UserType'] = {'Type': 'integer', 'Label': 'Tipo de Usuario', 'Input': 'combo', \
            'Values': {0: 'Super',1: 'Administrador',2: 'Profesional',3: 'Cliente'},'Level':[0,1],\
            'ValuesLevel':{0:[0,1,2,3],1:[1,2,3],2:[3],3:[]}}
        res['Name'] = {'Type': 'text', 'Label': 'Nombre', 'Input': 'text'}
        return res

    @classmethod
    def htmlView(cls):
        Tabs = {}
        Tabs[0] = {"Name":"Información del Usuario", "Fields": [[0,["id"],["Name"]]]}
        Tabs[1] = {"Name":"Configuración del Usuario", "Fields": [[0,["id"]],[1,["Password"]],[2,["UserType"]],[3,["Active"]]]}
        return Tabs

    def filterFields(self,fields):
        if self.id:
            del fields['Password']

    @classmethod
    def getUserFromDataBase(cls,username,all=False):
        user = cls.getRecordById(username)
        if user:
            if all:
                return User(user.id,user.Password,user.Active,user.UserType)
            else:
                return user

    @classmethod
    def addNewUser(cls,username,password):
        from sqlalchemy.orm import sessionmaker
        session = Session()
        new_user = User(username,password,0,None)
        new_user.syncVersion = 0
        new_user.UserType = 3
        session.add(new_user)
        try:
            session.commit()
        except:
            session.rollback()
        user = session.query(User).filter_by(id=username).first()
        session.close()
        if user:
            return User(user.id,user.Password,user.Active,user.UserType)

    @classmethod
    def get(cls,username):
        user_data = cls.getUserFromDataBase(username)
        return user_data

    def __init__(self, id=None, Password=None, Active=None, UserType=None):
        self.id = id
        self.Password = Password
        self.Active = Active
        self.UserType = UserType

    def check(self):
        if hasattr(self,"_new") and not self.id: return Error("Completar Código")
        return True

    @classmethod
    def canUserCreate(self):
        if current_user.UserType in (0,1):
            return True

    @classmethod
    def canUserDelete(self):
        if current_user.UserType == 0:
            return True

    @classmethod
    def canUserEdit(self,record):
        if current_user.UserType in (0,1) or current_user.id==record.id:
            return True

    @classmethod
    def getUserFieldsReadOnly(cls,record,fieldname):
        if current_user.UserType==1:
            if record and record.UserType==3:
                return 1 #solo insertar nuevos
        if current_user.UserType==2:
            return 2 #nunca

Base.metadata.create_all(engine)
