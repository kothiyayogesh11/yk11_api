from flask_restplus import Namespace, fields
import socket
import time
from datetime import datetime, date, time, timedelta
from flask import jsonify, request
import pymongo
from database import DB
from bson import json_util, ObjectId
from apis.utils.common import *
from apis.libraries.send_mail import Send_mail
import requests
import apis.utils.role as role
import apis.utils.subscription as subscription
import logging
import apis.utils.message_constants as MSG_CONST
import apis.utils.constants as CONST
from werkzeug.security import generate_password_hash, check_password_hash
import dateutil
import isodate
import datetime
import time

#logging.basicConfig(filename='logs/vendor.log', level=logging.DEBUG)   

# Declare tables name in vars
tbl_v002_vendors = "v002_vendors"
tbl_v003_vendor_users = "v003_vendor_users"
tbl_a017_history = "a017_history"
tbl_a005_otp_verify = "a005_otp_verify"
tbl_v004_outlets = "v004_outlets"
tbl_v026_tour_steps = 'v026_tour_steps'
tbl_a001_email_template="a001_email_template"


def dto(self,ns):
    Login = ns.model('LoginModel', {
        'email_phone': fields.String(required=True, description='Email or mobile number is required'),
        'password': fields.String(required=True, description='Password filed is empty')
    })
    return Login

def loginOtpModel(self,ns):
    LoginOtp = ns.model('LoginOtpModel', {
        'phone': fields.String(required=True, description='Phone number is required')
    })
    return LoginOtp
# Send Login OTP

def verificationCodeModel(self, ns):
    verificationCodeModel = ns.model('verificationCodeModel', {
        'code': fields.String(required=True, description='Verification code is empty')
    })
    return verificationCodeModel

def getVendorById(vendor_id):
    return True

# Vendor Login
def login(self):
    requestData = request.json
    code = 200
    status = True
    message = ""
    responseData = {}

    
    if not requestData:
        code = 201
        status = False
        message = MSG_CONST.VENDOR_LOGIN_EMPTY_PAYLOAD
    else:
        findUser = {}
        emailPhone = requestData["email_phone"]
        # getUser = DB.find_one(tbl_v003_vendor_users,{"$or":[{"email":emailPhone},{"contact_number":emailPhone}]})
        getUser = DB.find_one(tbl_v003_vendor_users,{"$and":[{"$or":[{"email":emailPhone},{"contact_number":emailPhone}]},{"is_delete":{"$ne":1}}]})
        # print(getUser)

        
        if getUser:
            findVendor = {}
            findVendor["_id"] = ObjectId(getUser["vendor_id"]["$oid"])
            # print(findVendor["_id"])
            notVendor = {"create_by":0,"update_date":0,"update_by":0,"profile_otp":0}
            getVendor = DB.find_one(tbl_v002_vendors,findVendor, notVendor)

            if not getVendor:
                code = 200
                status = False
                message = MSG_CONST.USER_VENDOR_NOT_FOUND
            elif (getVendor["status"] == 3) or  ("is_delete" in getVendor and getVendor["is_delete"] == 1):
                code = 200
                status = False
                message = MSG_CONST.VENDOR_PROFILE_DELETE            
            else:
                
                userObjId = ObjectId(getUser["_id"]["$oid"])
                vendorObjId = ObjectId(getUser["vendor_id"]["$oid"])
                if "password" in getUser and check_password_hash(getUser["password"],requestData["password"]):
                    # Verify email if it is not and using send password method on mail
                    """ if "email_verify" in getUser and getUser["email_verify"] == 0:
                        verifyEmail = DB.update_one(tbl_v003_vendor_users,{"email_verify":1},{"_id":ObjectId(userObjId)}) """
                    responseData = getSession(userObjId, vendorObjId)
                    update_tour_steps = DB.update_one(tbl_v026_tour_steps,{"is_first_login":True},{"vendor_id":vendorObjId})
                    code = 200
                    status = True
                    message = MSG_CONST.VENDOR_LOGIN_SUCCESS
                elif "login_otp" in getUser and  str(getUser["login_otp"]) == str(requestData["password"]):
                    responseData = getSession(userObjId, vendorObjId)
                    update_tour_steps = DB.update_one(tbl_v026_tour_steps,{"is_first_login":True},{"vendor_id":vendorObjId})
                    code = 200
                    status = True
                    message = MSG_CONST.VENDOR_LOGIN_SUCCESS
                else:
                    code = 200
                    status = False
                    message = MSG_CONST.VENDOR_INVALIDE_LOGIN_CRADS
                
        else:
            code = 200
            status = False
            message = MSG_CONST.VENDOR_INVALIDE_LOGIN_CRADS

        
    response = output_json(responseData,message,status,code)
    # print(responseData)
    #logging.debug('vendor_login: {}'.format(response))
    return response

