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
from werkzeug.security import generate_password_hash, check_password_hash
import copy
import sys

#logging.basicConfig(filename='vendor.log', level=logging.DEBUG)   

# Declare tables name in vars
tbl_v002_vendors = "v002_vendors"
tbl_v003_vendor_users = "v003_vendor_users"
tbl_v004_outlets = "v004_outlets"
tbl_v023_accomodation = "v023_accomodation"
tbl_v014_amenities = "v014_amenities"
tbl_v026_tour_steps = "v026_tour_steps"
tbl_a013_tag_master = "a013_tag_master"

def SaveAccomodation(self):
    code = 201
    status = False
    message = ""
    responseData = {}
    todayDate = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    ip_address = socket.gethostbyname(socket.gethostname())
    requestData = dict(request.json)
    find_outlet = DB.find_one(tbl_v004_outlets,{"_id":ObjectId(requestData['outlet_id'])})

    
    if find_outlet:
        amenities = requestData["amenities_id"]
        amenities_ids = []
        for ids in amenities:
            amenities_id = ObjectId(ids)
            amenities_ids.append(amenities_id)
        requestData['amenities_id'] = amenities_ids
        if requestData['accomodation_id'] == "":
            del requestData['accomodation_id']
            requestData["vendor_id"] = ObjectId(requestData["vendor_id"])
            requestData["outlet_id"] = ObjectId(requestData["outlet_id"])
            requestData["status"] = 1
            requestData["is_delete"] = 0
            requestData["created_by"] = ObjectId(requestData["user_id"])
            requestData["created_date"] = todayDate
            requestData["insert_ip"] = ip_address
            del requestData['user_id']
            act = DB.insert(tbl_v023_accomodation,requestData)
            update_tour_steps = DB.update_one(tbl_v026_tour_steps,{"setup_accomodation":True},{"vendor_id":ObjectId(requestData["vendor_id"])})
            responseData['accomodation_id'] = act
            if act:
                code = 200
                status = True
                message = MSG_CONST.ACCOMODATION_INSERTED_SUCCESS
            else:
                code = 201
                status = False
                message = MSG_CONST.ACCOMODATION_INSERTED_FAILED
        else:
            requestData["vendor_id"] = ObjectId(requestData["vendor_id"])
            requestData["outlet_id"] = ObjectId(requestData["outlet_id"])
            requestData['accomodation_id'] = ObjectId(requestData['accomodation_id'])
            requestData["updated_by"] = ObjectId(requestData["user_id"])
            requestData["updated_date"] = todayDate
            requestData["updated_ip"] = ip_address
            del requestData['user_id']
            act = DB.update_one(tbl_v023_accomodation,requestData,{"_id":requestData["accomodation_id"]})
            if act:
                code = 200
                status = True
                message = MSG_CONST.ACCOMODATION_UPDATED_SUCCESS
            else:
                code = 201
                status = False
                message = MSG_CONST.ACCOMODATION_UPDATED_FAILED
    response = output_json(responseData,message,status,code)
    logging.debug('SaveAccomodation: {}'.format(response))
    return response



def accomodation_list(self,outlet_id):
    code = 201
    status = False
    message = ""
    responseData = {}
    addData = {}
    get_all_Data = {}
    
    fieldsList = {"_id":1,"outlet_id":1,"title" : 1,"price" : 1,"room_type":1,"Number_room":1}
    if outlet_id != "":
        get_all_Data = DB.find_using_aggregate(tbl_v023_accomodation,[{"$match":{"outlet_id":ObjectId(outlet_id),"is_delete":0}},{"$sort":{"_id":-1}},{"$project":fieldsList}])
    else:
        get_all_Data = []
    if(get_all_Data):
        code = 200
        status = True
        message = MSG_CONST.ACCOMODATION_LIST_SUCCESS
    else :
        code = 200
        status = False
        message = MSG_CONST.ACCOMODATION_GET_FAIL
    response = output_json(get_all_Data,message,status,code)
    logging.debug('accomodation_list: {}'.format(response))
    return response


def remove_accomodation(self):
    code = 201
    status = False
    message = ""
    requestData = dict(request.json)
    responseData = {}
    todayDate = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    ip_address = request.remote_addr
    find_accomodation_id = DB.find_one(tbl_v023_accomodation,{"_id":ObjectId(requestData['accomodation_id'])},"ALL")
    
    if find_accomodation_id:
        delete_accomodation_id = DB.update_one(tbl_v023_accomodation,{"is_delete":1},{"_id":ObjectId(requestData['accomodation_id'])})
        if delete_accomodation_id:
            code = 200
            status = True
            message = MSG_CONST.ACCOMODATION_DELETED_SUCCESS
        else:
            code = 201
            status = False
            message = MSG_CONST.ACCOMODATION_DELETE_FAILED
    else:
        code = 201
        status = False
        message = MSG_CONST.ACCOMODATION_NOT_FOUND   
        
    response = output_json(responseData,message,status,code)
    logging.debug('remove_accomodation: {}'.format(response))
    return response

def getAccomodation(self):
    code = 200
    status = False
    message = ""
    responseData = {}
    find_accomodation_arr={}
    if request.args.get("accomodation_id") and request.args.get("accomodation_id") != "":
        accomodation_id = ObjectId(request.args.get("accomodation_id")) 
        find_accomodation = DB.find_one(tbl_v023_accomodation,{"_id":accomodation_id},'ALL')
        if(find_accomodation):
            find_accomodation_arr['data']=find_accomodation        
            code = 200
            status = True
            message = MSG_CONST.ACCOMODATION_GET_SUCCESS
        else:
            find_accomodation_arr = []
            code = 201
            status = False
            message = MSG_CONST.ACCOMODATION_GET_FAIL
    else:
        find_accomodation_arr = []
        code = 201
        status = False
        message = "something went wrong"
    response = output_json(find_accomodation_arr,message,status,code)
    logging.debug('getAccomodation: {}'.format(response))
    return response 

def getAmenitiesByOutlet(self):
    code = 200
    status = False
    message = ""
    responseData = {}
    todayDate = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    ip_address = request.remote_addr
    accomodationData = DB.find_all_where(tbl_a013_tag_master,{"type":"amenities"},{"_id":1,"title":1})
    serCat = []
    if accomodationData:
        for x in accomodationData:
            serCat.append({"_id":x["_id"]["$oid"],"title":x["title"]})
        responseData = serCat
        status = True
        message = MSG_CONST.ACCOMODATION_GET_AMENITIES_SUCCESS
        code = 200
    else:
        responseData = serCat
        status = True
        message = MSG_CONST.VENDOR_NO_RECORD_FOUND
        code = 200
    response = output_json(responseData,message,status,code)
    logging.debug('getMeditationByOutlet: {}'.format(response))
    return response