from flask_restplus import Namespace, fields
import socket
import time
import re
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
import dateutil
import isodate
import datetime
import pdb

##logging.basicConfig(filename='vendor.log', level=logging.DEBUG)   

# Declare tables name in vars
tbl_v002_vendors = "v002_vendors"
tbl_v003_vendor_users = "v003_vendor_users"
tbl_v004_outlets = "v004_outlets"
tbl_v014_amenities = "v014_amenities"
tbl_v015_membership = "v015_membership"
tbl_v016_subscription = "v016_subscription"
tbl_u002_booking = "u002_booking"
tbl_v012_services = "v012_services"
tbl_v026_tour_steps = "v026_tour_steps"





def get_count_data(self,outlet_id,vendor_id):
    table_name = ["u002_booking","v012_services","v003_vendor_users"]
    Total_count = {}
    for table in table_name:
        if table == "u002_booking":
            get_count = DB.find_using_aggregate(table,[{"$match": {"spa.outlet_id":str(outlet_id)}},{"$count":"count"}])
        elif table == "v012_services":
            get_count = DB.find_using_aggregate(table,[{"$match": {"outlet_id":ObjectId(outlet_id)}},{"$count":"count"}])
        elif table == "v003_vendor_users":
            get_count = DB.find_using_aggregate(table,[{"$match": {"vendor_id":ObjectId(vendor_id)}},{"$count":"count"}])
        count_arr=table.split('_') 
        if get_count!=[]:
            for x in get_count:
                Total_count[count_arr[1]] = x['count']
        else:
            Total_count[count_arr[1]] = 0
    return  output_json(Total_count, MSG_CONST.VENDOR_BOOKINGDATA_SUCCESS, True, 200)


def get_analytics(self,vendor_id,outlet_id):
    res_data={}
    data=[]
    days = 30
    # if request_type == "Last 15 Days":
    #     days = 15
    # elif request_type == "Last 30 Days":
    #    days = 30
    # elif request_type == "Last 60 Days":
    #    days = 60
    current_time = datetime.datetime.now()
    after_time = datetime.datetime.now() - datetime.timedelta(days)
    d = current_time.strftime("%Y-%m-%d %H:%M:%S")
    e = after_time.strftime("%Y-%m-%d %H:%M:%S")
    getAll = DB.find_all_where(tbl_v004_outlets,{'vendor_id':ObjectId(vendor_id)},{'name':1,'area':1,'status':1})
    
    if outlet_id != "":
        for x in getAll:

            # booking_count = DB.find_using_aggregate("u002_booking",[{"$match": {"insert_date":{"$gte": dateutil.parser.parse(e),"$lte":dateutil.parser.parse(d)},"spa.outlet_id":ObjectId(x['_id']['$oid']),"status":2}},{"$count":"count"}])
            booking_count = DB.find_using_aggregate("u002_booking",[{"$match":{"spa.outlet_id":ObjectId(x['_id']['$oid']),"status":2}},{"$count":"count"}])
            if booking_count!=[]:
                x['booking_count']=booking_count[0]['count']
            else:
                x['booking_count']=0

            service_count = DB.find_using_aggregate("v012_services",[{"$match":{"outlet_id":ObjectId(x['_id']['$oid']),"status":1,"is_delete":0}},{"$count":"count"}])
            if service_count!=[]:
                x['service_count']=service_count[0]['count']
            else:
                x['service_count']=0

            staff_count = DB.find_using_aggregate("v003_vendor_users",[{"$match": {"outlet_id":ObjectId(x['_id']['$oid']),"is_delete":0}},{"$count":"count"}])
            if staff_count!=[]:
                x['staff_count']=staff_count[0]['count']
            else:
                x['staff_count']=0        

            feedback_count = DB.find_using_aggregate("v013_feedback",[{"$match": {"outlet_id":ObjectId(x['_id']['$oid'])}},{"$count":"count"}])
            if feedback_count!=[]:
                x['feedback_count']=feedback_count[0]['count']
            else:
                x['feedback_count']=0
            
            offer_count = DB.find_using_aggregate("v019_offer_details",[{"$match": {"outlet_id":ObjectId(x['_id']['$oid']),"is_delete":0}},{"$count":"count"}])
            if offer_count!=[]:
                x['offer_count']=offer_count[0]['count']
            else:
                x['offer_count']=0                        

            data.append(x)
        res_data['outlet_list']=data
        booking = DB.find_all_where("u002_booking",{"$and":[{"spa.outlet_id":ObjectId(outlet_id),"status":int(2)}]},"ALL")
        res_data['booking']=booking
    else:
        res_data['outlet_list']=[]
        res_data['booking']=[] 

    
    
    GetToursteps = DB.find_all_where(tbl_v026_tour_steps,{'vendor_id':ObjectId(vendor_id)},"ALL")
    res_data['tour_steps'] = GetToursteps
    
    if outlet_id != "":
        GetTotalSales = DB.find_all_where("u002_booking",{"$and":[{"spa.outlet_id":ObjectId(outlet_id),"status":int(2)}]},{"_id":0,"total_price":1})
        tot_price = []
        for x in GetTotalSales:
            price = x['total_price']
            tot_price.append(price)
        total_price = sum(tot_price)     
        res_data['total_sale'] = total_price
        
        GetPendingOutlets = DB.find_using_aggregate("v004_outlets",[{"$match":{"vendor_id":ObjectId(vendor_id),"status":0,"is_delete":0}},{"$count":"count"}])     
        res_data['pending_outlets'] = GetPendingOutlets
        
        GetTotalBooking = DB.find_using_aggregate("u002_booking",[{"$match":{"spa.outlet_id":ObjectId(outlet_id)}},{"$count":"count"}])
        res_data['total_booking'] = GetTotalBooking
        
        GetTotalFeedback = DB.find_using_aggregate("v013_feedback",[{"$match":{"vendor_id":ObjectId(vendor_id)}},{"$count":"count"}])
        res_data['total_feedback'] = GetTotalFeedback
        
    else:
        res_data['total_sale'] = 0
        res_data['pending_outlets'] = []
        res_data['total_booking'] = []
        res_data['total_feedback'] = []
    
    return  output_json(res_data, MSG_CONST.DASHBOARD_STATS, True, 200)


