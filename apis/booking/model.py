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
import sys
import dateutil
import isodate
import datetime
import time

tbl_u002_booking = "u002_booking"
tbl_v004_outlets = "v004_outlets"
tbl_u001_users = "u001_users"
tbl_v012_services = "v012_services"
tbl_a001_email_template = "a001_email_template"

def getAvailableSlotModel(self, ns):
    getSlot = ns.model('getAvailableSlotModel', {
        'outlet_id':fields.String(required=False, description="Provide newly added outlet id" ),
        'user_id': fields.String(required=True, min_length=1, example=1, description='User id is required'),
        'vendor_id': fields.String(required=True, min_length=1, example=1, description='vendor id is required'),
        'service_id': fields.String(required=True, min_length=1, description='Service id is required'),
        "date" : fields.String(required=False, description='Outlet service'),
        "gender" : fields.String(required=True, description='Massager gender'),
        "duration":fields.Integer(required=True, description='DUration of service'),
    })
    return getSlot

def createOrderModel(self, ns):
    getSlot = ns.model('getAvailableSlotModel', {
        'outlet_id':fields.String(required=True, description="Provide newly added outlet id" ),
        'user_id': fields.String(required=True, min_length=1, example=1, description='User id is required'),
        'vendor_id': fields.String(required=True, min_length=1, example=1, description='vendor id is required'),
        'booking_date': fields.String(required=True, min_length=1, description='Service id is required'),
        "payment_method" : fields.String(required=True, description='Provide valid payment method'),
        "guest_details" : fields.List(fields.Raw,required=False, description='Massager gender')
    })
    return getSlot
    

def get_booking_data(self,outlet_id):
    data={}
    # todaydate = datetime.datetime.now()
    # y = todaydate.strftime("%m-%d-%Y %H:%M:%S")
    # ts = int(time.time())
    # upcoming = DB.find_all_where("u002_booking",{"$and":[{"spa.services.start_timestamp":{"$gt": (ts)}},{"spa.outlet_id":str(outlet_id),"status":int(2)}]},"ALL")
    # history = DB.find_all_where("u002_booking",{"$and":[{"spa.services.start_timestamp":{"$lt": (ts)}},{"spa.outlet_id":str(outlet_id),"status":int(2)}]},"ALL")
    # both_data["upcoming_data"]=upcoming
    # both_data["history_data"]=history
    
    # if upcoming and history == None:
    #     return output_json("", MSG_CONST.VENDOR_BOOKINGDATA_FAILED, False, 201)
    # else:
    #     return output_json(booking, MSG_CONST.VENDOR_BOOKINGDATA_SUCCESS, True, 200)     

    selectField = {"user_id":1,"booking_id":1,"booking_no":1,"spa":1,"outlet_id":1,"created_date":1,"payment_status":1,'price':1,'services':1}
    if outlet_id != "":
        booking = DB.find_all_where("u002_booking",{"$and":[{"spa.outlet_id":ObjectId(outlet_id),"status":int(2)}]},"ALL")
        data['booking']=booking
    else:
        data['booking']=[]
    return output_json(data, MSG_CONST.VENDOR_BOOKINGDATA_SUCCESS, True, 200)     



