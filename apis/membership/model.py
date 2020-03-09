from flask_restplus import Namespace, fields
import socket
import time
from datetime import datetime, date, time, timedelta
from flask import jsonify, request
from database import DB
from bson import json_util, ObjectId
from apis.utils.common import *
from apis.libraries.send_mail import Send_mail
import logging
import requests
import apis.utils.message_constants as MSG_CONST
import apis.utils.constants as CONST
import apis.utils.subscription as subscription
from apis.utils.gst import *
from werkzeug.security import generate_password_hash, check_password_hash
import pymongo
import math
import calendar
logging.basicConfig(filename='vendor.log', level=logging.DEBUG)


def subscriptionModel(self, ns):
    subscriptionModel = ns.model('subscriptionModel', {
        'user_id': fields.String(required=True, min_length=1, example=1, description='User id is required'),
        'vendor_id': fields.String(required=True, min_length=1, example=1, description='vendor id is required')
    })
    return subscriptionModel

# Declare tables name in vars
tbl_v002_vendors = "v002_vendors"
tbl_v003_vendor_users = "v003_vendor_users"
tbl_v004_outlets = "v004_outlets"
tbl_v005_roles = "v005_roles"
tbl_v015_membership = "v015_membership"
tbl_v016_subscription = "v016_subscription"
tbl_v026_tour_steps = "v026_tour_steps"
tbl_a014_vendor_membership_offer = "a014_vendor_membership_offer"
tbl_a015_referral_value = "a015_referral_value"
tbl_a016_reference_data = "a016_reference_data"
tbl_v012_services = "v012_services"
tbl_v013_feedback = "v013_feedback"
tbl_v019_offer_details = "v019_offer_details"
tbl_a001_email_template="a001_email_template"


