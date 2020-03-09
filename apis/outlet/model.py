from flask_restplus import Namespace, fields
import socket
import time
import re
from datetime import datetime, date, time, timedelta
from flask import jsonify, request
from database import DB
from bson import json_util, ObjectId
from apis.utils.common import *
from apis.libraries.send_mail import Send_mail
import requests
import logging
import apis.utils.message_constants as MSG_CONST
import apis.utils.constants as CONST
from werkzeug.security import generate_password_hash, check_password_hash
import sys
import dateutil
import isodate
import datetime
import time
import pymongo

#logging.basicConfig(filename='vendor.log', level=logging.DEBUG)   

# Declare tables name in vars
tbl_v002_vendors = "v002_vendors"
tbl_v003_vendor_users = "v003_vendor_users"
tbl_v004_outlets = "v004_outlets"
tbl_v014_amenities = "v014_amenities"
tbl_v015_membership = "v015_membership"
tbl_v016_subscription = "v016_subscription"
tbl_u002_booking = "u002_booking"
tbl_v012_services = "v012_services"
tbl_v026_tour_steps = "v026_tour_steps"
tbl_a001_email_template="a001_email_template"


def addBusinessModel(self,ns):
    addOutlet = ns.model('addOutletModel', {
        'outlet_id':fields.String(required=False, description="Provide newly added outlet id" ),
        'user_id': fields.String(required=True, min_length=1, example=1, description='User id is required'),
        'logo': fields.String(required=False, example=1, description='User id is required'),
        'vendor_id': fields.String(required=True, min_length=1, example=1, description='vendor id is required'),
        'name': fields.String(required=True, min_length=1, description='Name is required'),
        'category': fields.String(required=True, min_length=1, description='Category id is required'),
        'latitude':fields.Float(required=False, description="Provide latitude of outlet."),
        'longitude':fields.Float(required=False, description="Provide longitude outlet"),
        'address': fields.String(required=True, min_length=1, description='Address is required'),
        'pin_code': fields.Integer(required=False, min_length=1, description='Area pin code is required'),
        'area': fields.String(required=False, description='Area id is required'),
        'country': fields.String(required=True, min_length=1, description='Country id is required'),
        'state': fields.String(required=True, min_length=1, description='State is required'),
        'city': fields.String(required=True, min_length=1, description='City is required'),
        "images" : fields.List(fields.String,required=False, description='Outlet images'),
    })
    return addOutlet
    

def addgellaryModel(self,ns):
    addOutlet = ns.model('addgellaryModel', {
        'user_id': fields.String(required=True, min_length=1, example=1, description='User id is required'),
        'vendor_id': fields.String(required=True, min_length=1, example=1, description='vendor id is required'),
        'outlet_id':fields.String(required=True, min_length=1, description="Provide newly added outlet id" ),
        "images" : fields.List(fields.String,required=False, description='Outlet images'),
        "videos" : fields.List(fields.String,required=False, description='Outlet video'),
        "description": fields.String(required=False, description='Business id is required'),
    })
    return addOutlet

def addDetailsModel(self,ns):
    addOutlet = ns.model('addDetailsModel', {
        'user_id': fields.String(required=True, min_length=1, example=1, description='User id is required'),
        'vendor_id': fields.String(required=True, min_length=1, example=1, description='vendor id is required'),
        'outlet_id':fields.String(required=True, min_length=1, description="Provide newly added outlet id" ),
        'email': fields.List(fields.String,required=True, description='email id is required'),
        'reservation_number': fields.List(fields.String,required=False, description='Reservation  contact number'),
        'contact_number': fields.List(fields.String,required=True,description='Provide contact number.'),
    })
    return addOutlet

def addServiceModel(self,ns):
    addOutlet = ns.model('addServiceModel', {
        'user_id': fields.String(required=True, min_length=1, example=1, description='User id is required'),
        'vendor_id': fields.String(required=True, min_length=1, example=1, description='vendor id is required'),
        'outlet_id':fields.String(required=True, min_length=1, description="Provide newly added outlet id" ),
        'masseurs': fields.List(fields.String,required=False, description='Is massesure are male, female or both.'),
        'allow_customers_gender': fields.String(required=False, min_length=1, enum=["male","female","both"], description='Provide allowed customer gender.'),
        'timings': fields.Raw(required=True, min_length=1, description='Provide business times slot'),
        'amenities': fields.List(fields.String,required=True, min_length=1, description='Provide business times slot')
    })
    return addOutlet