def getSession(user_id, vendor_id):
    is_token_available = DB.find_one(tbl_v003_vendor_users,{'_id':ObjectId(user_id),'security_token':None})
    if is_token_available != None:
        sessionToken = session_token(tbl_v003_vendor_users)
        upd = DB.update_one(tbl_v003_vendor_users,{"login_otp":None,"security_token":str(sessionToken)},{"_id":user_id})

    # Get vendor
    findVendor = {}
    findVendor["_id"] = vendor_id
    notVendor = {"create_by":0,"update_date":0,"update_by":0, "create_by":0,"_id":0,"profile_otp":0,"insert_ip":0,"insert_ip":0,"is_read":0,"insert_date":0}
    getVendor = DB.find_one(tbl_v002_vendors,findVendor, notVendor)
    # print(getVendor)
    if getVendor:
        getVendor["vendor_id"] = str(vendor_id)
        getVendor["authority_user"] = str(getVendor["authority_user"]["$oid"])

    # Get User
    findUser = {}
    findUser["_id"] = user_id
    notUser = {"update_date":0,"update_by":0,"_id":0, "create_by":0, "login_otp":0,"email_otp":0,"contact_otp":0,"profile_otp":0,"password":0}
    getUser = DB.find_one(tbl_v003_vendor_users,findUser, notUser)
    if getUser:
        getUser["vendor_id"] = str(vendor_id)
        getUser["user_id"] = str(user_id)
        if "role" in getUser and getUser["role"] and not isinstance(getUser["role"],str):
            # Get user role data
            getUser["role"] = getUser["role"]["$oid"]
            roleData = role.RoleAccess(getUser["role"],getUser["vendor_id"]).getRoleAccess()
            getUser["role_data"] = roleData
    data = getUser
    data["vendor_data"] = getVendor
    data["subscription"] = subscription.VendorSubscription(str(vendor_id)).getVendorSubscription()
    
    # Get OUTLETS
    check_is_owner = DB.find_one(tbl_v003_vendor_users,{"_id":ObjectId(user_id)},"ALL")
    if 'is_owner' in check_is_owner:
        check_owner = True
    else:
        check_owner = False
    if check_owner == True:
        outletsList = DB.find_by_key(tbl_v004_outlets,{"vendor_id":vendor_id,"is_delete":0},{"_id":1,"name":1,"slugs":1,"area":1,"city":1})
    else:
        find_outlets = DB.find_by_key(tbl_v003_vendor_users,{"_id":ObjectId(user_id),"is_delete":0},{"outlet_id":1})
        outletsList = []
        for x in find_outlets:
            outlet_ids = x['outlet_id']
            for ids in outlet_ids:
                outlet_id = ids['$oid']
                out_id = ObjectId(outlet_id)
                outlets_ids = DB.find_one(tbl_v004_outlets,{"_id":ObjectId(out_id),"is_delete":0},{"_id":1,"name":1,"slugs":1,"area":1,"city":1})
                outletsList.append(outlets_ids)
    if outletsList:
        outlet_data = []
        for x in outletsList:
            y = {}
            y["_id"] = x["_id"]["$oid"]
            if "area" in x and x["area"] != "":
                y["name"] = x["name"] + " - " + x["area"]
            elif "city" in x and x["city"] != "":
                y["name"] = x["name"] + " - " + x["city"]
            else:
                y["name"] = x["name"]
            outlet_data.append(y)
        data["outlets_list"] = outlet_data
    else:
        data["outlets_list"] = []
    
    # Add login history in History table
    if request.headers.get('Device-Id'):
        DB.insert(tbl_a017_history,{"type":"login","user_id":user_id,"vendor_id":vendor_id,"device":get_device_name(request.headers.get('Device-Id')),"ip_address":socket.gethostbyname(socket.gethostname()),"inserted_date":get_current_date(),"desc":"Login successfully"})

    return data

