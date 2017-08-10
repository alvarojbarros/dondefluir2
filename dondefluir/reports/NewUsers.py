# -*- coding: utf-8 -*-

from tools.dbconnect import Session
from tools.Tools import *
from dondefluir.db.User import User
from sqlalchemy import func

class NewUsers():

    @classmethod
    def reportFilters(cls):
        res = {}
        res['FromDate'] = {'Type': 'date', 'Label': 'Desde','Input':'datetime', 'Value': today().strftime("%Y-%m-%d")}
        res['ToDate'] = {'Type': 'date', 'Label': 'Hasta','Input':'datetime', 'Value': today().strftime("%Y-%m-%d")}
        return res

    @classmethod
    def htmlView(cls):
        Tabs = {}
        Tabs['Filters'] = {"Fields": [["FromDate","ToDate"]]}
        return Tabs

    @classmethod
    def run(cls,filters):
        fd = filters['FromDate'].split('-')
        td = filters['ToDate'].split('-')
        FromDate = date(int(fd[0]),int(fd[1]),int(fd[2]))
        ToDate = date(int(td[0]),int(td[1]),int(td[2]))
        session = Session()
        records = session.query(func.concat(func.year(User.CreatedDate),'-',func.month(User.CreatedDate)), func.count(User.CreatedDate).label('CNT'))\
            .filter(User.CreatedDate.between(FromDate,ToDate))\
            .group_by(func.concat(func.year(User.CreatedDate),'-',func.month(User.CreatedDate)))\
            .order_by(func.concat(func.year(User.CreatedDate),'-',func.month(User.CreatedDate)).desc())\
            .all()
        session.close()
        columns = ['Mes','Cantidad']
        return {'Columns': columns,'Rows': records}
