from flask import Flask,jsonify, request
from database import DB
from config import Config
import os, sys
from flask_mail import Mail
import apis.utils.constants as CONST
from apis.utils.common import *
from werkzeug.exceptions import HTTPException
from werkzeug.exceptions import default_exceptions
from flask_cors import CORS
import logging 

def create_app(object):
    app = Flask(__name__)
    CORS(app)
    # Set email configurations
    app.config.update(
        dict(
            MAIL_SERVER = CONST.MAIL_SERVER,
            MAIL_PORT = CONST.MAIL_PORT,
            MAIL_USE_TLS = CONST.MAIL_USE_TLS,
            MAIL_USE_SSL = CONST.MAIL_USE_SSL,
            MAIL_USERNAME = CONST.MAIL_USERNAME,
            MAIL_PASSWORD = CONST.MAIL_PASSWORD,
            MAIL_DEBUG = True
        )
	)
    
    mail = Mail(app=app)
    
    @app.errorhandler(Exception)
    def handle_error(e):
        code = 500
        if isinstance(e, HTTPException):
            code = e.code
        return jsonify(status=code,error=str(e),message="Something went wrong"), code

    # Token validation on each request
    @app.before_request
    def hook():
        is_validate = validate_token(app.config["STATIC_TOKEN"])
        if is_validate != True:
            return output_json({},"Request is not valid!",status=False,code=401)

    for ex in default_exceptions:
        app.register_error_handler(ex, handle_error)

    print(f'ENV is set to: {app.config["ENV"]}')
    if app.config["ENV"] == "production":
        app.config.from_object("config.ProductionConfig")
        print(f'MONGO_URI: {app.config["MONGO_URI"]}') 
    else:
        app.config.from_object("config.DevelopmentConfig")
        print(f'MONGO_URI: {app.config["MONGO_URI"]}')      

    # initializa db
    DB.init(app)
    return app
    
    