def outletImagesModel(self, ns):
    outletImages = ns.model('outletImagesModel', {
        'user_id': fields.String(required=True, min_length=1, example=1, description='User id is required'),
        'outlet_id':fields.String(required=True, min_length=1, description="Provide newly added outlet id" ),
        'vendor_id': fields.String(required=True, min_length=1, example=1, description='vendor id is required'),
        'images': fields.List(fields.String,required=True, description='Service category id')
    })
    return outletImages

def outletListModel(self, ns):
    outletList = ns.model('outletListModel', {
        'vendor_id': fields.String(required=True, min_length=1, example=1, description='vendor id is required')
    })
    return outletList

def outletGstModel(self, ns):
    outletGst = ns.model('outletGstModel', {
        'user_id': fields.String(required=True, min_length=1, example=1, description='User id is required'),
        'vendor_id': fields.String(required=True, min_length=1, example=1, description='vendor id is required'),
        'outlet_id':fields.String(required=True, min_length=1, description="Provide newly added outlet id" ),
        'images': fields.List(fields.String,required=True, description='Service category id')
    })
    return outletGst

def removeListingModel(self, ns):
    removeListingModel = ns.model('removeListingModel', {
        'user_id': fields.String(required=True, min_length=4, description='User id is required'),
        'vendor_id': fields.String(required=True, min_length=4, description='vendor id is required'),
        'outlet_id':fields.String(required=True, min_length=4, description="Provide outlet id" )
    })
    return removeListingModel

def saveBusiness(self):
    status = True
    message = ""
    code = 200
    responseData = {}

    requestData = dict(request.json)
    todayDate = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    data = {}
    outLetData = {}
    business = {}
    user_id     = ObjectId(requestData["user_id"])
    outlet_id = requestData["outlet_id"]
    
    business = DB.find_one(tbl_v002_vendors,{'_id':ObjectId(requestData['vendor_id'])},{'business_type':1})
    business_type = business['business_type']
    
    find_outlet = DB.find_all_where(tbl_v004_outlets,{'vendor_id':ObjectId(requestData['vendor_id'])})
    if (find_outlet):
        data["first_outlet"] = False
    else:
        data["first_outlet"] = True
    if outlet_id:
        outlet_id = ObjectId(requestData["outlet_id"])
        outLetData = DB.find_one(tbl_v004_outlets,{"_id":outlet_id})
    else:
        data["outlet_id"] = None #DB.find_max_id(tbl_v004_outlets, "outlet_id")
    data["vendor_id"]   = ObjectId(requestData["vendor_id"])
    data["name"]        = requestData["name"].strip(" ").title()
    data["logo"]        = requestData["logo"] if "logo" in requestData else ""
    data["category"]    = ObjectId(requestData["category"])
    data["pin_code"]    = requestData["pin_code"]
    data["address"]     = requestData["address"]
    data["area"]        = requestData["area"].lower()
    data["city"]        = requestData["city"].lower()
    data["state"]       = requestData["state"]
    data["country"]     = requestData["country"]
    data["latitude"]    = float(requestData["latitude"])
    data["longitude"]   = float(requestData["longitude"])
    slugs = re.sub(r"\s+", '-', requestData["name"].lower())
    
    outlet_slug = DB.find_all_where(tbl_v004_outlets,{"slugs":slugs},'ALL')
    if outlet_slug:    
        data["slugs"]        = re.sub(r"\s+", '-', requestData["name"].lower())+"-2"
    else:
        data["slugs"]        = re.sub(r"\s+", '-', requestData["name"].lower())
    act = False
    if outlet_id and outLetData:
        data["update_by"]           = user_id
        data["update_ip"]           = socket.gethostbyname(socket.gethostname())
        data["update_date"]         = todayDate
        act = DB.update_one(tbl_v004_outlets,data,{"_id":outlet_id})
        responseData["outlet_id"]   = requestData["outlet_id"]
    else:
        data["insert_by"]           = user_id
        data["insert_ip"]           = socket.gethostbyname(socket.gethostname())
        data["insert_date"]         = todayDate
        data["is_delete"]           = 0
        data["status"]              = 4
        data['business_type'] = business_type
        data["female_count"] = 0
        data["male_count"] = 0
        act = DB.insert(tbl_v004_outlets,data)
        res= DB.update_one(tbl_v026_tour_steps,{"setup_outlet":True},{"vendor_id":ObjectId(requestData["vendor_id"])})
        responseData["outlet_id"]   = act

    if act:
        status = True
        message = MSG_CONST.VENDOR_OUTLET_DETAILS_SAVE_SUCCESS
        code = 200
    else:
        status = False
        message = MSG_CONST.N_TECH_PROB
        code = 201
        responseData = {}
    
    response = output_json(responseData,message,status,code)
    #logging.debug('vendor_save_outlet: {}'.format(response))
    return response

