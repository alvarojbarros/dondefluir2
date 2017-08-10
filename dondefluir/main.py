# -*- coding: utf-8 -*-

from flask import render_template, request,jsonify
from flask import Blueprint
from tools.DBTools import *
from dondefluir.db.User import User
from dondefluir.db.Company import Company
from dondefluir.db.Notification import Notification
from dondefluir.db.Service import Service
from dondefluir.db.Activity import Activity,ActivitySchedules,ActivityUsers
from dondefluir.db.Payment import Payment
from sqlalchemy import or_
import getsettings
settings = getsettings.getSettings()
from settings import *

blue_dondefluir = Blueprint('blue_dondefluir', __name__,template_folder='templates',static_url_path='/dondefluir/static',static_folder='static')

def getActivitiesTableName():
    if current_user.UserType==3:
        return "Mi agenda"
    else:
        return "Todas las actividades"

def getCompanyTemplate():
    if current_user.UserType==3:
        return "company_icon.html"
    else:
        return "company.html"

def getPaymentsTableName():
    if current_user.UserType==3:
        return "Mis Pagos"
    elif current_user.UserType==0:
        return "Pagos"
    else:
        return "Pagos Recibidos"

def addElementToList(Elements,Element,UserType):
    if ('Level' not in Element) or (UserType in Element['Level']):
        if not Element['Module'] in Elements:
            Elements[Element['Module']] = {}
        Elements[Element['Module']][Element['Index']] = Element

def getMyFunction(function,params):
    res = eval('%s(%s)' % (function,str(params)))
    return res

def getProfessional(favorite,companyId):
    session = Session()
    if not favorite:
        records = session.query(User).filter_by(FindMe=True)\
            .join(Company,User.CompanyId==Company.id)
        if companyId:
            records = records.filter(User.CompanyId==companyId)
        records  = records.with_entities(User.id,User.Name,Company.Name.label("CompanyName"),User.Title,User.City)
    else:
        from dondefluir.db.UserFavorite import UserFavorite
        records = session.query(User)\
            .join(UserFavorite,User.id==UserFavorite.FavoriteId)\
            .filter_by(UserId=current_user.id,Checked=True)\
            .join(Company,User.CompanyId==Company.id)
        if companyId:
            records = records.filter(User.CompanyId==companyId)
        records  = records.with_entities(User.id,User.Name,Company.Name.label("CompanyName"),User.Title,User.City)
    session.close()
    return records


def getUserNote(*args):
    custId = args[0]['custId']
    from dondefluir.db.UserNote import UserNote
    records = UserNote.getRecordList(UserNote,custId)
    return records


def getCustomer(args):
    favorite = args.get('favorite',None)
    session = Session()
    if not favorite:
        records = session.query(User).filter_by(UserType=3)
    else:
        from dondefluir.db.UserFavorite import UserFavorite

        records1 = session.query(User).filter_by(UserType=3)\
            .join(UserFavorite,User.id==UserFavorite.FavoriteId)\
            .filter_by(UserId=current_user.id,Checked=True)\
            .with_entities(User.id, User.Name,User.Closed,User.UserType)

        records2 = session.query(User).filter_by(UserType=3)\
            .join(UserFavorite, User.id == UserFavorite.UserId)\
            .filter_by(FavoriteId=current_user.id, Checked=True) \
            .with_entities(User.id, User.Name,User.Closed,User.UserType)

        #records = records1.union_all(records2)
        records = records1

    session.close()
    return records

def isUserAdmin(*args):
    if current_user.UserType in (0,1):
        return True
    return False

def getBreakCalendarDates(act,dates):
    for d in dates:
        schedule = dates[d]
        for j in range(len(schedule)):
            if act.TransDate==schedule[j]['Date']:
                if (act.StartTime>schedule[j]['StartTime'] and act.EndTime<schedule[j]['EndTime']):
                    dic = {'FechaStr':schedule[j]['FechaStr'],'StartTime': schedule[j]['StartTime'],'EndTime': act.StartTime,'Date': schedule[j]['Date']}
                    schedule.insert(j+1,dic)
                    dic = {'FechaStr': schedule[j]['FechaStr'],'StartTime': act.EndTime,'EndTime': schedule[j]['EndTime'],'Date': schedule[j]['Date']}
                    schedule.insert(j+2,dic)
                    del schedule[j]
                    return dates
                if (act.StartTime>schedule[j]['StartTime'] and act.StartTime<schedule[j]['EndTime'] and act.EndTime>=schedule[j]['EndTime']):
                    schedule[j]['EndTime'] = act.StartTime
                    return dates
                if (act.StartTime<=schedule[j]['StartTime'] and act.EndTime<schedule[j]['EndTime'] and act.EndTime>schedule[j]['StartTime']):
                    schedule[j]['StartTime'] = act.EndTime
                    return dates
                if (act.StartTime == schedule[j]['StartTime'] and act.EndTime == schedule[j]['EndTime']):
                    del schedule[j]
                    return dates
    return dates

