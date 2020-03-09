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
#logging.basicConfig(filename='logd/vendor.log', level=logging.DEBUG)   

# Declare tables name in vars
tbl_v002_vendors = "v002_vendors"
tbl_v003_vendor_users = "v003_vendor_users"
tbl_v006_service_category = "v006_service_category"
tbl_v007_services_master = "v007_services_master"
tbl_v026_tour_steps = 'v026_tour_steps'
tbl_a017_history = "a017_history"
tbl_a001_email_template = 'a001_email_template'

def updateModel(self,ns):
    updateProfile = ns.model('updateModel', {
        # 'vendor_id': fields.Integer(required=True, min_length=1, example=1, description='Vendor ID is Required'),
        'business_name': fields.String(required=True, min_length=2, max_length=130, example="Wellness Spa", description='Name of business is required'),
        'address1': fields.String(required=False, min_length=1, description='Address1 or mobile number is required'),
        'city': fields.String(required=False, min_length=1, description='City is required'),
        'state': fields.String(required=False, min_length=1, description='State is required'),
        'country': fields.String(required=False, min_length=1, description='Country is required'),
        'latitude':fields.String(required=False, description='Latitude is required'),
        'longitude': fields.String(required=False, description='Longitude name is required'),
        'location_type': fields.String(required=False, min_length=1, enum=["Hotel","Market","Mall","Residential","Airport","Other",""], description='Where is the spa located?'),
        'email': fields.String(required=True, min_length=1, description='Email is required'),
        'office_type': fields.String(required=False, min_length=1, enum=["Head office","City Office","State Office","Other",""], description='Office type is required'),
        'contact_number': fields.String(required=True, min_length=1, description='Contact number is required'),
        'contact_person': fields.String(required=True, min_length=1, description='Contact person name is required'),
        'contact_person_number': fields.String(required=False, description='Contact person number is required'),
        'contact_person_role': fields.String(required=False, enum=["owner","manager","employee",""], description='Contact person role'),
        'cancelled_cheque': fields.String(required=False, description='Cancelled cheque is required'),
        'bank_account_number': fields.String(required=False, description='Office type is required'),
        'ifsc_code': fields.String(required=False, description='Office type is required'),
        'address_proof_type': fields.String(required=False, enum=["Lease Agreement","Electricity Bill","Telephonic Bill",""], example="Lease Agreement", description='Office type is required'),
        'address_proof': fields.String(required=False, description='Address proof document url'),
        'gst_number': fields.String(required=False, description='Office type is required'),
        'pan_number': fields.String(required=False,  description='Pan number'),
        'pan_card': fields.String(required=False,  description='URL '),
        'male_staff': fields.Integer(required=False, description='Office type is required'),
        'female_staff': fields.Integer(required=False, description='Office type is required'),
        'spa_for': fields.String(required=False, enum=["male","female","both",""], description='Office type is required'),
        'cover_img_h':fields.String(required=False, description='Provide cover image for horizontal'),
        'cover_img_v':fields.String(required=False, description='Provide cover image in vertical'),
        'massage_room': fields.Integer(required=False, description='Number of massage room.'),
        'about': fields.String(required=False, description='Office type is required'),
        'description': fields.String(required=False, description='Office type is required'),
        'timing': fields.Raw(required=False, example='{"weekday_start":"10:00","weekday_end":"19:00","weekend_start":"10:00","weekend_end":"10:00","close":"Monday"}', description='Office type is required'),
        'amenities': fields.Raw(required=False,  example='{"id":"title"}', description='Office type is required')
    })
    return updateProfile

def changePasseordM(self,ns):
    changePasswordModel = ns.model('changePasswordModel', {
        'user_id': fields.String(required=True, min_length=1, example=1, description='vendor id is required'),
        'old_password': fields.String(required=True, min_length=1, description='password is required'),
        'new_password': fields.String(required=True, min_length=4, max_length=16, description='password is required'),
    })
    return changePasswordModel

