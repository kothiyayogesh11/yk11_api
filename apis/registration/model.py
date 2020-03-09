""" 
Created By : Yogesh Kothiya
Date : 2019-09-09
Use : All before login action
"""
from flask_restplus import Namespace, fields
import socket
import time
from datetime import datetime, date, time, timedelta
from dateutil.relativedelta import relativedelta
from flask import jsonify, request
from database import DB
from bson import json_util, ObjectId
import apis.utils.role as role
from apis.utils.common import output_json, random_n_digits, genOtp, validEmail, isMobile, uniqueString
# from apis.libraries.send_mail import Send_mail
import requests
import logging
import re
import apis.utils.message_constants as MSG_CONST
import apis.utils.constants as CONST
import apis.utils.subscription as subscription
from werkzeug.security import generate_password_hash, check_password_hash
import dateutil
import random
import string

#logging.basicConfig(filename='vendor.log', level=logging.DEBUG)   

# Declare tables name in vars
tbl_v002_vendors        = "v002_vendors"
tbl_v003_vendor_users   = "v003_vendor_users"
tbl_a005_otp_verify     = "a005_otp_verify"
tbl_v004_outlets        = "v004_outlets"
tbl_v026_tour_steps = "v026_tour_steps"
tbl_v027_newsletter = "v027_newsletter"
tbl_v017_modules = "v017_modules"
tbl_v018_module_access="v018_module_access"
tbl_a001_email_template="a001_email_template"


# Declare Models
def vendorModel(self,ns):
    RegistrationModel = ns.model('RegistrationModel', {
        '_id': fields.String(required=False, description='Post Title'),
        'business_name': fields.String(required=True, min_length=1, description='Business Name is empty'),
        'contact_number': fields.String(required=True, min_length=10, max_length=13, description='contact number'),
        'contact_person':fields.String(required=True, min_length=2, max_length=180, description='contact person name'),
        'email': fields.String(required=True, description='Email address'),
        'address1': fields.String(required=True, min_length=4, description='Head office address'),
        'city': fields.String(required=True, description='City name'),
        'state': fields.String(required=True, description='State name'),
        'country': fields.String(required=True, description='Country name'),
        'latitude': fields.String(required=False, description='latitude of business location'),
        'longitude': fields.String(required=False, description='longitude of business location'),
        'business_type' : fields.String(required=False, description='Tye of Business')
    })
    return RegistrationModel

def contactPersonOtp(self, ns):
    contactPersonOtp = ns.model('contactPersonOtp', {
        'contact_number': fields.String(required=True, min_length=10, max_length=10, description='Business contact person number')
    })
    return contactPersonOtp

def verifyEmail(self,ns):
    verify = ns.model('verifyEmailModel', {
        'otp': fields.Integer(required=True, description='Email otp is required'),
        'password': fields.String(required=True, min_length=4, description='Password otp is required')
    })
    return verify

def forgotPassword(self,ns):
    ForgotPassword = ns.model('ForgotPassword', {
        'otp': fields.String(required=True, description='Unique key is empty'),
        'password':fields.String(required=True, description="Password should not empty")
    })
    return ForgotPassword

def addRole(roleId=None, vendorId=None,userId=None):
    print("vendor_id -- add Role table")
    role.RoleAccess(roleId, str(vendorId), userId).addDefaultRolePerminssion()
    return True

