from flask_restplus import Namespace, fields
import socket
import time
#from datetime import datetime, date, time, timedelta
from flask import jsonify, request
import pymongo
from database import DB
from bson import json_util, ObjectId
from apis.utils.common import *
from apis.libraries.send_mail import Send_mail
import requests
import logging
import apis.utils.subscription as subscription
import apis.utils.message_constants as MSG_CONST
import apis.utils.constants as CONST
import apis.utils.role as role
import sys
import copy
from werkzeug.security import generate_password_hash, check_password_hash

#logging.basicConfig(filename='/logs/vendor.log', level=logging.DEBUG)

# Declare tables name in vars
tbl_v002_vendors = "v002_vendors"
tbl_v003_vendor_users = "v003_vendor_users"
tbl_v004_outlets = "v004_outlets"
tbl_v005_roles = "v005_roles"
tbl_a013_tag_master = "a013_tag_master"
tbl_v026_tour_steps = "v026_tour_steps" 
tbl_v017_modules = "v017_modules"
tbl_v018_module_access = "v018_module_access"
tbl_a001_email_template="a001_email_template"

def addStaffModel(self, ns):
    returnModel = ns.model('addStaffModel', {
        'user_id': fields.String(required=False, min_length=1, example=1, description='User id is required'),
        'outlet_id': fields.List(fields.String,required=True, description='Outletid id is required'),
        'vendor_id': fields.String(required=True, min_length=1, example=1, description='vendor id is required'),
        'staff_id': fields.String(required=False, description="Provide registred user id"),
        'name': fields.String(required=True, min_length=1, description='Name is required'),
        'gender': fields.String(required=True, enum=["male", "female", "both"], description='Name is required'),
        'email': fields.String(required=False, description='Email is required'),
        'password': fields.String(required=False, max_length=16, description='Password field is required'),
        'role': fields.String(required=False, description='Provide role required')
    })
    return returnModel


def roleListModel(self, ns):
    roleListModel = ns.model('roleListModel', {
        'user_id': fields.String(required=True, min_length=1, example=1, description='User id is required'),
        'vendor_id': fields.String(required=True, min_length=1, example=1, description='vendor id is required')
    })
    return roleListModel


def designationtModel(self, ns):
    designationtModel = ns.model('designationtModel', {
        'user_id': fields.String(required=True, min_length=1, example=1, description='User id is required'),
        'vendor_id': fields.String(required=True, min_length=1, example=1, description='vendor id is required')
    })
    return designationtModel

def outletModel(self, ns):
    outletModel = ns.model('outletModel', {
        'user_id': fields.String(required=True, min_length=1, example=1, description='User id is required'),
        'vendor_id': fields.String(required=True, min_length=1, example=1, description='vendor id is required')
    })
    return outletModel



def emailVerifyModel(self, ns):
    emailVerifyModel = ns.model('emailVerifyModel', {
        'user_id': fields.String(required=True, min_length=1, example=1, description='User id is required'),
        'vendor_id': fields.String(required=True, min_length=1, example=1, description='vendor id is required'),
        'email': fields.String(required=False, example=1, description='email is required')
    })
    return emailVerifyModel


def contactVerifyModel(self, ns):
    roleListModel = ns.model('roleListModel', {
        'user_id': fields.String(required=True, min_length=1, example=1, description='User id is required'),
        'vendor_id': fields.String(required=True, min_length=1, example=1, description='vendor id is required'),
        'contact_number': fields.String(required=True, example=1, description='email is required')
    })
    return roleListModel


def staffListModel(self, ns):
    staffListModel = ns.model('staffListModel', {
        'user_id': fields.String(required=True, min_length=1, example=1, description='User id is required'),
        'vendor_id': fields.String(required=True, min_length=1, example=1, description='vendor id is required'),
        'outlet_id': fields.String(required=True, example=1, description='Outlet id is required')
    })
    return staffListModel

def removeStaffModel(self, ns):
    removeStaffModel = ns.model('removeStaffModel', {
        'user_id': fields.String(required=True, min_length=1, example=1, description='User id is required'),
        'vendor_id': fields.String(required=True, min_length=1, example=1, description='vendor id is required'),
        'staff_id': fields.String(required=True, example=1, description='Staff id is required')
    })
    return removeStaffModel