# Vendor Login
def getProfile(self,vendor_id):
    
    if not vendor_id:
        code = 201
        status = False
        message = MSG_CONST.VENDOR_EMPTY_ID
        responseData = {}
    else:
        
        getVendor = DB.find_one(tbl_v002_vendors,{"_id":ObjectId(vendor_id)})
        
        if getVendor:
            getVendor["vendor_id"] = vendor_id
            code = 200
            status = True
            message = MSG_CONST.VENDOR_SUCCESS
            responseData = getVendor
        else:
            code = 201
            status = False
            message = MSG_CONST.VENDOR_INVALID_ID
            responseData = getVendor
    response = output_json(responseData,message,status,code)
    #logging.debug('vendor_get_profile: {}'.format(response))
    return response

def updateProfile(self):
    # todayDate = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    todayDate = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    ip_address = socket.gethostbyname(socket.gethostname())
    requestData = request.json
    user_id = ObjectId(requestData['_id'])
    # code = 201
    # status = False
    # message = MSG_CONST.VENDOR_EMPTY_ID
    responseData = {}
    # print(requestData)
    
    
    if "_id" in requestData and requestData["_id"] != "":
        _id = ObjectId(requestData['_id'])
        selectField = {"_id":1,"email":1,"contact_number":1,"gst_number":1}
        getVendorData = DB.find_one(tbl_v002_vendors,{"_id":ObjectId(requestData['_id'])},selectField)
        act = None
        if requestData["gstn"] != "":
            res = GST(requestData["gstn"]).verifyGst()
            if res and "error" in res and res["error"] == False:
                act = DB.update_one(tbl_v002_vendors, {"gstn":requestData["gstn"],"gstn_verify":1},{"_id":ObjectId(requestData["_id"])})
                status = True
                message = "GST Number has been verified Successfully..!"
            else:
                act=None
            #     status = False
            #     message = "Sorry, Entered GST number is Invalid..!"
            responseData["Gst_no"] = requestData["gstn"]
        pan_card = None
        if requestData['pan_card'] != "":
            pan_card = 1
        if getVendorData:
            updateData = {}
            updateData["business_name"] = requestData["business_name"]
            updateData["business_registered_type"] = requestData["business_registered_type"]
            updateData["contact_person"] = requestData["contact_person"]
            updateData["address1"]      = requestData["address1"]
            updateData["city"]      = requestData["city"]
            updateData["state"]      = requestData["state"]
            updateData["pincode"]      = requestData["pincode"]
            updateData["landmark"] = requestData["landmark"]
            updateData["contact_number"]      = requestData["contact_number"]
            updateData["email"]         = requestData["email"]
            updateData["gst_not_available"] = requestData["gst_not_vailable"]
            updateData["pan_card"]= requestData["pan_card"]
            updateData["latitude"]         = requestData["latitude"]
            updateData["longitudes"]         = requestData["longitudes"]
            updateData["update_by"] =  user_id
            updateData["update_date"] = todayDate
            updateData["update_ip"] = ip_address
            updateData["status"] = 0
            updateStatus = DB.update_one(tbl_v002_vendors,updateData,{"_id":_id})
            
            if (updateStatus != None) and (act):
                code = 200
                status = True
                message = "Bussiness Detail has been saved successfully with GST"
            elif (updateStatus != None) and (act == None) and not(pan_card):
                code = 200
                status = True
                message = "Bussiness Detail Saved without GST..!"
            elif (updateStatus != None) and (pan_card):
                code = 200
                status = True
                message = "Bussiness Detail has been saved successfully"
            else:
                # if act==None:
                # code = 201
                # status = True
                # message = "Bussiness Detail has been saved successfully..!"
                # else:
                code = 201
                status = False
                message = MSG_CONST.VENDOR_FAILED_UPDATE_PROFILE
        else:
            code = 201
            status = False
            message = MSG_CONST.VENDOR_INVALID_ID
    else:
        code = 201
        status = False
        message = MSG_CONST.VENDOR_EMPTY_ID
    
    # responseData = updateData
    response = output_json(responseData,message,status,code)
    #logging.debug('vendor_update_profile: {}'.format(response))
    return response

