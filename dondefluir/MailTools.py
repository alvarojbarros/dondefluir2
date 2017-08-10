# -*- coding: utf-8 -*-

from tools.Mail import sendMail
from flask import render_template
from dondefluir.db.Service import Service
from dondefluir.db.Company import Company
from dondefluir.db.User import User
from datetime import date,time
import getsettings
settings = getsettings.getSettings()
from tools.Tools import *
from mako.template import Template
import io
folder = "%s/%s" %(settings.app_folder,settings.template_folder)

def strToDate(d):
    if isinstance(d,date): return d
    return date(int(d[:4]),int(d[5:7]),int(d[8:10]))

def strToTime(d):
    if isinstance(d,time): return d
    return time(int(d[:2]),int(d[3:5]),0)


def getVars(user,activity):
    var = {}
    var['UserName'] = user.Name
    var['ActivityTitle'] = 'Cita'
    if activity.Type==0 and activity.ServiceId:
        service = Service.getRecordById(activity.ServiceId)
        if service and service.Name:
            var['ActivityTitle'] = service.Name
    elif activity.Type in (1,2) and activity.Comment:
        var['ActivityTitle'] = activity.Comment
    elif activity.Type in (1,2) and activity.ServiceId:
        service = Service.getRecordById(activity.ServiceId)
        if service and service.Name:
            var['ActivityTitle'] = service.Name
    var['ProfId'] = activity.ProfId
    prof = User.getRecordById(activity.ProfId)
    if prof and prof.Name:
        var['ProfId'] = prof.Name
    var['UserAddress'] = ''
    if prof and prof.Address:
        var['UserAddress'] = prof.Address
        if prof and prof.City:
            var['UserAddress'] += " %s" % prof.City
    var['UserPhone'] = ''
    if prof and prof.Phone:
        var['UserPhone'] = prof.Phone
    if len(activity.Schedules)>0:
        row = activity.Schedules[0]
        transdate = strToDate(row.TransDate)
        datestr = "%s %i de %s de %i" % (WeekName[transdate.weekday()],transdate.day,meses[transdate.month],transdate.year)
        var['TransDateStr'] = datestr
        var['TransDate'] = transdate.strftime("%d.%m.%Y")
        var['StartTime'] = strToTime(row.StartTime).strftime("%H:%M")
        var['EndTime'] = strToTime(row.EndTime).strftime("%H:%M")
    company = Company.getRecordById(activity.CompanyId)
    var['CompanyName'] = ''
    if company and company.Name:
        var['CompanyName'] = company.Name
    var['WebSite'] = ''
    if company and company.WebSite:
        var['WebSite'] = company.WebSite
    if company and company.Address and not var['UserAddress']:
        var['UserAddress'] = company.Address
        if company.City:
            var['UserAddress'] += " %s" % company.City
    if company and company.Phone and not var['UserPhone']:
        var['UserPhone'] = company.Phone
    return var

def getTemplateHTML(f,var):
    res = Template(f.read(), default_filters=['decode.utf8'], input_encoding='utf-8', output_encoding='utf-8').render(var=var)
    return res

def sendMailUpdateActivity(user,activity):
    var = getVars(user,activity)
    f = io.open('%s/notificacionesModificacionCita.html' % folder,'r', encoding="utf-8")
    msj = getTemplateHTML(f,var)
    subject = ' Actividad modificada: %s - %s con %s' % (var['TransDate'],var['ActivityTitle'],var['ProfId'])
    return sendMail(user.Email,subject,msj)

def sendMailCancelActivity(user,activity):
    var = getVars(user,activity)
    f = io.open('%s/notificacionesCancelacionCita.html' % folder,'r', encoding="utf-8")
    msj = getTemplateHTML(f,var)
    subject = ' Actividad cancelada: %s - %s con %s' % (var['TransDate'],var['ActivityTitle'],var['ProfId'])
    return sendMail(user.Email,subject,msj)

def sendMailConfirmActivity(user,activity):
    var = getVars(user,activity)
    f = io.open('%s/notificacionesConfirmacionCita.html' % folder,'r', encoding="utf-8")
    msj = getTemplateHTML(f,var)
    subject = ' Actividad confirmada: %s - %s con %s' % (var['TransDate'],var['ActivityTitle'],var['ProfId'])
    return sendMail(user.Email,subject,msj)

def sendMailNewActivity(user,activity):
    var = getVars(user,activity)
    f = io.open('%s/notificacionesCreacionCita.html' % folder,'r', encoding="utf-8")
    msj = getTemplateHTML(f,var)
    subject = ' Nueva actividad: %s - %s con %s' % (var['TransDate'],var['ActivityTitle'],var['ProfId'])
    return sendMail(user.Email,subject,msj)

def sendNewUserMail(user,name,password):
    f = io.open('%s/notificacionesCreacionUsuario.html' % folder,'r', encoding="utf-8")
    msj = Template(f.read(), default_filters=['decode.utf8'], input_encoding='utf-8', output_encoding='utf-8')\
        .render(user=user,name=name,password=password)
    subject = 'Te damos la bienvenida a Donde Fluir!'
    return sendMail(user,subject,msj)

def sendMailNewCustActivity(user,activity):
    var = getVars(user,activity)
    f = io.open('%s/notificacionesNuevosClientesActividad.html' % folder,'r', encoding="utf-8")
    msj = getTemplateHTML(f,var)
    subject = ' Hay nuevos clientes en el %s: %s - %s con %s' % (['la Actividad','el Curso','el Evento'][activity.Type] \
        ,var['TransDate'],var['ActivityTitle'],var['ProfId'])
    return sendMail(user.Email,subject,msj)

def sendPasswordRecoverMail(email,newpwd,username):
    f = io.open('%s/notificacionesCambioPassword.html' % folder, 'r', encoding="utf-8")
    var = {'Email': email, 'UserName': username, 'Password': newpwd}
    msj = getTemplateHTML(f, var)
    return sendMail(email,'Donde Fluir: Recuperar Password',msj)
