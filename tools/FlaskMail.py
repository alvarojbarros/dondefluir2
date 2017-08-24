from main import mail
from flask_mail import Message
import settings


def sendFlaskMail(email,subject,message):
    return
    sender = "%s <%s>" % (settings.AccountName,settings.Sender)
    receivers = [email]
    msg = Message(subject,sender=sender,recipients=receivers)
    msg.html = message
    mail.send(msg)
