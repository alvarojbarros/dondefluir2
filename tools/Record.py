# -*- coding: utf-8 -*-

from sqlalchemy import Column, Integer
from tools.dbconnect import Session
from sqlalchemy.orm import sessionmaker
from tools.Tools import *
from flask_login import current_user
import copy
import threading


def toJSONValue(class_type,value):
    if class_type== 'Integer':
        value = value if (value!=None) else ''
    elif class_type == 'Boolean':
        value = True if value else False
    elif class_type== 'Float':
        value = "%.2f" % value if value else ''
    elif class_type== 'String':
        value = value if value else ''
    elif class_type== 'Variant':
        value = value if value else ''
    elif class_type== 'DateTime':
        value = value.strftime("%Y-%m-%dT%H:%M:%S") if value else ''
    elif class_type== 'Date':
        value = value.strftime("%Y-%m-%d") if value else ''
    elif class_type== 'Time':
        value = value.strftime("%H:%M:%S") if value else ''
    return value

def fromJSONValue(class_type,value):
    if class_type == 'Integer':
        value = int(value)
    elif class_type == 'Boolean':
        value = True if value=='true' else False
    elif class_type == 'Float':
        value = float(value)
    elif class_type == 'String':
        pass
    elif class_type == 'Variant':
        pass
    elif class_type == 'DateTime':
        value = stringToDateTime(value)
    elif class_type == 'Date':
        value = stringToDate(value)
    elif class_type == 'Time':
        value = stringToTime(value)
    return value

def getRowById(detail,id):
    for row in detail:
        if str(row.id) == id:
            return row

class Record(object):
    syncVersion = Column(Integer)

    @classmethod
    def getFields(cls):
        res = {}
        for column in cls.__table__.columns:
            res[column.key] = column.type.__class__.__name__
        relationships = cls.__mapper__.relationships
        for relational in relationships.items():
            res[relational[0]] = {}
            for r_column in relational[1].table.columns:
                res[relational[0]][r_column.key] = r_column.type.__class__.__name__
        return res

    def toJSON(self):
        res = {}
        for column in self.__table__.columns:
            value = self.__getattribute__(column.key)
            res[column.key] = toJSONValue(column.type.__class__.__name__, value)
        relationships = self.__mapper__.relationships.keys()
        for relational in relationships:
            res[relational] = [row.toJSON() for row in self.__getattribute__(relational)]
        return res

    def fromJSON(self,json):
        for column in self.__table__.columns:
            value = json.get(column.key,None)
            if value:
                value = fromJSONValue(column.type.__class__.__name__ ,value)
                self.__setattr__(column.key,value)
        relationships = self.__mapper__.relationships
        for relational in relationships.items():
            relational_key = relational[0]
            detail = self.__getattribute__(relational_key)

            json_rows = json.get(relational_key, [])

            #delete missed rows
            missed_rows = []
            for row in detail:
                if str(row.id) not in [json_row.get('id','') for json_row in json_rows]:
                    missed_rows.append(row)
            for row in missed_rows:
                detail.remove(row)

            for json_row in json_rows:
                id = json_row.get('id','')
                detail_row = None
                if id:
                    #update existing rows
                    detail_row = getRowById(detail,id)
                else:
                    RowClass = relational[1].mapper.class_
                    detail_row = RowClass()
                    detail.append(detail_row)
                if detail_row:
                    for r_column in relational[1].table.columns:
                        row_name = r_column.key
                        value = json_row.get(row_name, None)
                        if value:
                            value = fromJSONValue(r_column.type.__class__.__name__, value)
                            detail_row.__setattr__(r_column.key, value)


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

    @classmethod
    def getLinksTo(self,record_list):
        return {}

    @classmethod
    def recordListFilters(cls):
        return [],[]

    @classmethod
    def getRecordTitle(self):
        return ['id']

    def setOldFields(self):
        self.OldFields = {}
        for column in self.__table__.columns:
            self.OldFields[column.key] = copy.copy(getattr(self, column.key))

    def afterSaveJS(self):
        return ''


class DetailRecord(object):

    @classmethod
    def getUserFieldsReadOnly(cls,fieldname):
        return 0

    def toJSON(self):
        res = {}
        for column in self.__table__.columns:
            value = self.__getattribute__(column.key)

            res[column.key] = toJSONValue(column.type.__class__.__name__ ,value)
        return res

