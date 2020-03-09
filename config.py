import os
class Config(object):
    DEBUG = True
    TESTING = True
    DB_NAME="spafest-dev"
    SECRET_KEY = "B\xb2?.\xdf\x9f\xa7m\xf8\x8a%,\xf7\xc4\xfa\x91"
    MONGO_URI="mongodb+srv://itech:itech%40123@cluster0-wbh2p.mongodb.net/test?retryWrites=true&w=majority"
    IMAGE_UPLOADS = "/home/username/projects/my_app/app/static/images/uploads"
    SESSION_COOKIE_SECURE = False
    SMS_SERVER = "http://ui.netsms.co.in/"
    SMS_USER = "iTechNotion"
    SMS_PASSWORD = "itech@006"
    STATIC_TOKEN = "5uEDbB9P97DLyMWV"
    

class ProductionConfig(Config):
    DEBUG = False
    MONGO_URI="mongodb+srv://itech:itech%40123@cluster0-wbh2p.mongodb.net/test?retryWrites=true&w=majority"
    DB_NAME="wellnessta-dev"
    IMAGE_UPLOADS = "/home/username/projects/my_app/app/static/images/uploads"
    SESSION_COOKIE_SECURE = True
    SMS_SERVER : "http://ui.netsms.co.in/"
    SMS_USER : "iTechNotion"
    SMS_PASSWORD : "itech@006"
    STATIC_TOKEN = "5uEDbB9P97DLyMWV"

class DevelopmentConfig(Config):
    DEBUG = True
    MONGO_URI="mongodb+srv://itech:itech%40123@cluster0-wbh2p.mongodb.net/test?retryWrites=true&w=majority"
    DB_NAME="spafest-dev"
    IMAGE_UPLOADS = "/home/username/projects/my_app/app/static/images/uploads"
    SESSION_COOKIE_SECURE = False
    SMS_SERVER : "http://ui.netsms.co.in/"
    SMS_USER : "iTechNotion"
    SMS_PASSWORD : "itech@006"
    STATIC_TOKEN = "5uEDbB9P97DLyMWV"

class TestingConfig(Config):
    DEBUG = True
    TESTING = True
    MONGO_URI="mongodb+srv://itech:itech%40123@cluster0-wbh2p.mongodb.net/test?retryWrites=true&w=majority"
    DB_NAME="spafest-dev"
    IMAGE_UPLOADS = "/home/username/projects/my_app/app/static/images/uploads"
    SESSION_COOKIE_SECURE = False
    SMS_SERVER : "http://ui.netsms.co.in/"
    SMS_USER : "iTechNotion"
    SMS_PASSWORD : "itech@006"
    STATIC_TOKEN = "5uEDbB9P97DLyMWV"    