def saveStaff(self):
    
    code = 201
    status = False
    message = ""
    responseData = {}
    todayDate = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    ip_address = socket.gethostbyname(socket.gethostname())
    website = "https://vendor.wellnessta.in"
    requestData = dict(request.json)
    # role = DB.find_one(tbl_v005_roles,{"_id":ObjectId(requestData['role'])},{"name":1})
    
    # if requestData["staff_design"] == "5e2af18affccb954c0d7c7d4":
    #     designation = DB.find_one(tbl_a013_tag_master,{"_id":ObjectId(requestData['staff_design'])},{"title":1})
    # elif requestData["staff_design"] == "5e2af1cdba2de554c027ba31":
    #     designation = DB.find_one(tbl_a013_tag_master,{"_id":ObjectId(requestData['staff_design'])},{"title":1})
    # else:
    #     designation = DB.find_one(tbl_a013_tag_master,{"_id":ObjectId(requestData['staff_design'])},{"title":1})        
    
    receiver_user_id = DB.find_one(tbl_v003_vendor_users,{"vendor_id":ObjectId(requestData['vendor_id'])},{"_id":1})
    receiver_id = receiver_user_id['_id']['$oid']
    user_name = requestData["name"]
    username = requestData["email"]
    password = requestData["password"]
    # role_name = role["name"]
    data = {}
    user_id = 0
    userData = {}
    
    create_by = ObjectId(requestData["user_id"])
    # outlet_id = ObjectId(requestData["outlet_id"])
    
    outlets = requestData["outlet_id"]
    outlet_ids = []
    for ids in outlets:
        outlets_id = ObjectId(ids)
        outlet_ids.append(outlets_id)
    outlet_id = outlet_ids
    # print(outlets[0])
    
    vendor_id = ObjectId(requestData["vendor_id"])
    staff_id = ObjectId(
        requestData["staff_id"]) if "staff_id" in requestData and requestData["staff_id"] != "" else ""

    # Validate Email Unique or not
    checkEmail = DB.find_one(tbl_v003_vendor_users, {"_id": {
                             "$nin": [staff_id]}, "email": requestData["email"].strip(" ")}, {"_id": 0})
    
    if requestData["staff_type"] == "managerial_staff":
        if checkEmail:
            message = MSG_CONST.VENDOR_SAVE_EMAIL_EXISTS
            response = output_json(responseData, message, status, code)
            #logging.debug('vendor_save_staff: {}'.format(response))
            return response

    checkNumber = DB.find_one(tbl_v003_vendor_users, {"_id": {"$nin": [
                              staff_id]}, "contact_number": requestData["contact_number"].strip(" ")}, {"_id": 0})
    
    data["vendor_id"] = vendor_id
    data["outlet_id"] = outlet_id
    data["name"] = requestData["name"].strip(" ").title()
    data["gender"] = requestData["gender"]
    data["contact_number"] = requestData["contact_number"]
    data["email"] = requestData["email"].strip(" ")
    data["password2"]=requestData["password"]
    if requestData["staff_type"] == "managerial_staff":
        # data["role"] = ObjectId(requestData["role"])
        data["profile_picture"] = requestData["profile_picture"].strip(" ")
        if requestData["password"] != "":
            data["password"] = generate_password_hash(
            requestData["password"].strip(" "))
        elif not requestData["password"] and staff_id == "":
            message = MSG_CONST.VENDOR_SAVE_PASSWORD_EMPTY
            response = output_json(responseData, message, status, code)
            #logging.debug('vendor_save_staff: {}'.format(response))
            return response
    data["staff_type"] = requestData["staff_type"]
    data["designation"] = requestData["staff_design"]
    
    # if requestData["staff_design"] == "5e2af18affccb954c0d7c7d4":
    #     data["designation"] = ObjectId(requestData["staff_design"])
    # elif requestData["staff_design"] == "5e2af1cdba2de554c027ba31":
    #     data["designation"] = ObjectId(requestData["staff_design"])
    # else:
    #     data["designation"] = ObjectId(requestData["staff_design"])

    
    act = None
    if staff_id:
        find_gender_count = DB.find_one(tbl_v004_outlets,{"_id":ObjectId(outlets[0])},{"_id":0,"female_count":1,"male_count":1})
        male_count = find_gender_count["male_count"]
        female_count = find_gender_count["female_count"]

        find_gender = DB.find_one(tbl_v003_vendor_users,{"_id":ObjectId(requestData["staff_id"])},{"_id":0,"gender":1})
        if find_gender['gender'] != requestData['gender']:
            if (find_gender['gender'] == 'female') and (requestData['gender'] == "male"):
                gender_count = DB.update_one(tbl_v004_outlets,{"male_count":male_count + 1, "female_count":female_count - 1},{"_id":ObjectId(outlets[0])})
            else:
                gender_count = DB.update_one(tbl_v004_outlets,{"male_count":male_count - 1, "female_count":female_count + 1},{"_id":ObjectId(outlets[0])})
                
        data["update_by"] = create_by
        data["update_ip"] = ip_address
        act = DB.update_one(tbl_v003_vendor_users, data, {"_id": staff_id})
    else:
        if requestData["is_theraphist"] == "true":
            if(requestData['gender'] == 'male'):
                Booking = DB.find_all_where(tbl_v003_vendor_users,{"$and":[{"outlet_id":ObjectId(outlets[0])},{"gender":"male"},{"is_delete": 0}]},"ALL")
                total_male_count = len(Booking)
                male_count = DB.update_one(tbl_v004_outlets,{"male_count":total_male_count + 1},{"_id":ObjectId(outlets[0])})
            elif(requestData['gender'] == 'female'):
                Booking = DB.find_all_where(tbl_v003_vendor_users,{"$and":[{"outlet_id":ObjectId(outlets[0])},{"gender":"female"},{"is_delete": 0}]},"ALL")
                total_female_count = len(Booking)
                male_count = DB.update_one(tbl_v004_outlets,{"female_count":total_female_count + 1 },{"_id":ObjectId(outlets[0])})
            data["is_theraphist"] = True
        else:
            data["is_theraphist"] = False
        data["create_by"] = create_by
        data["insert_ip"] = ip_address
        data["is_delete"] = 0
        data["email_verify"] = 0
        data["contact_verify"] = 0
        act = DB.insert(tbl_v003_vendor_users, data)
        res= DB.update_one(tbl_v026_tour_steps,{"setup_staff":True},{"vendor_id":vendor_id})
        responseData["staff_id"] = act
    if act:
        code = 200
        status = True
        message = MSG_CONST.VENDOR_SAVE_USER_SUCCESS 
    else:
        code = 201
        status = False
        message = MSG_CONST.VENDOR_SAVE_USER_FAILED
    response = output_json(responseData, message, status, code)
    #logging.debug('vendor_save_staff: {}'.format(response))
    return response