def get_calendar_data(self,outlet_id):
    todaydate = datetime.datetime.now()
    y = todaydate.strftime("%m-%d-%Y %H:%M:%S")
    ts = int(time.time())
    get_calendar=[]
    get_service = []
    selectField = {"_id":1,"user_id":1,"booking_id":1,"booking_no":1,"spa":1,"outlet_id":1,"created_date":1,"payment_status":1,'price':1,'services':1}
    # Booking = DB.find_all_where("u002_booking",{"$and":[{"spa.services.start_timestamp":{"$gt": (ts)}},{"spa.outlet_id":ObjectId(outlet_id),"status":int(2)}]},"ALL")
    if outlet_id != "":
        Booking = DB.find_all_where("u002_booking",{"$and":[{"spa.outlet_id":ObjectId(outlet_id),"status":int(2)}]},"ALL")
        outlet_name = DB.find_one(tbl_v004_outlets,{"_id":ObjectId(outlet_id)},{"name":1,"_id":0})
    else:
        Booking = []
        outlet_name = []
    # get_calendar.append(outlet_name)
    
    for x in Booking:
        # get_calendar.append(x['_id'])
        for spa_data in x['spa']:
            for i in spa_data['services']:
                service_cnt=0
                i["start_time"] = datetime.datetime.fromtimestamp(i["start_timestamp"]).strftime("%Y-%m-%d %H:%M:%S %p")
                i["end_time"] = datetime.datetime.fromtimestamp(i["end_timestamp"]).strftime("%Y-%m-%d %H:%M:%S %p")
                i['outlet_name']=outlet_name['name']
                i['outlet_id']=outlet_id
                i['booking_id']=x['_id']['$oid']
                get_service.append(i)
                # get_calendar.append(get_service)
                service_cnt=service_cnt+1
    if Booking == None:
        return  output_json("", MSG_CONST.VENDOR_BOOKINGDATA_FAILED, False, 201)
    else:
        
        return  output_json(get_service, MSG_CONST.VENDOR_BOOKINGDATA_SUCCESS, True, 200)
    
    
def calendar_status(self):
    todayDate = datetime.datetime.now()
    ip_address = socket.gethostbyname(socket.gethostname())
    requestData = dict(request.json)
    outlet_id = requestData['outlet_id']
    booking_id = requestData['booking_id']
    cal_update={}
    cal_update['update_ip'] = ip_address
    cal_update['update_date'] = todayDate
    
    if requestData['status_button'] == "approve":
        cal_update['status'] = 2
        cal_status = DB.find_one("u002_booking",{"spa.outlet_id":str(outlet_id)},"ALL")
        if cal_status:
            cal_update = DB.update_one("u002_booking",cal_update,{"_id":ObjectId(booking_id)})
    elif requestData['status_button'] == "cancel":
        cal_update['status'] = 3
        cal_status = DB.find_one("u002_booking",{"spa.outlet_id":str(outlet_id)},"ALL")
        if cal_status:
            cal_update = DB.update_one("u002_booking",cal_update,{"_id":ObjectId(booking_id)})      
    
    if cal_update == None:
        return output_json({}, MSG_CONST.VENDOR_BOOKINGDATA_FAILED, False, 201)
    else:
        return output_json(cal_update, MSG_CONST.VENDOR_BOOKINGDATA_SUCCESS, True, 200) 