# Done By Jyoti
def get_membership_data(self,vendor_id):
    curr_plan_id=''
    billing_data=DB.find_by_key(tbl_v016_subscription,{"$and":[{"vendor_id":ObjectId(vendor_id),"status":int(1)}]},{},[("index",pymongo.DESCENDING)])
    
    if billing_data!=[]:
        billing_data=billing_data[-1]
        curr_plan_id=billing_data['plan_id']['$oid']
    vendor_data = DB.find_one(tbl_v002_vendors,{"_id":ObjectId(vendor_id),'referral_used':{"$ne":True},'referral_by':{"$ne":None}})
    ref_data=None
    referral_disc_data=None
    if vendor_data != None:
        # get reference data
        ref_data = DB.find_one(tbl_a016_reference_data,{'name':'module'},{'value1':1})
        # get referral discount data
        referral_disc_data = DB.find_one(tbl_a015_referral_value,{"module":ref_data['value1']})
    
    membership_data=DB.find_all(tbl_v015_membership)
    for x in membership_data:
        plan_id = x["_id"]["$oid"]
    
        if curr_plan_id!='':
            if curr_plan_id==plan_id:
                x["current_active"]=True
            else:
                x["current_active"]=False    
        else:
            x["current_active"]=False            

        plan_price = x["price"]
        x["monthly_price"] =  x["price"]
        if RepresentsInt(x['price']):
            x["yearly_price"] =  int(x["price"]) * 12
        x["yearly_price"] =  x["price"]
        if referral_disc_data != None and RepresentsInt(plan_price):
            x['referred_discount'] = int(referral_disc_data['value'])
        discount_data = DB.find_one(tbl_a014_vendor_membership_offer,{"plan_id":ObjectId(plan_id)},{"monthly_offer":1,"yearly_offer":1,"sub_id":1})
        if(discount_data):
            monthly_applied_discount = int(discount_data["monthly_offer"]) #monthly_discount
            yearly_applied_discount = int(discount_data["yearly_offer"]) #yearly_discount            
            find_price = DB.find_one(tbl_v015_membership,{"_id":ObjectId(plan_id)},{"price":1})
            price = float(find_price["price"])

            a = math.ceil(price * 12 * (100-monthly_applied_discount) / 100) #monthly_discount
            mon_disc_price=math.ceil(a/12)
            
            b = math.ceil(price * 12 * (100-yearly_applied_discount) / 100) #yearly_discount            
            year_final_disc_price=math.ceil(b)
            # monthly_discount_price = math.ceil(price * monthly_applied_discount / 100) #monthly_discount
            # yearly_discount_price = math.ceil(price * yearly_applied_discount / 100) #yearly_discount            
            # mon_disc_price = price - monthly_discount_price
            # year_disc_price = price - yearly_discount_price
            # year_final_disc_price = year_disc_price * 12
            x['monthly_discount_price'] = math.ceil(mon_disc_price)
            x['monthly_discount'] = monthly_applied_discount
            x['yearly_discount_price'] = math.ceil(year_final_disc_price)   
            x['yearly_monthly_price'] = math.ceil(year_final_disc_price/12)          
            x['yearly_discount'] = yearly_applied_discount  
            x['sub_id']=discount_data["sub_id"]

            # Calculate referred price for plan on avail discount price
            if referral_disc_data != None and RepresentsInt(plan_price):
                x['referred_monthly_price'] = math.ceil(int(x['monthly_discount_price']) - ((int(x['monthly_discount_price']) * int(x['referred_discount'])) / 100))
                x['referred_yearly_price'] = math.ceil(int(x['yearly_discount_price']) - ((int(x['yearly_discount_price']) * int(x['referred_discount'])) / 100))
                x['referred_yearly_monthly_price'] = math.ceil(x['referred_yearly_price']/12)
        else:
            # Calculate referred price for plan
            if referral_disc_data != None and RepresentsInt(plan_price):
                x['referred_monthly_price'] = math.ceil(int(plan_price) - ((int(plan_price) * int(x['referred_discount'])) / 100))
                x['referred_yearly_price'] = math.ceil((int(plan_price)* 12) - ((int(plan_price)* 12 * int(x['referred_discount'])) / 100))
                x['referred_yearly_monthly_price'] = math.ceil(x['referred_yearly_price']/12) 
            # update_price = DB.update_one(tbl_v015_membership,{"discount_price":float(disc_price)},{"_id":ObjectId(plan_id)}) 

    
    return output_json( membership_data,MSG_CONST.VENDOR_MEMBERSHIPDATA_SUCCESS, True, 200,None)

# Get Vendor Subscription and membership details
def getVendorSubscription(self):
    code = 200
    status = False
    message = ""
    responseData = {}
    requestData = dict(request.json)
    
    responseData = subscription.VendorSubscription(requestData["vendor_id"]).getVendorSubscription()
    if responseData:
        code = 200
        status = True
        message = MSG_CONST.VENDOR_SUBSCRIPTION_SUCCESS
    else:
        code = 200
        status = False
        message = MSG_CONST.VENDOR_SUBSCRIPTION_FAILED
    response = output_json(responseData, message, status, code)
    logging.debug('vendor_outlet_remove: {}'.format(response))
    return response