def change_password(self):
    requestData = request.json
    code = 201
    status = False
    message = MSG_CONST.VENDOR_EMPTY_ID
    responseData = {}
    data = {}
    if "user_id" in requestData:
        getVendor = DB.find_one(tbl_v003_vendor_users,{"_id":ObjectId(requestData["user_id"])},{"user_id":1,"password":1,"_id":1})
        if getVendor:
            if check_password_hash(getVendor["password"],requestData['old_password']):
                data["password"] = generate_password_hash(requestData['new_password'])
                update = DB.update_one(tbl_v003_vendor_users,data,{"_id":ObjectId(requestData["user_id"])})
                if update:
                    code = 200
                    status = True
                    message = MSG_CONST.VENDOR_SUCCESS_UPDATE_PASSWORD
                else:
                    code = 201
                    status = False
                    message = MSG_CONST.VENDOR_FAILED_UPDATE_PASSWORD
            else:
                code = 201
                status = False
                message = MSG_CONST.VENDOR_INVALID_OLD_PASSWORD
        else:
            code = 201
            status = False
            message = MSG_CONST.VENDOR_INVALID_ID
    else:
        code = 201
        status = False
        message = MSG_CONST.VENDOR_EMPTY_ID
    response = output_json(responseData,message,status,code)
    #logging.debug('vendor_password_update: {}'.format(response))
    return response

""" def fx(self):
    file = pd.ExcelFile("text.xlsx")
    df1 = file.parse(0)
    
    cat = df1["Category"].fillna("") if "Category" in df1 else []
    ser = df1["Sub-Category"].fillna(0) if "Sub-Category" in df1 else []
    catList = []
    serList = {}
    catIds = {}
    for x in range(len(cat)):
        if cat[x] and cat[x] and cat[x] != "" and not (any(d['name'] == cat[x] for d in catList)):
            catList.append({"name":cat[x]})

        if ser[x] and ser[x] != "" and cat[x]:
            if cat[x] in serList:
                serList[cat[x]].append(ser[x])
            else:
                serList[cat[x]] = []
                serList[cat[x]].append(ser[x])
    
    gerCat = DB.find_by_key(tbl_v006_service_category,{"is_default":1},{"_id":1,"category_name":1})
    for x in gerCat:
        catIds[x["category_name"]] = ObjectId(x["_id"]["$oid"])
    insCart = []
    for x in serList:
        catId = catIds[x]
        for y in serList[x]:
            insCart.append({"category_id":catId,"name":y})
    ids = DB.insert_many(tbl_v007_services_master,insCart)

    print(ids)
    
    return "X" """
    
def update_bank_data(self):
    todayDate = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    ip_address = socket.gethostbyname(socket.gethostname())
    requestData = request.json
    code = 201
    status = False
    message = MSG_CONST.VENDOR_EMPTY_ID
    responseData = {}
    if "vendor_id" in requestData and requestData["vendor_id"] != "":
        selectField = {"_id":1,"account_data":1}
        getBankData = DB.find_one(tbl_v002_vendors,{"_id":ObjectId(requestData['vendor_id'])},selectField)
        if getBankData:
            updateData = {}
            updateData['account_data']={}
            updateData['account_data']["bank_name"] = requestData["bank_name"]
            updateData['account_data']["IFSC_CODE"] = requestData["ifsc"]
            updateData['account_data']["holder_name"]      = requestData["holder_name"]
            updateData['account_data']["account_no"] = requestData["account_no"]
            updateData['account_data']["confirm_account_no"]         = requestData["confirm_account_no"]
            updateData["update_date"] = todayDate
            updateData["update_ip"] = ip_address
            updateData["status"] = 0
            updateStatus = DB.update_one(tbl_v002_vendors,updateData,{"_id":ObjectId(requestData['vendor_id'])})
            update_tour_steps = DB.update_one(tbl_v026_tour_steps,{"setup_account":True},{"vendor_id":ObjectId(requestData['vendor_id'])})
            if updateStatus != None:
                code = 200
                status = True
                message = MSG_CONST.ACCOUNT_DETAILS_SUCCESS
            else:
                code = 201
                status = False
                message = MSG_CONST.ACCOUNT_DETAILS_FAILED
        else:
            code = 201
            status = False
            message = MSG_CONST.VENDOR_INVALID_ID
    else:
        code = 201
        status = False
        message = MSG_CONST.VENDOR_EMPTY_ID
    response = output_json(responseData,message,status,code)
    #logging.debug('update_bank_data: {}'.format(response))
    return response