# Declare all methods which perform action on routs request
def add_user(vendorData):
    data = {}
    # todayDate               = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    todayDate = datetime.now().strftime('%Y-%m-%d')    
    expiry_date = datetime.now() + timedelta(days=30)
    nextMonth = datetime.strftime(expiry_date,'%Y-%m-%d')
    # nextMonth               = datetime.today()+ relativedelta(months=1)
    # nextMonth               = nextMonth.strftime('%Y-%m-%d %H:%M:%S')
    user_id                 = None  #DB.find_max_id(tbl_v003_vendor_users, "user_id")
    vendor_id               = vendorData["vendor_id"]
    contact_number          = vendorData["contact_number"].replace(" ","")
    contact_number          = contact_number.replace("+","")
    
    data["user_id"]         = user_id
    data["vendor_id"]       = vendor_id
    data["name"]            = vendorData["contact_person"]
    data["contact_number"]  = contact_number
    data["contact_verify"]  = 0; #int(vendorData["contact_verify"])
    data["contact_otp"]     = vendorData["contact_otp"]
    data["email"]           = vendorData["email"]
    data["email_verify"]    = 0
    data["email_otp"]       = vendorData["email_otp"]
    data["profile_picture"] = None
    data["is_owner"] = True
    roleId = None
    if "role" in vendorData and vendorData["role"]:
        data["role"]        = vendorData["role"]
        roleId              = vendorData["role"]
    else:
        roleId              = "5e326741d5acf5158e1c0b2d"
        data["role"]        = ObjectId("5e326741d5acf5158e1c0b2d")
        # roleId              = "5da6e4619bbd1d2faab37184"
        # data["role"]        = ObjectId("5da6e4619bbd1d2faab37184")
        
    
    data["is_delete"] = 0
    data["update_date"] = todayDate
    
    ip_address = socket.gethostbyname(socket.gethostname())
    addUser = DB.insert(tbl_v003_vendor_users,data)
    if addUser:
        get_modules = DB.find_all_where(tbl_v017_modules,{"status":1,"is_menu":0},'ALL')
        for x1 in get_modules:
            data2={}
            data2["vendor_id"] = ObjectId(addUser)
            data2["vendor_email"] = vendorData["email"]
            data2["module_id"] = ObjectId(x1["_id"]['$oid'])
            data2["module_name"] = x1["name"]
            data2['access'] =  True
            data2['access_type'] =  'write'
            data2['is_delete'] =  0
            data2["insert_by"] = ObjectId(addUser)
            data2["insert_date"] = todayDate
            data2["insert_ip"] = ip_address
            module_data = DB.insert(tbl_v018_module_access,data2)
        # addRole(roleId, vendor_id,addUser)
        upd = DB.update_one(tbl_v003_vendor_users,{"create_by":ObjectId(addUser)},{"_id":ObjectId(addUser)})
        upd = DB.update_one(tbl_v002_vendors,{"authority_user":ObjectId(addUser)},{"_id":ObjectId(vendor_id)})
        return addUser
    else:
        return False
    # if addUser:
    #     addRole(roleId, vendor_id,addUser)
    #     upd = DB.update_one(tbl_v003_vendor_users,{"create_by":ObjectId(addUser)},{"_id":ObjectId(addUser)})
    #     upd = DB.update_one(tbl_v002_vendors,{"authority_user":ObjectId(addUser)},{"_id":ObjectId(vendor_id)})
    #     subData = {}
    #     subData["vendor_id"] = str(vendor_id)
    #     subData["user_id"] = str(addUser)
    #     subData["plan_id"] = "5dd2651ae43f471c21403eee"
    #     subData["price"] = 0.00
    #     subData["tax"]  = 0.00
    #     subData["tot_price"] = 0.00
    #     subData["txn_id"] = ""
    #     subData["payment_type"] = "no_payment"
    #     subData["payment_status"] = 1
    #     subData["payment_date"] = todayDate
    #     subData["type"] = "vendor"
    #     subData["expiry_date"] = nextMonth
    #     subData["start_date"] = todayDate
    #     subData["status"] = 1
    #     subData["created_date"] = todayDate
    #     addSub = subscription.VendorSubscription(str(vendor_id),str(user_id)).addMemberShip(subData)
    #     return addUser
    # else:
    #     return False