def buy_plan(self,data):
    todayDate = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    if data["paymentData"]["amount"]!="0":
        logging.debug('step 1- Initiate payment order : vendorID-'+str(data['vendor_id'])+',userID-'+str(data['user_id'])+',planID-'+str(data['plan_id'])+',Date-'+todayDate)
    
    data['plan_id'] = ObjectId(data['plan_id'])
    data['vendor_id'] = ObjectId(data['vendor_id'])
    data["paymentData"]["user_id"] = data['user_id']
    data['user_id'] = ObjectId(data['user_id'])
    today = datetime.now()
    if data['plan_type'] == 'monthly':
        after_one_month_date = datetime.now() + timedelta(days=30)
    else:
        after_one_month_date = datetime.now() + timedelta(days=365)        
    data["create_date"] = datetime.strftime(today,'%Y-%m-%d')
    data["start_date"] = datetime.strftime(today,'%Y-%m-%d')
    data["payment_date"] = datetime.strftime(today,'%Y-%m-%d')
    data["expiry_date"] = datetime.strftime(after_one_month_date,'%Y-%m-%d')
    if data["paymentData"]["amount"]=="0":
        data["status"]=1
        data["payment_status"]=1
    if data['gst_number'] == "":
        data['gst_status'] = False
    insertedId = DB.insert("v016_subscription",data)
    res= DB.update_one(tbl_v026_tour_steps,{"is_membership_buy":True},{"vendor_id":ObjectId(data["vendor_id"])})
    
    data2={}
    if data["paymentData"]["amount"]=="0":
        data2["subscription"] = subscription.VendorSubscription(str(data['vendor_id'])).getVendorSubscription()
        #send email to vendor
        vendor_name = DB.find_one(tbl_v002_vendors,{"_id":ObjectId(data['vendor_id'])},{'email':1,'contact_person':1,'_id':0,"referral_by":1,'referral_used':1})
        email_arr = DB.find_one(tbl_a001_email_template,{'type':'vendor_membership_buy'},{'title':1})
        notificationObject = {}
        emailObject = {}
        emailObject["to"] = [vendor_name["email"]]
        emailObject["template"] = "vendor_membership_buy"
        emailObject["replace_value"] = {}
        emailObject["replace_value"]["user_name"] = vendor_name["contact_person"].capitalize()
        emailObject["replace_value"]["link"] = CONST.VENDOR_WEB
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
    
    #import pdb; pdb.set_trace()
    if data["paymentData"]["amount"]!="0":
        if data['plan_type'] == 'monthly':
            logging.debug('vendor_outlet_remove: {}'.format(data))        
            a=datetime.now() + timedelta(minutes=10)
            data["paymentData"]["sub_id"] = data['sub_id']
            data["paymentData"]["start_at"] = calendar.timegm(a.utctimetuple())
            payment_response = requests.post(CONST.PAYMENT_CLIENT+"payment/createsubscription",json=data["paymentData"])
            payment_response_json = payment_response.json()
            DB.update_one("v016_subscription",{"subscription_id":payment_response_json["id"],"short_url":payment_response_json["short_url"],"payment_status":payment_response_json["status"],"request_data":data,"response_data":payment_response_json},{"_id":ObjectId(insertedId)})
            payment_response_json["plan_id"] = insertedId
            logging.debug('step 2- payment v016_subscription created : vendorID-'+str(data['vendor_id'])+',userID-'+str(data['user_id'])+',planID-'+str(data['plan_id'])+',orderId-'+str(payment_response_json["id"])+',Date-'+todayDate)
            response = output_json(payment_response_json,"Payment Created Succefully",True,200)
            logging.debug('buy_plan: {}'.format(response))
            return response    
        if data['plan_type'] == 'yearly':
            logging.debug('vendor_outlet_remove: {}'.format(data))        
            data["paymentData"]["amount"] = eval(str(round(eval(data["paymentData"]["amount"])))+"00")
            payment_response = requests.post(CONST.PAYMENT_CLIENT+"payment/createorder",json=data["paymentData"])
            payment_response_json = payment_response.json()
            DB.update_one("v016_subscription",{"order_id":payment_response_json["id"],"payment_status":payment_response_json["status"],"request_data":data,"response_data":payment_response_json},{"_id":ObjectId(insertedId)})
            payment_response_json["plan_id"] = insertedId
            logging.debug('step 2- payment order created : vendorID-'+str(data['vendor_id'])+',userID-'+str(data['user_id'])+',planID-'+str(data['plan_id'])+',orderId-'+str(payment_response_json["id"])+',Date-'+todayDate)
            response = output_json(payment_response_json,"Payment Created Succefully",True,200)
            logging.debug('buy_plan: {}'.format(response))
            return response
    else:
        response = output_json(data2,"membership inserted Succefully",True,200)
        return response
        

