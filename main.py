# -*- coding: utf-8 -*-

from flask import Flask
app = Flask(__name__)
from flask import redirect, url_for, request, render_template,jsonify
from flask_login import LoginManager, login_required, login_user, logout_user,current_user
import settings
from flask_mail import Mail
import re
from flask import render_template, request,jsonify
from tools.DBTools import *
from db.User import User
from db.Company import Company
from db.Notification import Notification
from db.Service import Service
from db.Activity import Activity,ActivitySchedules,ActivityUsers
from db.Payment import Payment
from sqlalchemy import or_
from tools.dbconnect import Session
#from flask_socketio import SocketIO, send, emit


app.config.update(
    DEBUG = True,
    TEMPLATES_AUTO_RELOAD = True,
    SECRET_KEY = settings.SECRET_KEY,
    UPLOAD_FOLDER = './tmp/',
    MAIL_SERVER = 'smtp-relay.gmail.com',
    MAIL_PORT = 25,
)


app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['MAIL_SERVER'] = 'smtp-relay.gmail.com'

mail = Mail(app)

# flask-login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

#socketio = SocketIO(app, manage_session=False)

# some protected url
@app.route('/')
@login_required
def home():
    return render_template(settings.templates['home_template'],current_user=current_user,app_name=settings.app_name)

# somewhere to login
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == 'POST':
        username = request.form['username']
        if username: username = username.replace(" ", "")
        username = User.getUserIdByEmail(username)
        password = request.form['password']
        if username or password:
            if not password or not username:
                return render_template(settings.templates['loggin_template'],error_msg='Debe Ingresar Usuario y Password',signUp=False,app_name=settings.app_name)
            user = User.get(username)
            if not user:
                return render_template(settings.templates['loggin_template'],error_msg='Usuario no Registrado',signUp=False,app_name=settings.app_name)
            if (user.Password == password):
                if login_user(user):
                    return redirect('/')
        return render_template(settings.templates['loggin_template'],error_msg='Datos Incorrectos',signIn=False,app_name=settings.app_name)
    else:
        return render_template(settings.templates['loggin_template'],signUp=False,app_name=settings.app_name)


# somewhere to login
@app.route("/signin", methods=["GET", "POST"])
def signin():
    if request.method == 'POST':
        username1 = request.form['username1']
        username2 = request.form['username2']
        if username1: username1 = username1.replace(" ", "")
        if username2: username2 = username2.replace(" ", "")
        password1 = request.form['password1']
        password2 = request.form['password2']
        name = request.form['name']
        if password1 or password2 or username1 or username2:
            if not username1:
                return render_template(settings.templates['loggin_template'],error_msg='Debe Ingresar Email',\
                                       signUp=True,app_name=settings.app_name)
            if username1!=username2:
                return render_template(settings.templates['loggin_template'],error_msg='Los Email no coinciden',\
                                       signUp=True,app_name=settings.app_name)
            match = re.match('^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$', username1)
            if not match:
                return render_template(settings.templates['loggin_template'], error_msg='Debe ingresar un correo válido', \
                                       signUp=True, app_name=settings.app_name)
            user = User.getUserIdByEmail(username1)
            if user:
                return render_template(settings.templates['loggin_template'],error_msg='Usuario ya registrado: %s' % username1,signUp=True,app_name=settings.app_name)
            if password1 != password2:
                return render_template(settings.templates['loggin_template'],error_msg='Los Password no coinciden',signUp=True,app_name=settings.app_name)
            new_user = User.addNewUser(username1,password1,name)
            if new_user:
                login_user(new_user)
                return redirect('/')
            else:
                return render_template(settings.templates['loggin_template'],error_msg=new_user,signUp=True,app_name=settings.app_name)
        return render_template(settings.templates['loggin_template'],error_msg='Datos Incorrectos',signIn=False,app_name=settings.app_name)
    else:
        return render_template(settings.templates['loggin_template'],signUp=False,app_name=settings.app_name)

# somewhere to logout
@app.route("/logout")
@login_required
def logout():
    logout_user()
    return render_template(settings.templates['loggin_template'],app_name=settings.app_name)
    #return Response('<p>Logged out</p>')