def getRoleList(self):
    requestData = dict(request.json)
    cnt=''
    if requestData["outlet_id"]!='':
        userdata = DB.find_all_where(tbl_v003_vendor_users,{"outlet_id": ObjectId(requestData["outlet_id"]),'staff_type':'managerial_staff','is_delete':0} ,{"_id": 1, "name": 1})
        cnt=len(userdata)
    roleData = DB.find_all(tbl_v005_roles, {"_id": 1, "name": 1})
    if roleData:
        for x in range(len(roleData)):
            roleData[x]["_id"] = roleData[x]["_id"]["$oid"]
        code = 200
        status = True
        message = MSG_CONST.VENDOR_SUCCESS
        responseData = roleData
    else:
        code = 200
        status = False
        message = MSG_CONST.VENDOR_NO_RECORD_FOUND
    response = output_json(cnt, message, status, code)
    #logging.debug('vendor_get_role_list_staff: {}'.format(response))
    return response



# def getDesignationList(self):
#     designationData = DB.find_all(tbl_a013_tag_master,{"_id": 1, "title": 1})
#     if designationData:
#         for x in range(len(designationData)):
#             designationData[x]["_id"] = designationData[x]["_id"]["$oid"]
#         code = 200
#         status = True
#         message = MSG_CONST.VENDOR_SUCCESS
#         responseData = designationData
#     else:
#         code = 200
#         status = False
#         message = MSG_CONST.VENDOR_NO_RECORD_FOUND
#     response = output_json(responseData, message, status, code)
#     #logging.debug('getDesignationList: {}'.format(response))
#     return response