def success_plan_payment(self,data):
    #import pdb; pdb.set_trace()
    if data['plan_type']=="yearly":
        todayDate = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        logging.debug('3 step - Initiate payment request : userID-'+str(data['user_id'])+',subscriptionID-'+str(data["plan_id"])+',orderID-'+str(data["razorpay_order_id"])+',paymentID-'+str(data["razorpay_payment_id"])+',signature-'+str(data["razorpay_signature"])+',Date-'+todayDate)
        post_data = {
                "razorpay_order_id":data["razorpay_order_id"],
                "razorpay_payment_id":data["razorpay_payment_id"],
                "razorpay_signature":data["razorpay_signature"],
                'user_id': data['user_id']
            }
        res = requests.post(CONST.PAYMENT_CLIENT+'payment/success', json=post_data)
        res_json = res.json()
        res_json_data = res_json["data"]
        if res_json_data["status"]=="captured":
            status1=1
        else:
            status1=0    

        if res_json["status"] == True:
            upd_data = {
                "payment_method":res_json_data["method"],
                "payment_id":res_json_data["id"],
                "payment_currency":res_json_data["currency"],
                "payment_status":status1,
                "status":status1,
                "request_data":data,
                "response_data":res_json_data
            }
            DB.update_one("v016_subscription",upd_data,{"_id":ObjectId(data["plan_id"])})
        if status1==1:
            logging.debug('4 step - Payment Success : userID-'+str(data['user_id'])+',subscriptionID-'+str(data["plan_id"])+',orderID-'+str(data["razorpay_order_id"])+',paymentID-'+str(data["razorpay_payment_id"])+',paymet_status-'+str(res_json_data["status"])+',payment_method-'+str(res_json_data["method"])+',Date-'+todayDate)
        else:
            logging.debug('5 step - Payment Failed : userID-'+str(data['user_id'])+',subscriptionID-'+str(data["plan_id"])+',orderID-'+str(data["razorpay_order_id"])+',paymentID-'+str(data["razorpay_payment_id"])+',paymet_status-'+str(res_json_data["status"])+',payment_method-'+str(res_json_data["method"])+',Date-'+todayDate)
        get_id = DB.find_one("v016_subscription",{"_id":ObjectId(data["plan_id"])},{'plan_id':1,'vendor_id':1,'_id':0,'start_date':1,'expiry_date':1,'price':1})
    if data['plan_type']=="monthly":
        status1=1
        upd_data = {
                "payment_id":data["razorpay_payment_id"],
                "payment_currency":"INR",
                "payment_status":status1,
                "status":status1,
                "request_data":data,
                "response_data":data,
                "payment_method":"creditcard"
            }
        DB.update_one("v016_subscription",upd_data,{"subscription_id":str(data["razorpay_subscription_id"])})
        ins_data={}
        ins_data['request_date']=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        ins_data['response_date']=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        ins_data['request_data']=data
        ins_data['response_data']=data
        ins_data['type']="sucess_subcription"
        ins_data['user_id']=ObjectId(data['user_id'])
        inserted_id = DB.insert("a012_audit_trail",ins_data)
        get_id = DB.find_one("v016_subscription",{"subscription_id":str(data["razorpay_subscription_id"])},{'plan_id':1,'vendor_id':1,'_id':0,'start_date':1,'expiry_date':1,'price':1})
    

    
    package_name = DB.find_one(tbl_v015_membership,{"_id":ObjectId(get_id["plan_id"]['$oid'])},{'title':1,'_id':0})
    vendor_name = DB.find_one(tbl_v002_vendors,{"_id":ObjectId(get_id['vendor_id']['$oid'])},{'email':1,'contact_person':1,'_id':0,"referral_by":1,'referral_used':1,'business_name':1,'city':1,'contact_number':1})
 
    # Add offer coupons to referred user
    if status1==1 and 'referral_by' in vendor_name and vendor_name['referral_by'] != None and 'referral_used' in vendor_name and vendor_name['referral_used'] != True: 
        response = add_offers_for_referralby(vendor_name['referral_by']['$oid'])
        if response == False:
            return output_json({}, MSG_CONST.COUPON_NOT_GENERATE, True, 200)
    # If payment done successfully then update referral_used to true
    if status1==1 and 'referral_used' in vendor_name and vendor_name['referral_used'] != True:
        DB.update_one(tbl_v002_vendors,{"referral_used":True},{"_id":ObjectId(get_id['vendor_id']['$oid'])})
        if 'referral_by' in vendor_name:
            if vendor_name['referral_by']!=None:
                vendor_name2 = DB.find_one(tbl_v002_vendors,{"_id":ObjectId(vendor_name['referral_by']['$oid'])},{'email':1,'contact_person':1,'_id':0})
                email_arr = DB.find_one(tbl_a001_email_template,{'type':'vendor_refferal_subscription_buy'},{'title':1})
                notificationObject = {}
                emailObject = {}
                emailObject["to"] = [vendor_name2["email"]]
                emailObject["template"] = "vendor_refferal_subscription_buy"
                emailObject["replace_value"] = {}
                emailObject["replace_value"]["user_name"] = vendor_name2["contact_person"].capitalize()
                emailObject["replace_value"]["user_name2"] = vendor_name['contact_person'].capitalize()
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
        
        
    if status1==1:
        #send email to vendor
        email_arr = DB.find_one(tbl_a001_email_template,{'type':'vendor_membership_buy'},{'title':1})
        notificationObject = {}
        emailObject = {}
        emailObject["to"] = [vendor_name["email"]]
        emailObject["template"] = "vendor_membership_buy"
        emailObject["replace_value"] = {}
        emailObject["replace_value"]["user_name"] = vendor_name["contact_person"].capitalize()
        emailObject["replace_value"]["link"] = CONST.VENDOR_WEB
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
        #send email to admin
        email_arr = DB.find_one(tbl_a001_email_template,{'type':'admin_vendor_membership_buy'},{'title':1})
        notificationObject = {}
        emailObject = {}
        emailObject["to"] = [CONST.ADMIN_EMAIL]
        emailObject["template"] = "admin_vendor_membership_buy"
        emailObject["replace_value"] = {}
        emailObject["replace_value"]["business_name"] = vendor_name["business_name"]
        emailObject["replace_value"]["city"] = vendor_name["city"]
        emailObject["replace_value"]["plan_name"] = package_name["title"]
        emailObject["replace_value"]["plan_period"] = get_id["start_date"] +' TO '+ get_id["expiry_date"]
        emailObject["replace_value"]["plan_amount"] = '₹ '+get_id["price"]
        emailObject["replace_value"]["plan_payment_mode"] = upd_data["payment_method"]
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

        notificationObject = {}
        smsObject = {}
        smsObject["to"] = vendor_name['contact_number']
        smsObject["template"] = "vendor_payment_success"
        smsObject["replace_value1"] = package_name["title"]+' plan'
        smsObject["replace_value2"] = get_id["price"]
        smsObject["replace_value3"] = data["razorpay_payment_id"]
        notificationObject["sms"] = smsObject
        res = requests.post(CONST.NOTIFACTION_CLIENT, json=notificationObject)
        response = dict(res.json())

        data2={}
        data2["subscription"] = subscription.VendorSubscription(str(get_id['vendor_id']['$oid'])).getVendorSubscription()
        # print(data2)
        response = output_json(data2, "Plan payment made successfully", True, 200)
        return response
    else:
        email_arr = DB.find_one(tbl_a001_email_template,{'type':'vendor_membership_buy_failed'},{'title':1})
        notificationObject = {}
        emailObject = {}
        emailObject["to"] = [vendor_name["email"]]
        emailObject["template"] = "vendor_membership_buy_failed"
        emailObject["replace_value"] = {}
        emailObject["replace_value"]["user_name"] = vendor_name["contact_person"].capitalize()
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
        response = output_json(data2, "Error in Payment of Plan", False, 200)    
        return response
    # else:
    #     response = output_json(data2, "Error in Payment of Plan", False, 200)
    #     return response
    # logging.debug('success_plan_payment: {}'.format(response))
    
    