def getDetails(self):
    status = True
    message = ""
    code = 200
    responseData = {}

    outlet_id = request.args.get("outlet_key")
    
    if outlet_id:
        
        outlet_id = ObjectId(outlet_id)
        getData = DB.find_one(tbl_v004_outlets,{"_id":outlet_id},{"update_date":0,"insert_by":0,"insert_date":0,"update_by":0,"update_ip":0})
        
        if getData and (("is_delete" in getData and getData["is_delete"] == 0) or "is_delete" not in getData):
            if "user_id" in getData and "$oid" in getData["user_id"] :
                getData["user_id"]      = getData["user_id"]["$oid"] 
            else:
                getData["user_id"]      = None
            services_category = []
            if "services_category" in getData and getData["services_category"]:
                for x in getData["services_category"]:
                    services_category.append(str(x["$oid"]))
            getData["services_category"] = services_category
            getData["vendor_id"] = getData["vendor_id"]["$oid"]
            getData["outlet_id"] = getData["_id"]["$oid"]
            
            responseData = getData
            message = MSG_CONST.VENDOR_SUCCESS
            status = True
            
        else:
            responseData = {}
            message = MSG_CONST.VENDOR_OUTLET_NOT_FOUND
            status = False
    else:
        responseData = {}
        message = MSG_CONST.VENDOR_OUTLET_NOT_FOUND
        status = True

    response = output_json(responseData,message,status,code)
    #logging.debug('vendor_get_outlet: {}'.format(response))
    return response

def saveGellary(self):
    requestData = dict(request.json)
    todayDate = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    data = {}

    status = True
    message = ""
    code = 200
    responseData = {}
    
    user_id     = ObjectId(requestData["user_id"])
    outlet_id   = ObjectId(requestData["outlet_id"])
    vendor_id   = ObjectId(requestData["vendor_id"])

    outLetData = DB.find_one(tbl_v004_outlets,{"_id":outlet_id,"vendor_id":vendor_id})
    if not outLetData:
        status = False
        message = MSG_CONST.VENDOR_OUTLET_INVALID_ID
        code = 201
    else:
        data["description"] = requestData["description"]
        data["images"]      = requestData["images"]
        data["videos"]      = requestData["videos"]
        data["update_ip"]   = socket.gethostbyname(socket.gethostname())
        data["update_date"] = todayDate
        data["update_by"]   = user_id
        upd = DB.update_one(tbl_v004_outlets,data,{"_id":outlet_id,"vendor_id":vendor_id})
        
        if upd:
            status = True
            message = MSG_CONST.VENDOR_OUTLET_DETAILS_SAVE_SUCCESS
            code = 200
        else:
            status = False
            message = MSG_CONST.N_TECH_PROB
            code = 201

    response = output_json(responseData,message,status,code)
    #logging.debug('saveGellary: {}'.format(response))
    return response


