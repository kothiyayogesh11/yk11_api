from flask_restplus import Namespace, fields
import socket
import time
import pymongo
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

#logging.basicConfig(filename='vendor.log', level=logging.DEBUG)   

tbl_v002_vendors = "v002_vendors"
tbl_v004_outlets = "v004_outlets"
tbl_v025_vendor_inquiry = "v025_vendor_inquiry"
tbl_a001_email_template="a001_email_template"


def get_vendor_inquiry_data(self,outlet_id,inquiry_id):
    code = 201
    status = False
    message = ""
    responseData = {}
    Data = {}
    fieldsList = {"_id":1,"business_name":1,"business_type":1,"name":1,"phone":1,"email":1,"city":1,"reply":1}
    if inquiry_id != "":
        get_vendor_inquiry_data =  DB.find_using_aggregate(tbl_v025_vendor_inquiry,[{"$match":{"_id":ObjectId(inquiry_id)}},{"$project":fieldsList}])
        Data['inquiry_data'] = get_vendor_inquiry_data[0]
    else:
        Data['inquiry_data'] = ''
    code = 200
    status = True
    message = MSG_CONST.OFFER_SUCCESS
    response = output_json(Data,message,status,code)
    #logging.debug('get_vendor_inquiry_data: {}'.format(response))
    return response





def vendor_inquiry_data(self):
    code = 201
    status = False
    message = ""
    responseData = {}
    addData = {}
    todayDate = datetime.datetime.now();
    ip_address = socket.gethostbyname(socket.gethostname())
    requestData = dict(request.json)
    fieldsList = {"_id":1,"status":1}

    addData["business_name"] = requestData["business_name"]
    addData["business_type"] = requestData["business_type"]
    addData["name"] = requestData["name"]
    addData["phone"] = requestData["phone"]
    addData["email"] = requestData["email"]
    addData['city'] = requestData["city"]
    addData['subject'] = requestData["subject"]
    addData['message'] = requestData["message"]
    addData['inserted_on'] = todayDate
    addData["status"] = 0
    addData["insert_ip"] = ip_address
    act = DB.insert(tbl_v025_vendor_inquiry,addData)
    if(act):
        #send email to vendor
        email_arr = DB.find_one(tbl_a001_email_template,{'type':'vendor_inquiry'},{'title':1})
        notificationObject = {}
        emailObject = {}
        emailObject["to"] = [addData["email"]]
        emailObject["template"] = "vendor_inquiry"
        emailObject["replace_value"] = {}
        emailObject["replace_value"]["user_name"] = addData["name"].capitalize()
        emailObject["replace_value"]["link"] = CONST.VENDOR_WEB+'register'
        emailObject["replace_value"]["link2"] = CONST.CLIENT_WEB
        emailObject["replace_value"]["link3"] = CONST.VENDOR_WEB
        emailObject["sender"] = {}
        emailObject["sender"]["type"] = "SYS"
        emailObject["sender"]["id"] = "1"
        emailObject["receiver"] = {}
        emailObject["receiver"]["type"] = "vendor"
        emailObject["receiver"]["id"] = "1"
        emailObject["subject"] = email_arr['title']
        notificationObject["email"] = emailObject
        res = requests.post(CONST.NOTIFACTION_CLIENT, json=notificationObject)
        response = dict(res.json())

        #send email to admin
        email_arr = DB.find_one(tbl_a001_email_template,{'type':'admin_vendor_inquiry'},{'title':1})
        notificationObject = {}
        emailObject = {}
        emailObject["to"] = [CONST.ADMIN_EMAIL]
        emailObject["template"] = "admin_vendor_inquiry"
        emailObject["replace_value"] = {}
        emailObject["replace_value"]["user_name"] = addData["name"].capitalize()
        emailObject["replace_value"]["inq_email"] = addData["email"]
        emailObject["replace_value"]["inq_subject"] = addData["subject"]
        emailObject["replace_value"]["inq_message"] = addData["message"]
        emailObject["replace_value"]["link"] = CONST.ADMIN_WEB+'vendorinquiry/list'
        emailObject["sender"] = {}
        emailObject["sender"]["type"] = "SYS"
        emailObject["sender"]["id"] = "1"
        emailObject["receiver"] = {}
        emailObject["receiver"]["type"] = "vendor"
        emailObject["receiver"]["id"] = "1"
        emailObject["subject"] = email_arr['title']
        notificationObject["email"] = emailObject
        res = requests.post(CONST.NOTIFACTION_CLIENT, json=notificationObject)
        response = dict(res.json())




        code = 200
        status = True
        message = MSG_CONST.VENDOR_INQUIRY_SUCCESS    
    else:
        code = 201
        status = False
        message = MSG_CONST.VENDOR_INQUIRY_FAILED
    response = output_json(responseData,message,status,code)
    #logging.debug('vendor_inquiry_data: {}'.format(response))
    return response