def save_vendor(self):
    status = True
    message = ""
    code = 200
    responseData = {}
    # todayDate = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    todayDate = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    todayDate_dis = datetime.now().strftime('%d,%b %Y')
    # Get max vendor ID
    vendor_id = None # DB.find_max_id(tbl_v002_vendors, "vendor_id")

    # Auto set
    data = dict(request.json)
    # print(data)
    requestData = request.json

    contact_number = data["contact_number"].replace(" ","")
    contact_number = contact_number.replace("+","")
    data["contact_number"] = contact_number
    
    if validEmail(data["email"]) == False:
        status = False
        message = MSG_CONST.VENDOR_PROVIDE_VALID_EMAIL
        code = 202
        response = output_json(responseData,message,status,code)
        #logging.debug('vendor_save: {}'.format(response))
        return response
    
    emailOtp = genOtp(6,tbl_v002_vendors,{},"email_otp")
    accountId = genOtp(6,tbl_v002_vendors,{},"account_id")
    OTP = genOtp(6, tbl_a005_otp_verify, {}, "profile_otp")
    
    data["account_id"] = accountId
    data["vendor_id"] = vendor_id
    data["email_verify"]    = 0
    data["profile_otp"] = emailOtp
    # data["create_by"] = vendor_id
    data["insert_ip"]   = socket.gethostbyname(socket.gethostname())
    data["insert_date"] = todayDate
    data["update_date"] = todayDate
    # data["update_by"] = vendor_id
    # data["is_delete"] = 0
    data["status"] = 4
    #Check email already exists
    if DB.find_by_key(tbl_v002_vendors,{"$and":[{"email":data["email"]},{"status":{"$ne":3}}]}):
        status = False
        message = MSG_CONST.VENDOR_SAVE_EMAIL_EXISTS
        code = 202
    elif DB.find_by_key(tbl_v002_vendors,{"$and":[{"contact_number":data["contact_number"]},{"status":{"$ne":3}}]}):
        status = False
        message = MSG_CONST.VENDOR_SAVE_CONTACT_EXISTS
        code = 202
    
    checkUser = DB.find_one(tbl_v003_vendor_users,{"$and":[{"email":data["email"]},{"is_delete":{"$ne":1}}]})
    if checkUser:
        status = False
        message = MSG_CONST.VENDOR_SAVE_EMAIL_EXISTS
        code = 202
        response = output_json(responseData,message,status,code)
        #logging.debug('vendor_save: {}'.format(response))
        return response
        
    # Check Contact already exists
    if status == True:
        
        data["is_read"] = 0

        # Referral code 
        refer_by_user =None
        if 'refral_code' in data and data['refral_code'] != '' and data['refral_code'] != None:
            refer_by_user = DB.find_one(tbl_v002_vendors,{'referral_code':data['refral_code']})
            if refer_by_user == None:
                return output_json({},MSG_CONST.REF_CODE_NOT_FOUND,False)
            else:
                #send email to vendor
                email_arr = DB.find_one(tbl_a001_email_template,{'type':'vendor_refferal_signup'},{'title':1})
                notificationObject = {}
                emailObject = {}
                emailObject["to"] = [refer_by_user["email"]]
                emailObject["template"] = "vendor_refferal_signup"
                emailObject["replace_value"] = {}
                emailObject["replace_value"]["user_name"] = refer_by_user["contact_person"].capitalize()
                emailObject["replace_value"]["user_name2"] = data['contact_person'].capitalize()
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

        data["referral_by"] = None
        if refer_by_user != None:
            data["referral_by"] = ObjectId(refer_by_user['_id']['$oid'])
        data["referral_code"] = randomStringDigits()

        # check if referral code exists
        
        is_referral_code_exist = DB.find_one(tbl_v002_vendors,{'referral_code':data["referral_code"]})
        if is_referral_code_exist != None:
            data["referral_code"] = randomStringDigits()
        data["referral_used"] = False
        
        del data['refral_code']
        insertId = DB.insert(tbl_v002_vendors,data)
        
        inert_tour_steps = DB.insert(tbl_v026_tour_steps,{"vendor_id":ObjectId(insertId),"is_first_time":False,"status":0,"created_date":todayDate,"is_active_account" : False,"setup_role": False,"setup_account" : False,"setup_docs" : False,"setup_outlet" : False,"setup_service" : False,"setup_staff" : False,"setup_offers" : False,"setup_booking" : False,"is_membership_buy" : False,"setup_offer":False,"is_first_login":False,"setup_accomodation":False})
        if insertId != "":
            vendorObjId = ObjectId(insertId)
            updateCreated = DB.update_one(tbl_v002_vendors,{"create_by":vendorObjId},{"_id":vendorObjId})
            data["vendor_id"] = vendorObjId
            data["contact_verify"] = 0
            data["email_verify"] = 0
            data["email_otp"] = emailOtp
            data["contact_otp"] = OTP

            # Add user
            addUser = add_user(data)

            # Add outlet
            if addUser:
                userObjId = ObjectId(addUser)
                data["user_id"] = userObjId
                # add_outlet(self,data)
            
            
            responseData["vendorId"] = str(vendorObjId)
            message = MSG_CONST.VENDOR_SAVE_SUCCESS
            status = True
            code = 200
            verifyLink = CONST.VENDOR_WEB+"email-set-password/"+str(emailOtp)

            
            email_arr = DB.find_one(tbl_a001_email_template,{'type':'vendor_register'},{'title':1})
            #send email to vendor
            notificationObject = {}
            emailObject = {}
            emailObject["to"] = [requestData["email"]]
            emailObject["template"] = "vendor_register_prelaunch"
            emailObject["replace_value"] = {}
            emailObject["replace_value"]["link"] = verifyLink
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
            
            #to admin
            
            if requestData["business_type"]=='massage_and_spa':
                business_name="Massage and spa"
            elif requestData["business_type"]=='meditation_services':
                business_name="Meditation services"                 
            elif requestData["business_type"]=='naturopathy':
                business_name="Naturopathy"                 

            email_arr = DB.find_one(tbl_a001_email_template,{'type':'admin_new_vendor_registered'},{'title':1})
            notificationObject = {}
            emailObject = {}
            emailObject["to"] = [CONST.ADMIN_EMAIL]
            emailObject["template"] = "admin_new_vendor_registered"
            emailObject["replace_value"] = {}
            emailObject["replace_value"]["date"] = todayDate_dis
            emailObject["replace_value"]["business_name"] = requestData["business_name"]
            emailObject["replace_value"]["business_category"] = business_name
            emailObject["replace_value"]["link"] = CONST.ADMIN_WEB+'vendors/Vendordetails?vendor_id='+str(vendorObjId)
            emailObject["sender"] = {}
            emailObject["sender"]["type"] = "SYS"
            emailObject["sender"]["id"] = ""
            emailObject["receiver"] = {}
            emailObject["receiver"]["type"] = "admin"
            emailObject["receiver"]["id"] = ""
            emailObject["subject"] = email_arr['title']
            notificationObject["email"] = emailObject
            
            res = requests.post(CONST.NOTIFACTION_CLIENT, json=notificationObject)
            response = dict(res.json())
            
            # Send OTP Payload
            notificationObject = {}
            smsObject = {}
            smsObject["to"] = contact_number
            smsObject["template"] = "vendor_otp"
            smsObject["replace_value1"] = str(OTP)
            smsObject["replace_value2"] = 'verification process'
            smsObject["replace_value3"] = CONST.SMS_VALID
            
            notificationObject["sms"] = smsObject
            res = requests.post(CONST.NOTIFACTION_CLIENT, json=notificationObject)
            response = dict(res.json())
            
        else:
            message = MSG_CONST.VENDOR_SAVE_FAILED
            status = False  
            code = 201

    response = output_json(responseData,message,status,code)
    #logging.debug('vendor_save: {}'.format(response))
    return response