def businessDetails(self):
    
    requestData = dict(request.json)
    # todayDate = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    todayDate = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    data = {}

    status = True
    message = ""
    code = 200
    responseData = {}
    
    user_id     = ObjectId(requestData["user_id"])
    outlet_id   = ObjectId(requestData["outlet_id"])
    vendor_id   = ObjectId(requestData["vendor_id"])

    outLetData = DB.find_one(tbl_v004_outlets,{"_id":outlet_id,"vendor_id":vendor_id})

    if not outLetData:
        status = False
        message = MSG_CONST.VENDOR_OUTLET_INVALID_ID
        code = 201
    else:

        """ if requestData["email"]:
            for email in requestData["email"]:
                if validEmail(email) == False:
                    status = False
                    message = MSG_CONST.VENDOR_PROVIDE_VALID_EMAIL
                    code = 201
                    response = output_json(responseData,message,status,code)
                    #logging.debug('vendor_outlet_save_business: {}'.format(response))
                    return response
                else:
                    checkEmail = DB.find_one(tbl_v004_outlets,{"_id":{"$nin":[outlet_id]},"email":{"$in":[email]}},{"outlet_id":1,"_id":1})
                    
                    if checkEmail:
                        message = MSG_CONST.VENDOR_SAVE_EMAIL_EXISTS
                        response = output_json(responseData,message,status,code)
                        #logging.debug('vendor_save_outlet_business_details: {}'.format(response))
                        return response """

        data["email"]       = requestData["email"]

        data["reservation_number"]  = requestData["reservation_number"]
        data["contact_number"]      = requestData["contact_number"]
        data["landline_number"] = requestData['landline_number']
        data["update_ip"]   = socket.gethostbyname(socket.gethostname())
        data["update_date"] = todayDate
        data["update_by"]   = user_id
        upd = DB.update_one(tbl_v004_outlets,data,{"_id":outlet_id,"vendor_id":vendor_id})

        if upd:
            status = True
            message = MSG_CONST.VENDOR_OUTLET_DETAILS_SAVE_SUCCESS
            code = 200
        else:
            status = False
            message = MSG_CONST.N_TECH_PROB
            code = 201

    response = output_json(responseData,message,status,code)
    #logging.debug('vendor_outlet_save_business: {}'.format(response))
    return response

def servicesDetails(self):

    requestData = dict(request.json)
    todayDate = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    data = {}

    status = True
    message = ""
    code = 200
    responseData = {}

    user_id     = ObjectId(requestData["user_id"])
    outlet_id   = ObjectId(requestData["outlet_id"])
    vendor_id   = ObjectId(requestData["vendor_id"])
    
    find_is_first = DB.find_all_where(tbl_v004_outlets,{"vendor_id":vendor_id})
    total_outlets = len(find_is_first)
    # find_is_first = DB.find_all_where(tbl_v004_outlets,{"$and":[{"vendor_id":vendor_id},{"status":{"$ne":3}}]})
    # getUser = DB.find_one(tbl_v003_vendor_users,{"$and":[{"$or":[{"email":emailPhone},{"contact_number":emailPhone}]},{"is_delete":{"$ne":1}}]})
    
    if(total_outlets > 1):
        responseData['first_outlet'] = False
    else:
        responseData['first_outlet'] = True
    
    outLetData = DB.find_one(tbl_v004_outlets,{"_id":outlet_id,"vendor_id":vendor_id},{"_id":0})
    if not outLetData:
        status = False
        message = MSG_CONST.VENDOR_OUTLET_INVALID_ID
        code = 201
    else:
        data["timings"]    = requestData["timings"]
        if 'masseurs' in requestData:
            data["masseurs"]    = requestData["masseurs"]
        if 'allow_customers_gender' in requestData:
           data["allow_customers_gender"] = requestData["allow_customers_gender"]            
        if 'spa_type' in requestData:
            data["spa_type"]    = requestData["spa_type"].lower()

        data["amenities"]   = requestData["amenities"]
        data["update_ip"]   = socket.gethostbyname(socket.gethostname())
        data["update_date"] = todayDate
        data["update_by"]   = user_id
        find_status = DB.find_one(tbl_v004_outlets,{"_id":outlet_id},{"status":1,"is_firsttime":1})
        
        if 'is_firsttime' in find_status:
            data["is_firsttime"]=False
        else:
            data["is_firsttime"]=True
            
        if data["is_firsttime"]==True:
            userData = DB.find_one(tbl_v003_vendor_users,{"_id":user_id},{"_id":0,"name":1})
            email_arr = DB.find_one(tbl_a001_email_template,{'type':'vendor_outlet_add'},{'title':1})
            notificationObject = {}
            emailObject = {}
            emailObject["to"] = [CONST.ADMIN_EMAIL]
            emailObject["template"] = "vendor_outlet_add"
            emailObject["replace_value"] = {}
            emailObject["replace_value"]["user_name"] = userData['name'].capitalize()
            emailObject["replace_value"]["link"] = CONST.ADMIN_WEB+'outlets/details?outlet_id='+str(outlet_id)
            emailObject["sender"] = {}
            emailObject["sender"]["type"] = "SYS"
            emailObject["sender"]["id"] = "1"
            emailObject["receiver"] = {}
            emailObject["receiver"]["type"] = "vendor"
            emailObject["receiver"]["id"] = "1"
            sub=email_arr['title'].replace('|user_name|', userData['name'])
            emailObject["subject"] = sub
            notificationObject["email"] = emailObject
            res = requests.post(CONST.NOTIFACTION_CLIENT, json=notificationObject)
            response = dict(res.json())

        get_status = find_status['status']
        if get_status == 1:
            data["status"] = 1
        else:
            data["status"] = 0
        upd = DB.update_one(tbl_v004_outlets,data,{"_id":outlet_id,"vendor_id":vendor_id})

        if upd:
            status = True
            message = MSG_CONST.VENDOR_OUTLET_DETAILS_SAVE_SUCCESS
            code = 200
        else:
            status = False
            message = MSG_CONST.N_TECH_PROB
            code = 201

    response = output_json(responseData, message, status, code)
    #logging.debug('vendor_outlet_save_business: {}'.format(response))
    return response