# Vendor Login
def generateLoginOtp(self):
    code = 200
    status = False
    message = MSG_CONST.VENDOR_NOT_FOUND
    responseData = {}
    requestData = request.json
    
    if "phone" not in requestData:
        code = 201
        status = False
        message = MSG_CONST.VENDOR_NOT_FOUND
    else:
        
        if isMobile(requestData["phone"]):
            getUser = DB.find_one(tbl_v003_vendor_users,{"contact_number":str(requestData["phone"])})
            if getUser:
                OTP = genOtp(6, tbl_v003_vendor_users, {}, "login_otp")
                upd = DB.update_one(tbl_v003_vendor_users,{"login_otp":int(OTP)},{"contact_number":str(requestData["phone"])})
                if upd:
                    
                    # Send OTP Payload
                    notificationObject = {}
                    smsObject = {}
                    smsObject["to"] = requestData["phone"]
                    smsObject["template"] = "vendor_otp"
                    smsObject["replace_value1"] = str(OTP)
                    smsObject["replace_value2"] = 'login'
                    smsObject["replace_value3"] = CONST.SMS_VALID
                    
                    notificationObject["sms"] = smsObject
                    res = requests.post(CONST.NOTIFACTION_CLIENT, json=notificationObject)
                    response = dict(res.json())
                    print(response)

                    if "data" in response and "sms" in response["data"]:
                        response = response["data"]["sms"]
                        status = bool(response["status"])
                        message = response["message"]
                        responseData = response["data"]
                    else:
                        code = 201
                        status = False
                        message = MSG_CONST.N_FAILED_TO_SEND_SMS
                else:
                    code = 201
                    status = False
                    message = MSG_CONST.N_TECH_PROB
            else:
                code = 201
                status = False
                message = MSG_CONST.VENDOR_INVALIDE_CONTACT_NUMBER
        else:
            getUser = DB.find_one(tbl_v003_vendor_users,{"email":str(requestData["phone"])})
            
            if getUser:
                email_arr = DB.find_one(tbl_a001_email_template,{'type':'vendor_login_otp_request'},{'title':1})
                OTP = genOtp(6, tbl_v003_vendor_users, {}, "login_otp")
                upd = DB.update_one(tbl_v003_vendor_users,{"login_otp":int(OTP)},{"email":str(requestData["phone"])})
                if upd:
                    notificationObject = {}
                    emailObject = {}
                    emailObject["to"] = [requestData["phone"]]
                    emailObject["template"] = "vendor_login_otp_request"
                    emailObject["replace_value"] = {}
                    emailObject["replace_value"]["OTP"] = str(OTP)
                    emailObject["sender"] = {}
                    emailObject["sender"]["type"] = "SYS"
                    emailObject["sender"]["id"] = "1"
                    emailObject["receiver"] = {}
                    emailObject["receiver"]["type"] = "vendor"
                    emailObject["receiver"]["id"] = "1"
                    sub=email_arr['title'].replace('|OTP|', str(OTP))
                    emailObject["subject"] = sub
                    notificationObject["email"] = emailObject
                    res = requests.post(CONST.NOTIFACTION_CLIENT, json=notificationObject)
                    response = dict(res.json())

                    if "data" in response and "email" in response["data"]:
                        response = response["data"]["email"]
                        status = bool(response["status"])
                        if status == True:
                            # message = response["message"]
                            message = MSG_CONST.VENDOR_EMAIL_LOGIN_OTP
                        else:
                            message = "Failed to send OTP on email"
                        responseData = response["data"]
                    else:
                        code = 201
                        status = False
                        message = MSG_CONST.N_FAILED_TO_SEND_SMS
                else:
                    code = 201
                    status = False
                    message = MSG_CONST.N_TECH_PROB

            else:
                code = 201
                status = False
                message = MSG_CONST.VENDOR_USER_EMAIL_OR_PHONE_VALID

    response = output_json(responseData,message,status,code)
    #logging.debug('user_generate_otp: {}'.format(response))
    return response

def checkUserLogin(self):
       
    code = 201
    status = False
    message = MSG_CONST.VENDOR_CONTACT_EMPTY
    responseData = {}

    requestData = dict(request.json)
    
    if "email_phone" in requestData and requestData["email_phone"] != "":
        emailPhone = requestData["email_phone"]
        getUser = DB.find_one(tbl_v003_vendor_users,{"$or":[{"email":emailPhone},{"contact_number":emailPhone}]},{"_id":1})
        
        if getUser:
            code = 200
            status = True
            message = MSG_CONST.VENDOR_USER_EMAIL_OR_PHONE_VALID
        else:
            code = 200
            status = False
            message = MSG_CONST.VENDOR_USER_EMAIL_OR_PHONE_ARE_NOT_VALID
    else:
        code = 200
        status = True
        message = MSG_CONST.VENDOR_EMAIL_OR_PHONE_EMPTY

    response = output_json(responseData,message,status,code)
    #logging.debug('user_generate_otp: {}'.format(response))
    return response