""" 
Created By : Yogesh Kothiya
"""
def getAvailableSlot(self):
    status = True
    message = ""
    code = 200
    responseData = {}
    
    todayDate = datetime.datetime.now()
    ip_address = socket.gethostbyname(socket.gethostname())
    requestData = dict(request.json)
    
    isAvailable = True
    outlet_id = ObjectId(requestData['outlet_id'])
    
    userId = ObjectId(requestData['user_id'])
    vendor_id = ObjectId(requestData['vendor_id'])
    serivce_id = ObjectId(requestData['service_id']) if "service_id" in requestData and requestData["service_id"] else ""
    gender = requestData['gender'].lower() 

    bookingDateStr = requestData['date']

    bookingDate = requestData['date'].split("-")
    bookingDay = datetime.datetime(int(bookingDate[0]),int(bookingDate[1]), int(bookingDate[2]))
    bookingDay = bookingDay.strftime("%A").lower()
    gender = [gender.lower()]
    durationService = requestData["duration"] if requestData["duration"] > 0 else 30
    getOutLetdata = DB.find_one(tbl_v004_outlets,{"_id":outlet_id},{"_id":0,"name":1,"timings."+bookingDay:1,"staff_count":1,"male_count":1,"female_count":1})
    availableSlot = []

    if getOutLetdata:
        isOpen = getOutLetdata["timings"][bookingDay]["isOpen"]

        if isOpen == True or isOpen == "true":
            getBuffer = DB.find_one(tbl_v012_services,{"_id":serivce_id},{"_id":0,"buffer":1,"prices."+str(durationService):1})
            if getBuffer:
                print(getBuffer)
                staff_count = int(getOutLetdata["staff_count"]) if "staff_count" in getOutLetdata else 0
                male_count = int(getOutLetdata["male_count"]) if "male_count" in getOutLetdata else 0
                female_count = int(getOutLetdata["female_count"]) if "female_count" in getOutLetdata else 0

                if requestData['gender'].lower() == "any" and int(male_count) + int(female_count) == 0:
                    responseData = {}
                    message = "No employee available"
                    status = False
                elif requestData['gender'].lower() == 'male' and male_count == 0:
                    responseData = {}
                    message = "No male employee available"
                    status = False
                elif requestData['gender'].lower() == 'female' and female_count == 0:
                    responseData = {}
                    message = "No employee available"
                    status = False
                else:
                    bufferStart = int(getBuffer["buffer"]["before"]) if "buffer" in getBuffer and "before" in getBuffer["buffer"] and getBuffer["buffer"]["before"] else 15

                    bufferEnd = int(getBuffer["buffer"]["after"]) if "buffer" in getBuffer and "after" in getBuffer["buffer"] and getBuffer["buffer"]["after"] else 15
                    
                    slotsList = getOutLetdata["timings"][bookingDay]["slots"]
                    if slotsList:
                        bookingWhere = {}
                        bookingWhere["spa.outlet_id"] = {"$in":[ObjectId(requestData['outlet_id'])]}
                        bookingWhere["spa.services.date"] = {"$eq":requestData['date']}
                        
                        bookingData = DB.find_by_key(tbl_u002_booking,bookingWhere,{"spa.services":1,"_id":0})
                        boockedService = []

                        for s in range(len(bookingData)):
                            for x in range(len(bookingData[s]["spa"])):
                                for ch in range(len(bookingData[s]["spa"][x]["services"])):
                                    boockedService.append(bookingData[s]["spa"][x]["services"][ch])
                        
                        for sl in range(len(slotsList)):
                            startTime  = slotsList[sl]["startTime"]
                            endTime  = slotsList[sl]["endTime"]
                            startTime = startTime.split(" ")
                            startTime = bookingDateStr+ " " + convert24(startTime[0]+":00" + startTime[1])
                            endTime = endTime.split(" ")
                            endTime = bookingDateStr+ " " + convert24(endTime[0]+":00" + endTime[1])
                            startTime = datetime.datetime.strptime(startTime, '%Y-%m-%d %H:%M:%S')
                            endTime = datetime.datetime.strptime(endTime, '%Y-%m-%d %H:%M:%S')
                            i = 0
                            while startTime <= endTime:
                                start_timestamp = int(datetime.datetime.timestamp(startTime))
                                isAvailable = True
                                genderCount = {"male":male_count,"female":female_count,"any":male_count + female_count}
                                totalEmployee = male_count + female_count
                                
                                for x in range(len(boockedService)):
                                    startBookedTime = int(boockedService[x]["start_timestamp"]) - (int(bufferStart) * 60)
                                    boockedService[x]["duration"] = int(boockedService[x]["duration"]) if int(boockedService[x]["duration"]) > 0 else 30

                                    end_timestamp = start_timestamp     

                                    endBookedTime = startBookedTime + (int(boockedService[x]["duration"]) * 60) + bufferEnd * 60
                                    
                                    prefer = boockedService[x]["prefer"].lower()
                                    if int(genderCount[requestData['gender']]) <= 0 or totalEmployee <= 0:
                                        isAvailable = False
                                    elif startBookedTime >= start_timestamp and startBookedTime <= end_timestamp or endBookedTime >= start_timestamp and endBookedTime >= end_timestamp:
                                        isAvailable = True
                                        genderCount[requestData['gender']] = int(genderCount[requestData['gender']]) - 1
                                        totalEmployee = totalEmployee - 1
                                    else:
                                        isAvailable = True
                                price = getBuffer["prices"][str(durationService)] if str(durationService) in getBuffer["prices"] else False
                                availableSlot.append({"availibility":isAvailable,"startTime":datetime.datetime.strftime(startTime, '%I:%M %p'),"duration":requestData["duration"],"remain":totalEmployee,"price":price})
                                startTime = startTime + datetime.timedelta(minutes=15)
                                i = i + 1
                        responseData = availableSlot
                    else:
                        status = False
                        message = "No slots created"
            else:
                status = False
        else:
            status = False
            message = "Today is close"
    else:
        status = False
    response = output_json(responseData,message,status,code)
    return response