# def saveLocation(self):
#     requestData = dict(request.json)
#     # todayDate = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
#     todayDate = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
#     data = {}
    
#     status = True
#     message = ""
#     code = 200
#     responseData = {}

#     user_id     = ObjectId(requestData["user_id"])
#     outlet_id   = ObjectId(requestData["outlet_id"])
#     vendor_id   = ObjectId(requestData["vendor_id"])
    

#     outLetData = DB.find_one(tbl_v004_outlets,{"_id":outlet_id,"vendor_id":vendor_id})

#     if not outLetData:
#         status = False
#         message = MSG_CONST.VENDOR_OUTLET_INVALID_ID
#         code = 201
#     else:
#         #data = requestData
#         data["pin_code"]    = requestData["pin_code"]
#         data["address"]     = requestData["address"]
#         data["area"]        = requestData["area"].lower()
#         data["city"]        = requestData["city"].lower()
#         data["state"]       = requestData["state"]
#         data["country"]     = requestData["country"]

#         data["latitude"]    = float(requestData["latitude"])
#         data["longitude"]   = float(requestData["longitude"])
#         data["update_ip"]   = socket.gethostbyname(socket.gethostname())
#         data["update_date"] = todayDate
#         data["update_by"]   = user_id
#         upd = DB.update_one(tbl_v004_outlets,data,{"_id":outlet_id,"vendor_id":vendor_id})

#         if upd:
#             status = True
#             message = MSG_CONST.VENDOR_OUTLET_DETAILS_SAVE_SUCCESS
#             code = 200
#         else:
#             status = False
#             message = MSG_CONST.N_TECH_PROB
#             code = 201

#     response = output_json(responseData,message,status,code)
#     #logging.debug('vendor_outlet_save_location: {}'.format(response))
#     return response



def addImages(self):
    requestData = dict(request.json)
    # todayDate = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    todayDate = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    data = {}

    status = True
    message = ""
    code = 200
    responseData = {}

    user_id     = ObjectId(requestData["user_id"])
    outlet_id   = ObjectId(requestData["outlet_id"])
    vendor_id   = ObjectId(requestData["vendor_id"])

    outLetData = DB.find_one(tbl_v004_outlets,{"_id":outlet_id,"vendor_id":vendor_id},{"_id":0})
    if not outLetData:
        status = False
        message = MSG_CONST.VENDOR_OUTLET_INVALID_ID
        code = 201
    else:
        data["images"] = requestData["images"]
        data["update_ip"]   = socket.gethostbyname(socket.gethostname())
        data["update_date"] = todayDate
        data["update_by"]   = user_id
        upd = DB.update_one(tbl_v004_outlets,data,{"_id":outlet_id,"vendor_id":vendor_id})

        if upd:
            status = True
            message = MSG_CONST.VENDOR_OUTLET_DETAILS_SAVE_SUCCESS
            code = 200
        else:
            status = False
            message = MSG_CONST.N_TECH_PROB
            code = 201

    response = output_json(responseData, message, status, code)
    #logging.debug('vendor_outlet_save_business: {}'.format(response))
    return response