# handle login failed
@app.errorhandler(401)
def page_not_found(e):
    return render_template(settings.templates['loggin_template'],error='Datos Incorrectos',app_name=settings.app_name)


# callback to reload the user object
@login_manager.user_loader
def load_user(userid):
    return User.get(userid)

@app.route('/_recover_password')
def recover_password():
    session = Session()
    session.expire_on_commit = False
    email = request.args['email']
    record = session.query(User).filter_by(Email=email).first()
    if not record:
        return jsonify(result={'res': False,'Error':'No hay usuario registrado para este Email'})
    else:
        record.Password = passwordRamdom()
        try:
            session.commit()
            from tools.MailTools import sendPasswordRecoverMail
            res = sendPasswordRecoverMail(email,record.Password,record.Name)
            if res:
                session.close()
                return jsonify(result={'res': True})
            else:
                session.close()
                return jsonify(result={'res': False,'Error': 'No se pudo enviar el correo'})
        except Exception as e:
            session.rollback()
            session.close()
            return jsonify(result={'res': False,'Error':str(e)})


@app.route('/_change_password')
@login_required
def change_password():
    pwd = request.args['pwd']
    if current_user.Password!=pwd:
        return jsonify(result={'res': False,'Error':'Es password actual ingresado es incorrecto'})
    newpwd = request.args['newpwd']
    session = Session()
    record = session.query(User).filter_by(id=current_user.id).first()
    if not record:
        session.close()
        return jsonify(result={'res': False,'Error':'Usuario no encotrado'})
    else:
        record.Password = newpwd
        try:
            session.commit()
            session.close()
            return jsonify(result={'res': True})
        except Exception as e:
            session.rollback()
            session.close()
            return jsonify(result={'res': False,'Error':str(e)})
        return jsonify(result={'res':True,'id':res.id,'syncVersion':res.syncVersion})

@app.route('/import_table', methods=['GET', 'POST'])
@login_required
def import_table():
    if request.method == 'POST':
        f = request.files['file']
        if f.filename == '':
            return 'No selected file'
        if f:
            res = importTable(f)
            return render_template('import_table.html',Msj=res,current_user=current_user)
    return render_template('import_table.html',current_user=current_user)

@app.route('/_save_files', methods=['GET', 'POST'])
@login_required
def save_files():
    if request.method == 'POST':
        for key in request.files.keys():
            table = request.form[key + '-table']
            id = request.form[key + '-id']
            f = request.files[key]
            if not os.path.exists("%s/%s" %(settings.images_url,settings.images_folder)):
                cmd = "sudo mkdir %s/%s" %(settings.images_url,settings.images_folder)
                os.system(cmd)
            if not os.path.exists('%s/%s/%s' % (settings.images_url,settings.images_folder,table)):
                cmd = "sudo mkdir %s/%s/%s" % (settings.images_url,settings.images_folder,table)
                os.system(cmd)
            path = '%s/%s/%s' % (settings.images_url,settings.images_folder,table)
            fname = '%s.%s' % (key,id)
            f.save(os.path.join(path,fname))
    return jsonify(result={'res': True})

@app.route('/_update_linkto',methods=['POST'])
def update_linkto():
    if request.method == "POST":
        data = json.loads(request.form.get('data'))
        table = data.get('TableName')
        fields = data.get('fields')
        TableClass = getTableClass(table)
        record = TableClass()
        record.fromJSON(fields)
        links = TableClass.getLinksTo([record])
        return jsonify(result=links)


def saveNewRecord(TableClass,fields):
    del fields['id']
    new_record = TableClass()
    getDetailDict(fields)
    session = Session()
    session.expire_on_commit = False
    new_record.fromJSON(fields)
    if not new_record.beforeInsert():
        return jsonify(result={'res': False, 'Error': 'Error en Campos'})
    res = new_record.check()
    if not res:
        return jsonify(result={'res': False, 'Error': str(res)})
    session.add(new_record)
    res = new_record.afterInsert()
    if not res:
        return jsonify(result={'res': False, 'Error': str(res)})
    try:
        session.commit()
    except Exception as e:
        session.rollback()
        session.close()
        return jsonify(result={'res': False, 'Error': str(e)})
    new_record.callAfterCommitInsert()
    RunJS = new_record.afterSaveJS()
    session.close()
    return jsonify(result={'res': True, 'record': new_record.toJSON(), 'RunJS': RunJS})