# def add_outlet(self, outletData):
#     if outletData:
#         todayDate = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
#         # Get max vendor ID
#         outlet_id = None #DB.find_max_id(tbl_v004_outlets, "outlet_id")
#         data = {}
#         data["outlet_id"]       = outlet_id
#         data["vendor_id"]       = outletData["vendor_id"]
#         data["user_id"]         = outletData["user_id"]
#         data["name"]            = outletData["business_name"]
#         data["slugs"]           = re.sub(r"\s+", '-', outletData["business_name"].lower())
#         data["category_id"]     = ObjectId("5d8c901e60d793434cd62b03")
#         data["contact_number"]  = outletData["contact_number"]
#         data["address"]         = outletData["address1"]
#         data["city"]            = outletData["city"].lower()
#         data["state"]           = outletData["state"]
#         data["country"]         = outletData["country"]
#         data["status"]          = 0
#         data["insert_by"]       = outletData["user_id"]
#         data["is_delete"]       = 0
#         data["insert_date"]     = todayDate
#         data["service_count"]   = 1
#         data["staff_count"]     = 1
#         data["is_read"]         = 0
#         data["is_document"]     = 0
#         data["business_type"]=outletData["business_type"]
#         # data["spa_type"]=outletData["spa_type"]
#         return DB.insert(tbl_v004_outlets,data)

