from flask_restplus import Namespace, fields
import socket
import time
import pymongo
from datetime import datetime, date, time, timedelta
from flask import jsonify, request
from database import DB
from bson import json_util, ObjectId
import json
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
import copy
from pytz import timezone
import pytz

#logging.basicConfig(filename='vendor.log', level=logging.DEBUG)   

tbl_v013_feedback = "v013_feedback"
tbl_v004_outlets = "v004_outlets"
tbl_v019_offer_details = "v019_offer_details"
tbl_v012_services = "v012_services"
tbl_v026_tour_steps = 'v026_tour_steps'
tbl_v002_vendors='v002_vendors'
tbl_v028_meditation_naturopathy='v028_meditation_naturopathy'
tbl_v025_vendor_inquiry = 'v025_vendor_inquiry'
tbl_a001_email_template = 'a001_email_template'

india_tz = pytz.timezone('Asia/Kolkata')

def get_offer_data(self,outlet_id,offer_id,vendor_id):
    get_services = []
    get_offer_Data = []
    code = 201
    status = False
    message = ""
    responseData = {}
    Data = {}
    
    fieldsList = {"outlet_id":1,"_id":1,"offer_type":1,"name":1,"offer_name":1,"type":1,"value":1,"start_date":{"$dateToString":{"format":"%Y-%m-%d %H:%M:%S","date":"$start_date"}},"due_date":{"$dateToString":{"format":"%Y-%m-%d %H:%M:%S","date":"$due_date"}},"start_time":1,"end_time":1,"limitation":1,"all_services":1,"service_ids":1,"coupon_code":1,"firsttime_signup":1,"fest_membership":1}
    if outlet_id != "":
        vendor_arr = DB.find_one(tbl_v002_vendors,{"_id":ObjectId(vendor_id)},{"_id":0,"business_type":1})
        if vendor_arr['business_type']=="massage_and_spa":
            get_services =  DB.find_using_aggregate("v012_services",[{"$match":{"outlet_id":ObjectId(outlet_id),"status":1}}])
        else:
            get_services =  DB.find_using_aggregate(tbl_v028_meditation_naturopathy,[{"$match":{"outlet_id":ObjectId(outlet_id),"status":1}}])    

        get_offer_count = DB.find_all_where("v019_offer_details",{"outlet_id":ObjectId(outlet_id),"is_delete":0})
        total_offer = len(get_offer_count)
        Data['total_count'] = total_offer
    else:
        Data['total_count'] = 0
        get_services = []
    get_outlets = DB.find_all_where(tbl_v004_outlets,{"vendor_id":ObjectId(vendor_id)},{"_id":1,"name":1})
    
    if offer_id != "":
        get_offer_Data =  DB.find_using_aggregate("v019_offer_details",[{"$match":{"_id":ObjectId(offer_id)}},{"$project":fieldsList}])
        Data['offer_data'] = get_offer_Data[0]
        for x in get_offer_Data:
            start_time = x['start_time']
            end_time = x['end_time']
            if type(start_time) == int and type(start_time) == int:
                s_time = datetime.datetime.fromtimestamp(start_time, india_tz)
                st_time = s_time.strftime("%I:%M %p")
                e_time = datetime.datetime.fromtimestamp(end_time, india_tz)
                ed_time = e_time.strftime("%I:%M %p")
                Data['offer_data']['start_time'] = st_time
                Data['offer_data']['end_time'] = ed_time
            else:
                Data['offer_data']['start_time'] = start_time
                Data['offer_data']['end_time'] = end_time
    else:
        Data['offer_data'] = ''
    Data['outlets'] = get_outlets   
    Data['services'] = get_services
    code = 200
    status = True
    message = MSG_CONST.OFFER_SUCCESS
    response = output_json(Data,message,status,code)
    #logging.debug('get_offer_data: {}'.format(response))
    return response