def allOutletList(self):
    requestData = dict(request.json)
    vendor_id   = ObjectId(requestData["vendor_id"])

    status = True
    message = ""
    code = 200
    responseData = []
    
    getAll = DB.find_by_key(tbl_v004_outlets,{"vendor_id":vendor_id,"is_delete":0},{"insert_by":0,"insert_date":0,"outlet_id":0,"update_by":0})
    
    if getAll:
        resData = []
        i = 0
        for x in getAll:
            x["_id"] = str(x["_id"]["$oid"])
            if "category" in x and "$oid" in x["category"] :
                x["category"] = str(x["category"]["$oid"])

            if "user_id" in x and "$oid" in x["user_id"] :
                x["user_id"] = str(x["user_id"]["$oid"])

            if "vendor_id" in x and "$oid" in x["vendor_id"] :
                x["vendor_id"] = str(x["vendor_id"]["$oid"])            
            resData.append(x)
                        
        responseData = list(reversed(resData))
        status = True
        message = MSG_CONST.VENDOR_SUCCESS
        code = 200
    else:
        status = False
        message = MSG_CONST.N_TECH_PROB
        code = 201

    response = output_json(responseData, message, status, code)
    #logging.debug('vendor_outlet_get_details: {}'.format(response))
    return response


def saveGST(self):
    pass

def getOutLetForServices(self):
    status = True
    message = ""
    code = 200
    responseData = {}

    requestData = dict(request.json)
    if "vendor_id" in requestData and requestData["vendor_id"] != "":
        vendor_id   = ObjectId(requestData["vendor_id"])
        getAll = DB.find_by_key(tbl_v004_outlets,{"vendor_id":vendor_id},{"_id":1,"name":1})
        if getAll:
            resData = []
            i = 0
            for x in getAll:
                x["_id"] = str(x["_id"]["$oid"])
                resData.append(x)
            responseData = resData
            status = True
            message = MSG_CONST.VENDOR_SUCCESS
            code = 200
        else:
            status = False
            message = MSG_CONST.N_TECH_PROB
            code = 201
    else:
        status = False
        message = MSG_CONST.VENDOR_OUTLET_NOT_FOUND
        code = 201
    response = output_json(responseData, message, status, code)
    #logging.debug('vendor_outlet_get_for_service: {}'.format(response))
    return response

""" def updateTime(self):
    requestData = dict(request.json)
    DB.update_many(tbl_v004_outlets,requestData) """

def amenities_list(self):
    status = True
    message = ""
    code = 200
    responseData = {}

    amData = []
    amenitiesData = DB.find_by_key(tbl_v014_amenities,{"status":1},{"title":1,"_id":1})
    if amenitiesData:
        for x in amenitiesData:
            amData.append(x["title"])
        status = True
        message = MSG_CONST.VENDOR_SUCCESS
        code = 200
    else:
        status = False
        message = MSG_CONST.VENDOR_OUTLET_NOT_FOUND
        code = 200
    responseData = amData
    response = output_json(responseData, message, status, code)
    #logging.debug('vendor_outlet_get_amenities_list: {}'.format(response))
    return response

