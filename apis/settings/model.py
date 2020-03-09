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
from apis.utils.gst import *


#logging.basicConfig(filename='logs/vendor.log', level=logging.DEBUG)   

# Declare tables name in vars
tbl_v002_vendors = "v002_vendors"
tbl_v003_vendor_users = "v003_vendor_users"
tbl_a005_otp_verify = "a005_otp_verify"
tbl_v004_outlets = "v004_outlets"

def verifyGstModel(self,ns):
    gst = ns.model('verifyGstModel', {
        'vendor_id': fields.String(required=True, description='Login user vendor id'),
        'user_id': fields.String(required=True, description='Login user id'),
        'gstn': fields.String(required=True, description='Provide GST number for validation')
    })
    return gst

def vendorProfileModel(self,ns):
    gst = ns.model('vendorProfileModel', {
        'vendor_id': fields.String(required=True, description='Login user vendor id'),
        'user_id': fields.String(required=True, description='Login user id')
    })
    return gst
# Vendor Login
def searchGst(self):
    requestData = request.json

    code = 200
    status = True
    message = ""
    responseData = {}
    res = GST(requestData["gstn"]).verifyGst()
    
    if res and "error" in res and res["error"] == False:
        status = True
    else:
        status = False
    responseData = requestData["gstn"]
    message = res["message"] if res["message"] else "Something went wrong."
    response = output_json(responseData,message,status,code)
    #logging.debug('vendor_gst_verify: {}'.format(response))
    return response

def saveGst(self):
    requestData = request.json
    code = 200
    status = True
    message = ""
    responseData = {}
    res = GST(requestData["gstn"]).verifyGst()
    
    if res and "error" in res and res["error"] == False:
        act = DB.update_one(tbl_v002_vendors, {"gstn":requestData["gstn"],"gstn_verify":1},{"_id":ObjectId(requestData["vendor_id"])})
        if act:
            status = True
            responseData = []
            message = MSG_CONST.VENDOR_GST_SAVE_SUCCESS
        else:
            status = False
            responseData = []
            message = MSG_CONST.VENDOR_GST_SAVE_FAILED
    else:
        status = False
        responseData = []
        message = MSG_CONST.VENDOR_GST_SAVE_FAILED
    response = output_json(responseData,message,status,code)
    #logging.debug('vendor_gst_save: {}'.format(response))
    return response

def getVendorProfile(self):
    requestData = request.json
    code = 200
    status = True
    message = ""
    responseData = {}

    getVendorData = DB.find_one(tbl_v002_vendors,{"_id":ObjectId(requestData["vendor_id"])},{"update_by":0,"email_verify_code":0,"create_by":0,"insert_date":0,"update_date":0,"insert_ip":0})
    getoutletData = DB.find_one(tbl_v002_vendors,{"_id":ObjectId(requestData["vendor_id"])},{"docs":1,"_id":0})
    
    if getVendorData:
        getVendorData["_id"] = getVendorData["_id"]["$oid"]
        getVendorData["authority_user"] = getVendorData["authority_user"]["$oid"]
        responseData['profile']=getVendorData
        if getoutletData:
            responseData['docs']= getoutletData
        else:
            responseData['docs']= ""
    else:
        pass           
    response = output_json(responseData,message,status,code)
    return response