def updateRecord(TableClass,fields):
    getDetailDict(fields)
    session = Session()
    session.expire_on_commit = False
    record = session.query(TableClass).filter_by(id=fields['id']).first()
    if not record:
        return jsonify(result={'res': False, 'Error': 'Registro no Encontrado'})
    if not record.checkSyncVersion(fields.get('syncVersion', None)):
        return jsonify(result={'res': False, 'Error': 'Otro Usuario ha modoficado el Registro'})
    record.fromJSON(fields)
    res = record.check()
    if not res:
        return jsonify(result={'res': False, 'Error': str(res)})
    record.syncVersion += 1
    res = record.afterUpdate()
    if not res:
        return jsonify(result={'res': False, 'Error': str(res)})
    try:
        session.commit()
    except Exception as e:
        session.rollback()
        session.close()
        return jsonify(result={'res': False, 'Error': str(e)})
    record.callAfterCommitUpdate()
    session.close()
    RunJS = record.afterSaveJS()
    return jsonify(result={'res': True, 'record': record.toJSON(), 'RunJS': RunJS})


@app.route('/_save_record',methods=["GET", "POST"])
def save_record():
    if request.method == 'POST':
        data = json.loads(request.form.get('data'))
        fields = data.get('fields')
        table = data.get('TableName')
        TableClass = getTableClass(table)
        res = {}
        for key in fields:
            if fields[key]=='null': fields[key] = None
        id = fields.get('id',None)
        session = Session()
        session.expire_on_commit = False
        if not id:
            return saveNewRecord(TableClass,fields)
        else:
            return updateRecord(TableClass,fields)

@app.route('/_delete_record')
def delete_record():
    table = request.args.get('TableName')
    TableClass = getTableClass(table)
    _id = request.args.get('id')
    if _id==current_user.id:
        return jsonify(result={'res': False, 'Error': 'No se puede borrar usuario actual'})
    if _id:
        session = Session()
        record = session.query(TableClass).filter_by(id=_id).first()
        if not record:
            return jsonify(result={'res': False, 'Error': 'Registro no encontrado'})
        res = session.delete(record)
        try:
            session.commit()
            session.close()
            return jsonify(result={'res': True})
        except Exception as e:
            session.rollback()
            session.close()
            return jsonify(result={'res': False, 'Error': str(e)})


@app.route('/_get_template')
def get_template():
    template = request.args.get('Template')
    var = {}
    functions = []
    for key in request.args:
        var[key] = request.args.get(key)
        if var[key]=='True': var[key] = True
        if var[key]=='False': var[key] = False
    if request.args.get('Functions'):
        functions = request.args.get('Functions')
    res = render_template(template,var=var)
    return jsonify(result={'html':res, 'functions': functions})

def getRecordByFilters(table,filters,values):
    TableClass = getTableClass(table)
    session = Session()
    if not filters:
        record = TableClass()
        record.defaults()
        for f in values:
            record.__setattr__(f,values[f])
    else:
        record = session.query(TableClass).filter_by(**filters).first()
        if not record:
            return {'res':False}
    fields = TableClass.getFields()
    recordTitle = TableClass.getRecordTitle()
    canEdit = TableClass.canUserEdit(record)
    canDelete = TableClass.canUserDelete()
    events = TableClass.getEvents()
    links = TableClass.getLinksTo([record])
    res = record.toJSON()
    session.close()
    return {'record': res, 'fields': fields, 'links': links,'recordTitle':recordTitle,'canEdit':canEdit
        , 'canDelete':canDelete, 'events': events}


@app.route('/_get_record', methods=['POST'])
def get_record():
    if request.method == "POST":
        data = json.loads(request.form.get('data'))
        values = data.get('values')
        if not values: values = {}
        filters = data.get('filters')
        table = filters.get('TableName')
        new_filters = {}
        for f in filters:
            if f not in ['TableName','NotFilterFields','_state']:
                new_filters[f] = filters[f]
        res = getRecordByFilters(table, new_filters, values)
        return jsonify(result=res)

