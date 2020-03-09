from flask_restplus import Namespace, fields
import socket
import time
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
import apis.utils.crads as setting
from werkzeug.security import generate_password_hash, check_password_hash
import copy

#logging.basicConfig(filename='vendor.log', level=logging.DEBUG)   

# Declare tables name in vars
tbl_v002_vendors = "v002_vendors"
tbl_v003_vendor_users = "v003_vendor_users"
tbl_v021_spotlight = "v021_spotlight"
tbl_v004_outlets = "v004_outlets"
tbl_v019_offer_details = "v019_offer_details"

def addSpotlightModel(self,ns):
    addOutlet = ns.model('addOutletModel', {
        'outlet_id':fields.String(required=True, description="Provide newly added outlet id" ),
        'user_id': fields.String(required=True, min_length=1, example=1, description='User id is required'),
        'vendor_id': fields.String(required=True, min_length=1, example=1, description='vendor id is required'),
        'subject': fields.String(required=True,  description='Subject is required'),
        'description': fields.String(required=True, description='Description is required'),
        'image': fields.String(required=False, description='Images id is required')
    })
    return addOutlet

def listSpotlightModel(sself, ns):
    addOutlet = ns.model('listSpotlightModel', {
        'vendor_id': fields.String(required=True, min_length=1, example=1, description='vendor id is required')
    })
    return addOutlet


def saveSpotlight(self):
    code = 201
    status = False
    message = ""
    responseData = {}
    todayDate = datetime.now()
    ip_address = socket.gethostbyname(socket.gethostname())
    requestData = dict(request.json)
    
    requestData["insertIp"] = ip_address
    requestData["insertDate"] = todayDate
    requestData["view_status"] = 0
    requestData["status"] = 0
    requestData["payment_status"] = 0
    requestData["user_id"] = ObjectId(requestData["user_id"])
    requestData["vendor_id"] = ObjectId(requestData["vendor_id"])
    requestData["outlet_id"] = ObjectId(requestData["outlet_id"])

    getVendorData = DB.find_one(tbl_v002_vendors,{"_id":requestData["vendor_id"]},{"_id":0,"contact_person":1})
    getUser = DB.find_one(tbl_v003_vendor_users,{"_id":requestData["user_id"]},{"name":1,"contact_number":1,"email":1,"_id":0})
    getOutlet = DB.find_one(tbl_v004_outlets,{"_id":requestData["outlet_id"]},{"name":1})
    if getUser and getVendorData and getOutlet:
        ins = DB.insert(tbl_v021_spotlight,requestData)
        if ins:

            adminData = setting.crads(requestData["vendor_id"], requestData["user_id"]).adminContact()
            """ Send mail to the vendor client """
            notificationObject = {}
            emailObject = {}
            emailObject["to"] = [getUser["email"]]
            emailObject["template"] = "add_spotlight"
            emailObject["replace_value"] = {}
            emailObject["replace_value"]["user_name"] = getUser["name"].capitalize()
            emailObject["sender"] = {}
            emailObject["sender"]["type"] = "admin"
            emailObject["sender"]["id"] = "1"
            emailObject["receiver"] = {}
            emailObject["receiver"]["type"] = "vendor"
            emailObject["receiver"]["id"] = "1"
            emailObject["subject"] = "Wellnessta - Spotlight"
            notificationObject["email"] = emailObject

            res = requests.post(CONST.NOTIFACTION_CLIENT, json=notificationObject)
            res = res.json()

            """ Send mail to the admin """
            notificationObject = {}
            emailObject = {}
            emailObject["to"] = [adminData["email"]]
            emailObject["template"] = "reply_spotlight"
            emailObject["replace_value"] = {}
            emailObject["replace_value"]["user_name"] = adminData["name"].capitalize()
            emailObject["replace_value"]["vendor_name"] = getVendorData["contact_person"]
            emailObject["replace_value"]["outlet_name"] = getOutlet["name"]
            emailObject["sender"] = {}
            emailObject["sender"]["type"] = "vendor"
            emailObject["sender"]["id"] = "1"
            emailObject["receiver"] = {}
            emailObject["receiver"]["type"] = "admin"
            emailObject["receiver"]["id"] = "1"
            emailObject["subject"] = "Wellnessta - Spotlight"
            notificationObject["email"] = emailObject
            res = requests.post(CONST.NOTIFACTION_CLIENT, json=notificationObject)
            res = res.json()           

            status = True
            message = "Spotlight has been inserted"
            responseData = ins
        else:
            status = False
            message = "Failed to add spotlight"
            responseData = {}

    response = output_json(responseData,message,status,code)
    return response

def getSpotlight(self):
   
    code = 200
    status = False
    message = ""
    responseData = {}
    todayDate = datetime.now()
    ip_address = socket.gethostbyname(socket.gethostname())
    requestData = dict(request.json)
    
    requestData["vendor_id"] = ObjectId(requestData["vendor_id"])
    getOutlet = DB.find_by_key(tbl_v004_outlets,requestData,{"name":1,"_id":1})
    getList = DB.find_by_key(tbl_v021_spotlight,requestData,{"_id":1,"subject":1,"description":1,"image":1,"status":1,"outlet_id":1})
    if getList:
        ol = {}
        for x in range(len(getOutlet)):
            ol[getOutlet[x]["_id"]["$oid"]] = str(getOutlet[x]["name"]).title()
        
        for x in range(len(getList)):
            getList[x]["outlet_id"] = ol[getList[x]["outlet_id"]["$oid"]] if getList[x]["outlet_id"] and getList[x]["outlet_id"]["$oid"] in ol else ""

        status = True
        message = "Success"
        responseData = getList
    else:
        status = True
        message = "No, record founds"
        responseData = []
   
    response = output_json(responseData,message,status,code)
    return response

def get_referal_code(self,vendor_id):
    code = 200
    status = False
    message = ""
    responseData = {}
    refferal=DB.find_all("a016_reference_data",{})
    for x in refferal:
        find_referel_code = DB.find_all_where(tbl_v019_offer_details,{"vendor_id":ObjectId(vendor_id),"module":str(x['value3'])},"ALL")
    if find_referel_code:
        code = 200
        status = True
        message = "Get referel code successfully..!"
    else:
        code = 201
        status = False
        message = "Something went Wrong..!"
  
    response = output_json(find_referel_code,message,status,code)
    logging.debug('get_referal_code: {}'.format(response))
    return response

def Spotlight_status(self): 
    code = 201
    status = False
    message = ""
    responseData = {}
    addData = {}
    requestData = dict(request.json)
    spot_id = requestData['spot_id']
    code = 201
    get_spot_status = DB.find_one(tbl_v021_spotlight,{"_id":ObjectId(spot_id)})
    if(get_spot_status):
        updateStatus = DB.update_one(tbl_v021_spotlight,{"status":5},{"_id":ObjectId(spot_id)}) 
        if updateStatus:
            code = 200
            status = True
            message = "Data Updated SuccessFully..!"
        else :
            code = 201
            status = False
            message = "Something Went Wrong..!"
    response = output_json(addData,message,status,code)
    return response