# Verify registration email
def verify_email(self):
    requestData = request.json
    # todayDate = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    todayDate = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    responseData = {}
    
    if "otp" not in requestData:
        message = MSG_CONST.VENDOR_EXPIRED_LINK
        status = False
        code = 201
    else:

        otp = requestData["otp"]
        getVendor = DB.find_one(tbl_v002_vendors,{"profile_otp":otp})
        
        if getVendor and "profile_otp" in getVendor and "authority_user" in getVendor:

            authId = getVendor["authority_user"]["$oid"]
            
            
            password = generate_password_hash(requestData['password'])
            setPass = {"password":password,"update_by":ObjectId(authId),"email_verify":1,"email_otp":None,"update_date":todayDate}
            updatePassword = DB.update_one(tbl_v003_vendor_users,setPass,{"_id":ObjectId(authId)})
            if updatePassword:
                
                setVal = {"profile_otp":None,"email_verify":1,"update_date":todayDate,"update_by":ObjectId(authId)}
                where = {"profile_otp":otp,"_id":ObjectId(getVendor["_id"]["$oid"])}
                
                response = DB.update_one(tbl_v002_vendors,setVal,where)
                
                if response:
                    responseData["email"] = getVendor["email"]
                    message = MSG_CONST.VENDOR_EMAIL_VERIFY_BUSINESS
                    status = True
                    code = 200
            else:
                message = MSG_CONST.N_TECH_PROB
                status = False
                code = 201
        else:
            message = MSG_CONST.VENDOR_EXPIRED_LINK
            status = False
            code = 201
    
    response = output_json(responseData,message,status,code)
    #logging.debug('vendor_verify_email: {}'.format(response))
    return response

# verify_contact
def verify_contact(self,otp):
    responseData = {}
    if not otp:
        message = "Invalide contact number."
        status = False
        code = 200
    else:
        getVendor = DB.find_one(tbl_v002_vendors,{"conatct_otp":otp})
        if getVendor and "conatct_otp" in getVendor:
            setVal = {"conatct_otp":None,"contact_verify":1,"update_date":datetime.now(),"update_by":ObjectId(getVendor["_id"]["$oid"])}
            where = {"conatct_otp":otp,"_id":ObjectId(getVendor["_id"]["$oid"])}
            response = DB.update_one(tbl_v002_vendors,setVal,where)
            if response:
                message = "Your contact number has been verified successfully."
                status = True
                code = 200
            else:
                message = "Failed to update"
                status = False
                code = 201
        else:
            message = "Undefined link."
            status = False
            code = 201
    response = output_json(responseData,message,status,code)
    #logging.debug('vendor_verify_person_contact: {}'.format(response))
    return response

# Generate Contact person OTP

def generate_contact_person_otp(self):
    
    requestData = request.json
    message = "Failed to send OTP"
    status = False
    code = 200
    responseData = {}

    if "contact_number" in requestData:

        getUser = DB.find_one(tbl_v003_vendor_users,{"contact_number":requestData["contact_number"]})


        if not getUser:
            code = 200
            status = False
            message = MSG_CONST.VENDOR_INVALIDE_CONTACT_NUMBER
        elif getUser["is_delete"] == 1:
            code = 200
            status = False
            message = MSG_CONST.VENDOR_PROFILE_DELETE
        else:

            OTP = genOtp(6, tbl_v003_vendor_users, {}, "contact_otp")
            ins = DB.update_one(tbl_v003_vendor_users,{"contact_otp":int(OTP)},{"contact_number":requestData["contact_number"]})
            if ins:
                # Send OTP Payload
                notificationObject = {}
                smsObject = {}
                smsObject["to"] = requestData["contact_number"]
                smsObject["template"] = "vendor_otp"
                smsObject["replace_value1"] = str(OTP)
                smsObject["replace_value2"] = 'verification process'
                smsObject["replace_value3"] = CONST.SMS_VALID
                
                notificationObject["sms"] = smsObject
                res = requests.post(CONST.NOTIFACTION_CLIENT, json=notificationObject)
                response = dict(res.json())

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
        message = MSG_CONST.VENDOR_CONTACT_EMPTY

    response = output_json(responseData,message,status,code)
    #logging.debug('vendor_verify_contact: {}'.format(response))
    return response