def offer_data(self):
    code = 201
    status = False
    message = ""
    responseData = {}
    addData = {}
    todayDate = datetime.datetime.now();
    ip_address = socket.gethostbyname(socket.gethostname())
    requestData = dict(request.json)
    date_string = requestData['due_date']
    date_string2 = requestData['start_date']
    
    date_time = datetime.datetime.strptime(date_string, '%m/%d/%Y')
    start_date = datetime.datetime.strptime(date_string2, '%m/%d/%Y')
    
    end_time_stamp = int(datetime.datetime.timestamp(india_tz.localize(date_time)))
    start_time_stamp = int(datetime.datetime.timestamp(india_tz.localize(start_date)))
    
    
    fieldsList = {"outlet_id":1,"_id":1,"offer_name":1,"type":1,"value":1,"due_date":1,"limitation":1,"all_services":1,"services":1, "service_ids":1,"is_coupon":1,"coupon_code":1,"first_offer":1}
    
    if requestData["offer_type"] == "offpeak":
        start_t = requestData["start_time"]
        end_t = requestData["end_time"]
        start_date_and_time =  requestData['start_date'] + requestData["start_time"]
        end_date_and_time =  requestData['due_date'] + requestData["end_time"]
        start_time = datetime.datetime.strptime(start_date_and_time,'%m/%d/%Y%I:%M %p')
        end_time = datetime.datetime.strptime(end_date_and_time,'%m/%d/%Y%I:%M %p')
        s_time = int(datetime.datetime.timestamp(india_tz.localize(start_time)))
        e_time = int(datetime.datetime.timestamp(india_tz.localize(end_time)))
        addData['start_time'] = s_time
        addData['end_time'] = e_time
    else:
        addData['start_time'] = start_time_stamp
        addData['end_time'] = end_time_stamp  
    
    requestData['start_date'] = start_date
    requestData['due_date'] = date_time
    addData["offer_name"] = requestData["offer_name"]
    offer_value = requestData['value']
    addData["type"] = requestData["type"]
    addData["value"] = float(requestData["value"])
    addData["all_services"] = requestData["all_services"]
    addData["firsttime_signup"] = requestData["firsttime_signup"]
    addData["fest_membership"] = requestData["fest_membership"]
    addData["offer_type"] = requestData["offer_type"]
    addData['start_date'] = start_date
    addData['due_date'] = date_time
    addData['module']="offer"
    if requestData["all_services"] == False:
        services = requestData["service_ids"]
        service_ids = []
        for ids in services:
            service_id = ObjectId(ids)
            service_ids.append(service_id)
        addData['service_ids'] = service_ids
    else:
        service_ids = []
        addData['service_ids'] = service_ids
    coupen_code = DB.randomStringDigits()
    if requestData['offer_type'] == "coupon":
        addData['coupon_code'] = requestData["coupon_code"]
        addData["limitation"] = int(requestData["limitation"])
    else:
        addData["coupen_code"] = ""
        addData["limitation"] = ""
    addData["is_delete"] = 0
    addData["insert_date"] = todayDate
    addData["insert_ip"] = ip_address

    if requestData["offer_id"] == "":
        if requestData['outlet_id'] == 'all': # for all outlet add
            outlet_data = []

            outLetData = DB.find_all_where(tbl_v004_outlets,{"vendor_id":ObjectId(requestData['vendor_id'])})
            for x in outLetData:
                outlet_id = x["_id"]['$oid']
                test = copy.copy(requestData)
                test['outlet_id'] = ObjectId(outlet_id)
                test["module"] = "offer"
                test["status"] = 1
                test["is_delete"] = 0
                outlet_data.append(test)
            act = DB.insert_many(tbl_v019_offer_details,outlet_data)
            update_tour_steps = DB.update_one(tbl_v026_tour_steps,{"setup_offers":True},{"vendor_id":ObjectId(requestData["vendor_id"])})
            code = 200
            status = True
            message = MSG_CONST.OFFER_SUCCESS 
        else:
            addData['outlet_id'] = ObjectId(requestData['outlet_id'])
            find_offer_in_outlet = DB.find_all_where(tbl_v019_offer_details,{"outlet_id":ObjectId(requestData['outlet_id']),"is_delete":0})
            if (find_offer_in_outlet):
                addData['first_offer'] = False
            else:
                addData['first_offer'] = True
            act = DB.insert(tbl_v019_offer_details,addData)
            update_tour_steps = DB.update_one(tbl_v026_tour_steps,{"setup_offers":True},{"vendor_id":ObjectId(requestData["vendor_id"])})
            
            code = 200
            status = True
            message = MSG_CONST.OFFER_SUCCESS 
    else:
        if requestData['offer_type'] == "offpeak":
            act = DB.update_one("v019_offer_details",{"offer_name":requestData["offer_name"],"offer_type":requestData["offer_type"],"start_date":start_date,"due_date":date_time,"start_time":s_time,"end_time":e_time,"type":requestData["type"],"value":float(requestData["value"]),"limitation":"","all_services":requestData["all_services"],"service_ids":service_ids,"coupon_code":"","first_offer":False},{"_id":ObjectId(requestData['offer_id'])})
            code = 200
            status = True
            message = MSG_CONST.OFFER_SUCCESS
        elif requestData['offer_type'] == "coupon":
            act = DB.update_one("v019_offer_details",{"offer_name":requestData["offer_name"],"offer_type":requestData["offer_type"],"start_date":start_date,"due_date":date_time,"start_time":"","end_time":"","type":requestData["type"],"value":float(requestData["value"]),"limitation":int(requestData["limitation"]),"all_services":requestData["all_services"],"coupon_code":requestData["coupon_code"],"service_ids":service_ids,"first_offer":False},{"_id":ObjectId(requestData['offer_id'])})
            code = 200
            status = True
            message = MSG_CONST.OFFER_SUCCESS
        else:
            act = DB.update_one("v019_offer_details",{"offer_name":requestData["offer_name"],"offer_type":requestData["offer_type"],"start_date":start_date,"due_date":date_time,"start_time":"","end_time":"","type":requestData["type"],"value":float(requestData["value"]),"limitation":"","all_services":requestData["all_services"],"service_ids":service_ids,"coupon_code":"","first_offer":False},{"_id":ObjectId(requestData['offer_id'])})
            code = 200
            status = True
            message = MSG_CONST.OFFER_SUCCESS
    response = output_json(responseData,message,status,code)
    #logging.debug('add_offer: {}'.format(response))
    return response

