# Create By : Yogesh Kothiya
# Uses : Manage Role

from flask import jsonify, request
import socket
import apis.utils.constants as CONST
from datetime import datetime, date, time, timedelta
import pymongo
from database import DB
import json
from bson import json_util, ObjectId

class crads:
    def __init__(self,vendor_id=None,userId=None):
        # self.todayDate = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.todayDate = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.ip_address = socket.gethostbyname(socket.gethostname())
        self.user_id = userId
        self.vendor_id = vendor_id
        self.tbl_v005_roles = "v005_roles"
        self.tbl_v018_module_access = "v018_module_access"
        self.tbl_v017_modules = "v017_modules"
        self.tbl_a011_settings = "a011_settings"
        

    def adminContact(self):
        adminData = DB.find_one(self.tbl_a011_settings, {"setting_for":"admin_contact"},{"_id":0,"name":1,"email":1,"mobile":1,"address":1})
        return adminData

    