# Verify contact person number
def verify_contact_person_number(self):
    responseData = {}
    otp = request.args.get("otp")
    
    if not otp:
        message = "Provide valid code"
        status = False
        code = 201
    else:
        getOTP = DB.find_one(tbl_v003_vendor_users,{"contact_otp":int(otp)})
        
        if getOTP and "contact_otp" in getOTP:
            upd = DB.update_one(tbl_v003_vendor_users,{"contact_otp":None,"contact_verify":1},{"_id":ObjectId(getOTP["_id"]["$oid"])})
            message = MSG_CONST.VENDOR_PROFILE_CREATED # "Your contact number has been verified successfully."
            status = True
            code = 200
        else:
            message = "Invalid code provided"
            status = False
            code = 201
    response = output_json(responseData,message,status,code)
    #logging.debug('vendor_verify_contact: {}'.format(response))
    return response

# forgot_password send request for email link
def forgot_password_request(self):
    data = request.json
    responseData = {}
    getUser = None

    uniquePass = uniqueString(10)
    
    if "email" in data and data["email"] != "":
        if isMobile(data["email"]):
            getUser = DB.find_one(tbl_v003_vendor_users,{"contact_number":data["email"],"is_delete":0})
        else:
            getUser = DB.find_one(tbl_v003_vendor_users,{"email":data["email"],"is_delete":0})
        
        if not getUser:
            if isMobile(data["email"]):
                message = MSG_CONST.VENDOR_INVALIDE_CONTACT_NUMBER
            else:
                message = MSG_CONST.VENDOR_INVALIDE_EMAIL
            status = False
            code = 201
        else:
            # Send mail code
            # uniquePass = genOtp(6,tbl_v003_vendor_users,{"user_id":getUser["user_id"],"email_otp":0})
            updateOtp = DB.update_one(tbl_v003_vendor_users, {"password":generate_password_hash(uniquePass)},{"_id":ObjectId(getUser["_id"]["$oid"])})
            if not updateOtp:
                message = MSG_CONST.N_TECH_PROB
                status = False
                code = 200
            else:
                notificationObject = {}
                if isMobile(data["email"]):
                    # Send OTP Payload
                    notificationObject = {}
                    smsObject = {}
                    smsObject["to"] = data["email"]
                    smsObject["template"] = "forget_password"
                    smsObject["replace_value1"] = str(uniquePass)
                    smsObject["replace_value2"] = 'Wellnessta'
                    notificationObject["sms"] = smsObject
                    res = requests.post(CONST.NOTIFACTION_CLIENT, json=notificationObject)
                    response = dict(res.json())
                else:
                    email_arr = DB.find_one(tbl_a001_email_template,{'type':'vendor_forgot_password'},{'title':1})
                    notificationObject = {}
                    emailObject = {}
                    emailObject["to"] = [data["email"]]
                    emailObject["template"] = "vendor_forgot_password"
                    emailObject["replace_value"] = {}
                    emailObject["replace_value"]["user_name"] = getUser["name"].capitalize()
                    emailObject["replace_value"]["pass"] = str(uniquePass)
                    emailObject["sender"] = {}
                    emailObject["sender"]["type"] = "SYS"
                    emailObject["sender"]["id"] = "1"
                    emailObject["receiver"] = {}
                    emailObject["receiver"]["type"] = "vendor"
                    emailObject["receiver"]["id"] = "1"
                    emailObject["subject"] = email_arr['title']
                    notificationObject["email"] = emailObject

                res = requests.post(CONST.NOTIFACTION_CLIENT, json=notificationObject)
                res = res.json()
                if("status" in res and res["status"]):
                    if "email" in res["data"] and res["data"]["email"]["data"] and "message" in res["data"]["email"]["data"]:
                        res["data"]["email"]["data"]["message"] = ""

                    elif "sms" in res["data"] and res["data"]["sms"]["data"] and "message" in res["data"]["sms"]["data"]:
                        res["data"]["sms"]["data"]["message"] = ""

                    responseData = res["data"]
                    message = res["message"]
                    status = res["status"]
                    code = 200
                else:
                    responseData = {}
                    message = MSG_CONST.N_FAILED_TO_SEND_EMAIL
                    status = False
                    code = 201
    else:
        message = MSG_CONST.VENDOR_PROVIDE_VALID_EMAIL
        status = False
        code = 201
        responseData = {}
    
    response = output_json(responseData,message,status,code)
    #logging.debug('forgot_password_request: {}'.format(response))
    return response