@app.route('/_get_current_user_type')
def get_current_user_type():
    return jsonify(result={'user_type':current_user.UserType,'user_id':current_user.id})

@app.route('/_record_list')
def record_list():
    table = request.args.get('Table')
    fields = request.args.get('Fields').split(',')
    order_by = request.args.get('OrderBy',None)
    desc = request.args.get('Desc',None)
    limit = request.args.get('Limit',None)
    TableClass = getTableClass(table)
    records = TableClass.getRecordList(TableClass,limit=limit,order_by=order_by,desc=desc)
    filtersKeys,filtersNames = TableClass.recordListFilters()
    filters = {}
    links =     TableClass.getLinksTo(records)
    res = setColumns(records,links,filtersKeys,filters)
    for fieldname in fields:
        if fieldname[:6]=='Image':
            for dic in res:
                dic[fieldname] = getImageLink(table,dic['id'],fieldname)
    return jsonify(result={'records': res,'filters': filters, 'filtersNames': filtersNames})

@app.route('/_get_report')
def get_report():
    report_foder = settings.report_folder
    reportclass = request.args.get('Report')
    var = {}
    exec('from %s.%s import %s as ReportClass' % (report_foder,reportclass,reportclass),var)
    Report = var['ReportClass']
    filters = Report.reportFilters()
    htmlView = Report.htmlView()
    return jsonify(result={'filters': filters, 'htmlView': htmlView, 'ReportClass': reportclass})


@app.route('/_run_report')
def run_report():
    report_foder = settings.report_folder
    reportclass = request.args.get('Report')
    var = {}
    exec('from %s.%s import %s as ReportClass' % (report_foder,reportclass,reportclass),var)
    Report = var['ReportClass']
    filters = {}
    for key in request.args:
        if key!='Report':
            filters[key] = request.args.get(key)
    res = Report.run(filters)
    return jsonify(result=res)

@app.context_processor
def override_url_for():
    return dict(url_for=dated_url_for)

def dated_url_for(endpoint, **values):
    if endpoint == 'static':
        filename = values.get('filename', None)
        if filename:
            file_path = os.path.join(app.root_path,
                                     endpoint, filename)
            values['q'] = int(os.stat(file_path).st_mtime)
    return url_for(endpoint, **values)


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
        from db.UserFavorite import UserFavorite
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
    from db.UserNote import UserNote
    records = UserNote.getRecordList(UserNote,custId)
    return records


def getCustomer(args):
    favorite = args.get('favorite',None)
    session = Session()
    if not favorite:
        records = session.query(User).filter_by(UserType=3)
    else:
        from db.UserFavorite import UserFavorite

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

@app.route('/_get_calendar_events')
def get_calendar_events():
    profId = request.args.get('profId',None)
    companyId = request.args.get('companyId',None)
    eventId = request.args.get('eventId',None)
    res = showProfessionalEvents({'profId':profId,'eventId':eventId,'companyId': companyId})
    return jsonify(result=res)


@app.route('/_get_calendar_dates')
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

@app.route('/_get_favorite')
def get_favorite():
    from db.UserFavorite import UserFavorite
    favId = request.args.get('favId')
    session = Session()
    session.expire_on_commit = False
    record = session.query(UserFavorite).filter_by(UserId=current_user.id,FavoriteId=favId).first()
    if not record or not record.Checked:
        return jsonify(result=False)
    else:
        return jsonify(result=True)

@app.route('/_set_favorite')
def set_favorite():
    from db.UserFavorite import UserFavorite
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
    from db.UserService import UserService
    from db.Service import Service
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
            , 'KeyPayco': r.KeyPayco, 'CompanyPayment':r.CompanyPayment,'ProfName': r.ProfName, 'ProfId': r.ProfId})
        k += 1
    return res

@app.route('/_get_professional_list')
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