def getDesignationListByManagerial(self):
    designationData = DB.find_all_where(tbl_a013_tag_master,{"type":"managerial-staff"},{"_id": 1, "title": 1})
    if designationData:
        for x in range(len(designationData)):
            designationData[x]["_id"] = designationData[x]["_id"]["$oid"]
        code = 200
        status = True
        message = MSG_CONST.VENDOR_SUCCESS
        responseData = designationData
    else:
        code = 200
        status = False
        message = MSG_CONST.VENDOR_NO_RECORD_FOUND
    response = output_json(responseData, message, status, code)
    #logging.debug('getDesignationList: {}'.format(response))
    return response


def getDesignationListByoperational(self):
    designationData = DB.find_all_where(tbl_a013_tag_master,{"type":"operational-staff"},{"_id": 1, "title": 1})
    if designationData:
        for x in range(len(designationData)):
            designationData[x]["_id"] = designationData[x]["_id"]["$oid"]
        code = 200
        status = True
        message = MSG_CONST.VENDOR_SUCCESS
        responseData = designationData
    else:
        code = 200
        status = False
        message = MSG_CONST.VENDOR_NO_RECORD_FOUND
    response = output_json(responseData, message, status, code)
    #logging.debug('getDesignationList: {}'.format(response))
    return response






def getOutletList(self):
    requestData = dict(request.json)
    OutletData = DB.find_all_where(tbl_v004_outlets,{"vendor_id":ObjectId(requestData["vendor_id"])},{"_id": 1, "name": 1})
    if OutletData:
        for x in range(len(OutletData)):
            OutletData[x]["_id"] = OutletData[x]["_id"]["$oid"]
        code = 200
        status = True
        message = MSG_CONST.VENDOR_SUCCESS
        responseData = OutletData
    else:
        OutletData = []
        code = 200
        status = False
        responseData = OutletData
        message = MSG_CONST.VENDOR_NO_RECORD_FOUND
    response = output_json(responseData, message, status, code)
    #logging.debug('getOutletList: {}'.format(response))
    return response




def emailCheckStaff(self):
    code = 201
    status = False
    message = ""
    responseData = {}

    requestData = dict(request.json)
    data = {}
    user_id = 0
    userData = {}

    if "email" in requestData and requestData["email"]:
        where = {"email": requestData["email"]}
        if requestData["staff_id"]:
            where["_id"] = {"$ne": ObjectId(requestData["staff_id"])}

        emailData = DB.find_one(tbl_v003_vendor_users, where, {"vendor_id": 1, "email": 1})
        if emailData:
            status = False
            message = MSG_CONST.VENDOR_SAVE_EMAIL_EXISTS
            responseData = {}
        else:
            status = True
            message = MSG_CONST.VENDOR_EMAIL_IS_AVAILABLE
            responseData = {}
    else:
        status = False
        message = MSG_CONST.VENDOR_EMAIL_EMPTY
        responseData = {}

    response = output_json(responseData, message, status, code)
    #logging.debug('vendor_verify_staff_email: {}'.format(response))
    return response


def contactCheckStaff(self):
    code = 201
    status = False
    message = ""
    responseData = {}

    requestData = dict(request.json)
    data = {}
    user_id = 0
    userData = {}

    if "contact_number" in requestData and requestData["contact_number"]:
        where = {"contact_number": requestData["contact_number"]}
        if requestData["staff_id"]:
            where["_id"] = {"$ne": ObjectId(requestData["staff_id"])}

        emailData = DB.find_one(tbl_v003_vendor_users, where, {"vendor_id": 1, "contact_number": 1})
        if emailData:
            status = False
            message = MSG_CONST.VENDOR_CONTACT_NUMBER_EXISTS
            responseData = {}
        else:
            status = True
            message = MSG_CONST.VENDOR_CONTACT_NUMBER_IS_AVAILABLE
            responseData = {}
    else:
        status = False
        message = MSG_CONST.VENDOR_CONTACT_STAFF_NUMBER_EMPTY
        responseData = {}

    response = output_json(responseData, message, status, code)
    #logging.debug('vendor_verify_staff_email: {}'.format(response))
    return response