# forgot_password update
def forgot_password(self):

    message = "Your link has been expired."
    status = False
    code = 201
    responseData = {}

    requestData = request.json
    userData = DB.find_one(tbl_v003_vendor_users,{"email_otp":int(requestData["otp"])})
    
    if not userData or int(requestData["otp"]) == 0:
        message = "Your link has been expired."
        status = False
        code = 201
        responseData = {}
    elif "password" in requestData and requestData["password"] != "":
        data = {}
        data["password"] = generate_password_hash(requestData['password'])
        updateData = {"password":data["password"],"email_otp":None,"update_by":ObjectId(userData["_id"]["$oid"])}
        updateWhere = {"email_otp":int(requestData["otp"]),"_id":ObjectId(userData["_id"]["$oid"])}
        update = DB.update_one(tbl_v003_vendor_users,updateData,updateWhere)

        if not update:
            message = MSG_CONST.N_TECH_PROB
            status = False
            code = 201
            responseData = {}
        else:
            message = MSG_CONST.VENDOR_SUCCESS_UPDATE_PASSWORD
            status = True
            code = 200
            responseData = {}
    else:
        message = "Your password is empty, please provide password to update"
        status = False
        code = 201
        responseData = {}
    response = output_json(responseData,message,status,code)
    #logging.debug('forgot_password: {}'.format(response))
    return response




def tour_steps(self):
    code = 201
    status = False
    message = ""
    responseData = {}
    requestData = dict(request.json)
    # print(requestData)
    # print(requestData['data'][0])
    requestData['data'][0]["vendor_id"] = ObjectId(requestData['data'][0]["vendor_id"])
    todayDate =  todayDate = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    ip_address = socket.gethostbyname(socket.gethostname())
    find_tour_steps = DB.find_one(tbl_v026_tour_steps,{"vendor_id":requestData['data'][0]['vendor_id']})
    if find_tour_steps:
        update_tour_steps = DB.update_one(tbl_v026_tour_steps,requestData['data'][0],{"vendor_id":requestData['data'][0]['vendor_id']})
        if update_tour_steps:
            message = "Subscription Updated Succesfully"
            status = True
            code = 200
            responseData = {}
        else:
            message = "Sorry, Something Went Wrong1"
            status = False
            code = 201
            responseData = {}
    else:
        message = "Sorry, Something Went Wrong2"
        status = False
        code = 201
        responseData = {}
    
    response = output_json(responseData,message,status,code)
    #logging.debug('tour_steps: {}'.format(response))
    return response


def get_tour_steps(self,vendor_id):
    code = 201
    status = False
    message = ""
    responseData = {}
    # data = {}
    todayDate =  todayDate = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    ip_address = socket.gethostbyname(socket.gethostname())
    
    Gettour_steps = DB.find_one(tbl_v026_tour_steps,{"vendor_id":ObjectId(vendor_id)},"ALL")
    
    if Gettour_steps:
        message = "get tour details successfully"
        status = True
        code = 200
        responseData = {}
    else:
        message = "Sorry, Something Went Wrong"
        status = False
        code = 201
        responseData = {}
    
    response = output_json(Gettour_steps,message,status,code)
    #logging.debug('get_tour_steps: {}'.format(response))
    return response