# def vendor_inquiry_data(self):
#     code = 201
#     status = False
#     message = ""
#     responseData = {}
#     addData = {}
#     todayDate = datetime.datetime.now();
#     ip_address = socket.gethostbyname(socket.gethostname())
#     requestData = dict(request.json)
#     fieldsList = {"_id":1,"status":1}
#     Data = DB.find_one(tbl_v004_outlets,{"$and":[{"_id":ObjectId(requestData['outlet_id']),"vendor_id":ObjectId(requestData["vendor_id"])}]})
#     addData["outlet_id"] = ObjectId(requestData['outlet_id'])
#     addData["vendor_id"] = ObjectId(requestData["vendor_id"])
#     addData["business_name"] = requestData["business_name"]
#     addData["business_type"] = requestData["business_type"]
#     addData["name"] = requestData["name"]
#     addData["phone"] = requestData["phone"]
#     addData["email"] = requestData["email"]
#     addData['city'] = requestData["city"]
#     addData['inserted_on'] = todayDate
#     addData["status"] = 0
#     addData["insert_ip"] = ip_address
#     if(Data):
#             if requestData["inquiry_id"] == "":
#                 act = DB.insert(tbl_v025_vendor_inquiry,addData)
#                 code = 200
#                 status = True
#                 message = MSG_CONST.VENDOR_INQUIRY_SUCCESS    
#             else:
#                 act = DB.update_one(tbl_v025_vendor_inquiry,{"business_name":requestData["business_name"],"business_type":requestData["business_type"],"name":requestData["name"],"phone":requestData["phone"],"email":requestData["email"],"city":requestData["city"],"reply":requestData["reply"],"status":1,"updated_on":todayDate,"updated_ip":ip_address},{"_id":ObjectId(requestData['inquiry_id'])})
#                 code = 200
#                 status = True
#                 message = MSG_CONST.VENDOR_INQUIRY_UPDATE_SUCCESS
#     else:
#         code = 201
#         status = False
#         message = MSG_CONST.VENDOR_INQUIRY_FAILED
#     response = output_json(responseData,message,status,code)
#     #logging.debug('vendor_inquiry_data: {}'.format(response))
#     return response


def get_all_vendor_inquiry_data(self,outlet_id):
    code = 201
    status = False
    message = ""
    responseData = {}
    addData = {}
    get_all_Data = {}
    fieldsList = {"_id":1,"business_name":1,"business_type":1,"name":1,"phone":1,"email":1,"city":1,"reply":1}
    get_all_Data = DB.find_using_aggregate(tbl_v025_vendor_inquiry,[{"$match":{"outlet_id":ObjectId(outlet_id),"status":0}},{"$sort":{"_id":-1}},{"$project":fieldsList}])
    if(get_all_Data):
            code = 200
            status = True
            message = MSG_CONST.OFFER_SUCCESS
    else :
        code = 200
        status = False
        message = MSG_CONST.VENDOR_INQUIRY_FAILED
    response = output_json(get_all_Data,message,status,code)
    #logging.debug('get_all_vendor_inquiry_data: {}'.format(response))
    return response