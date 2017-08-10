# -*- coding: utf-8 -*-
from tools.Mail import sendMail

def sendPasswordRecoverMail(email,newpwd,username):
    msj = "\n"
    msj += "Estimado %s\n" % username
    msj += "Su nuevo password es: %s\n" % newpwd
    msj += "\n"
    return sendMail(email,'Donde Fluir: Recuperar Password',msj)