def createBooking(self):
    status = True
    message = ""
    code = 200
    responseData = {}

    requestData = request.json
    todaydate = get_current_date().strftime("%Y-%m-%d %H:%M:%S")
    outlet_id   = ObjectId(requestData['outlet_id'])
    userId      = ObjectId(requestData['user_id'])
    vendor_id   = ObjectId(requestData['vendor_id'])
    outletData = DB.find_one(tbl_v004_outlets,{"_id":outlet_id},{"_id":0,"name":1,"allow_customers_gender":1})
    guest_details = requestData["guest_details"]
    bookingDate  = requestData["booking_date"]

    insArr = {}
    insArr["user_id"] = None
    insArr["temp_user_id"] = None
    insArr["status"] = 2 # default
    insArr["spa"] = []
    bookPrice = 0.0
    guestDetails = []
    for x in range(len(guest_details)):
        spaObj = {}
        spaObj["outlet_name"] = outletData["name"]
        spaObj["outlet_id"] = outlet_id
        spaObj["services"] = []

        guestService = {}
        serviceData = DB.find_one(tbl_v012_services,{"_id":ObjectId(guest_details[x]["service_id"])},{"_id":0,"images":1,"name":1,"buffer":1})
        guestService["service_id"] = ObjectId(guest_details[x]["service_id"])
        guestService["name"] = serviceData["name"]
        guestService["images"] = serviceData["images"]
        guestService["service_status"] = 0

        startTime = guest_details[x]["time"]
        endTime  = startTime
        startTime = startTime.split(" ")
        startTime = bookingDate+ " " + convert24(startTime[0]+":00" + startTime[1])
        endTime = endTime.split(" ")
        endTime = bookingDate+ " " + convert24(endTime[0]+":00" + endTime[1]) 
        startTime = datetime.datetime.timestamp(datetime.datetime.strptime(startTime, '%Y-%m-%d %H:%M:%S'))
        endTime = datetime.datetime.timestamp(datetime.datetime.strptime(endTime, '%Y-%m-%d %H:%M:%S')) + (int(guest_details[x]["duration"]) * 60 ) + 60 * int(serviceData["buffer"]["after"]) if "after" in serviceData["buffer"] else 0

        guestService["start_timestamp"] = startTime
        guestService["end_timestamp"] = endTime
        guestService["duration"] = guest_details[x]["duration"]
        guestService["date"] = bookingDate
        guestService["day"] = (datetime.datetime.strptime(bookingDate, '%Y-%m-%d').strftime('%A')).lower()
        guestService["time"] = guest_details[x]["time"]
        guestService["price"] = float(guest_details[x]["price"])
        bookPrice += float(guest_details[x]["price"])
        guestService["convenience_fee"] = 0
        guestService["is_for_guest"] = False
        guestService["guest_details"] = {"gender":guest_details[x]["gender"],"name":guest_details[x]["name"],"mobile":guest_details[x]["mobile"]}
        booking_no = generate_booking_no(guest_details[x]["name"], bookingDate)
        guestService["booking_no"] = booking_no
        
        guestDetails.append({"gender":guest_details[x]["gender"],"name":guest_details[x]["name"],"mobile":guest_details[x]["mobile"],"booking_no":booking_no,"service_id":ObjectId(guest_details[x]["service_id"]),"is_for_guest":False})

        guestService["prefer"] = guest_details[x]["prefer"]
        
        guestService["allow_customers_gender"] = outletData["allow_customers_gender"]
        spaObj["services"].append(guestService)
        insArr["spa"].append(spaObj)
    insArr["created_date"] = todaydate
    insArr["convenience_fee"] = 0
    insArr["gst"] = 0
    insArr["gst_in_percentage"] = 0
    insArr["price"] = round(bookPrice,2)
    insArr["total_price"] = round(bookPrice,2)
    insArr["agree_terms"] = True
    insArr["booking_id"] = ObjectId()
    insArr["donate_ngo"] = False
    insArr["donate_ngo_value"] = 0
    insArr["guest_details"] = guestDetails
    insArr["is_login"] = False
    insArr["paymentData"] = {}
    insArr["subscribe_newsletter"] = False
    insArr["order_id"] = ""
    insArr["payment_status"] = 1
    insArr["payment_currency"] = "INR"
    insArr["payment_id"] = ""
    insArr["payment_method"] = requestData["payment_method"]

    insertId = DB.insert(tbl_u002_booking,insArr)
    if insertId:
        # If need to send SMS then uncomment this code
        """ for x in range(len(guestDetails)):
            notificationObject = {}
            smsObject = {}
            smsObject["to"] = guestDetails[x]["mobile"]
            smsObject["template"] = "vendor_otp"
            smsObject["replace_value1"] = str(OTP)
            smsObject["replace_value2"] = 'login'
            smsObject["replace_value3"] = CONST.SMS_VALID
            
            notificationObject["sms"] = smsObject
            res = requests.post(CONST.NOTIFACTION_CLIENT, json=notificationObject)
            response = dict(res.json()) """
        response = output_json({"orderId":insertId},MSG_CONST.CALANDER_BOOKING_SUCCESS,True,200)
    else:
        response = output_json({"orderId":None},MSG_CONST.CALANDER_BOOKING_FAILED,True,200)
    return response