def removeListing(self):
    code = 200
    status = False
    message = ""
    responseData = {}
    # todayDate = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    todayDate = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    ip_address = socket.gethostbyname(socket.gethostname())
    requestData = dict(request.json)
    
    vendor_id = ObjectId(requestData["vendor_id"])
    user_id = ObjectId(requestData["user_id"])
    outlet_id = ObjectId(requestData["outlet_id"])
    outletData = DB.find_one(tbl_v004_outlets,{"_id":outlet_id},{"_id":1,"is_delete":1})
    
    if outletData:
        act = DB.update_one(tbl_v004_outlets,{"is_delete":1,"update_by":user_id,"update_date":todayDate,"update_ip":ip_address},{"_id":outlet_id})
        if act:
            status = True
            message = MSG_CONST.VENDOR_OUTLET_REMOVE_SUCCESS
            code = 200
        else:
            status = False
            message = MSG_CONST.VENDOR_OUTLET_REMOVE_FAILED
            code = 200
    else:
        status = False
        message = MSG_CONST.VENDOR_OUTLET_NOT_FOUND
        code = 200
    response = output_json(responseData, message, status, code)
    #logging.debug('vendor_outlet_remove: {}'.format(response))
    return response

def branch(self,id,vendor_id,outlet_id):
    data = {}
    Total_count = {}
    todaydate = datetime.datetime.now()
    y = todaydate.strftime("%m-%d-%Y %H:%M:%S")
    ts = int(time.time())
    selectField={"name":1,"address":1,"city":1,"logo":1}
    branch_data=DB.find_one("v004_outlets",{"_id": ObjectId(id)},selectField)
    data['branch'] = branch_data
    table_name = ["u002_booking","v012_services","v003_vendor_users"]
    # selectFields = {"user_id":1,"booking_id":1,"booking_no":1,"spa":1,"outlet_id":1,"created_date":1,"payment_status":1,'price':1,'services':1}
    upcoming = DB.find_all_where("u002_booking",{"$and":[{"spa.services.start_timestamp":{"$gt": (ts)}},{"spa.outlet_id":str(outlet_id),"status":int(2)}]},"ALL")
    newdata2=[]
    for x in upcoming:
        # newdata.append(x)    
        spa = x['spa']
        newdata=[]
        for y in spa:
            service = y['services']
            services = len(service)
            y['total_services']= services
            newdata.append(y)
            x['spa']=newdata
        newdata2.append(x)
    data['booking']=newdata2
    
    for table in table_name:
        if table == "u002_booking":
            get_count = DB.find_using_aggregate(table,[{"$match":{"$and":[{"spa.outlet_id":str(id)},{"status":2}]}},{"$count":"count"}])
        elif table == "v012_services":
            get_count = DB.find_using_aggregate(table,[{"$match":{"$and":[ {"outlet_id":ObjectId(id)},{"is_delete":0}]}},{"$count":"count"}])
        elif table == "v003_vendor_users":
            get_count = DB.find_using_aggregate(table,[{"$match":{"$and":[{"outlet_id":ObjectId(id)},{"is_delete":0}]}},{"$count":"count"}])
        count_arr=table.split('_') 
        if get_count!=[]:
            for x in get_count:
                Total_count[count_arr[1]] = x['count']
        else:
            Total_count[count_arr[1]] = 0
    data['count']=Total_count
    
    return output_json(data,MSG_CONST.VENDOR_OUTLET_BRANCH_SUCCESS, True, 200)

# def upload_documents(self):
#     # todayDate = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
#     from datetime import datetime, date, time, timedelta
#     todayDate = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
#     ip_address = socket.gethostbyname(socket.gethostname())
#     requestData = request.json
#     user_id = ObjectId(requestData['_id'])
#     code = 201
#     status = False
#     message = MSG_CONST.VENDOR_EMPTY_ID
#     responseData = {}
#     if "_id" in requestData and requestData["_id"] != "":
#         _id = ObjectId(requestData['_id'])
#         selectField = {"vendor_id":1,"outlet_id":1,"docs":1,"_id":1}
#         getoutletData = DB.find_one("v004_outlets",{"_id":ObjectId(requestData['_id'])},selectField)
#         if getoutletData:
#             updateData = {}
            
#             updateData["docs."+requestData["name"]] = requestData["docs"]
#             updateData["update_by"] =  user_id
#             updateData["update_date"] = todayDate
#             updateData["update_ip"] = ip_address
            
