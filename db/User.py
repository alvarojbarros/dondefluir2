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

    @classmethod
    def fieldsDefinition(cls):
        res = Record.fieldsDefinition()
        res['id'] = {'Type': 'integer','Hidde': True}
        res['Email'] = {'Type': 'text', 'Label': 'Email','Input':'text'}
        res['Password'] = {'Type': 'text', 'Label': 'Password','Input':'password'}
        res['Active'] = {'Type': 'integer', 'Label': 'Activo', 'Input': 'checkbox','Level':[0]}
        res['UserType'] = {'Type': 'integer', 'Label': 'Tipo de Usuario', 'Input': 'combo', \
            'Values': {0: 'Super',1: 'Administrador',2: 'Profesional',3: 'Cliente'},\
            'ValuesLevel':{0:[0,1,2,3],1:[1,2,3],2:[3],3:[]},'ShowIf':['UserType',["0","1","2"],-1]}
        res['CompanyId'] = {'Type': 'integer', 'Label': 'Empresa', 'Input': 'combo','Level':[0]\
            ,'LinkTo':{'Table':'Company','Show':['Name']},'ShowIf':['UserType',["0","1","2"],-1]}
        res['Name'] = {'Type': 'text', 'Label': 'Nombre', 'Input': 'text'}
        res['Title'] = {'Type': 'text', 'Label': 'Profesión', 'Input': 'text','Level':[0,1,2]}
        res['FindMe'] = {'Type': 'integer', 'Label': 'Perfil Público. Activa esta opción para que los usuarios puedan ver tu perfil en la plataforma', 'Input': 'checkbox','Level':[0,1,2],'ShowIf':['UserType',["0","1","2"],-1]}
        res['FixedSchedule'] = {'Type': 'integer', 'Label': 'Horarios Fijos', 'Input': 'checkbox','Level':[0,1,2],'ShowIf':['UserType',["0","1","2"],-1]}
        res['MinTime'] = {'Type': 'integer', 'Label': 'Tiempo Mínimo', 'Input': 'integer','Level':[0,1,2],'ShowIf':['UserType',["0","1","2"],-1]}
        res['MaxTime'] = {'Type': 'integer', 'Label': 'Tiempo Máximo', 'Input': 'integer','Level':[0,1,2],'ShowIf':['UserType',["0","1","2"],-1]}
        res['ShowDays'] = {'Type': 'integer', 'Label': 'Disponibilidad de horarios desde: Días de anterioridad mínima para solicitar citas.', 'Input': 'integer','Level':[0,1,2],'ShowIf':['UserType',["0","1","2"],-1]}
        res['ShowFromDays'] = {'Type': 'integer', 'Label': 'Disponibilidad de horarios hasta: cantidad máxima de días visibles en la agenda para los usuarios.', 'Input': 'integer','Level':[0,1,2],'ShowIf':['UserType',["0","1","2"],-1]}
        res['Phone'] = {'Type': 'text', 'Label': 'Teléfono', 'Input': 'text'}
        res['Comment'] = {'Type': 'text', 'Label': 'Perfil Profesional','Input':'textarea','rows':'4','Level':[0,1,2],'ShowIf':['UserType',["0","1","2"],-1]}
        res['Address'] = {'Type': 'text', 'Label': 'Dirección', 'Input': 'text'}
        res['City'] = {'Type': 'text', 'Label': 'Ciudad', 'Input': 'text'}
        res['EditSchedule'] = {'Type': 'integer', 'Label': 'Editar Agenda', 'Input': 'combo', \
            'Values': {0: 'SI',1: 'NO'},'Level':[0,1],'ShowIf':['UserType',["0","1","2"],-1]}
        res['Schedules'] = {'Type':[],'Label':'Horarios','Class':'UserSchedule',\
            'fieldsDefinition': UserSchedule.fieldsDefinition(),'Level':[0,1,2],'ShowIf':['UserType',["0","1","2"],-1]}
        res['Favorite'] = {'Type': 'integer', 'Label': 'Agregar a Favoritos', 'Input': 'button','Level':[0,1,2],'Persistent':False, \
            'Method':'getFavorite()','onClick': 'setFavorite(this,"1")','Class':'btn btn-primary btn-rounded waves-effect waves-light m-t-20'}
        res['ImageProfile'] = {'Type': 'text', 'Label': 'Imagen de Perfil', 'Input': 'fileinput' ,\
                               'SubLabel':'Tamaño sugerido: 300px x 300px. Peso máximo: 150kb'}
        res['NtfActivityNew'] = {'Type': 'integer', 'Label': 'Nueva Actividad', 'Input': 'checkbox'}
        res['NtfActivityCancel'] = {'Type': 'integer', 'Label': 'Actividad Cancelada', 'Input': 'checkbox'}
        res['NtfActivityChange'] = {'Type': 'integer', 'Label': 'Actividad Modificada', 'Input': 'checkbox'}
        res['NtfActivityReminder'] = {'Type': 'integer', 'Label': 'Recordatorio de Actividad ', 'Input': 'checkbox'}
        res['NtfReminderDays'] = {'Type': 'integer', 'Label': 'Días de Antelación para Recordatorio', 'Input': 'integer'}
        res['NtfReminderHours'] = {'Type': 'integer', 'Label': 'Horas de Antelación para Recordatorio', 'Input': 'integer'}
        res['NtfActivityConfirm'] = {'Type': 'integer', 'Label': 'Actividad Confirmada', 'Input': 'checkbox'}
        res['NtfActivityNewCust'] = {'Type': 'integer', 'Label': 'Nuevos Clientes', 'Input': 'checkbox','Level':[0,1,2],'ShowIf':['UserType',["0","1","2"],-1]}
        res['Closed'] = {'Type': 'integer', 'Label': 'Cerrado', 'Input': 'checkbox','Level': [0]}
        res['CreatedDate'] = {'Type': 'date','Hidde': True}
        return res

    @classmethod
    def htmlView(cls):
        Tabs = {}
        Tabs[0] = {"Name":"Información del Usuario", "Fields": [[0,["Name","Phone"]],[3,["Address","City"]] \
            ,[6,["Comment"]],[7,["Title","ImageProfile"]]]}
        Tabs[1] = {"Name":"Configuración del Usuario", "Fields": [[0,["Email","Password"]],[2,["UserType","Closed"]] \
            ,[4,["CompanyId","EditSchedule"]],[6,["FindMe"]],[7,["Favorite"]]]}
        Tabs[2] = {"Name":"Agenda","Fields": [[0,["ShowFromDays","ShowDays"]],[1,["FixedSchedule"]],[2,["MaxTime","MinTime"]],[3,["Schedules"]]]\
            ,'ShowIf':['UserType',["0","1","2"],-1]}
        Tabs[3] = {"Name":"Notificaciones por correo", "Fields": [[0,["NtfActivityNew","NtfActivityCancel"]] \
            ,[2,["NtfActivityConfirm","NtfActivityNewCust"]],[2,["NtfActivityChange"]]]}
        return Tabs

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
        if current_user.UserType==1:
            session = Session()
            records = session.query(cls).filter(cls.CompanyId==current_user.CompanyId,cls.UserType>=1)
            session.close()
        elif current_user.UserType==2:
            session = Session()
            records = session.query(cls).filter(cls.CompanyId==current_user.CompanyId, \
                or_(cls.UserType==3,cls.id==current_user.id))
            session.close()
        else:
            records = Record.getRecordList(TableClass)
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
        res['UserType'] = {self.CUST: 'Cliente'}
        if current_user.UserType==0:
            res['UserType'][self.SUPER] = 'Super'
            res['UserType'][self.ADMIN] = 'Administrador'
        if current_user.UserType==1:
            res['UserType'][self.ADMIN] = 'Administrador'
            res['UserType'][self.PROF] = 'Profesional'
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

    @classmethod
    def fieldsDefinition(cls):
        res = DetailRecord.fieldsDefinition()
        res['id'] = {'Type': 'integer','Hidde': True}
        res['StartTime'] = {'Type': 'time', 'Label': 'Desde','Input':'time','Class':'col-xs-6 p-b-20'}
        res['EndTime'] = {'Type': 'time', 'Label': 'Hasta','Input':'time','Class':'col-xs-6 p-b-20'}
        res['d1'] = {'Type': 'integer', 'Label': 'Lu', 'Input': 'checkbox','Class':'col-xs-3 col-sm-1 p-b-20'}
        res['d2'] = {'Type': 'integer', 'Label': 'Ma', 'Input': 'checkbox','Class':'col-xs-3 col-sm-1 p-b-20'}
        res['d3'] = {'Type': 'integer', 'Label': 'Mi', 'Input': 'checkbox','Class':'col-xs-3 col-sm-1 p-b-20'}
        res['d4'] = {'Type': 'integer', 'Label': 'Ju', 'Input': 'checkbox','Class':'col-xs-3 col-sm-1 p-b-20'}
        res['d5'] = {'Type': 'integer', 'Label': 'Vi', 'Input': 'checkbox','Class':'col-xs-3 col-sm-1 p-b-20'}
        res['d6'] = {'Type': 'integer', 'Label': 'Sa', 'Input': 'checkbox','Class':'col-xs-3 col-sm-1 p-b-20'}
        res['d7'] = {'Type': 'integer', 'Label': 'Do', 'Input': 'checkbox','Class':'col-xs-3 col-sm-1 p-b-20'}
        res['__order__'] = cls.fieldsOrder()
        res['__lenght__'] = "1"
        return res

    @classmethod
    def htmlView(cls):
        Tabs = {}
        Tabs['0'] = ['StartTime','EndTime']
        Tabs['1'] = ['d1','d2','d3','d4','d5','d6','d7']
        return Tabs

    @classmethod
    def fieldsOrder(cls):
        return ['id','StartTime','EndTime','d1','d2','d3','d4','d5','d6','d7']

    def fieldsDetail(self):
        return []

Index('Email', User.Email, unique=True)

Base.metadata.create_all(engine)