def generate_booking_no(name,date):
    try:
        s = name.split(" ")
        name_part=""
        for values in s: 
            name_part = name_part+values[0].upper()
            if len(name_part) > 6:
                name_part = name_part[0:6]
        ts_part = str(datetime.now().timestamp()).split(".")[1][-6:]
        return name_part +str(date[0:2])+ ts_part
    except:
        return None

def get_service_data(self,outlet_id):
    data={}   
    arr1=[]
    arr2=[]
    arr3=[]
    selectField = {'spa':1,"_id":1}
    days=1
    current_time = datetime.datetime.now()
    after_time = datetime.datetime.now() + datetime.timedelta(int(days))
    today_date = current_time.strftime("%Y-%m-%d")
    end_date= after_time.strftime("%Y-%m-%d")
    #for all bookings
    if outlet_id != '':
        booking=DB.find_all_where(tbl_u002_booking,{"spa.outlet_id":ObjectId(outlet_id),"status":2,"payment_status":1},selectField)
        if booking != []:
            for bookings in booking: 
                    for spa in bookings['spa']:
                        if spa['outlet_id']['$oid'] == outlet_id:
                            for service in spa['services']:
                                book_date = datetime.datetime.strptime(service['date'],"%Y-%m-%d")
                                service['date'] = book_date.strftime("%d" +" "+ "%b" + ","+" "+ "%Y")
                                service_name=DB.find_one(tbl_v012_services,{"_id":ObjectId(service['service_id']['$oid'])},{"name":1})
                                service['service_name']=service_name['name']
                                arr1.append(service)
    # for today booking
        booking=DB.find_using_aggregate(tbl_u002_booking,[{"$match":{"$and":[{"spa.outlet_id":ObjectId(outlet_id)},{"status":int(2)},{"payment_status":1},{"spa.services.date":str(today_date)}]}},{"$project":{"spa.services":1}}])
        if booking != []:
            for bookings in booking: 
                    for spa in bookings['spa']:
                        if spa['outlet_id']['$oid'] == outlet_id:
                            for service in spa['services']:
                                if str(service['date']) == str(today_date):
                                    book_date = datetime.datetime.strptime(service['date'],"%Y-%m-%d")
                                    service['date'] = book_date.strftime("%d" +" "+ "%b" + ","+" "+ "%Y")
                                    service_name=DB.find_one(tbl_v012_services,{"_id":ObjectId(service['service_id']['$oid'])},{"name":1})
                                    service['service_name']=service_name['name']
                                    arr2.append(service)
    # for tomorrow booking
        booking=DB.find_using_aggregate(tbl_u002_booking,[{"$match":{"$and":[{"spa.outlet_id":ObjectId(outlet_id)},{"status":int(2)},{"payment_status":1},{"spa.services.date":str(end_date)}]}},{"$project":{"spa":1}}])
        if booking != []:
            for bookings in booking: 
                    for spa in bookings['spa']:
                        if spa['outlet_id']['$oid'] == outlet_id:
                            for service in spa['services']:
                                if str(service['date']) == str(end_date):
                                    book_date = datetime.datetime.strptime(service['date'],"%Y-%m-%d")
                                    service['date'] = book_date.strftime("%d" +" "+ "%b" + ","+" "+ "%Y")
                                    service_name=DB.find_one(tbl_v012_services,{"_id":ObjectId(service['service_id']['$oid'])},{"name":1})
                                    service['service_name']=service_name['name']
                                    arr3.append(service)
        data['all']=arr1
        data['today']=arr2
        data['tomorrow']=arr3
    else:
        data['all']=[]
        data['today']=[]
        data['tomorrow']=[]
    return output_json(data, MSG_CONST.VENDOR_BOOKINGDATA_SUCCESS, True, 200)  

