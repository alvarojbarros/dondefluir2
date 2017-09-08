# -*- coding: utf-8 -*-

from sqlalchemy import Table, Column, Integer, String, ForeignKey, Date, Time, Float, or_, Boolean
from tools.dbconnect import engine,MediumText,Session
from tools.Record import Record,DetailRecord
from sqlalchemy.ext.declarative import declarative_base
from tools.Tools import *
from tools.DBTools import *
from db.User import User
from db.Company import Company
from db.Service import Service
from db.UserService import UserService
from db.Notification import Notification
from flask_login import current_user
from sqlalchemy.orm import relationship,aliased
from sqlalchemy.sql.expression import cast
from tools.MailTools import sendMailNewActivity,sendMailUpdateActivity,sendMailConfirmActivity,sendMailCancelActivity,sendMailNewCustActivity

Base = declarative_base()

class Activity(Base,Record):

    __tablename__ = 'activity'
    id = Column(Integer, primary_key=True)
    CustId = Column(Integer, ForeignKey(User.id), nullable=True)
    ProfId = Column(Integer, ForeignKey(User.id), nullable=False)
    CompanyId = Column(Integer, ForeignKey(Company.id))
    ServiceId = Column(Integer, ForeignKey(Service.id), nullable=True)
    Type = Column(Integer)
    Comment = Column(String(100))
    Image = Column(String(100))
    MaxPersons = Column(Integer)
    Price = Column(Float)
    Description = Column(MediumText())
    Users = relationship('ActivityUsers', cascade="all, delete-orphan")
    Schedules = relationship('ActivitySchedules', cascade="all, delete-orphan")
    Status = Column(Integer)
    OnlinePayment = Column(Boolean)

    StatusList = ['Tomar este curso','Anular Inscripción']

    ACTIVITY_NEW = 0
    ACTIVITY_UPDATE = 1
    ACTIVITY_CANCEL = 2
    ACTIVITY_CONFIRM = 3
    ACTIVITY_NEW_CUST = 4
    ACTIVITY_NEAR = 5

    REQUESTED = 0
    CONFIRMED = 1
    CANCELLED = 2

    TYPE_MEETING = 0
    TYPE_COURSE = 1
    TYPE_EVENT = 2
    TYPE_BLOCK = 3

    def __init__(self):
        super(self.__class__,self).__init__()
        #super().__init__()

    @classmethod
    def getEventList(cls,UserId=None,CompanyId=None,limit=None,order_by=None,desc=None):
        UserProf = aliased(User)
        session = Session()
        records = session.query(cls) \
            .filter(or_(cls.Type==1,cls.Type==2)) \
            .join(ActivitySchedules,cls.id==ActivitySchedules.activity_id)\
            .filter(ActivitySchedules.TransDate>=today()) \
            .join(Company,cls.CompanyId==Company.id)\
            .join(UserProf,cls.ProfId==UserProf.id)\
            .outerjoin(Service,cls.ServiceId==Service.id)\
            .with_entities(cls.Comment,UserProf.Name.label('ProfId') \
            ,ActivitySchedules.TransDate \
            ,ActivitySchedules.StartTime \
            ,ActivitySchedules.EndTime,cls.id,cls.Status,Company.Name.label('CompanyId')\
            ,Service.Name.label('ServiceId'))
        if UserId:
           records = records.filter(cls.ProfId==UserId)
        if CompanyId:
           records = records.filter(cls.CompanyId==CompanyId)
        if order_by and desc: records = records.order_by(ActivitySchedules.TransDate.desc())
        elif order_by: records = records.order_by(ActivitySchedules.TransDate)
        else: records = records.order_by(ActivitySchedules.TransDate)
        if limit: records = records.limit(limit)
        session.close()
        return records

    @classmethod
    def getRecordList(cls,TableClass,custId=None,limit=None,order_by=None,desc=None,ProfId=None,Alias=False):
        if Alias:
            UserProf = aliased(User)
            UserCust = aliased(User)

        session = Session()
        records = session.query(cls)
        if current_user.UserType==3:
            records = records.filter_by(CustId=current_user.id)
        if custId and current_user.UserType in (1,2):
            records = records.filter_by(CompanyId=current_user.CompanyId,CustId=custId)
        if current_user.UserType==2:
            records = records.filter_by(ProfId=current_user.id)
        records = records.join(ActivitySchedules,cls.id==ActivitySchedules.activity_id)\
            .filter(ActivitySchedules.TransDate>=today())
        if Alias:
            records = records.join(UserProf,cls.ProfId==UserProf.id)\
                .outerjoin(UserCust,cls.CustId==UserCust.id)\
                .outerjoin(Service,cls.ServiceId==Service.id)
        if current_user.UserType==0:
            records = records.filter(or_(ProfId==None,cls.ProfId==ProfId))
        if not Alias:
            records = records.with_entities(cls.Comment,cls.ProfId,ActivitySchedules.TransDate,ActivitySchedules.StartTime \
                ,ActivitySchedules.EndTime,cls.id,cls.Status,cls.CustId,cls.CompanyId,cls.ServiceId,cls.Type)
        else:
            records = records.with_entities(cls.Comment, UserProf.id.label('ProfId'), ActivitySchedules.TransDate \
                ,ActivitySchedules.StartTime , ActivitySchedules.EndTime, cls.id, cls.Status, UserCust.id.label('CustId')\
                , cls.CompanyId, Service.id.label('ServiceId'), cls.Type, UserCust.Name.label('CustName'))
        if not custId and current_user.UserType in (1,2):
            records = records.filter(Activity.CompanyId==current_user.CompanyId)
        if order_by and desc: records = records.order_by(ActivitySchedules.TransDate.desc())
        elif order_by: records = records.order_by(ActivitySchedules.TransDate)
        if limit: records = records.limit(limit)
        session.close()
        return records


    @classmethod
    def getUserFieldsReadOnly(cls,record,fieldname):
        if current_user.UserType == 1:
            if fieldname in ['Type']:
                return 1 #solo insertar nuevos
            elif fieldname in ['CompanyId']:
                return 2 # nunca
        if current_user.UserType == 2:
            if fieldname in ['CustId','Type']:
                return 1 #solo insertar nuevos
            elif fieldname in ('ProfId','CompanyId'):
                return 2 # nunca
        if current_user.UserType == 3:
            if fieldname in ['Comment']:
                return 1 #solo insertar nuevos
            elif fieldname in ('ProfId','CompanyId','TransDate','StartTime','EndTime','CustId','Type','Status','Price'):
                return 2 # nunca
        return 0 # siempre

    @classmethod
    def recordListFilters(cls):
        if current_user.UserType==2:
            return ['Type','ServiceId','Status','CustId'],\
                   {'Type':'Tipo de Actividad','ServiceId':'Servicio','Status':'Estado','CustId':'Cliente'}
        if current_user.UserType==3:
            return ['CompanyId','ServiceId','Status','ProfId']\
                   ,{'CompanyId':'Empresa','ServiceId':'Servicio','Status':'Estado','ProfId':'Profesional'}
        return ['Type','ServiceId','Status','ProfId','CustId'], \
                {'Type':'Tipo de Actividad','ServiceId': 'Servicio', 'Status': 'Estado'
                    , 'ProfId': 'Profesional','CustId':'Cliente'}

    def defaults(self):
        if current_user.UserType in (0,1,2):
            self.ProfId = current_user.id
        self.Status = 0
        self.CompanyId = current_user.CompanyId

    def check(self):
        #if not self.ServiceId:
        #    return Error("Debe Elegir un Servicio")
        if not len(self.Schedules):
            return Error("Debe ingresar horarios")
        if self.Type in (1,2) and not self.Comment:
            return Error("Debe ingresar Nombre del Curso o Evento")
        res = self.checkSchedules()
        if not res: return res
        return True

    def getOverlapHeader(self,UserId,TransDate,StartTime,EndTime,ActivityUser):
        session = Session()
        records = session.query(Activity) \
            .filter(Activity.Status!=2,ActivityUser==UserId,Activity.id!=self.id) \
            .join(ActivitySchedules,Activity.id==ActivitySchedules.activity_id)\
            .filter(ActivitySchedules.TransDate==TransDate,~ or_(ActivitySchedules.EndTime<=StartTime,ActivitySchedules.StartTime>=EndTime)) \
            .join(User,ActivityUser==User.id)\
            .with_entities(User.Name,ActivitySchedules.TransDate,ActivitySchedules.StartTime \
            ,ActivitySchedules.EndTime,Activity.id,Activity.Status)
        session.close()
        if records.count()>0:
            return True
        return False

    def getOverlapCustRow(self,UserId,TransDate,StartTime,EndTime):
        session = Session()
        records = session.query(Activity) \
            .filter(Activity.Status!=2,Activity.id!=self.id) \
            .join(ActivitySchedules,Activity.id==ActivitySchedules.activity_id)\
            .filter(ActivitySchedules.TransDate==TransDate,~ or_(ActivitySchedules.EndTime<=StartTime,ActivitySchedules.StartTime>=EndTime)) \
            .join(ActivityUsers,Activity.id==ActivityUsers.activity_id)\
            .filter(ActivityUsers.CustId==UserId)\
            .join(User,ActivityUsers.CustId==User.id)\
            .with_entities(User.Name,ActivitySchedules.TransDate,ActivitySchedules.StartTime \
            ,ActivitySchedules.EndTime,Activity.id,Activity.Status)
        session.close()
        if records.count()>0:
            return True
        return False

    def checkSchedules(self):
        if self.ProfId:
            for row in self.Schedules:
                res = self.getOverlapHeader(self.ProfId,row.TransDate,row.StartTime,row.EndTime,Activity.ProfId)
                if res: return Error('Superposición de Horarios')
                res = self.getOverlapCustRow(self.ProfId,row.TransDate,row.StartTime,row.EndTime)
                if res: return Error('Superposición de Horarios')
        if self.CustId:
            for row in self.Schedules:
                res = self.getOverlapHeader(self.CustId,row.TransDate,row.StartTime,row.EndTime,Activity.CustId)
                if res: return Error('Superposición de Horarios')
                res = self.getOverlapCustRow(self.CustId,row.TransDate,row.StartTime,row.EndTime)
                if res: return Error('Superposición de Horarios')
        for crow in self.Users:
            if crow.CustId:
                for row in self.Schedules:
                    res = self.getOverlapHeader(crow.CustId,row.TransDate,row.StartTime,row.EndTime,Activity.CustId)
                    if res: return Error('Superposición de Horarios')
                    res = self.getOverlapCustRow(crow.CustId,row.TransDate,row.StartTime,row.EndTime)
                    if res: return Error('Superposición de Horarios')
        return True

    @classmethod
    def canUserCreate(self):
        if current_user.UserType in (0,1,2):
            return True

    @classmethod
    def canUserDelete(self):
        if current_user.UserType in (0,1,2):
            return True

    @classmethod
    def canUserAddRow(self):
        if current_user.UserType in (0,1,2):
            return True

    @classmethod
    def canUserDeleteRow(self):
        if current_user.UserType in (0,1,2):
            return True

    @classmethod
    def customGetFieldsDefinition(cls,record,res):
        if current_user.UserType==3:
            res['Type']['Input'] = 'Hidde'
            res['OnlinePayment']['Input'] = 'Hidde'
        if current_user.UserType!=3 and record.Type!=0:
            res['Comment']['Label'] = 'Nombre de Curso/Evento'
        return res

    def setNotification(self,comment,user_id,type):
        ntf = Notification()
        ntf.defaults()
        ntf.UserId = user_id
        if self.Comment:
            ntf.Comment = "%s: %s" %(comment,self.Comment)
        else:
            ntf.Comment = comment
        ntf.Action = ""
        session = Session()
        res = ntf.save(session)
        if not res: return res
        return True

    def setNotificationActivityUpdate(self,UserId):
        res = True
        if self.OldFields['Status']==self.Status:
            res = self.setNotification("Actividad Modificada",UserId,self.ACTIVITY_UPDATE)
        elif self.Status==1:
            res = self.setNotification("Actividad Confirmada",UserId,self.ACTIVITY_CONFIRM)
        elif self.Status==2:
            res = self.setNotification("Actividad Cancelada",UserId,self.ACTIVITY_CANCEL)
        return res


    def setMailActivity(self,user_id,type):
        user = User.getRecordById(user_id)
        if user:
            if type==self.ACTIVITY_UPDATE and user.NtfActivityChange:
                res = sendMailUpdateActivity(user,self)
            elif type==self.ACTIVITY_NEW and user.NtfActivityNew:
                res = sendMailNewActivity(user,self)
            elif type==self.ACTIVITY_CANCEL and user.NtfActivityCancel:
                res = sendMailCancelActivity(user,self)
            elif type==self.ACTIVITY_CONFIRM and user.NtfActivityConfirm:
                res = sendMailConfirmActivity(user,self)
            elif type==self.ACTIVITY_NEW_CUST and user.NtfActivityNewCust:
                res = sendMailNewCustActivity(user,self)
        return True

    def setMailActivityUpdate(self,UserId):
        res = True
        if self.OldFields['Status']==self.Status:
            res = self.setMailActivity(UserId,self.ACTIVITY_UPDATE)
        elif self.Status==1:
            res = self.setMailActivity(UserId,self.ACTIVITY_CONFIRM)
        elif self.Status==2:
            res = self.setMailActivity(UserId,self.ACTIVITY_CANCEL)
        return res


    def afterCommitUpdate(self):
        if self.ProfId and current_user.id!=self.ProfId:
            if len(self.Users)==len(self.OldFields['Users']):
                res = self.setNotificationActivityUpdate(self.ProfId)
                if not res: return res
            else:
                res = self.setNotification("Actividad Modificada. Nuevos Clientes",self.ProfId,self.ACTIVITY_NEW_CUST)
                if not res: return res
        if self.CustId and current_user.id!=self.CustId:
            res = self.setNotificationActivityUpdate(self.CustId)
            if not res: return res
        if len(self.Users)==len(self.OldFields['Users']):
            for row in self.Users:
                if row.CustId:
                    res = self.setNotificationActivityUpdate(row.CustId)
                    if not res: return res

        if self.ProfId:
            if len(self.Users)==len(self.OldFields['Users']):
                res = self.setMailActivityUpdate(self.ProfId)
                if not res: return res
            else:
                res = self.setMailActivity(self.ProfId,self.ACTIVITY_NEW_CUST)
                if not res: return res
        if self.CustId:
            res = self.setMailActivityUpdate(self.CustId)
            if not res: return res
        if len(self.Users)==len(self.OldFields['Users']):
            for row in self.Users:
                if row.CustId:
                    res = self.setMailActivityUpdate(row.CustId)
                    if not res: return res

        return True

    def afterCommitInsert(self):
        if self.ProfId and current_user.id!=self.ProfId: self.setNotification("Nueva Actividad",self.ProfId,self.ACTIVITY_NEW)
        if self.CustId and current_user.id!=self.CustId: self.setNotification("Nueva Actividad",self.CustId,self.ACTIVITY_NEW)
        for row in self.Users:
            if row.CustId: self.setNotification("Nueva Actividad",row.CustId,self.ACTIVITY_NEW)

        if self.ProfId: self.setMailActivity(self.ProfId,self.ACTIVITY_NEW)
        if self.CustId: self.setMailActivity(self.CustId,self.ACTIVITY_NEW)
        for row in self.Users:
            if row.CustId: self.setMailActivity(row.CustId,self.ACTIVITY_NEW)

        return True

    @classmethod
    def getLinksTo(self,record_list):
        res = {'CompanyId':{},'ProfId':{},'ServiceId':{},'Type':{},'Status':{},'CustId':{}}
        session = Session()
        if current_user.UserType==3:
            records = session.query(Company)\
                .filter(Company.id.in_([r.CompanyId for r in record_list]))
        elif current_user.UserType>0:
            records = session.query(Company).filter_by(id=current_user.CompanyId)
        for record in records:
            res['CompanyId'][record.id] = [record.Name,record.Closed]
        session.close()
        session = Session()
        records = session.query(User)
        if current_user.UserType==3:
            records = records.filter(User.id.in_([r.ProfId for r in record_list]))
        elif current_user.UserType>0:
            records = records.filter(User.CompanyId==current_user.CompanyId,User.UserType<3)
        for record in records:
            res['ProfId'][record.id] = [record.Name,record.Closed]

        records = session.query(User)
        if current_user.UserType==3:
            records = records.filter(User.id.in_([r.CustId for r in record_list]))
        elif current_user.UserType>0:
            records = records.filter(User.CompanyId==current_user.CompanyId,User.UserType==3)
        for record in records:
            res['CustId'][record.id] = [record.Name,record.Closed]

        try:
            count = record_list.count()
        except:
            count = len(record_list)
        if count==1 and  record_list[0].ProfId:
            records = session.query(UserService)\
                .filter_by(UserId=record_list[0].ProfId)\
                .join(Service,Service.id==UserService.ServiceId)\
                .with_entities(Service.id,Service.Name)
        else:
            records = session.query(UserService) \
                .join(Service, Service.id == UserService.ServiceId) \
                .filter(Service.CompanyId.in_([r.CompanyId for r in record_list]))\
                .with_entities(Service.id,Service.Name)
        for record in records:
            #print(record.Name,record.id )
            res['ServiceId'][record.id] = [record.Name,0]

        res['Type'][self.TYPE_MEETING] = ['Cita',0]
        res['Type'][self.TYPE_COURSE] = ['Curso',0]
        res['Type'][self.TYPE_EVENT] = ['Evento',0]
        res['Type'][self.TYPE_BLOCK] = ['Bloqueo de Horarios',0]

        res['Status'][self.REQUESTED] = ['Solicitada',0]
        res['Status'][self.CANCELLED] = ['Confirmada',0]
        res['Status'][self.CONFIRMED] = ['Cancelada',0]


        session.close()
        return res

    @classmethod
    def getRecordTitle(self):
        return ['ProfId','CustId','ServiceId']


class ActivityUsers(Base,DetailRecord):
    __tablename__ = 'activityusers'
    id = Column(Integer, primary_key=True)
    activity_id = Column(Integer, ForeignKey('activity.id'), nullable=False)
    CustId = Column(Integer, ForeignKey(User.id), nullable=False)

class ActivitySchedules(Base,DetailRecord):
    __tablename__ = 'activityschedules'
    id = Column(Integer, primary_key=True)
    activity_id = Column(Integer, ForeignKey('activity.id'), nullable=False)
    TransDate = Column(Date)
    StartTime = Column(Time)
    EndTime = Column(Time)

    @classmethod
    def getUserFieldsReadOnly(cls,fieldname):
        if current_user.UserType == 3:
            if fieldname in ('TransDate','StartTime','EndTime'):
                return 2 # nunca
        return 0 # siempre


Base.metadata.create_all(engine)