# Yogesh Kothiya - Sun - 08 - Dec - 2019
def AddMembershipPlan(self):
    code = 200
    status = False
    message = ""
    responseData = {}
    requestData = dict(request.json)
    
    responseData = subscription.VendorSubscription(requestData["vendor_id"],requestData["user_id"]).addMemberShip(requestData)
    if responseData:
        code = 200
        status = True
        message = MSG_CONST.VENDOR_SUBSCRIPTION_SUCCESS
    else:
        code = 200
        status = False
        message = MSG_CONST.VENDOR_SUBSCRIPTION_FAILED
    response = output_json(responseData, message, status, code)
    logging.debug('vendor_outlet_remove: {}'.format(response))
    return response


def Getmembership(self):
    code = 200
    status = False
    message = ""
    responseData = {}
    fieldList = {"_id" : ObjectId("5e231eff3ea007549a3f85b6"),"title" : 1,"days" : 1,"price" : 1,"listing_onwebsite" : 1,"booking_scanQR" : 1,"booking_paymentgateway" : 1,"booking_manage_web" : 1,"booking_manage_app" : 1,"booking_commission" : 1,"outlet_photo" : 1,"outlet_video" : 1,"outlet_review" : 1,"outlet_rating" : 1,"outlet_promotional" : 1,"booking_invoice" : 1,"service_count" : 1,"outlet_promocode" : 1,"service_offer" : 1,"outlet_featured" : 1,"general_coupon_manage" : 1,"general_salespackage" : 1,"general_vendor_loylalty" : 1,"booking_livechat" : 1,"general_rate_customer" : 1,"outlet_manage_roles" : 1,"outlet_inventory_manage" : 1,"outlet_flash_deals" : 1,"general_sales_giftcard" : 1,"booking_report" : 1,"outlet_branches" : 1,"outlet_assign_admin" : 1,"general_emp_manage" : 1,"outlet_account_report":1,"outlet_verified_discount" : 1}
    membership_data = DB.find_all(tbl_v015_membership,fieldList)
    for x in membership_data:
        plan_id = x["_id"]["$oid"]
        plan_price = x["price"]
        discount_data = DB.find_one(tbl_a014_vendor_membership_offer,{"plan_id":ObjectId(plan_id)},{"monthly_offer":1,"yearly_offer":1})
        if(discount_data):
            monthly_applied_discount = int(discount_data["monthly_offer"]) #monthly_discount
            yearly_applied_discount = int(discount_data["yearly_offer"]) #yearly_discount            
            find_price = DB.find_one(tbl_v015_membership,{"_id":ObjectId(plan_id)},{"price":1})
            price = float(find_price["price"])
            monthly_discount_price = price * monthly_applied_discount // 100 #monthly_discount
            yearly_discount_price = price * yearly_applied_discount // 100 #yearly_discount            
            mon_disc_price = price - monthly_discount_price
            year_disc_price = price - yearly_discount_price
            year_final_disc_price = year_disc_price * 12
            x['monthly_discount_price'] = mon_disc_price
            x['monthly_discount'] = monthly_applied_discount
            x['yearly_discount_price'] = year_final_disc_price   
            x['yearly_monthly_price'] = year_final_disc_price/12            
            x['yearly_discount'] = yearly_applied_discount            
            # update_price = DB.update_one(tbl_v015_membership,{"discount_price":float(disc_price)},{"_id":ObjectId(plan_id)}) 
    if(membership_data):
        code = 200
        status = False
        message = MSG_CONST.GET_PLAN
    else:
        code = 200
        status = False
        message = MSG_CONST.PLAN_FAILED
    response = output_json(membership_data, message, status, code)
    logging.debug('vendor_outlet_remove: {}'.format(response))
    return response