@blue_dondefluir.route('/_get_calendar_events')
def get_calendar_events():
    profId = request.args.get('profId',None)
    companyId = request.args.get('companyId',None)
    eventId = request.args.get('eventId',None)
    res = showProfessionalEvents({'profId':profId,'eventId':eventId,'companyId': companyId})
    return jsonify(result=res)


@blue_dondefluir.route('/_get_calendar_dates')
def get_calendar_dates():
    profId = request.args.get('id')
    AddActivities = request.args.get('AddActivities',False)
    res = getCalendarDates(profId,AddActivities)
    for d in res:
        list = res[d]
        for dic in list:
            for i in dic:
                if i in ('StartTime','EndTime'):
                    dic[i] = dic[i].strftime("%H:%M")
                elif i == 'Date' and isinstance(dic[i],date):
                    dic[i] = dic[i].strftime("%Y-%m-%d")
    return jsonify(result=res)


def getCalendarDates(profId,AddActivities=False):
    session = Session()
    user = session.query(User).filter_by(id=profId).first()
    if not user:
        return []

    ShowFromDays = 0
    if user.ShowFromDays: ShowFromDays = user.ShowFromDays
    d = addDays(today(),ShowFromDays)
    ShowDays = user.ShowDays
    if not ShowDays: ShowDays = 15
    td = addDays(d,ShowDays)

    activities = session.query(Activity) \
        .filter(Activity.ProfId==profId,Activity.Status!=2) \
        .join(ActivitySchedules,Activity.id==ActivitySchedules.activity_id)\
        .filter(ActivitySchedules.TransDate>=d,ActivitySchedules.TransDate<=td) \
        .outerjoin(Service,Service.id==Activity.ServiceId)\
        .outerjoin(User,Activity.CustId==User.id)\
        .with_entities(ActivitySchedules.TransDate,ActivitySchedules.StartTime,ActivitySchedules.EndTime,Service.Name.label('Name') \
            ,Activity.Comment,Activity.id,User.Name.label('Customer'))
    dates = {}

    while d<td:
        weekday = d.weekday()
        for row in user.Schedules:
            found = False
            if (weekday==0 and row.d1): found = True
            if (weekday==1 and row.d2): found = True
            if (weekday==2 and row.d3): found = True
            if (weekday==3 and row.d4): found = True
            if (weekday==4 and row.d5): found = True
            if (weekday==5 and row.d6): found = True
            if (weekday==6 and row.d7): found = True
            if found:
                datestr = WeekName[weekday] + " " + d.strftime("%d/%m/%Y")
                datekey = d.strftime("%Y-%m-%d")
                if datekey not in dates:
                    dates[datekey] = []
                dates[datekey].append({'FechaStr':datestr,'StartTime':row.StartTime,'EndTime':row.EndTime,'CompanyId':user.CompanyId,'Date':d})
        d = addDays(d,1)

    for activity in activities:
        dates = getBreakCalendarDates(activity,dates)

    if user.FixedSchedule:
        newArray = {}
        for d in sorted(dates):
            schedules = dates[d]
            for i in range(len(schedules)):
                lastTime = addMinutesToTime(schedules[i]['EndTime'],-user.MinTime)
                startTime = schedules[i]['StartTime']
                while (startTime<=lastTime):
                    datestr = schedules[i]['FechaStr']
                    if d not in newArray:
                        newArray[d] = []
                    endTime = addMinutesToTime(startTime,user.MinTime)
                    newArray[d].append({'FechaStr':datestr,'StartTime':startTime,'EndTime':endTime,'CompanyId':user.CompanyId,'Date':d})
                    startTime = addMinutesToTime(startTime,user.MinTime)
        dates = newArray
    if AddActivities:
        for activity in activities:
            d = activity.TransDate
            weekday = d.weekday()
            datestr = WeekName[weekday] + " " + d.strftime("%d/%m/%Y")
            datekey = d.strftime("%Y-%m-%d")
            dates[datekey].append({'FechaStr':datestr,'StartTime':activity.StartTime,'EndTime':activity.EndTime \
                ,'CompanyId':user.CompanyId, 'Date':d, 'Comment': activity.Comment, 'Service': activity.Name \
                , 'id': activity.id, 'Customer': activity.Customer})
    session.close()
    return dates