def insert_newsletter(self):
    code = 201
    status = False
    message = ""
    requestData = dict(request.json)
    
    data = {}
    todayDate = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    ip_address = socket.gethostbyname(socket.gethostname())
    data["email"] = requestData['email']
    data["created_date"] = todayDate
    data["page_referance"] = requestData['page_referance']
    data["type"] = requestData['type']
    data['status'] =  0
    data["inserted_ip"] = ip_address
    module_data = DB.insert(tbl_v027_newsletter,data)

    if module_data:
        # Send e-mail
        email_arr = DB.find_one(tbl_a001_email_template,{'type':'subscribe_success'},{'title':1})
        notificationObject = {}
        emailObject = {}
        emailObject["to"] = [requestData['email']]
        emailObject["template"] = "subscribe_success"
        emailObject["replace_value"] = {}
        emailObject["replace_value"]["user_name"] = requestData['email']
        emailObject["sender"] = {}
        emailObject["sender"]["type"] = "SYS"
        emailObject["sender"]["id"] = "1"
        emailObject["receiver"] = {}
        emailObject["receiver"]["type"] = "vendor"
        emailObject["receiver"]["id"] = "1"
        emailObject["subject"] = email_arr['title']
        notificationObject["email"] = emailObject
        res = requests.post(CONST.NOTIFACTION_CLIENT, json=notificationObject)
        response1 = dict(res.json())
        code = 200
        status = True
        message = "Data Inserted Successfully..!"
    else:
        data=[]
        code = 201
        status = False
        message = "Sorry, something went wrong..!"

    response = output_json(code,message,status,data)
    #logging.debug('insert_newsletter: {}'.format(response))
    return response



def change_password(self):
    status = True
    message = ""
    code = 201
    responseData = {}
    requestData = dict(request.json)
    todayDate = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    find_password = DB.find_one(tbl_v003_vendor_users,{"_id":ObjectId(requestData['user_id'])},{"password":1})
    get_password = find_password['password']
    
    check_password = check_password_hash(get_password,requestData["old_password"])
    if (check_password):
        update_passowrd = DB.update_one(tbl_v003_vendor_users,{"password":generate_password_hash(requestData['new_password'])},{"_id":ObjectId(requestData['user_id'])})
        if update_passowrd:
            code = 200
            status = True
            message = MSG_CONST.VENDOR_SUCCESS_UPDATE_PASSWORD
        else:
            code = 201
            status = False
            message = MSG_CONST.VENDOR_FAILED_UPDATE_PASSWORD    
    else:
        code = 201
        status = True
        message = MSG_CONST.VENDOR_INVALID_OLD_PASSWORD
    response = output_json(code,message,status,responseData)
    #logging.debug('change_password: {}'.format(response))
    return response


def delete_account(self):
    status = True
    message = ""
    code = 201
    responseData = {}
    Data = {}
    requestData = dict(request.json)
    ip_address = socket.gethostbyname(socket.gethostname())
    todayDate = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    Data['is_delete'] = int(1)
    Data['status'] = int(3)
    Data['deleted_by'] = ObjectId(requestData['user_id'])
    Data['deleted_date'] = todayDate
    Data['deleted_ip'] = ip_address
    
    
    find_password = DB.find_one(tbl_v003_vendor_users,{"_id":ObjectId(requestData['user_id'])})
    
    if find_password:
        delete_user = DB.update_one(tbl_v003_vendor_users,Data,{"_id":ObjectId(requestData['user_id'])})
        delete_vendor = DB.update_one(tbl_v002_vendors,Data,{"_id":ObjectId(requestData['vendor_id'])})
        status = True
        message = "Account has been Deleted Successfully..!"
        code = 200
    else:
        status = False
        message = "Something went wrong..!"
        code = 201
        
    response = output_json(code,message,status,responseData)
    #logging.debug('delete_account: {}'.format(response))
    return response

def randomStringDigits(stringLength=6):
    """Generate a random string of letters and digits """
    lettersAndDigits = string.ascii_letters + string.digits
    return ''.join(random.choice(lettersAndDigits) for i in range(stringLength))