def check_gst(self):
    code = 201
    status = False
    message = ""
    responseData = {}
    requestData = dict(request.json)
    find_vendor = DB.find_one(tbl_v002_vendors,{"_id":ObjectId(requestData["vendor_id"])})
    if(find_vendor):
        res = GST(requestData["gst_number"]).verifyGst()
        if res and "error" in res and res["error"] == False:
            # act = DB.update_one(tbl_v016_subscription, {"gst_no":requestData["gst_number"],"gst_validate":True},{"_id":ObjectId(requestData["_id"])})
            act = DB.update_one(tbl_v002_vendors,{"gstn":requestData["gst_number"],"gstn_verify":1},{"_id":ObjectId(requestData["vendor_id"])})
            responseData['gst_number'] = requestData["gst_number"]
            code = 200
            status = True
            message = "GST Number has been verified Successfully..!"
        else:
            responseData['gst_number'] = ''
            code = 201
            status = False
            message = "Entered Gst number is Wrong"
    else:
        code = 201
        status = False
        message = "Sorry, Something went Wrong..!"
    
    response = output_json(responseData,message, status, code)
    logging.debug('check_gst: {}'.format(response))
    return response



def subscription_details(self):
    code = 200
    status = True
    message = ""
    responseData = {}
    requestData = dict(request.json)
    find_user = DB.find_all_where(tbl_v016_subscription,{"vendor_id":ObjectId(requestData["vendor_id"])},"ALL")
    if find_user!=[]:
        getSubscription = find_user[-1]
        plan_id = getSubscription['plan_id']['$oid']
        plan_data = DB.find_one(tbl_v015_membership,{"_id":ObjectId(plan_id)},"ALL")
        if requestData['type']=='staff':
            find_staff = DB.find_all_where(tbl_v003_vendor_users,{"vendor_id":ObjectId(requestData['vendor_id'])})
            responseData['more_staff_allow'] = len(find_staff)
        if requestData['type']=='service':
            allow_service = int(plan_data['service_count'])
            find_services = DB.find_all_where(tbl_v012_services,{"outlet_id":ObjectId(requestData['outlet_id'])})
            total_services = len(find_services)    
            if allow_service <= total_services:
                more_service_allow = False
            elif allow_service >total_services:
                more_service_allow = True
            elif allow_service == 9999:
                more_service_allow = True
            responseData['more_service_allow'] = more_service_allow                         
        if requestData['type'] == 'outlet':
            allow_outlet = int(plan_data['outlet_branches'])
            find_outlets = DB.find_all_where(tbl_v004_outlets,{"vendor_id":ObjectId(requestData['vendor_id'])})
            if find_outlets == []:
                more_outlet_allow = true
            else:
                total_outlets = len(find_outlets)    
                if allow_outlet <= total_outlets:
                    more_outlet_allow = False
                elif allow_outlet >total_outlets:
                    more_outlet_allow = True
                elif allow_outlet == 9999:
                    more_outlet_allow = True
            responseData['more_outlet_allow'] = more_outlet_allow                         
        if requestData['type'] == 'feedback':
            allow_feedback = plan_data['outlet_review']
            if allow_feedback == False:
                more_feedback_allow = False
            else: 
                more_feedback_allow = True
            responseData['more_feedback_allow'] = more_feedback_allow             
        if requestData['type'] == 'role':
            allow_role = plan_data['outlet_manage_roles']
            if allow_role == False:
                more_role_allow = False
            else:
                more_role_allow = True
            responseData['more_role_allow'] = more_role_allow 
        if requestData['type'] == 'report':
            allow_report = plan_data['outlet_account_report']
            if allow_report == False:
                more_report_allow = False
            else:
                more_report_allow = True
            responseData['more_report_allow'] = more_report_allow 
        if requestData['type'] == 'offer':
            allow_offer = plan_data['service_offer']
            if allow_offer == False:
                more_offer_allow = False
            if type(allow_offer) == str:
                allow_offer = int(plan_data['service_offer'])
                find_offers = DB.find_all_where(tbl_v019_offer_details,{"outlet":ObjectId(requestData['outlet_id'])})
                total_offers = len(find_offers)
                if allow_offer <= total_offers:
                    more_offer_allow = False
                elif allow_offer >total_offers:
                    more_offer_allow = True
                elif allow_offer == 9999:
                    more_offer_allow = True
            responseData['more_offer_allow'] = more_offer_allow 
    else:
        getSubscription=[]
        code = 201
        status = False
        message = "Something Went Wrong"
    
    response = output_json(responseData,message, status, code)
    logging.debug('subscription_details: {}'.format(response))
    return response