@blue_dondefluir.route('/_set_favorite')
def set_favorite():
    from dondefluir.db.UserFavorite import UserFavorite
    favId = request.args.get('favId')
    session = Session()
    session.expire_on_commit = False
    record = session.query(UserFavorite).filter_by(UserId=current_user.id,FavoriteId=favId).first()
    if not record:
        record = UserFavorite()
        record.UserId = current_user.id
        record.FavoriteId = favId
        record.CompanyId = current_user.CompanyId
        record.beforeInsert()
        record.Checked = True
        session.add(record)
    else:
        record.Checked = not record.Checked
    status = record.Checked
    res = record.save(session)
    if res:
        return jsonify(result={'res':True,'id':record.id,'Status': status})
    else:
        return jsonify(result={'res':False,'Error':str(res)})

def getUserService(params):
    session = Session()
    from dondefluir.db.UserService import UserService
    from dondefluir.db.Service import Service
    records = session.query(UserService)\
        .join(User,User.id==UserService.UserId)\
        .join(Service,Service.id==UserService.ServiceId)\
        .filter_by(CompanyId=current_user.CompanyId) \
        .with_entities(UserService.id,UserService.CompanyId,User.Name.label("UserName"),Service.Name.label("ServiceName"))
    session.close()
    return records

def showProfessionalEvents(*args):
    profId = args[0].get('profId',None)
    eventId = args[0].get('eventId',None)
    companyId = args[0].get('companyId',None)
    session = Session()
    records = session.query(Activity) \
        .join(Company,Activity.CompanyId==Company.id)\
        .join(User,Activity.ProfId==User.id)\
        .join(ActivitySchedules,Activity.id==ActivitySchedules.activity_id)\
        .filter(ActivitySchedules.TransDate>=today(),or_(Activity.Type==1,Activity.Type==2)) \
        .with_entities(Activity.Comment,Activity.ProfId,ActivitySchedules.TransDate,ActivitySchedules.StartTime \
        ,ActivitySchedules.EndTime,Activity.id,Activity.MaxPersons,Activity.Price,Activity.Description,Activity.OnlinePayment \
        ,Company.KeyPayco,Company.OnlinePayment.label('CompanyPayment'),User.Name.label('ProfName'))
    if eventId: records = records.filter(Activity.id==eventId)
    if profId: records = records.filter(Activity.ProfId==profId)
    if companyId: records = records.filter(Activity.CompanyId==companyId)
    res = {}
    k = 0
    for r in records:
        cnt = session.query(Activity).filter_by(id=r.id)\
            .join(ActivityUsers,Activity.id==ActivityUsers.activity_id)\
            .count()
        if r.id not in res:
            res[r.id] = []
        st = Activity.StatusList[0]
        stv = 0
        paid = 0

        if k==0:
            FindCust = session.query(Activity).filter_by(id=r.id)\
                .join(ActivityUsers,Activity.id==ActivityUsers.activity_id)\
                .filter(ActivityUsers.CustId==current_user.id)\
                .count()
            if FindCust:
                st = Activity.StatusList[1]
                stv = 1
                Paid = session.query(Payment)\
                    .filter_by(UserId=current_user.id,ActivityId=r.id,ResponseCode=1) \
                    .count()
                if Paid:
                    paid = 1

        TransDate = WeekName[r.TransDate.weekday()] + " " + r.TransDate.strftime("%d/%m/%Y")
        res[r.id].append({'Comment': r.Comment,'TransDate': TransDate, 'StartTime': r.StartTime.strftime("%H:%M") \
            , 'Description': r.Description, 'Price': r.Price, 'MaxPersons': r.MaxPersons, 'OnlinePayment': r.OnlinePayment \
            , 'EndTime': r.EndTime.strftime("%H:%M"), 'Status': st, 'Persons': cnt, 'StatusValue': stv, 'Paid': paid \
            , 'KeyPayco': r.KeyPayco, 'CompanyPayment':r.CompanyPayment,'ProfName': r.ProfName})
        k += 1
    return res