@app.route('/_set_cust_to_event')
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
    records = Activity.getRecordList(Activity,ProfId=UserId)
    list = []
    for record in records:
        st = "%sT%s" %(record.TransDate.strftime('%Y-%m-%d'),record.StartTime.strftime('%H:%M:%S'))
        et = "%sT%s" %(record.TransDate.strftime('%Y-%m-%d'),record.EndTime.strftime('%H:%M:%S'))
        onclick = ''' showActivity(%i)''' % record.id
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
        comment = ''
        if record.Type:
            comment = record.Comment
        elif record.CustName:
            comment = record.CustName
        list.append({'title': comment,'start':st,'end':st,'onclick':onclick,'id':id,'backgroundColor':BGColor, \
            'textColor': textColor, 'actType': record.Type})
    return list

@app.route('/calendar_data')
def return_data():
    UserId = request.args.get('UserId', '')
    res = getCalendarData(UserId)
    return jsonify(res)
    with open("events.json", "r") as input_data:
        return input_data.read()

@app.route('/_set_notification_read')
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

@app.route('/_get_notifications')
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


@app.route('/_get_current_date')
def get_current_date():
    date = today()
    w = date.weekday()
    m = date.month
    Y = date.year
    d = date.day
    hoy = 'Hoy es %s %i de %s de %i' %(WeekName[w],d,meses[m],Y)
    return jsonify(result=hoy)


@app.route('/_event_list')
def event_list():
    order_by = request.args.get('OrderBy',None)
    desc = request.args.get('Desc',None)
    limit = request.args.get('Limit',None)
    UserId = None
    CompanyId = None
    if current_user.UserType==1:
        CompanyId = current_user.CompanyId
    elif current_user.UserType==2:
        UserId = current_user.id
    records = Activity.getEventList(UserId,CompanyId,limit=limit,order_by=order_by,desc=desc)
    ids = []
    events = []
    for r in records:
        if r.id not in ids:
            ids.append(r.id)
            events.append(r)
    events = setColumns(events,[],[],[])
    return jsonify(result=events)

@app.route('/_cancel_activity')
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

@app.route('/epayco/<activity_id>')
def epayco(activity_id):
    return render_template('epayco_res.html',current_user=current_user,app_name=settings.app_name,activityId=activity_id)


@app.route('/_set_payment')
def set_payment():
    from db.Payment import Payment
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


@app.route('/_get_payment')
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


@app.route('/_customer_list')
def customer_list():
    vars = {}
    for key in request.args:
        vars[key] = request.args.get(key)
        if vars[key] in ('true','True'):
            vars[key] = True
        elif vars[key] in ('false', 'False'):
            vars[key] = False
    records = getCustomer(vars)
    links = User.getLinksTo(records)
    res = setColumns(records,links,[],[])
    return jsonify(result={'records': res,'filters': [], 'filtersNames': []})

@app.route('/_get_service_price')
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


@app.context_processor
def utility_processor():
    def sortDict(myDict):
        return sorted(myDict)
    def getCanUserCreate(table):
        return canUserCreate(table)
    def getCanUserAddRow(table):
        return canUserAddRow(table)
    def getCanUserDeleteRow(table):
        return canUserDeleteRow(table)
    def myFunction(function,params=None):
        return getMyFunction(function,params)
    def getTemplate(template):
        if "%s_template" % template in settings.templates:
            return settings.templates["%s_template" % template]
        return "%s.html" % template
    def getStrfTime(t,f):
        return t.strftime(f)
    def getImageURL(table,id,fieldname):
        return getImageLink(table,id,fieldname)
    def getConst(const):
        if const=='USER_ID': return current_user.id
        return getattr(settings,const)
    return dict(sortDict=sortDict \
        ,myFunction=myFunction \
        ,getCanUserCreate=getCanUserCreate \
        ,getCanUserAddRow=getCanUserAddRow \
        ,getCanUserDeleteRow=getCanUserDeleteRow \
        ,getTemplate=getTemplate \
        ,getStrfTime=getStrfTime \
        ,getImageURL=getImageURL \
        ,getConst=getConst \
        )

if __name__ == "__main__":
    #socketio.run(app, host="0.0.0.0")
    app.run(host= '0.0.0.0')