def getStaff(self):
    
    code = 201
    status = False
    message = ""
    responseData = {}
    user_id = request.args.get("staff_id")
    user_id = ObjectId(user_id) if user_id != "" else user_id
    data = {}
    userData = {}
    
    if user_id:
        selFiled = {"_id": 1, "vendor_id": 1, "outlet_id": 1, "name": 1, "gender": 1,
                    "contact_number": 1, "email": 1, "profile_picture": 1, "role": 1 , "designation":1, "staff_type":1,"is_theraphist":1}
        user_data = DB.find_one(tbl_v003_vendor_users, {"_id": user_id}, selFiled)
        
        if user_data:
            status =  True
            message = MSG_CONST.VENDOR_SUCCESS
            user_data["_id"] = user_data["_id"]["$oid"]
            user_data["outlet_id"] = [out_id['$oid'] for out_id in user_data["outlet_id"]]
            user_data["vendor_id"] = user_data["vendor_id"]["$oid"]
            # if user_data["staff_type"] == "managerial_staff":
                # if "role" in user_data and "$oid" in user_data["role"] and user_data["role"]["$oid"]:
                #     user_data["role"] = user_data["role"]["$oid"]
                # else:
                #     user_data["role"] = user_data["role"]
            if "designation" in user_data and "$oid" in user_data["designation"] and user_data["designation"]["$oid"]:
                user_data["designation"] = user_data["designation"]["$oid"]
            else:
                user_data["designation"] = user_data["designation"]    
            responseData = user_data
        else:
            status = False
            message = MSG_CONST.VENDOR_OUTLET_NOT_FOUND
            responseData = {}
    else:
        status = False
        message = MSG_CONST.VENDOR_USER_ID_EMPTY
        responseData = {}
    
    response = output_json(responseData, message, status, code)
    #logging.debug('vendor_get_user_data_email: {}'.format(response))
    return response


def staff_list(self):
    code = 201
    status = False
    message = ""
    responseData = []
    requestData = dict(request.json)
    if "outlet_id" in requestData:

        Designationdata = DB.find_all("a013_tag_master",{"title":1,"_id":1})
        DesignationList = {}
        if Designationdata:
            for d in Designationdata:
                DesignationList[d["_id"]["$oid"]] = d["title"].title()

        # """ Get Role Data """
        # roleData = DB.find_all(tbl_v005_roles,{"name":1,"_id":1})
        # roleList = {}
        # if roleData:
        #     for r in roleData:
        #         roleList[r["_id"]["$oid"]] = r["name"].title()
        
        """ Get User Data """
        selFiled = {"_id": 1, "vendor_id": 1, "outlet_id": 1, "name": 1, "gender": 1,
                    "contact_number": 1, "email": 1, "profile_picture": 1, "role": 1, "staff_type":1,"designation":1,"is_theraphist":1}
        if requestData["outlet_id"] != "":
            user_data = DB.find_by_key(tbl_v003_vendor_users, {"outlet_id": ObjectId(requestData["outlet_id"]),"is_delete":0}, selFiled)
            # user_data=user_data.reverse()
            #print(user_data)
            user_data=user_data[::-1]
            
        else:
            user_data =[]
            
        if user_data:
            status = True
            message = MSG_CONST.VENDOR_SUCCESS
            for x in range(len(user_data)):
                user_data[x]["_id"] = user_data[x]["_id"]["$oid"]
                getmodule = DB.find_by_key(tbl_v018_module_access, {"vendor_id": ObjectId(user_data[x]["_id"])})
                user_data[x]["vendor_id"] = user_data[x]["vendor_id"]["$oid"]
                user_data[x]["is_rights_assign"]=len(getmodule)
                # if "role" in user_data[x] and "$oid" in user_data[x]["role"]:
                #     user_data[x]["role"] = user_data[x]["role"]["$oid"]
                #     user_data[x]["role_name"] = roleList[user_data[x]["role"]]
                # else:
                #     user_data[x]["role"] = ""
                #     user_data[x]["role_name"] = ""

                # if "designation" in user_data[x] and "$oid" in user_data[x]["designation"]:
                #     user_data[x]["designation"] = user_data[x]["designation"]["$oid"]
                #     user_data[x]["designation_name"] = DesignationList[user_data[x]["designation"]]
                # else:
                #     user_data[x]["designation"] = ""
                #     user_data[x]["designation_name"] = ""    
                    
            responseData = user_data
        else:
            status = False
            message = MSG_CONST.VENDOR_OUTLET_NOT_FOUND
            responseData = []
    else:
        status = False
        message = MSG_CONST.VENDOR_USER_ID_EMPTY
        responseData = []
    # print(user_data)
    response = output_json(responseData, message, status, code)
    #logging.debug('vendor_get_staff_list_by_outlet: {}'.format(response))
    return response