@blue_dondefluir.route('/_get_professional_list')
def get_professional_list():
    favorite = request.args.get('favorite')=='true'
    companyId = request.args.get('CompanyId',None)
    records = getProfessional(favorite,companyId)
    fields = ['Name','id','CompanyName','Title','City']
    res = []
    for rec in records:
        r = {}
        for field in fields:
            r[field] = getattr(rec,field)
        r['Image'] = getImageLink('User',rec.id,'ImageProfile')
        res.append(r)
    return jsonify(result=res)


@blue_dondefluir.route('/_set_cust_to_event')
def set_cust_to_event():
    eventId = request.args.get('id')
    session = Session()
    session.expire_on_commit = False
    record = session.query(Activity).filter_by(id=eventId).first()
    if record:
        found = False
        st = 1
        for row in record.Users:
            if row.CustId==current_user.id:
                found = True
                record.Users.remove(row)
                st = 0
                break
        if not found:
            row = ActivityUsers()
            row.CustId = current_user.id
            record.Users.append(row)
        res = record.save(session)
        if res:
            return jsonify(result={'res':True,'label':Activity.StatusList[st],'st': st})
        else:
            return jsonify(result={'res':False,'Error':str(res)})
    return jsonify(result={'res':False,'Error':'Registro Inexistente'})


def getCalendarData(UserId):
    records = Activity.getRecordListCalendar(Activity,ProfId=UserId)
    list = []
    for record in records:
        st = "%sT%s" %(record.TransDate.strftime('%Y-%m-%d'),record.StartTime.strftime('%H:%M:%S'))
        et = "%sT%s" %(record.TransDate.strftime('%Y-%m-%d'),record.EndTime.strftime('%H:%M:%S'))
        onclick = ''' getRecordForm('Activity','recordform.html',id='%i')''' % record.id
        id = 'activity_%i' % record.id
        #tooltip = "%s\n" % record.Comment
        #tooltip += "Fecha: %s\n" % record.TransDate.strftime('%Y-%m-%d')
        #tooltip += "Horario: %s a %s\n" % (record.StartTime.strftime('%H:%M:%S'),record.EndTime.strftime('%H:%M:%S'))

        BGColor = 'yellow'
        textColor = 'black'
        if record.Status==1:
            BGColor = 'green'
            textColor = 'white'
        elif record.Status==2:
            BGColor = 'gray'
            textColor = 'white'
        list.append({'title': record.Comment,'start':st,'end':st,'onclick':onclick,'id':id,'backgroundColor':BGColor, \
            'textColor': textColor})
    return list

@blue_dondefluir.route('/data')
def return_data():
    UserId = request.args.get('UserId', '')
    res = getCalendarData(UserId)
    return jsonify(res)
    with open("events.json", "r") as input_data:
        return input_data.read()

@blue_dondefluir.route('/_set_notification_read')
def set_notification_read():
    nftId = request.args.get('id')
    session = Session()
    session.expire_on_commit = False
    record = session.query(Notification).filter_by(id=nftId).first()
    if record:
        record.Status = 1
        res = record.save(session)
        if res:
            return jsonify(result={'res':True})
        else:
            return jsonify(result={'res':False,'Error':str(res)})
    return jsonify(result={'res':False,'Error':'Registro Inexistente'})

@blue_dondefluir.route('/_get_notifications')
def get_notifications():
    session = Session()
    session.expire_on_commit = False
    record = session.query(Notification).filter_by(UserId=current_user.id,Status=0).order_by(Notification.TransDate.desc())
    cnt = record.count()
    l = []
    k = 0
    for r in record:
        k += 1
        l.append({'Comment':r.Comment,'TransDate': "%s %s" % (WeekName[int(r.TransDate.strftime("%w"))] \
            ,r.TransDate.strftime("%d/%m/%Y")),'id':r.id})
        if k>=4:
            break
    return jsonify(result={'cnt':cnt,'values':l})


@blue_dondefluir.route('/_get_current_date')
def get_current_date():
    date = today()
    w = date.weekday()
    m = date.month
    Y = date.year
    d = date.day
    hoy = 'Hoy es %s %i de %s de %i' %(WeekName[w],d,meses[m],Y)
    return jsonify(result=hoy)


