# -*- coding: utf-8 -*-

from sqlalchemy import Table, Column, Integer, String, ForeignKey, Time
from tools.dbconnect import engine,MediumText
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

    @classmethod
    def fieldsDefinition(cls):
        res = Record.fieldsDefinition()
        res['id'] = {'Type': 'text', 'Hidde':True, 'Label': 'Código','Input':'integer','Readonly':1}
        res['Active'] = {'Type': 'integer', 'Label': 'Activo', 'Input': 'checkbox','Level':[0]}
        res['Name'] = {'Type': 'text', 'Label': 'Nombre', 'Input': 'text'}
        res['Phone'] = {'Type': 'text', 'Label': 'Teléfono', 'Input': 'text'}
        res['Email'] = {'Type': 'text', 'Label': 'Email', 'Input': 'text'}
        res['WebSite'] = {'Type': 'text', 'Label': 'Web Site', 'Input': 'text'}
        res['Comment'] = {'Type': 'text', 'Label': 'Comentario', 'Input':'textarea','rows':'4'}
        res['Address'] = {'Type': 'text', 'Label': 'Dirección', 'Input': 'text'}
        res['City'] = {'Type': 'text', 'Label': 'Ciudad', 'Input': 'text'}
        res['ImageProfile'] = {'Type': 'text', 'Label': 'Imagen de Perfil. Tamaño sugerido: 300px x 300px. Peso máximo: 150kb', 'Input': 'fileinput'}
        res['OnlinePayment'] = {'Type': 'integer', 'Label': 'Habilitar Pagos en línea', 'Input': 'checkbox'}
        res['KeyPayco'] = {'Type': 'text', 'Label': 'Clave ePayco', 'Input': 'text'}
        res['Closed'] = {'Type': 'integer', 'Label': 'Cerrado', 'Input': 'checkbox','Level': [0]}
        return res

    @classmethod
    def htmlView(cls):
        Tabs = {}
        Tabs[0] = {"Name":"", "Fields": [[0,["Active"]],[1,["Name"]],[2,["Address","City"]],[3,["Phone"]],[4,["Email"]],[5,["WebSite"]],[6,["Comment"]] \
            ,[7,["ImageProfile"]],[8,["KeyPayco","OnlinePayment"]],[9,["Closed"]]]}
        return Tabs

    def defaults(self):
        self.Closed = 0

    def check(self):
        if not self.Name: return Error("Debe Completar el Nombre")
        return True

    @classmethod
    def canUserDelete(self):
        if current_user.UserType == 0:
            return True

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
