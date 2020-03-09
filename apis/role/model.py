from flask_restplus import Namespace, fields
import socket
import time
from datetime import datetime, date, time, timedelta
from flask import jsonify, request
from database import DB
from bson import json_util, ObjectId
from apis.utils.common import *
import logging
import apis.utils.message_constants as MSG_CONST
import apis.utils.constants as CONST
import apis.utils.role as role
import sys
#logging.basicConfig(filename='/logs/vendor.log', level=logging.DEBUG)

tbl_v002_vendors = "v002_vendors"
tbl_v003_vendor_users = "v003_vendor_users"
tbl_v004_outlets = "v004_outlets"
tbl_a008_role = "a008_role"
tbl_v017_modules = "v017_modules"
tbl_v005_roles  = "v005_roles"
tbl_v018_module_access = "v018_module_access"

def roleListModel(self, ns):
    roleListModel = ns.model('roleListModel', {
        'user_id': fields.String(required=False, min_length=1, example=1, description='User id is required'),
        'vendor_id': fields.String(required=True, min_length=1, example=1, description='vendor id is required'),
        'role': fields.String(required=False, description='Provide role required')
    })
    return roleListModel

def roleAccessSaveModel(self, ns):
    roleAccessSaveModel = ns.model('roleAccessSaveModel', {
        'user_id': fields.String(required=False, min_length=1, example=1, description='User id is required'),
        'vendor_id': fields.String(required=True, min_length=1, example=1, description='vendor id is required'),
        'role_id': fields.String(required=False, description='Provide role required'),
        'module_id': fields.String(required=False, description='Provide role required'),
        'access_type': fields.String(required=False, description='Provide role required')
    })
    return roleAccessSaveModel

def roleList(self):
    code = 201
    status = False
    message = ""
    responseData = {}
    todayDate = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    ip_address = socket.gethostbyname(socket.gethostname())

    roleList = role.RoleAccess().getAllRole()
    if roleList:
        responseData = roleList
        status = True
        code = 200
        message = MSG_CONST.VENDOR_SUCCESS
    else:
        responseData = {}
        status = False
        code = 200
        message = MSG_CONST.VENDOR_NO_RECORD_FOUND

    response = output_json(responseData, message, status, code)
    #logging.debug('vendor_role_list: {}'.format(response))
    return response


def manageRolePageAPI(self):
    code = 201
    status = False
    message = ""
    responseData = {}
    requestData = dict(request.json)
    ip_address = socket.gethostbyname(socket.gethostname())
    roleList = role.RoleAccess(None,requestData["vendor_id"]).manageRolePageAPI()
    if roleList:
        responseData = roleList
        status = True
        code = 200
        message = MSG_CONST.VENDOR_SUCCESS
    else:
        responseData = {}
        status = False
        code = 200
        message = MSG_CONST.VENDOR_NO_RECORD_FOUND

    response = output_json(responseData, message, status, code)
    #logging.debug('vendor_role_list: {}'.format(response))
    return response

def saveRoleAccess(self):
    code = 201
    status = False
    message = ""
    responseData = {}
    requestData = dict(request.json)
    act = role.RoleAccess(None,requestData["vendor_id"]).saveRoleAccess(requestData)
    if act:
        status = True
        code = 200
        message = MSG_CONST.VENDOR_SAVE_ROLE_SUCCESS
    else:
        responseData = {}
        status = False
        code = 200
        message = MSG_CONST.VENDOR_SAVE_ROLE_FAILED

    response = output_json(responseData, message, status, code)
    #logging.debug('vendor_role_list: {}'.format(response))
    return response

def getRoleAccess(self):
    code = 200
    status = False
    message = ""
    responseData = {}
    requestData = dict(request.json)
    
    act = role.RoleAccess(requestData["role"],requestData["vendor_id"],requestData["user_id"]).getRoleAccess()
    
    if act:
        responseData['menu_access'] = act
        status = True
        code = 200
        message = MSG_CONST.VENDOR_SAVE_ROLE_SUCCESS
    else:
        responseData = {}
        status = False
        code = 200
        message = MSG_CONST.VENDOR_SAVE_ROLE_FAILED

    Get_nav = DB.find_all_where(tbl_v017_modules,{"status":int(1),"is_menu":int(1)},"ALL",'index')
    responseData['header_menu'] = Get_nav
    # print(responseData)
    response = output_json(responseData, message, status, code)
    #logging.debug('vendor_role_list: {}'.format(response))
    return response


def create_new_role(self):
    code = 201
    status = False
    message = ""
    addData = {}
    responseData = {}
    requestData = dict(request.json)
    vendor_id = ObjectId(requestData["vendor_id"])
    
    find_vendor = DB.find_one(tbl_v002_vendors,{"_id":vendor_id})
    
    addData["name"] = requestData["name"]
    addData['vendor_id'] = vendor_id
    if find_vendor:
        add_role = DB.insert(tbl_a008_role,addData)
        code = 200
        status = True
        message = "Role added Successfully..!"
    else:
        code = 201
        status = False
        message = "Sorry, Something went wrong..!"
    response = output_json(add_role, message, status, code)
    #logging.debug('create_new_role: {}'.format(response))
    return response  



#######Get all Modules##########
    
def get_all_module(self,user_id,role_id):
    field_list = {"_id":1,"name":1}
    module_data = {}
    modules = DB.find_all_where(tbl_v017_modules,{"status":1,"is_menu":0},field_list)
    if role_id != "":
        role_data = DB.find_one(tbl_v005_roles,{"_id":ObjectId(role_id)},field_list)
    else:
        role_data = []
    module_data['modules'] = modules
    module_data['role'] = role_data
    if modules:
        code = 200
        status = True
        message = "Modules get successfully..!"
    else:
        code = 201
        status = False
        message = "Sorry, Something went wrong..!"
    response = output_json(module_data, message, status, code)
    #logging.debug('create_new_role: {}'.format(response))
    return response