@blue_dondefluir.route('/_event_list')
def event_list():
    fields = request.args.get('Fields').split(',')
    order_by = request.args.get('OrderBy',None)
    desc = request.args.get('Desc',None)
    limit = request.args.get('Limit',None)
    columns = eval(request.args.get('Columns',{}))
    UserId = None
    CompanyId = None
    if current_user.UserType==1:
        CompanyId = current_user.CompanyId
    elif current_user.UserType==2:
        UserId = current_user.id
    records = Activity.getEventList(UserId,CompanyId,limit=limit,order_by=order_by,desc=desc)
    fieldsDef = Activity.fieldsDefinition()
    res = fillRecordList(records,fields,fieldsDef)
    setColumns(res, columns, [], [])
    ids = []
    events = []
    for r in res:
        if r['id'] not in ids:
            ids.append(r['id'])
            events.append(r)
    return jsonify(result=events)

@blue_dondefluir.route('/_cancel_activity')
def cancel_activity():
    session = Session()
    session.expire_on_commit = False
    _id = request.args.get('id')
    record = session.query(Activity).filter_by(id=_id).first()
    if not record:
        return jsonify(result={'res': False,'Error':'Registro no Encontrado'})
    record.setOldFields()
    record.Status = record.CANCELLED
    res = record.check()
    if not res:
        return jsonify(result={'res': False,'Error':str(res)})
    record.syncVersion += 1
    res = record.afterUpdate()
    if not res:
        return jsonify(result={'res': False,'Error':str(res)})
    try:
        session.commit()
        session.close()
    except Exception as e:
        session.rollback()
        session.close()
        return jsonify(result={'res': False,'Error':str(e)})
    record.callAfterCommitUpdate()
    return jsonify(result={'res':True,'id': record.id,'syncVersion': record.syncVersion})

@blue_dondefluir.route('/epayco/<activity_id>')
def epayco(activity_id):
    return render_template('epayco_res.html',current_user=current_user,app_name=settings.app_name,activityId=activity_id)


@blue_dondefluir.route('/_set_payment')
def set_payment():
    from dondefluir.db.Payment import Payment
    activityId = request.args.get('activityId')
    session = Session()
    record = session.query(Activity).filter_by(id=activityId).first()
    companyId = record.CompanyId
    session.close()
    session = Session()
    session.expire_on_commit = False
    record = Payment()
    record.UserId = current_user.id
    record.CompanyId = companyId
    record.ActivityId = activityId
    record.ResponseCode = request.args.get('x_cod_response')
    record.Response = request.args.get('x_response')
    record.Amount = request.args.get('x_amount')
    record.TransDate = now()
    record.Reference = request.args.get('x_id_invoice')
    record.Reason = request.args.get('x_response_reason_text')
    record.TransactionId = request.args.get('x_transaction_id')
    record.BankName = request.args.get('x_bank_name')
    record.AutorizationCode = request.args.get('x_approval_code')
    record.Currency = request.args.get('x_currency_code')
    record.beforeInsert()
    session.add(record)
    res = record.save(session)
    if res:
        return jsonify(result={'res':True,'id':record.id})
    else:
        return jsonify(result={'res':False,'Error':str(res)})


@blue_dondefluir.route('/_get_payment')
def get_payment():
    activityId = request.args.get('activityId')
    userId = request.args.get('userId')
    session = Session()
    Paid = session.query(Payment)\
        .filter_by(UserId=userId ,ActivityId=activityId,ResponseCode=1) \
        .count()
    if Paid:
        return jsonify(result={'res':True})
    else:
        KeyPayco = ''
        companyId = request.args.get('companyId')
        company = Company.getRecordById(companyId)
        if company:
            KeyPayco = company.KeyPayco
        return jsonify(result={'res':False,'KeyPayco': KeyPayco})


@blue_dondefluir.route('/_customer_list')
def customer_list():
    vars = {}
    for key in request.args:
        vars[key] = request.args.get(key)
        if vars[key] in ('true','True'):
            vars[key] = True
        elif vars[key] in ('false', 'False'):
            vars[key] = False
    records = getCustomer(vars)
    fieldsDef = User.fieldsDefinition()
    fields = request.args.get('Fields').split(',')
    columns = eval(request.args.get('Columns','{}'))
    res = fillRecordList(records,fields,fieldsDef)
    setColumns(res,columns,[],[])
    return jsonify(result={'records': res,'filters': [], 'filtersNames': []})

@blue_dondefluir.route('/_get_service_price')
def get_service_price():
    ServiceId = request.args.get('ServiceId')
    session = Session()
    record = session.query(Service).filter_by(id=ServiceId).first()
    price = None
    if record and record.Price:
        price = record.Price
    session.close()
    if price:
        return jsonify(result=str(price))
    else:
        return jsonify(result=None)