# Get referal data by vendor id
def get_referral_data(self):
    vendor_id = ""

    # get vendor id from header
    if request.headers.get('vendor-id'):
            vendor_id = request.headers.get('vendor-id')
    if vendor_id == "" or vendor_id== None:
        return output_json({},MSG_CONST.VENDOR_ID_NOT_FOUND,False,200)

    # get referal data by vendor id
    user_data = DB.find_one(tbl_v002_vendors,{"_id":ObjectId(vendor_id)})
    if user_data == None:
        return output_json({},MSG_CONST.VENDOR_NOT_FOUND,False,200)

    # get data of user referral by this vendor
    refer_user_data = DB.find_all_where(tbl_v002_vendors,{"referral_by":ObjectId(vendor_id)},{"insert_date":1,'contact_person':1,'referral_used':1})
    if refer_user_data == None:
        refer_user_data=[]

    # create response
    response_data = {}
    response_data['user_data'] = user_data
    response_data['refer_user_data'] = refer_user_data

    return output_json(response_data,MSG_CONST.GET_REFERRAL_DATA_SUCCESS)

# Refer by email
def refer_by_email(self):
    requestData = dict(request.json)
    ins_data={}
    ins_data['refer_to_details'] = requestData['refer_to_details']
    ins_data['type'] = 'refer'
    ins_data['desc'] = 'Vendor refer by email(mutiple support)'
    ins_data['inserted_date'] = get_current_date()
    ins_data['ip_address'] = socket.gethostbyname(socket.gethostname())
    ins_data['user_id'] = request.headers.get('Vendor-User-Id')
    ins_data['vendor_id'] = request.headers.get('Vendor-Id')
    ins_data['device'] = get_device_name(request.headers.get('Device-Id'))

    db_response = DB.insert(tbl_a017_history,ins_data)
    if db_response == None:
        return output_json({},"Something Went Wrong..!",False,201)
    else:
        # get vendor user name
        vendor_user_data = DB.find_one(tbl_v003_vendor_users,{'_id':ObjectId(ins_data['user_id'])},{'name':1})
        vendor_username = vendor_user_data['name']
        # get template
        email_arr = DB.find_one(tbl_a001_email_template,{'type':'refer_by_email_all'})
        for refer_data in requestData['refer_to_details']:
            # send mail
            notificationObject = {}
            emailObject = {}
            emailObject["to"] = [refer_data['email']]
            emailObject["template"] = "refer_by_email_all"
            emailObject["replace_value"] = {}
            emailObject["replace_value"]["referral_code"] = requestData['referral_code']
            emailObject["replace_value"]["user_name"] = refer_data['name']
            emailObject["replace_value"]["user_name2"] = vendor_username
            emailObject["replace_value"]["link"] = CONST.VENDOR_WEB + 'register?referral-code=' + requestData['referral_code']
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

        return output_json({},MSG_CONST.VENDOR_REFER_BY_EMAIL_SUCCESS,True,200)