def validate_qr_code(self):
    vendor_id = ""
    booking_no = ''
    vendor_id = request.headers.get('Vendor-Id')
    if 'booking-no' in request.args:
        booking_no=request.args.get('booking-no')

    if vendor_id == '0' or vendor_id == '':
        return output_json({},MSG_CONST.VENDOR_ID_NOT_FOUND,False,201)

    # get booking data related to given booking no
    booking_data = DB.find_one(tbl_u002_booking,{"spa.services.booking_no":booking_no},'ALL')

    # format object
    upd_serv_index = 0
    service_data = {}
    for spa in booking_data['spa']:
        outlet_id = spa['outlet_id']['$oid']
        if 'services' in spa:
            for index,service in enumerate(spa['services']):
                if service['booking_no'] == booking_no:
                    upd_serv_index = index
                    service_data = service
                    service_data['outlet_id'] = outlet_id
                    break

    if service_data == {}:
        return output_json({},MSG_CONST.VENDOR_BOOKING_NUMBER_NOT_FOUND,False,201)
    if 'service_status' in service_data and service_data['service_status'] == 1:
        return output_json({},MSG_CONST.USER_SERVICE_AVAIL_BEFORE,False,201)

    current_date = get_current_date()
    dateString = current_date.strftime("%Y-%m-%d")
    if service_data['date'] != dateString:
        return output_json({},MSG_CONST.SERVICE_AVAIL_DATE_NOT_MATCHED,False,201)

    # get vendor id
    outlet_data = {}
    outlet_data = DB.find_one(tbl_v004_outlets,{"_id":ObjectId(service_data['outlet_id'])},{'vendor_id'})
    
    # match vendor id
    if outlet_data == {} or outlet_data == None or outlet_data['vendor_id']['$oid'] != vendor_id:
        return output_json({},MSG_CONST.VENDOR_NOT_FOUND,False,201)
    
    # update service status in of booking
    update_res = DB.update_one(tbl_u002_booking,{"spa.$.services."+str(upd_serv_index)+".service_status":1},{"spa.services.booking_no":booking_no})
    if update_res != 1:
        return output_json({},"Somthing went wrong!",False,201)

    return output_json({},MSG_CONST.QR_CODE_VERIFY_SUCCESS,True,200)

    