import os
class Config(object):
    DEBUG = True
    TESTING = True
    DB_NAME="miiot-dev"
    SECRET_KEY = "B\xb2?.\xdf\x9f\xa7m\xf8\x8a%,\xf7\xc4\xfa\x91"
    MONGO_URI="YOUR_CONNECTION_URL"
    IMAGE_UPLOADS = "/home/username/projects/my_app/app/static/images/uploads"
    SESSION_COOKIE_SECURE = False
    SMS_SERVER = ""
    SMS_USER = ""
    SMS_PASSWORD = ""
    STATIC_TOKEN = ""
    

class ProductionConfig(Config):
    DEBUG = False
    MONGO_URI="YOUR_CONNECTION_URL"
    DB_NAME="miiot-dev"
    IMAGE_UPLOADS = "/home/username/projects/my_app/app/static/images/uploads"
    SESSION_COOKIE_SECURE = True
    SMS_SERVER : ""
    SMS_USER : ""
    SMS_PASSWORD : ""
    STATIC_TOKEN = ""

class DevelopmentConfig(Config):
    DEBUG = True
    MONGO_URI="YOUR_CONNECTION_URL"
    DB_NAME="miiot-dev"
    IMAGE_UPLOADS = "/home/username/projects/my_app/app/static/images/uploads"
    SESSION_COOKIE_SECURE = False
    SMS_SERVER : ""
    SMS_USER : ""
    SMS_PASSWORD : ""
    STATIC_TOKEN = ""

class TestingConfig(Config):
    DEBUG = True
    TESTING = True
    MONGO_URI="YOUR_CONNECTION_URL"
    DB_NAME="miiot-dev"
    IMAGE_UPLOADS = "/home/username/projects/my_app/app/static/images/uploads"
    SESSION_COOKIE_SECURE = False
    SMS_SERVER : ""
    SMS_USER : ""
    SMS_PASSWORD : ""
    STATIC_TOKEN = ""    
