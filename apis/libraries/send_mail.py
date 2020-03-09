from flask_restplus import Resource, Namespace
from flask_mail import Mail, Message
import apis.utils.constants as CONST

class Send_mail(Resource):
    def __init__(self):
        pass

    def send(self,subject, recipients, body, attechment=None):
        mail = Mail(None)
        # print(str(recipients))
        send = mail.send_message(subject=subject, sender=CONST.MAIL_USERNAME, recipients=recipients, body=body)
        # print(send)
        return send