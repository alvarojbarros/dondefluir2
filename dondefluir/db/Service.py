# -*- coding: utf-8 -*-

from sqlalchemy import Column, Integer, String, ForeignKey, Float
from tools.dbconnect import engine,Session
from flask_login import current_user
from dondefluir.db.Company import Company
from tools.Record import Record
from sqlalchemy.ext.declarative import declarative_base
from tools.Tools import *

Base = declarative_base()

class Service(Base,Record):
    __tablename__ = 'service'
    id = Column(Integer, primary_key=True)
    Name = Column(String(100))
    CompanyId = Column(Integer, ForeignKey(Company.id), nullable=False)
    OnlinePayment = Column(Integer)
    Price = Column(Float)

    @classmethod
    def fieldsDefinition(cls):
        res = Record.fieldsDefinition()
        res['id'] = {'Type': 'text','Hidde': True,'Readonly':1}
        res['Name'] = {'Type': 'text', 'Label': 'Nombre', 'Input': 'text'}
        res['CompanyId'] = {'Type': 'integer', 'Label': 'Empresa', 'Input': 'combo','Level':[0],'LinkTo':{'Table':'Company','Show':['Name']}}
        res['OnlinePayment'] = {'Type': 'integer', 'Label': 'Habilitar Pagos en línea', 'Input': 'checkbox'}
        res['Price'] = {'Type': 'flaot', 'Label': 'Precio', 'Input': 'number'}
        return res

    def check(self):
        if hasattr(self,"_new"):
            self.CompanyId = current_user.CompanyId
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

Base.metadata.create_all(engine)