# def get_count_data(self):
#     days = 7
#     Total_count = {}
#     current_time = datetime.datetime.now()
#     after_time = datetime.datetime.now() - datetime.timedelta(days)
#     d = current_time.strftime("%Y-%m-%d %H:%M:%S")
#     e = after_time.strftime("%Y-%m-%d %H:%M:%S")
#     table_name = ["u002_booking","v012_services","v003_vendor_users"]
   
#     for table in table_name:
#         if table == "u002_booking":
#             get_count = DB.find_using_aggregate(table,[{"$match": {"created_date":{"$gte": str(dateutil.parser.parse(e)),"$lte":str(dateutil.parser.parse(d))}}},{"$count":"count"}])
#         elif table == "v012_services":
#             get_count = DB.find_using_aggregate(table,[{"$match": {"start_date":{"$gte": str(dateutil.parser.parse(e)),"$lte":str(dateutil.parser.parse(d))}}},{"$count":"count"}])
#         elif table == "v003_vendor_users":
#             get_count = DB.find_using_aggregate(table,[{"$count":"count"}])
#         count_arr=table.split('_') 
#         if get_count!=[]:
#             for x in get_count:
#                 Total_count[count_arr[1]] = x['count']
#         else:
#             Total_count[count_arr[1]] = 0
#     return  output_json(Total_count, MSG_CONST.VENDOR_BOOKINGDATA_SUCCESS, True, 200)


# def total_count_data(self,request_type):
#     days = 7
#     fieldsList = {"_id":1}
#     if request_type == "Last 15 Days":
#         days = 15
#     elif request_type == "Last 30 Days":
#        days = 30
#     elif request_type == "Last 60 Days":
#        days = 60
    
#     Total_count = {}
#     current_time = datetime.datetime.now()
#     after_time = datetime.datetime.now() - datetime.timedelta(days)
#     d = current_time.strftime("%Y-%m-%d %H:%M:%S")
#     e = after_time.strftime("%Y-%m-%d %H:%M:%S")
#     table_name = ["u002_booking","v012_services","v003_vendor_users"]
   
#     for table in table_name:
#         if request_type == "All":
#                 get_count = DB.find_using_aggregate(table,[{"$count":"count"}])
#         else:
#             if table == "u002_booking":
#                 get_count = DB.find_using_aggregate(table,[{"$match": {"created_date":{"$gte": str(dateutil.parser.parse(e)),"$lte":str(dateutil.parser.parse(d))}}},{"$count":"count"}])
#             elif table == "v012_services":
#                 get_count = DB.find_using_aggregate(table,[{"$match": {"start_date":{"$gte": str(dateutil.parser.parse(e)),"$lte":str(dateutil.parser.parse(d))}}},{"$count":"count"}])
#             elif table == "v003_vendor_users":
#                 get_count = DB.find_using_aggregate(table,[{"$count":"count"}])
#         count_arr=table.split('_')
#         if get_count!=[]:
#             for x in get_count:
#                 Total_count[count_arr[1]] = x['count']
#         else:
#             Total_count[count_arr[1]] = 0
#     return  output_json(Total_count, MSG_CONST.VENDOR_BOOKINGDATA_SUCCESS, True, 200)
    
    

# def button_data(self):
#     status = True
#     message = ""
#     code = 200
#     responseData = {}
    
#     fieldsList = {"name":1}
#     getAll = DB.find_all(tbl_v004_outlets,fieldsList)
#     output_json(responseData, message, status, code)
#     #logging.debug('vendor_outlet_get_details: {}'.format(response))
#     return response 