def sendVerificationLink(self):
    code = 201
    status = False
    message = MSG_CONST.VENDOR_CONTACT_EMPTY
    responseData = {}
    
    if request.args.get("vendor_id") and request.args.get("user_id"):
        vendor_id = ObjectId(request.args.get("vendor_id"))
        user_id = ObjectId(request.args.get("user_id"))
        vendor_data = DB.find_one(tbl_v002_vendors,{"_id":vendor_id},{"email":1,"email_verify":1})
        userData = DB.find_one(tbl_v003_vendor_users,{"_id":user_id},{"name":1})
        if vendor_data:
            if vendor_data["email_verify"] == 0:
                email_verify_code = uniqueString(30)
                verifyLink = CONST.VENDOR_WEB + 'login/verify_verification_email_vendor/' + email_verify_code

                notificationObject = {}
                emailObject = {}
                emailObject["to"] = [vendor_data["email"]]
                emailObject["template"] = "vendor_send_email_verify"
                emailObject["replace_value"] = {}
                emailObject["replace_value"]["user_name"] = userData["name"].capitalize()
                emailObject["replace_value"]["link"] = verifyLink
                emailObject["sender"] = {}
                emailObject["sender"]["type"] = "vendor"
                emailObject["sender"]["id"] = request.args.get("user_id")
                emailObject["receiver"] = {}
                emailObject["receiver"]["type"] = "vendor"
                emailObject["receiver"]["id"] = request.args.get("user_id")
                emailObject["subject"] = "Wellnessta - Verification vendor email"
                notificationObject["email"] = emailObject
                res = requests.post(CONST.NOTIFACTION_CLIENT, json=notificationObject)
                responseData = dict(res.json())
                if "status" in responseData and responseData["status"]:
                    upd = DB.update_one(tbl_v002_vendors,{"email_verify_code":email_verify_code},{"_id":vendor_id})
                    code = 200
                    status = True
                    message = MSG_CONST.VENDOR_EMAIL_VERIFICATION_MAIL_SEND_SUCCESS.replace("email", "email "+vendor_data["email"])
                else:
                    code = 200
                    status = False
                    message = MSG_CONST.N_FAILED_TO_SEND_EMAIL
            else:
                code = 200
                status = True
                message = MSG_CONST.VENDOR_EMAIL_ALREDY_VERIFIED
        else:
            code = 200
            status = False
            message = MSG_CONST.VENDOR_INVALID_ID
    else:
        code = 200
        status = False
        message = MSG_CONST.VENDOR_INVALID_ID

    response = output_json(responseData,message,status,code)
    #logging.debug('vendor_verify_email_request: {}'.format(response))
    return response

def vendorEmailVarification(self):
    code = 201
    status = False
    message = MSG_CONST.VENDOR_CONTACT_EMPTY
    responseData = {}
    
    # todayDate = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    todayDate = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    ip_address = socket.gethostbyname(socket.gethostname())
    requestData = dict(request.json)
    
    if "code" in requestData and requestData["code"]:
        vendorData = DB.find_one(tbl_v002_vendors,{"email_verify_code":requestData["code"]},{"_id":1,"business_name":1,"email":1,"authority_user":1,"contact_person":1})
        
        if vendorData:
            updateData = {}
            updateData["email_verify"] = 1
            updateData["update_date"] = todayDate
            updateData["update_id"] = ip_address
            updateData["email_verify_code"] = ""
            updateFlag = DB.update_one(tbl_v002_vendors,updateData,{"email_verify_code":requestData["code"]})

            if updateFlag:
                code = 200
                status = True
                message = MSG_CONST.VENDOR_EMAIL_VERIFIE_SUCCESS
            else:
                code = 200
                status = False
                message = MSG_CONST.VENDOR_EMAIL_VERIFIE_FAILED
        else:
            code = 200
            status = False
            message = MSG_CONST.VENDOR_EMAIL_VERIFIE_FAILED
    else:
        code = 200
        status = False
        message = MSG_CONST.VENDOR_INVALID_ID

    response = output_json(responseData,message,status,code)
    #logging.debug('vendor_verify_email_process: {}'.format(response))
    return response

# Vendor logout request
def logout_request(self):
    # Add login history in History table
    if request.headers.get('Vendor-User-Id') and request.headers.get('Device-Id') and request.headers.get('Vendor-Id'):
        DB.insert(tbl_a017_history,{"type":"logout","user_id":ObjectId(request.headers.get('Vendor-User-Id')),"vendor_id":ObjectId(request.headers.get('Vendor-Id')),"device":get_device_name(request.headers.get('Device-Id')),"ip_address":socket.gethostbyname(socket.gethostname()),"inserted_date":get_current_date(),"desc":"Logout successfully"})
    return output_json({},"logout success",True)