def remove_staff(self):
    code = 201
    status = False
    message = ""
    responseData = {}

    todayDate = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    ip_address = socket.gethostbyname(socket.gethostname())
    requestData = dict(request.json)
    updData = {"is_delete":1,"update_by":ObjectId(requestData["user_id"]),"update_ip":ip_address,"update_date":todayDate}
    find_gender_count = DB.find_one(tbl_v004_outlets,{"_id":ObjectId(requestData["outlet_id"])},{"_id":0,"female_count":1,"male_count":1})
    male_count = find_gender_count["male_count"]
    female_count = find_gender_count["female_count"]

    act = DB.update_one(tbl_v003_vendor_users,updData,{"_id":ObjectId(requestData["staff_id"])})
    find_gender = DB.find_one(tbl_v003_vendor_users,{"_id":ObjectId(requestData["staff_id"])},{"_id":0,"gender":1})
    if act:
        if find_gender['gender'] == "male":
            gender_count = DB.update_one(tbl_v004_outlets,{"male_count":male_count - 1},{"_id":ObjectId(requestData["outlet_id"])})
        else:
            gender_count = DB.update_one(tbl_v004_outlets,{"female_count":female_count - 1},{"_id":ObjectId(requestData["outlet_id"])})
        code = 200
        status = True
        message = MSG_CONST.VENDOR_STAFF_REMOVED_SUCCESS
    else:
        code = 200
        status = False
        message = MSG_CONST.VENDOR_STAFF_FAILED_REMOVED

    response = output_json(responseData, message, status, code)
    #logging.debug('vendor_remove_outlet_staff: {}'.format(response))
    return response

def role_staff(self):
    return role.RoleAccess().getAllRole()





def add_new_staff(self):
    code = 200
    status = False
    message = ""
    responseData = {}
    
    todayDate = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    ip_address = socket.gethostbyname(socket.gethostname())
    requestData = dict(request.json)
    find_vendor = DB.find_one(tbl_v002_vendors,{"_id":ObjectId(requestData["vendor_id"])})
    if (find_vendor):
        new_staff = {}
        new_staff['name'] = requestData["name"]
        insert_staff = DB.insert(tbl_v005_roles,new_staff)
        role_id = ObjectId(insert_staff)
        find_role = DB.find_one(tbl_v005_roles,{"_id":role_id},'ALL')
        find_modules = DB.find_all_where(tbl_v017_modules,{"$and":[{"status":int(1),"is_menu":int(0)}]},"ALL")
        for x in find_modules:
            addData = {}
            addData["vendor_id"] = ObjectId(requestData["vendor_id"])
            addData["vendor_email"] = requestData["email"]
            module_id = x["_id"]["$oid"]
            addData["module_id"] = ObjectId(module_id)        
            addData["module_name"] = x["name"]
            addData["role_id"] = role_id
            addData["role_name"] = find_role["name"]
            addData["access_type"] = "none"
            addData["is_delete"] = 0
            addData["insert_by"] = ObjectId(requestData["user_id"])
            addData["insert_date"] = todayDate
            addData["insert_ip"] = ip_address
            
            insert_module = DB.insert(tbl_v018_module_access,addData)
            code = 200
            status = True
            message = "Staff Added Successfully..!"
    else:
        addData = {}
        code = 201
        status = False
        message = "Something went Wrong"

    response = output_json(addData, message, status, code)
    #logging.debug('add_new_staff: {}'.format(response))
    return response

    