# get gst number by vendor id
def get_gst_by_vendor(self):
    vendor_id = ''
    gst = ''
    if request.headers.get('Vendor-Id'):
       vendor_id = request.headers.get('Vendor-Id')

    if vendor_id == '':
        return output_json({},MSG_CONST.VENDOR_EMPTY_ID,False)
    
    gst_in_dict = DB.find_one(tbl_v002_vendors,{"_id":ObjectId(vendor_id)},{"_id":0,"gstn":1})
    if gst_in_dict != {} and gst_in_dict != None:
        gst = gst_in_dict['gstn']
    
    return output_json({'gstn':gst},MSG_CONST.VENDOR_GST_GET_SUCCESS,True)

# when referred user buy paid plan then add offers for referred by user
def add_offers_for_referralby(referred_by_id):
    # get reference data
    ref_data = DB.find_one(tbl_a016_reference_data,{'name':'module'})
    # get referral discount data
    referral_disc_data = DB.find_all_where(tbl_a015_referral_value,{"module":{"$in":[ref_data['value2'],ref_data['value3'],ref_data['value4'],ref_data['value5']]}})
    
    dt = datetime.now()
    today = dt.replace(second=0, microsecond=0,hour=0,minute=0)
    ins_data_list = []
    for data in referral_disc_data:
        ins_data = {}
        ins_data['vendor_id'] = ObjectId(referred_by_id)
        ins_data['user_id'] = None
        ins_data['offer_name'] = "Referral "+ data['module'] + " offer"
        ins_data['type'] = data['value_type']
        ins_data['value'] = data['value']
        ins_data['module'] = data['module']
        ins_data['all_services'] = False
        ins_data['offer_type'] = 'coupon'
        ins_data['start_date'] = today
        ins_data['due_date'] = today + timedelta(days=data['period_in_days'])  
        ins_data['coupon_code'] = randomStringDigits(10)
        ins_data['limitation'] = 1
        ins_data['is_delete'] = 1
        ins_data['insert_date'] = datetime.now()
        ins_data['insert_ip'] = None
        ins_data['is_used'] = False
        ins_data['start_time'] = DB.get_timestamp_from_date(ins_data['start_date'])
        ins_data['end_time'] = DB.get_timestamp_from_date(ins_data['due_date'])
        ins_data_list.append(ins_data)

    if ins_data_list != []:
        DB.insert_many(tbl_v019_offer_details,ins_data_list)
        return True
    return False

def RepresentsInt(s):
    try: 
        int(s)
        return True
    except ValueError:
        return False

def randomStringDigits(stringLength=6):
    """Generate a random string of letters and digits """
    lettersAndDigits = string.ascii_letters + string.digits
    return ''.join(random.choice(lettersAndDigits) for i in range(stringLength))