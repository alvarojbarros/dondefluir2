# -*- coding: utf-8 -*-

def sendMail(email,subject,message):
    from tools.FlaskMail import sendFlaskMail
    try:
        sendFlaskMail(email,subject,message)
        return True
    except:
        pass