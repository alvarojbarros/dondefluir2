# -*- coding: utf-8 -*-

from sqlalchemy import Column, Integer
from tools.dbconnect import Session
from sqlalchemy.orm import sessionmaker
from tools.Tools import *
from flask_login import current_user
import copy
import threading

class Record(object):
    syncVersion = Column(Integer)

    @classmethod
    def fieldsDefinition(cls):
        res = {}
        res['syncVersion'] = {'Type': 'integer','Hidde': True}
        res['id'] = {'Type': 'integer','Hidde': True}
        return res

    def defaults(self):
        pass

    def filterFields(self,fields):
        return fields

    def check(self):
        return True

    def afterCommitInsert(self):
        pass

    def afterCommitUpdate(self):
        pass

    def afterInsert(self):
        return True

    def afterUpdate(self):
        return True

    def beforeInsert(self):
        if not self.syncVersion: self.syncVersion = 1
        return True

    def checkSyncVersion(self,version):
        if int(version)!=self.syncVersion:
            return False
        return True

    def callAfterCommitInsert(self):
        self.afterCommitInsert()
        '''
        try:
            threading.Thread(target=self.afterCommitInsert()).start()
        except:
            pass '''

    def callAfterCommitUpdate(self):
        self.afterCommitUpdate()
        '''try:
            threading.Thread(target=self.afterCommitUpdate()).start()
        except:
            pass'''


    @classmethod
    def canUserDelete(cls):
        return True

    @classmethod
    def canUserEdit(cls,record):
        return True

    @classmethod
    def canUserCreate(cls):
        return True

    @classmethod
    def canUserAddRow(cls):
        return True

    @classmethod
    def canUserDeleteRow(cls):
        return True

    @classmethod
    def getUserFieldsReadOnly(cls,rocord,fieldname):
        return 0

    @classmethod
    def isPersistent(cls,fieldname):
        fields = cls.fieldsDefinition()
        if 'Persistent' in fields[fieldname] and not fields[fieldname]['Persistent']:
            return False
        return True

    @classmethod
    def getfieldsDefinition(cls,record):
        res = cls.fieldsDefinition()
        for fname in res:
            readonly = cls.getUserFieldsReadOnly(record,fname)
            if readonly:
                res[fname]['Readonly'] = readonly
            if res[fname]['Type']==[]:
                dres = res[fname]['fieldsDefinition']
                dclass = res[fname]['Class']
                var = {}
                exec('from %s import %s as DetailName' % (cls.__module__,dclass),var)
                DetailClass = var['DetailName']
                for dname in dres:
                    dreadonly = DetailClass.getUserFieldsReadOnly(dname)
                    if dreadonly:
                        dres[dname]['Readonly'] = dreadonly
                if 'htmlView' not in res[fname]:
                    res[fname]['htmlView'] = DetailClass.htmlView()
        res = cls.customGetFieldsDefinition(record,res)
        return res

    @classmethod
    def customGetFieldsDefinition(cls,record,res):
        return res

    @classmethod
    def htmlView(cls):
        Tabs = {}
        Tabs[0] = {'Fields':[]}
        FieldsDefinition = cls.fieldsDefinition()
        for field in cls.fieldsDefinition():
            if 'Hidde' not in FieldsDefinition[field]:
                Tabs[0]['Fields'].append([12,[field]])
        return Tabs

    @classmethod
    def getHtmlView(cls):
        Tabs = cls.htmlView()
        if not Tabs: return Tabs
        to_remove = []

        for key in Tabs:
            tab = Tabs[key]
            if ('Level' in tab) and (current_user.UserType not in tab['Level']):
                to_remove.append(key)
            fields = tab['Fields']
            for line in fields:
                indexnr = fields.index(line)
                Tabs[key]['Fields'][indexnr][0] = int(12 / len(line[1]))
        for fn in to_remove:
            del Tabs[fn]
        return Tabs

    @classmethod
    def query(cls):
        session = Session()
        records = session.query(cls)
        session.close()
        return records

    @classmethod
    def getDefValue(cls,fieldname):
        Type = cls.fieldsDefinition()[fieldname]['Type']
        if Type==[]: return 0
        elif Type=='integer': return 0
        elif Type=='text': return ''
        return None

    @classmethod
    def getRecordList(cls,TableClass,limit=None,order_by=None,desc=None):
        session = Session()
        records = session.query(TableClass)
        if order_by and desc: records = records.order_by(TableClass.c[order_by].desc())
        elif order_by: records = records.order_by(TableClass.c[order_by])
        if limit: records = records.limit(limit)
        session.close()
        return records

    @classmethod
    def getAllRecordList(cls,TableClass):
        session = Session()
        records = session.query(TableClass)
        session.close()
        return records


    def save(self,session):
        if not self.syncVersion:
            self.syncVersion = 1
            session.add(self)
        else:
            if not self.checkSyncVersion(self.syncVersion):
                return Error('Otro Usuario ha modoficado el Registro')
            self.syncVersion += 1
        try:
            session.commit()
        except Exception as e:
            session.rollback()
            return Error(str(e))
        finally:
            session.close()
        return True

    @classmethod
    def getRecordById(cls,id):
        session = Session()
        record = session.query(cls).filter_by(id=id).first()
        session.close()
        return record

    def getLinkToFromRecord(self,TableClass):
        return TableClass.getRecordList(TableClass)

    @classmethod
    def recordListFilters(cls):
        return []

    @classmethod
    def getRecordTitle(self):
        return ['id']

    def setOldFields(self):
        self.OldFields = {}
        for field in self.fieldsDefinition():
            fieldDef = self.fieldsDefinition()[field]
            if 'Persistent' not in fieldDef or fieldDef['Persistent']==True:
                self.OldFields[field] = copy.copy(getattr(self,field))

    def afterSaveJS(self):
        return ''


class DetailRecord(object):

    @classmethod
    def htmlView(cls):
        rows = {}
        Tabs[0] = cls.fieldsDefinition().keys()
        return rows

    @classmethod
    def fieldsDefinition(cls):
        return {}

    @classmethod
    def fieldsOrder(cls):
        return cls.fieldsDefinition().keys()

    @classmethod
    def getUserFieldsReadOnly(cls,fieldname):
        return 0
