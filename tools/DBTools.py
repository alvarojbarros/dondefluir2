# -*- coding: utf-8 -*-

from sqlalchemy.orm import sessionmaker
from tools.dbconnect import Session
from flask_login import current_user
from tools.Tools import *
from flask import url_for
import os
import settings
from main import getMyFunction

FormatTypes = {'str':'String','datetime':'DateTime','integer':'Integer'}

def getFieldColum(fieldname,attrs):
    ftype = FormatTypes[attrs['Type']]
    if ftype=='String':
        ftype = '%s(%i)' %(ftype,attrs['Length'])
    res = "%s = Column(%s)" % (fieldname,ftype)
    return res

def filterFiedlsByUserAccess(fields):
    to_remove = []
    for fn in fields:
        field = fields[fn]
        if ('Level' in field) and (current_user.UserType not in field['Level']):
            to_remove.append(fn)
        if ('Values' in field and 'ValuesLevel' in field):
            levels = field['ValuesLevel']
            values_remove = []
            for value in field['Values']:
                user_level = levels[current_user.UserType]
                if value not in user_level:
                    values_remove.append(value)
            for value in values_remove:
                del field['Values'][value]
    for fn in to_remove:
        del fields[fn]


def importTable(f):
    if not f:
        return
    lines = str(f.read()).split('\\r\\n')
    c = 0
    k = 0
    fieldNames = []
    session = Session()
    for line in lines:
        fields = line.split('\\t')
        if c==0:
            table = fields[0][2:]
            var = {}
            exec('from %s import %s as TableName' % (table,table),var)
            TableClass = var['TableName']
            records = session.query(var['TableName'])
            session.close()
        elif c==1:
            fieldNames = fields
        elif len(fields)==len(fieldNames):
            dic = {}
            for i in range(len(fieldNames)):
                value = fields[i]
                if value:
                    dic[fieldNames[i]] = value
            new_record = TableClass(dic)
            if new_record.check():
                session.add(new_record)
                k += 1

        c += 1
    try:
        session.commit()
        session.close()
    except:
        session.rollback()
        session.close()
        return Error("Error al importar")
    return "Registros importados %i" % k

def fillRecordList(records,fields,fieldsDef=None):
    links = {}
    res = []
    for field in fields:
        if field in  fieldsDef:
            fieldDef = fieldsDef[field]
            if 'LinkTo' in fieldDef:
                links[field] = {}
                l = []
                for record in records:
                    value = getattr(record, field)
                    if value not in l:
                        l.append(value)
                session = Session()
                session.expire_on_commit = False
                if l:
                    linkto = fieldDef['LinkTo']
                    show = linkto['Show']
                    TableClass = getTableClass(linkto['Table'])
                    records_links = session.query(TableClass).filter(TableClass.id.in_(l))
                    for record in records_links:
                        show_list = []
                        for field_s in show:
                            show_list.append(getattr(record, field_s))
                        if show_list:
                            links[field][record.id] = [' '.join(show_list), 0]
                        else:
                            links[field][record.id] = [record.id, 0]
    for record in records:
        row = {}
        for field in fields:
            value = getattr(record,field)
            if isinstance(value,date):
                value = value.strftime("%d/%m/%Y")
            elif isinstance(value,time):
                value = value.strftime("%H:%M")
            elif (isinstance(value,int) or isinstance(value,str)) and fieldsDef:
                fieldDef = fieldsDef[field]
                if 'Values' in fieldDef:
                    value = fieldDef['Values'][value]
                elif links and 'LinkTo' in fieldDef:
                    value = links[field][value][0]
            row[field] = value
        res.append(row)
    return res

def getLinksTo(fields,record,fieldname=None):
    links = {}
    for fn in fields:
        if not fieldname or fn==fieldname:
            field = fields[fn]
            if ('LinkTo' in field):
                if ('Readonly' in field) and field['Readonly']==2 and record:
                    links[fn] = get_field_value(field['LinkTo'],record,fn)
                else:
                    links[fn] = get_linkto(field['LinkTo'],record)
    return links

def get_field_value(linkto,record,fn):
    table = linkto['Table']
    show = linkto['Show']
    TableClass = getTableClass(table)
    r = TableClass.getRecordById(getattr(record,fn))
    if r:
        show_list = []
        for field in show:
            show_list.append(getattr(r,field))
        if show_list:
            return {r.id: [' '.join(show_list),0]}
    return {getattr(record,fn): [getattr(record,fn),0]}


def get_linkto(linkto,record=None):
    res = {}
    table = linkto['Table']
    show = linkto['Show']
    method = linkto.get('Method',None)
    params = linkto.get('Params',None)
    filters = linkto.get('Filters',None)
    TableClass = getTableClass(table)
    if method:
        records = getMyFunction(method,params)
    elif record:
        records = record.getLinkToFromRecord(TableClass)
    else:
        records = TableClass.getRecordList(TableClass)
    for record in records:
        skip = False
        if filters:
            for filter_name in filters:
                if getattr(record,filter_name) not in filters[filter_name]:
                    skip = True
        if not skip:
            show_list = []
            for field in show:
                show_list.append(getattr(record,field))
            closed = hasattr(record,'Closed') and record.Closed
            res[record.id] = [' '.join(show_list),closed]
    return res

def getImageLink(table,id,fieldname):
    fname = '%s/%s.%s' %(table,fieldname,id)
    print(fname)
    print("%s/%s/%s" % (settings.images_url,settings.images_folder,fname))
    f = os.path.isfile("%s/%s/%s" % (settings.images_url,settings.images_folder,fname))
    if not f:
        url = url_for('static',filename='images/user.jpg')
    else:
        fname = "%s/%s" %(settings.images_folder,fname)
        url = url_for('static',filename=fname)
    return url
