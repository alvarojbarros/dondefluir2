# -*- coding: utf-8 -*-

from flask import Flask
app = Flask(__name__)
from flask import redirect, url_for, request, render_template,jsonify
from flask_login import LoginManager, login_required, login_user, logout_user,current_user
import getsettings
settings = getsettings.getSettings()
User = getsettings.getUserClass()
from tools.DBTools import *
from flask_mail import Mail
import re

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

app.register_blueprint(settings.custom_app)

# flask-login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

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
            from dondefluir.MailTools import sendPasswordRecoverMail
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

@app.route('/_update_linkto')
def update_linkto():
    table = request.args.get('TableName')
    fieldname = request.args.get('FieldName')
    fields = {}
    for key in request.args:
        if key not in ['TableName','_state']:
            fields[key] = request.args.get(key,None)
            if fields[key]=='null': fields[key] = None

    TableClass = getTableClass(table)
    record = TableClass()
    record.defaults()
    fieldsDef = TableClass.getfieldsDefinition(record)
    getDetailDict(fieldsDef)
    for key in fields:
        value = fields.get(key,None)
        if value:
            setValue(record,key,value)
    links = getLinksTo(fieldsDef,record,fieldname)
    return jsonify(result=links)


@app.route('/_save_record')
def save_record():
    table = request.args.get('TableName')
    TableClass = getTableClass(table)
    fields = {}
    for key in request.args:
        if key not in ['TableName','_state']:
            fields[key] = request.args.get(key,None)
            if fields[key]=='null': fields[key] = None
    _id = request.args.get('id')
    _state = int(request.args.get('_state'))

    session = Session()
    session.expire_on_commit = False
    if not _state:
        if not _id:
            del fields['id']
        new_record = TableClass()
        getDetailDict(fields)
        for key in fields:
            #defValue = TableClass.getDefValue(key)
            setValue(new_record,key,fields.get(key,None))
        new_record._new = True
        if not new_record.beforeInsert():
            return jsonify(result={'res': False,'Error':'Error en Campos'})
        res = new_record.check()
        if not res:
            return jsonify(result={'res': False,'Error':str(res)})
        session.add(new_record)
        res = new_record.afterInsert()
        if not res:
            return jsonify(result={'res': False,'Error':str(res)})
        try:
            session.commit()
        except Exception as e:
            session.rollback()
            session.close()
            return jsonify(result={'res': False,'Error':str(e)})
        new_record.callAfterCommitInsert()
        session.close()
        return jsonify(result={'res':True,'id':new_record.id,'syncVersion':new_record.syncVersion})
    else:
        record = session.query(TableClass).filter_by(id=_id).first()
        if not record.checkSyncVersion(fields.get('syncVersion',None)):
            return jsonify(result={'res': False,'Error':'Otro Usuario ha modoficado el Registro'})
        getDetailDict(fields)
        if not record:
            return jsonify(result={'res': False,'Error':'Registro no Encontrado'})
        record.setOldFields()
        for key in fields:
            setValue(record,key,fields.get(key,None))
        res = record.check()
        if not res:
            return jsonify(result={'res': False,'Error':str(res)})
        record.syncVersion += 1
        res = record.afterUpdate()
        if not res:
            return jsonify(result={'res': False,'Error':str(res)})
        try:
            session.commit()
        except Exception as e:
            session.rollback()
            session.close()
            return jsonify(result={'res': False,'Error':str(e)})
        record.callAfterCommitUpdate()
        session.close()
        RunJS = record.afterSaveJS()
        return jsonify(result={'res':True,'id':record.id,'syncVersion':record.syncVersion,'RunJS':RunJS})

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

def getRecordByFilters(table,filters,NotFilterFields=False):
    #NotFilterFields = False
    res = {}
    TableClass = getTableClass(table)
    session = Session()
    record = None
    if filters:
        record = session.query(TableClass).filter_by(**filters).first()
    if filters and not record:
        return {'res':False}
    if not filters:
        record = TableClass()
        record.defaults()
    fields = TableClass.getfieldsDefinition(record)
    htmlView = TableClass.getHtmlView()
    recordTitle = TableClass.getRecordTitle()
    canEdit = TableClass.canUserEdit(record)
    canDelete = TableClass.canUserDelete()
    if not NotFilterFields:
        filterFiedlsByUserAccess(fields)
    links = getLinksTo(fields,record)
    if record:
        if not NotFilterFields:
            record.filterFields(fields)
        from datetime import time,date
        for fname in fields:
            value = None
            if not TableClass.isPersistent(fname):
                if 'Method' in fields[fname]:
                    value = eval("record.%s" % fields[fname]['Method'])
            else:
                value = getattr(record,fname)
            if isinstance(value,list):
                res[fname] = []
                for row in value:
                    rfields = fields[fname]['fieldsDefinition']
                    rres = {}
                    for rfname in rfields:
                        if rfname[:2]=='__':
                            continue
                        rvalue = getattr(row,rfname)
                        if isinstance(rvalue,time):
                            rvalue = str(rvalue)
                        elif isinstance(rvalue,date):
                            rvalue = str(rvalue)
                        if value==None:
                            value = ''
                        rres[rfname] = rvalue
                    res[fname].append(rres)
            else:
                if isinstance(value,time):
                    value = str(value)
                elif isinstance(value,datetime):
                    value = value.strftime("%Y-%m-%dT%H:%M:%S")
                elif isinstance(value,date):
                    value = str(value)
                if value==None:
                    value = ''
                res[fname] = value
    session.close()
    return {'record': res, 'fields': fields, 'links': links,'htmlView':htmlView,'recordTitle':recordTitle,'canEdit':canEdit,'canDelete':canDelete}

@app.route('/_get_record')
def get_record():
    table = request.args.get('TableName')
    _state = request.args.get('_state','')
    NotFilterFields = request.args.get('NotFilterFields',None)
    filters = {}
    for f in request.args:
        if f not in ['TableName','NotFilterFields','_state']:
            filters[f] = request.args[f]
    res = getRecordByFilters(table,filters,NotFilterFields)
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
    columns = request.args.get('Columns',None)
    if columns: columns = eval(columns)
    TableClass = getTableClass(table)
    records = TableClass.getRecordList(TableClass,limit=limit,order_by=order_by,desc=desc)
    fieldsDef = TableClass.fieldsDefinition()
    filtersKeys = TableClass.recordListFilters()
    filtersNames = {}
    for field in filtersKeys:
        filtersNames[field] = fieldsDef[field]['Label']
    filters = {}
    res = fillRecordList(records,fields,fieldsDef)
    for fieldname in fields:
        if fieldname  in fieldsDef and 'Input' in fieldsDef[fieldname] and fieldsDef[fieldname]['Input']=='fileinput':
            for dic in res:
                dic[fieldname] = getImageLink(table,dic['id'],fieldname)
    setColumns(res,columns,filtersKeys,filters)

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
        return settings.getMyFunction(function,params)
    def getTemplate(template):
        if "%s_template" % template in settings.templates:
            return settings.templates["%s_template" % template]
        return "%s.html" % template
    def getStrfTime(t,f):
        return t.strftime(f)
    def getImageURL(table,id,fieldname):
        return getImageLink(table,id,fieldname)
    def getRecord(table,id):
        return getRecordByFilters(table,{'id': id})
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
        ,getRecord=getRecord \
        ,getConst=getConst \
        )

if __name__ == "__main__":
    app.run(host= '0.0.0.0')