def save_new_role(self):
    code = 201
    status = False
    message = ""
    responseData = {}
    addData = {}
    todayDate = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    ip_address = socket.gethostbyname(socket.gethostname())
    requestData = request.json
    staff_id = requestData[0]['vendor_id']
    fieldList =	{"_id" :1, "vendor_id" :1, "insert_by" :1, 
	"module_name" :1, "Feedback" :1,"module_id" :1, "access_type" :1, "vendor_email" :1,"email":1,"password2":1,"name":1}
    find_staff = DB.find_one(tbl_v003_vendor_users,{"_id":ObjectId(staff_id)},fieldList)
    vendor_email = find_staff['email']
    find_user = DB.find_all_where(tbl_v018_module_access,{"vendor_id":ObjectId(staff_id)},fieldList)
    if 'password2' in find_staff:
        password2=find_staff['password2']
    else:
        password2=''    

    if(find_user):
        for data in requestData:
            data["vendor_id"] = ObjectId(staff_id)
            data["module_id"] = ObjectId(data["module_id"])
            data["updated_by"] = ObjectId(data["insert_by"])
            data["vendor_email"] = vendor_email
            data["insert_by"] = ObjectId(data["insert_by"])
            data["updated_date"] = todayDate
            data["updated_ip"] = ip_address
            data['module_access_id'] = ObjectId(data['module_access_id'])
            module_data = DB.update_one(tbl_v018_module_access,data,{"_id":ObjectId(data['module_access_id'])})
    
    else:
        for data in requestData:
            data["vendor_id"] = ObjectId(staff_id)
            data["module_id"] = ObjectId(data["module_id"])
            data["vendor_email"] = vendor_email
            data["insert_by"] = ObjectId(data["insert_by"])
            data['module_access_id'] = ""
            data["insert_date"] = todayDate
            data["insert_ip"] = ip_address
            data['access'] =  True
            data["is_delete"] = 0
        module_data = DB.insert_many(tbl_v018_module_access,requestData)
        email_arr = DB.find_one(tbl_a001_email_template,{'type':'vendor_staff_assign'},{'title':1})
        notificationObject = {}
        emailObject = {}
        emailObject["to"] = [find_staff['email']]
        emailObject["template"] = "vendor_staff_assign"
        emailObject["replace_value"] = {}
        emailObject["replace_value"]["user_name"] = find_staff['name'].capitalize()
        emailObject["replace_value"]["email"] = find_staff['email']
        emailObject["replace_value"]["password"] = password2
        emailObject["sender"] = {}
        emailObject["sender"]["type"] = "vendor"
        emailObject["sender"]["id"] = "1"
        emailObject["receiver"] = {}
        emailObject["receiver"]["type"] = "staff"
        emailObject["receiver"]["id"] = "1"
        emailObject["subject"] = email_arr['title']
        notificationObject["email"] = emailObject
        res = requests.post(CONST.NOTIFACTION_CLIENT, json=notificationObject)
        responseData2 = dict(res.json())
        res2 = DB.update_one(tbl_v003_vendor_users,{'password2':''},{"_id":ObjectId(staff_id)})

    response = output_json(responseData,message,status,code)
    #logging.debug('save_new_role: {}'.format(response))
    return response




# def get_new_role(self,staff_id):
#     code = 201
#     status = False
#     message = ""
#     fieldList =	{"_id" :1, "vendor_id" :1, "insert_by" :1, 
# 	"module_name" :1, "Feedback" :1,"module_id" :1, "access_type" :1, "vendor_email" :1}
#     if staff_id != "":
#         find_staff = DB.find_by_key(tbl_v018_module_access,{"vendor_id":ObjectId(staff_id)},fieldList)
#     else:
#         find_staff=[]
#     if find_staff:
#         code = 200
#         status = True
#         message = "Get Successfully"
#     else:
#         code = 201
#         status = False
#         message = "Something Went Wrong..!"
#     response = output_json(find_staff,message,status,code)
#     #logging.debug('save_new_role: {}'.format(response))
#     return response
    
    
    
def get_all_module(self,staff_id):
    field_list = {"_id":1,"name":1,"title":1}
    module_data = {}
    modules = DB.find_all_where(tbl_v017_modules,{"status":1,"is_menu":0},field_list)
    staff_data = DB.find_all_where(tbl_v018_module_access,{"vendor_id":ObjectId(staff_id)},"ALL")
    staff_info = DB.find_all_where(tbl_v003_vendor_users,{"_id":ObjectId(staff_id)},"ALL")
    module_data['staff_info']=staff_info
    if(staff_data):
        module_data['staff_data'] = staff_data
        module_data['modules'] = modules
    else:
        module_data['modules'] = modules
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





def delete_access(self):
    code = 201
    status = False
    message = ""
    responseData = {}
    requestData=dict(request.json)
    todayDate = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    if requestData['delete_value']=='':
        act = DB.delete_many(tbl_v018_module_access,{"vendor_id":ObjectId(requestData["user_id"])})
   
    if act:
        code = 200
        status = True
        message = MSG_CONST.VENDOR_STAFF_REMOVED_SUCCESS
    else:
        code = 200
        status = False
        message = MSG_CONST.VENDOR_STAFF_FAILED_REMOVED

    response = output_json(responseData, message, status, code)
    return response