def get_all_offer_data(self,outlet_id):
    code = 201
    status = False
    message = ""
    responseData = {}
    addData = {}
    get_all_Data = {}
    
    fieldsList = {"outlet_id":1,"offer_type":1,"offer_name":1,"limitation":1,"coupon_code":1,"type":1,"value":1,"start_date":{"$dateToString":{"format":"%Y-%m-%d %H:%M:%S","date":"$start_date"}},"due_date":{"$dateToString":{"format":"%Y-%m-%d %H:%M:%S","date":"$due_date"}},"start_time":1,"end_time":1}
    # get_all_Data = DB.find_all_where("v019_offer_details",{"outlet_id":ObjectId(outlet_id)},{"is_delete":0},fieldsList)
    if outlet_id != "":
        get_all_Data = DB.find_using_aggregate(tbl_v019_offer_details,[{"$match":{"outlet_id":ObjectId(outlet_id),"is_delete":0,"module":"offer"}},{"$sort":{"_id":-1}},{"$project":fieldsList}])
    else:
        get_all_Data = []
    if(get_all_Data):
        code = 200
        status = True
        message = MSG_CONST.OFFER_SUCCESS
    else :
        code = 201
        status = False
        message = MSG_CONST.OFFER_TECH_PROB
    response = output_json(get_all_Data,message,status,code)
    #logging.debug('get_all_offer_data: {}'.format(response))
    return response

def delete_offer_data(self):
    code = 201
    status = False
    message = ""
    responseData = {}
    addData = {}
    requestData = dict(request.json)
    offer_id = requestData['offer_id']
    code = 201
    delete_offer = DB.find_one("v019_offer_details",{"_id":ObjectId(offer_id)})
    if(delete_offer):
        updateStatus = DB.update_one("v019_offer_details",{"is_delete":1},{"_id":ObjectId(offer_id)}) 
        if updateStatus:
            code = 200
            status = True
            message = "Data Deleted SuccessFully..!"
        else :
            code = 201
            status = False
            message = "Something Went Wrong..!"
    response = output_json(addData,message,status,code)
    #logging.debug('delete_offer_data: {}'.format(response))
    return response


def get_services_data(self):
    code = 201
    status = False
    message = ""
    responseData = {}
    addData = {}
    requestData = dict(request.json)
    outlet_id = requestData['outlet_id']
    code = 201
    get_services = DB.find_all_where(tbl_v012_services,{"outlet_id":ObjectId(outlet_id)})
    if(get_services):
        code = 200
        status = True
        message = "Service Get SuccessFully..!"
    else:
        get_services = []
        code = 201
        status = False
        message = "Something Went Wrong..!"
    response = output_json(get_services,message,status,code)
    return response

def apply_barter_offer(self):
    requestData = dict(request.json)
    requestData['type'] = 'barter'
    requestData['status'] = 0
    requestData['inserted_on'] = get_current_date()
    db_response = DB.insert(tbl_v025_vendor_inquiry,requestData)
    if db_response == None:
        return output_json({},"Something Went Wrong..!",False,201)
    else:
        email_arr = DB.find_one(tbl_a001_email_template,{'type':'vendor_apply_barter_offer'})
        notificationObject = {}
        emailObject = {}
        emailObject["to"] = [CONST.BATER_EMAIL]
        emailObject["template"] = "vendor_apply_barter_offer"
        emailObject["replace_value"] = {}
        emailObject["replace_value"]["user_name"] = requestData['name']
        emailObject["replace_value"]["business_name"] = requestData['business_name']
        emailObject["replace_value"]["email"] = requestData['email']
        emailObject["replace_value"]["intrested_in"] = requestData['offer_name']
        emailObject["replace_value"]["link"] = CONST.ADMIN_WEB + "vendorinquiry/list"
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
        return output_json({},MSG_CONST.BARTER_OFFER_APPLY_SUCCESS,True,200)