#             updateStatus = DB.update_one("v004_outlets",updateData,{"_id":_id})
#             res= DB.update_one(tbl_v026_tour_steps,{"setup_docs":True},{"vendor_id":ObjectId(requestData["vendor_id"])})
#             if updateStatus != None:
#                 code = 200
#                 status = True
#                 message =  MSG_CONST.OUTLET_SUCCESS
#             else:
#                 code = 201
#                 status = False
#                 message =  MSG_CONST.OUTLET_TECH_PROB
#         else:
#             code = 201
#             status = False
#             message =  MSG_CONST.OUTLET_INVALID
#     else:
#         code = 201
#         status = False
#         message =  MSG_CONST.OUTLET_EMPTY_ID
    
#     # responseData = updateData
#     response = output_json(responseData,message,status,code)
#     #logging.debug('upload_documents: {}'.format(response))
#     return response





def upload_documents(self):
    from datetime import datetime, date, time, timedelta
    todayDate = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    ip_address = socket.gethostbyname(socket.gethostname())
    requestData = request.json
    user_id = ObjectId(requestData['_id'])
    code = 201
    status = False
    message = MSG_CONST.VENDOR_EMPTY_ID
    responseData = {}
    if "_id" in requestData and requestData["_id"] != "":
        _id = ObjectId(requestData['_id'])
        selectField = {"vendor_id":1,"docs":1,"_id":1,"status" :1,"business_name":1}
        getoutletData = DB.find_one(tbl_v002_vendors,{"_id":ObjectId(requestData['_id'])},selectField)
        vendor_status = getoutletData['status']
       
        #send email to admin
        email_arr = DB.find_one(tbl_a001_email_template,{'type':'vendor_document_add'},{'title':1})
        notificationObject = {}
        emailObject = {}
        emailObject["to"] = [CONST.ADMIN_EMAIL]
        emailObject["template"] = "vendor_document_add"
        emailObject["replace_value"] = {}
        emailObject["replace_value"]["business_name"] = getoutletData["business_name"]
        emailObject["replace_value"]["link"] = CONST.ADMIN_WEB+'vendors/Vendordetails?vendor_id='+str(requestData['_id'])
        emailObject["sender"] = {}
        emailObject["sender"]["type"] = "SYS"
        emailObject["sender"]["id"] = "1"
        emailObject["receiver"] = {}
        emailObject["receiver"]["type"] = "vendor"
        emailObject["receiver"]["id"] = "1"
        sub=email_arr['title'].replace('|business_name|', str(getoutletData["business_name"]))
        emailObject["subject"] = sub
        notificationObject["email"] = emailObject
        res = requests.post(CONST.NOTIFACTION_CLIENT, json=notificationObject)
        response1 = dict(res.json())

        if getoutletData:
            updateData = {}
            updateData["docs."+requestData["name"]] = requestData["docs"]
            updateData["update_by"] =  user_id
            updateData["update_date"] = todayDate
            updateData["update_ip"] = ip_address
            updateData["status"] = 0
            updateStatus = DB.update_one(tbl_v002_vendors,updateData,{"_id":_id})
            res= DB.update_one(tbl_v026_tour_steps,{"setup_docs":True},{"vendor_id":_id})
            if updateStatus != None:
                code = 200
                status = True
                message =  MSG_CONST.OUTLET_SUCCESS
            else:
                code = 201
                status = False
                message =  MSG_CONST.OUTLET_TECH_PROB
        else:
            code = 201
            status = False
            message =  MSG_CONST.OUTLET_INVALID
    else:
        code = 201
        status = False
        message =  MSG_CONST.OUTLET_EMPTY_ID
    
    # responseData = updateData
    response = output_json(responseData,message,status,code)
    #logging.debug('upload_documents: {}'.format(response))
    return response



















def billing(self,vendor_id):
    billing_data=DB.find_by_key(tbl_v016_subscription,{"$and":[{"vendor_id":ObjectId(vendor_id),"status":int(1)}]},{},[("index",pymongo.DESCENDING)])
    billing_arr=[]
    for x in billing_data:
        membership=DB.find_one(tbl_v015_membership,{"_id": ObjectId(x['plan_id']['$oid'])},{"title":1,"_id":0 ,"price":1})
        if billing_data and membership and "title"and "price" in membership:
            x["title"] = membership["title"].title()
            billing_arr.append(x)      
    return output_json(billing_arr, True, 200)
