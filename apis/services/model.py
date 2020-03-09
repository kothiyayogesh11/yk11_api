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
# tbl_v012_service_type = "v012_service_type"
tbl_v006_service_category = "v006_service_category"
tbl_v012_services = "v012_services"
tbl_v007_services_master = "v007_services_master"
tbl_v023_accomodation = "v023_accomodation"
tbl_v026_tour_steps = "v026_tour_steps"
tbl_v014_amenities = "v014_amenities"


def addServicesModel(self,ns):
    addOutlet = ns.model('addOutletModel', {
        'service_id':fields.String(required=False, description="Provide service id" ),
        'outlet_id':fields.String(required=True, description="Provide newly added outlet id" ),
        'user_id': fields.String(required=True, min_length=1, example=1, description='User id is required'),
        'vendor_id': fields.String(required=True, min_length=1, example=1, description='vendor id is required'),
        'category_id': fields.List(fields.String,required=True, description='Category id is required'),
        'service_master_id':fields.List(fields.String,required=True, description='Service master id is required'),
        'name': fields.String(required=True, min_length=1, description='Address is required'),
        'benefits': fields.List(fields.String,required=False, description='City is required'),
        'note': fields.String(required=False, description='Note is required'),
        'description': fields.String(required=True, description='Description is required'),
        'images': fields.List(fields.String,required=False, description='Images id is required'),
        'buffer': fields.Raw(fields.String,required=True, min_length=1, description='Prices is required'),
        'prices': fields.Raw(fields.String,required=True, description='Prices is required'),
        'is_combo':fields.Integer(required=True, description='Note is required'),
    })
    return addOutlet

def addCategoryModel(self, ns):
    addService = ns.model('addServiceModel', {
        'user_id': fields.String(required=False, description='User id is required'),
        'vendor_id': fields.String(required=False, description='vendor id is required'),
        'category_id': fields.String(required=False, description='Category id is required'),
        'category_name': fields.String(required=True, min_length=1, description='Address is required'),
        'category_description': fields.String(required=False, description='Description is required'),
        'category_image': fields.List(fields.String,required=False, description='Note is required')
    })
    return addService

def CategoryListModel(self, ns):
    ServicesListModel = ns.model('ServicesListModel', {
        'vendor_id': fields.String(required=False, description='vendor id is required'),
        "business_type":fields.String(required=False, description='Business type')
    })
    return ServicesListModel

def removeServiceModel(self, ns):
    removeServiceModel = ns.model('removeServiceModel', {
        'user_id': fields.String(required=True, min_length=3, description='User id is required'),
        'vendor_id': fields.String(required=True, min_length=3, description='vendor id is required'),
        'service_id': fields.String(required=True, min_length=3, description='Service id is required')
    })
    return removeServiceModel

def removeServiceCategoryModel(self, ns):
    removeServiceCategoryModel = ns.model('removeServiceModel', {
        'user_id': fields.String(required=True, min_length=3, description='User id is required'),
        'vendor_id': fields.String(required=True, min_length=3, description='vendor id is required'),
        'category_id': fields.String(required=True, min_length=3, description='Service id is required')
    })
    return removeServiceCategoryModel

def getServiceForBookingModel(self, ns):
    returnServise = ns.model('removeServiceModel', {
        'user_id': fields.String(required=True, min_length=3, description='User id is required'),
        'vendor_id': fields.String(required=True, min_length=3, description='vendor id is required'),
        'outlet_id': fields.String(required=True, min_length=3, description='Service id is required')
    })
    return returnServise


def saveServices(self):
    code = 201
    status = False
    message = ""
    responseData = {}
    # todayDate = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    todayDate = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    ip_address = socket.gethostbyname(socket.gethostname())
    requestData = dict(request.json)
    db_outlet = DB.find_one(tbl_v004_outlets,{'_id':ObjectId(requestData['active_outletid'])})
    responseData['outlet_slug'] = db_outlet['slugs']

    #converting price in integer
    price = requestData['prices']
    for key in price:
        price[key] = int(price[key])
    requestData['prices'] = price
    data = {}
    user_id = 0
    userData = {}
    
    if (requestData["category_id"]== ['other']) and (requestData["service_master_id"]== []):
        category_name = {}
        service_name= {}
        category_name['category_name'] = requestData['service_category']
        # category_name['slug'] =  requestData['service_category'].replace(' ', '-').lower()
        slug = requestData['service_category'].replace(' ', '-').lower()
        find_slug = DB.find_all_where(tbl_v006_service_category,{"slug":slug},'ALL')
        if not(find_slug):
            category_name['slug'] = slug
        else:
            category_name['slug'] = slug+"-2"
        
        type_name = DB.find_one(tbl_v002_vendors,{"_id":ObjectId(requestData["vendor_id"])},{"_id":0,"business_type":1})
        if type_name == {}:
            category_name['type']="day-spa"
        else:
            category_name['type'] = type_name['business_type']
        category_name['status'] = 1
        category_name['vendor_id'] = ObjectId(requestData["vendor_id"])
        category = DB.insert(tbl_v006_service_category,category_name)
        
        
        #Save cetagory_id in Oullet table
        service_cat = []
        if requestData['outlet_id'] != 'all': 
            find_outlet = DB.find_one(tbl_v004_outlets,{"_id":ObjectId(requestData['outlet_id'])},{"_id":0,"services_category":1})
            if find_outlet!={}:
                service_category = find_outlet["services_category"]
                for ids in service_category:
                    category_ids = ids['$oid']
                    category_id = ObjectId(category_ids)
                    service_cat.append(category_id)
                service_cat.append(ObjectId(category))        
                category_insert = DB.update_one(tbl_v004_outlets,{"services_category":service_cat},{"_id":ObjectId(requestData['outlet_id'])})
        
        requestData["category_id"] = ObjectId(category)
        service_name["category_id"] = ObjectId(requestData["category_id"])
        service_name["vendor_id"]= ObjectId(requestData["vendor_id"])
        service_name['name'] = requestData['service_name']
        service_name['status'] = 1
        service = DB.insert(tbl_v007_services_master,service_name)
        requestData["service_master_id"] =  ObjectId(service)
        
    
    if(requestData["service_master_id"] == []) and (requestData["category_id"] != ['other'] and type(requestData["category_id"])!='<class "list">'):
        service_name={}
        service_name["category_id"] = ObjectId(requestData["category_id"])
        service_name["vendor_id"]= ObjectId(requestData["vendor_id"])
        service_name['name'] = requestData['service_name']
        service_name['status'] = 1
        service = DB.insert(tbl_v007_services_master,service_name)
        requestData["service_master_id"] =  ObjectId(service)    
        
        
    requestData["category_id"]   = requestData["category_id"]   
    requestData["user_id"]     = ObjectId(requestData["user_id"])
    requestData["vendor_id"]   = ObjectId(requestData["vendor_id"])
    # requestData["outlet_id"]   = ObjectId(requestData["outlet_id"])
    
    if requestData["category_id"] and isinstance(requestData["category_id"],list):
        for x in range(len(requestData["category_id"])):
            requestData["category_id"][x] = ObjectId(requestData["category_id"][x])
    elif requestData["category_id"] and isinstance(requestData["category_id"],str):
        requestData["category_id"] = [ObjectId(requestData["category_id"])]
    else:
        requestData["category_id"] = [ObjectId(requestData["category_id"])]
    service_id  = requestData["service_id"]
    requestData.pop("service_id")
    
    if requestData["service_master_id"] and isinstance(requestData["service_master_id"],list):
        for x in range(len(requestData["service_master_id"])):
            requestData["service_master_id"][x] = ObjectId(requestData["service_master_id"][x])
    elif requestData["service_master_id"] and isinstance(requestData["service_master_id"],str):
        requestData["service_master_id"] = [ObjectId(requestData["service_master_id"])]
    else:
        requestData["service_master_id"] = [ObjectId(requestData["service_master_id"])]

    get_service = DB.find_all_where(tbl_v012_services,{"vendor_id":ObjectId(requestData["vendor_id"]),"is_delete":0})
    if(get_service):
        responseData['first_service'] = False
    else:
        responseData['first_service'] = True
    if requestData['outlet_id'] == 'all': # for all outlet add
        service_data = []
        outLetData = DB.find_all_where(tbl_v004_outlets,{"vendor_id":requestData["vendor_id"]})
        for x in outLetData:
            outlet_id = x["_id"]['$oid']
            test = copy.copy(requestData)
            test['outlet_id'] = ObjectId(outlet_id)
            test["status"] = 1
            test["is_delete"] = 0
            test["insert_by"] = requestData["user_id"]
            test["insert_date"] = todayDate
            test["insert_ip"] = ip_address
            service_data.append(test)
        act = DB.insert_many(tbl_v012_services,service_data)
        update_tour_steps = DB.update_one(tbl_v026_tour_steps,{"setup_service":True},{"vendor_id":ObjectId(requestData["vendor_id"])})
        service_ids = []
        for service_id in act:
            service_ids.append(ObjectId(service_id))
        # set service id of seleted outlet
        db_response = DB.find_one(tbl_v012_services,{"outlet_id":ObjectId(requestData['active_outletid']),"_id":{"$in":service_ids}})
        responseData["service_id"] = db_response['_id']['$oid']
    ########
        if act:
            if "prices" in requestData and requestData["prices"]:
                min_price = requestData["prices"][min(requestData["prices"], key=requestData["prices"].get)]
                max_price = requestData["prices"][max(requestData["prices"], key=requestData["prices"].get)]
                totalService = DB.count_by_key(tbl_v012_services,{"outlet_id":requestData["outlet_id"],"is_delete":0})
                DB.update_many(tbl_v004_outlets,{"max_price":int(max_price),"min_price":int(min_price),"service_count":totalService},{"_id":requestData["outlet_id"]})
            code = 200
            status = True
            message = MSG_CONST.VENDOR_SERVICES_SUCCESS
        else:
            code = 200
            status = False
            message = MSG_CONST.N_TECH_PROB
    ###########
        
    else:  #for single outlet add
        requestData["outlet_id"]   = ObjectId(requestData["outlet_id"])
        outLetData = DB.find_one(tbl_v004_outlets,{"_id":requestData["outlet_id"],"vendor_id":requestData["vendor_id"]})
        if service_id != "": # for edit
            requestData["update_by"]    = requestData["user_id"]
            requestData["update_date"]  = todayDate
            requestData["update_ip"]    = ip_address
            requestData['is_first_service'] = False
            act = DB.update_one(tbl_v012_services,requestData,{"_id":ObjectId(service_id)})
            responseData["service_id"] = service_id
        elif requestData['outlet_id']!='all': # for single outlet add 
            requestData["status"] = 1
            requestData["is_delete"] = 0
            requestData["insert_by"] = requestData["user_id"]
            requestData["insert_date"] = todayDate
            requestData["insert_ip"] = ip_address
            act = DB.insert(tbl_v012_services,requestData)
            update_tour_steps = DB.update_one(tbl_v026_tour_steps,{"setup_service":True},{"vendor_id":ObjectId(requestData["vendor_id"])})
            responseData["service_id"] = act
        
        if act:
            if "prices" in requestData and requestData["prices"]:
                min_price = requestData["prices"][min(requestData["prices"], key=requestData["prices"].get)]
                max_price = requestData["prices"][max(requestData["prices"], key=requestData["prices"].get)]
                totalService = DB.count_by_key(tbl_v012_services,{"outlet_id":requestData["outlet_id"],"is_delete":0})
                DB.update_one(tbl_v004_outlets,{"max_price":int(max_price),"min_price":int(min_price),"service_count":totalService},{"_id":requestData["outlet_id"]})
            code = 200
            status = True
            message = MSG_CONST.VENDOR_SERVICES_SUCCESS
        else:
            code = 200
            status = False
            message = MSG_CONST.N_TECH_PROB

    response = output_json(responseData,message,status,code)
    #logging.debug('vendor_services_manage: {}'.format(response))
    return response

def getOutLetServicesCategory(self):
    code = 200
    status = False
    message = ""
    responseData = {}
    catData = []
    where = {}
    where['vendor_id'] = ObjectId(request.args.get("vendor_id")) if request.args.get("vendor_id") != "" else ""
    if request.args.get("category_id") and request.args.get("category_id") != "":
        where["_id"] = ObjectId(request.args.get("category_id"))
        catData = DB.find_one(tbl_v006_service_category,where,{"category_name":1,"category_description":1,"category_image":1})
        if catData:
            catData["_id"] = catData["_id"]["$oid"]    
            code = 200
            status = True
            message = MSG_CONST.VENDOR_SERVICES_SUCCESS
        else:
            code = 201
            status = False
            message = MSG_CONST.VENDOR_OUTLET_NOT_FOUND
    else:
        where["is_delete"] = 0
        getCategory = DB.find_by_key(tbl_v006_service_category,where,{"category_name":1,"category_description":1,"category_image":1})
        if getCategory:
            for data in getCategory:
                data["_id"] = data["_id"]["$oid"]
                catData.append(data)
            code = 200
            status = True
            message = MSG_CONST.VENDOR_SERVICES_SUCCESS
        else:
            code = 201
            status = False
            message = MSG_CONST.VENDOR_OUTLET_NOT_FOUND
    
    responseData = catData
    response = output_json(responseData,message,status,code)
    #logging.debug('vendor_services_list: {}'.format(response))
    return response

def saveCategoryServices(self):
    code = 201
    status = False
    message = ""
    responseData = {}
    requestData = dict(request.json)
    category_id = requestData["category_id"] if "category_id" in requestData else ""
    
    addData = {}
    if requestData["vendor_id"] and requestData["vendor_id"] != "":
        addData["vendor_id"] = ObjectId(requestData["vendor_id"])
    if requestData["user_id"] and requestData["user_id"] != "":
        addData["user_id"] = ObjectId(requestData["user_id"])

    addData["category_name"] = requestData["category_name"]
    addData["category_description"] = requestData["category_description"]
    addData["category_image"] = requestData["category_image"]
    
    
    if category_id != "":
        outLetData = DB.find_one(tbl_v006_service_category,{"_id":ObjectId(category_id)})
        if outLetData:
            act = DB.update_one(tbl_v006_service_category, addData, {"_id":ObjectId(category_id)})
        else: 
            act = False
        if act:
            responseData["category_id"] = str(act)
            code = 200
            status = True
            message = MSG_CONST.VENDOR_SERVICES_SUCCESS
        else:
            code = 200
            status = False
            message = MSG_CONST.N_TECH_PROB
    else:
        addData["status"] = 2
        addData["is_delete"] = 0
        act = DB.insert(tbl_v006_service_category,addData)
        if act:
            responseData["category_id"] = str(act)
            code = 200
            status = True
            message = MSG_CONST.VENDOR_SERVICES_SUCCESS
        else:
            code = 200
            status = False
            message = MSG_CONST.N_TECH_PROB

    response = output_json(responseData,message,status,code)
    #logging.debug('vendor_services category_manage: {}'.format(response))
    return response

def category_list_for_service(self):
    code = 201
    status = False
    message = ""
    responseData = {}
    requestData = dict(request.json)
    vendor_id = requestData["vendor_id"] if "vendor_id" in requestData else ""
    
    if vendor_id:
        vendor_id = ObjectId(requestData["vendor_id"])
        
        categoryData = DB.find_by_key(tbl_v006_service_category,{"$and":[{"$or":[{"vendor_id":vendor_id},{"is_default":1}]},{"type":requestData["business_type"]}]},{"_id":1,"category_name":1})
        if categoryData:
            resData = []
            for x in categoryData:
                x["_id"] = str(x["_id"]["$oid"])
                resData.append(x)
            responseData = resData
            status = True
            message = MSG_CONST.VENDOR_SUCCESS
            code = 200
        else:
            status = False
            message = MSG_CONST.N_TECH_PROB
            code = 201
    else:
        status = False
        message = MSG_CONST.VENDOR_OUTLET_NOT_FOUND
        code = 201
    response = output_json(responseData,message,status,code)
    #logging.debug('vendor_services category_list: {}'.format(response))
    return response


def getServicesByVendor(self):
    code = 200
    status = False
    message = ""
    responseData = []
    serData = []
    where = {}
   
    if request.args.get("vendor_id") and request.args.get("vendor_id") != "":
        where["vendor_id"] = ObjectId(request.args.get("vendor_id"))
        where["is_delete"] = 0
        where["status"] = 1
        if request.args.get("outlet_id"):
            where["outlet_id"] = ObjectId(request.args.get("outlet_id"))
        serData = DB.find_by_key(tbl_v012_services,where)
        
        if serData:
            
            getCat = DB.find_all(tbl_v006_service_category,{"category_name":1,"_id":1})
            
            catData = {}
            if getCat:
                for c in getCat:
                    if "category_name" in c and c["category_name"] != "":
                        catData[c["_id"]["$oid"]] = c["category_name"]
            
            getOut = DB.find_all(tbl_v004_outlets,{"name":1,"_id":1})
            outData = {}
            if getOut:
                for c in getOut: 
                   outData[c["_id"]["$oid"]] = c["name"]
            
            resData = []
            for x in serData:
                x["_id"]            = str(x["_id"]["$oid"])
                
                if "$oid" in x["user_id"]:
                    x["user_id"]        = str(x["user_id"]["$oid"])
                x["vendor_id"]      = str(x["vendor_id"]["$oid"])
                x["outlet_id"]      = str(x["outlet_id"]["$oid"])

                
                if "service_master_id" in x:
                    if isinstance(x["service_master_id"],list):
                        for sm in range(len(x["service_master_id"])):
                            x["service_master_id"][sm] = x["service_master_id"][sm]["$oid"] if "$oid" in x["service_master_id"][sm] else x["service_master_id"][sm]
                    else:
                        x["service_master_id"] = [x["service_master_id"]["$oid"] if "$oid" in x["service_master_id"] else x["service_master_id"]]

                if x["outlet_id"] in outData:
                    x["outlet_name"] = outData[x["outlet_id"]]
                catId = []
                if isinstance(x["category_id"],list):
                    for ci in range(len(x["category_id"])):
                        x["category_id"][ci]    = x["category_id"][ci]["$oid"]
                        if x["category_id"][ci] in catData:
                            catId.append({"category_id":x["category_id"][ci],"name":catData[x["category_id"][ci]].title()})
                            
                    x["category_id"] = catId
                else:
                    x["category_id"] = x["category_id"]["$oid"] if "$oid" in x["category_id"] else ""
                    if x["category_id"] in catData:
                        x["category_id"] =[{"category_id":x["category_id"],"name":catData[x["category_id"]].title()}]
                resData.append(x)
            responseData = list(reversed(resData))
            code = 200
            status = True
            message = MSG_CONST.VENDOR_SERVICES_SUCCESS
        else:
            code = 201
            status = False
            message = MSG_CONST.VENDOR_OUTLET_NOT_FOUND
    else:
        code = 201
        status = False
        message = MSG_CONST.VENDOR_EMPTY_ID
    
    response = output_json(responseData,message,status,code)
    #logging.debug('vendor_services_list: {}'.format(response))
    return response

def getServices(self):
    code = 200
    status = False
    message = ""
    responseData = {}
    serData = []
    where = {}

    if request.args.get("service_id") and request.args.get("service_id") != "":
        where["_id"] = ObjectId(request.args.get("service_id"))
        
        where["is_delete"] = 0
        where["status"] = 1
        serData = DB.find_one(tbl_v012_services,where)
        
        if serData:
            
            getCat = DB.find_all(tbl_v006_service_category,{"category_name":1,"_id":1})
            catData = {}
            if getCat:
                
                for c in getCat:
                    if "category_name" in c:
                        catData[c["_id"]["$oid"]] = c["category_name"]
            
            getOut = DB.find_all(tbl_v004_outlets,{"name":1,"_id":1})
            outData = {}
            if getOut:
                for c in getOut: 
                   outData[c["_id"]["$oid"]] = c["name"]
            
            resData = []
            serData["_id"]            = str(serData["_id"]["$oid"])
            if "$oid" in serData["user_id"]:
                serData["user_id"]        = str(serData["user_id"]["$oid"])
            serData["vendor_id"]      = str(serData["vendor_id"]["$oid"])
            serData["outlet_id"]      = str(serData["outlet_id"]["$oid"])
            
            if "service_master_id" in serData:
                    if isinstance(serData["service_master_id"],list):
                        for sm in range(len(serData["service_master_id"])):
                            serData["service_master_id"][sm] = serData["service_master_id"][sm]["$oid"] if "$oid" in serData["service_master_id"][sm] else serData["service_master_id"][sm]
                    else:
                        serData["service_master_id"] = serData["service_master_id"]["$oid"] if "$oid" in serData["service_master_id"] else serData["service_master_id"]
            
            if serData["outlet_id"] in outData:
                serData["outlet_name"] = outData[serData["outlet_id"]]
            
            catList = []
            catId = []
            if isinstance(serData["category_id"], list):
                
                for ci in range(len(serData["category_id"])):
                    
                    lCatId = serData["category_id"][ci]["$oid"] if "$oid" in serData["category_id"][ci] else serData["category_id"][ci]
                    catName = catData[lCatId] if lCatId in catData else ""
                    catList.append({"category_id":serData["category_id"][ci]["$oid"],"name":catName})
                    catId.append(serData["category_id"][ci]["$oid"])
            else:
                serData["category_id"]    = str(serData["category_id"]["$oid"])
                if serData["category_id"] in catData:
                    catList.append({"category_id":serData["category_id"],"name":catData[serData["category_id"]]})
                    catId.append(serData["category_id"])
            
            serData["category_data"] = catList
            serData["category_id"] = catId
            responseData = serData
            code = 200
            status = True
            message = MSG_CONST.VENDOR_SERVICES_SUCCESS
        else:
            code = 201
            status = False
            message = MSG_CONST.VENDOR_OUTLET_NOT_FOUND
    else:
        code = 201
        status = False
        message = MSG_CONST.VENDOR_EMPTY_ID
    
    response = output_json(responseData,message,status,code)
    #logging.debug('vendor_services_list: {}'.format(response))
    return response

def removeService(self):
    code = 200
    status = False
    message = ""
    responseData = {}
    # todayDate = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    todayDate = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    ip_address = socket.gethostbyname(socket.gethostname())
    requestData = dict(request.json)
    
    vendor_id = ObjectId(requestData["vendor_id"])
    user_id = ObjectId(requestData["user_id"])
    service_id = ObjectId(requestData["service_id"])
    serviceData = DB.find_one(tbl_v012_services,{"_id":service_id},{"_id":1,"is_delete":1})
    if serviceData:
        act = DB.update_one(tbl_v012_services,{"is_delete":1,"update_by":user_id,"update_date":todayDate,"update_id":ip_address},{"_id":service_id})
        if act:
            status = True
            message = MSG_CONST.VENDOR_SERVICES_REMOVE_SUCCESS
            code = 200
        else:
            status = False
            message = MSG_CONST.VENDOR_SERVICES_REMOVE_FAILED
            code = 200
    else:
        status = False
        message = MSG_CONST.N_TECH_PROB
        code = 200
    
    response = output_json(responseData,message,status,code)
    #logging.debug('vendor_services_remove: {}'.format(response))
    return response

def removeServiceCategory(self):
    code = 200
    status = False
    message = ""
    responseData = {}
    # todayDate = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    todayDate = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    ip_address = socket.gethostbyname(socket.gethostname())
    requestData = dict(request.json)
    
    vendor_id = ObjectId(requestData["vendor_id"])
    user_id = ObjectId(requestData["user_id"])
    category_id = ObjectId(requestData["category_id"])
    serviceData = DB.find_one(tbl_v006_service_category,{"_id":category_id},{"_id":1,"is_delete":1})
    if serviceData:
        act = DB.update_one(tbl_v006_service_category,{"is_delete":1,"update_by":user_id,"update_date":todayDate,"update_id":ip_address},{"_id":category_id})
        if act:
            status = True
            message = MSG_CONST.VENDOR_SERVICES_CATEGORY_REMOVE_SUCCESS
            code = 200
        else:
            status = False
            message = MSG_CONST.VENDOR_SERVICES_CATEGORY_REMOVE_FAILED
            code = 200
    else:
        status = False
        message = MSG_CONST.N_TECH_PROB
        code = 200
    response = output_json(responseData,message,status,code)
    #logging.debug('vendor_services_category_remoeve: {}'.format(response))
    return response

def getMasterServiceByCategory(self):
    code = 200
    status = False
    message = ""
    responseData = {}
    # todayDate = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    todayDate = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    ip_address = socket.gethostbyname(socket.gethostname())
    requestData = dict(request.json)
    category_id = requestData["category_id"] if "category_id" in requestData and requestData["category_id"] else ""
    vendor_id = requestData["vendor_id"] if "vendor_id" in requestData and requestData["vendor_id"] else ""

    for x in range(len(category_id)):
        category_id[x] = ObjectId(category_id[x])
    
    if category_id:
        serviceData = DB.find_by_key(tbl_v007_services_master,{"$and":[{"$or":[{"vendor_id":ObjectId(vendor_id)},{"is_default":1}]},{"category_id":{"$in":category_id}}]},{"_id":1,"name":1})
    else:
        serviceData = {}
    
    serCat = []
    if serviceData:
        for x in serviceData:
            serCat.append({"_id":x["_id"]["$oid"],"name":x["name"]})
        serCat.append({"_id":"other","name":"Other"})
        responseData = serCat
        status = True
        message = MSG_CONST.VENDOR_SUCCESS
        code = 200
    else:
        serCat.append({"_id":"other","value":"other","name":"Other"})
        responseData = serCat
        status = True
        message = MSG_CONST.VENDOR_NO_RECORD_FOUND
        code = 200
        # print(serCat)
    response = output_json(responseData,message,status,code)
    #logging.debug('vendor_services_category_remoeve: {}'.format(response))
    return response

def getServiceListMethod(self):
    code = 200
    status = False
    message = ""
    responseData = {}
    # todayDate = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    todayDate = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    ip_address = socket.gethostbyname(socket.gethostname())
    requestData = dict(request.json)
    where = {}
    if "vendor_id" in requestData and requestData["vendor_id"]:
        where["vendor_id"] = ObjectId(requestData["vendor_id"])

    if "outlet_id" in requestData and requestData["outlet_id"]:
        where["outlet_id"] = ObjectId(requestData["outlet_id"])
    serviceData = DB.find_by_key(tbl_v012_services,where,{"_id":1,"name":1,"prices":1})
    if serviceData:
        for x in range(len(serviceData)):
            serviceData[x]["_id"] = serviceData[x]["_id"]["$oid"]
        responseData = serviceData
        status = True
        message = MSG_CONST.VENDOR_SUCCESS
        code = 200
    else:
        status = False
        message = MSG_CONST.VENDOR_NO_RECORD_FOUND
        code = 200
    
    response = output_json(responseData,message,status,code)
    #logging.debug('vendor_services_get_all_by_vendor_outlet: {}'.format(response))
    return response

def category_data(self):
    fields = {"_id":1,"category_name":1}
    get_category=DB.find_all(tbl_v006_service_category,fields)
    return output_json(get_category, True, 200)

def service_data(self):
    requestData = dict(request.json)
    category_id = requestData['category_id']
    fields = {"_id":0,"name":1}
    get_service=DB.find_all_where(tbl_v007_services_master,{"category_id":ObjectId(category_id)},fields)
    return output_json(get_service, True, 200)



def get_accomodation_data(self,outlet_id,accomodation_id):
    code = 201
    status = False
    message = ""
    responseData = {}
    Data = {}
    # print(accomodation_id)
    fieldsList = {"_id":1,"title":1,"room_type":1,"city":1,"price":1,"max_person":1,"amenities":1}
    if accomodation_id != "":
        get_accomodation_Data =  DB.find_using_aggregate(tbl_v023_accomodation,[{"$match":{"_id":ObjectId(accomodation_id)}},{"$project":fieldsList}])
        Data['accomodation_data'] = get_accomodation_Data[0]
    else:
        Data['accomodation_data'] = ''

    # Get Aminities
    Data['amenities'] = []
    amenitiesData = DB.find_by_key(tbl_v014_amenities,{"status":1},{"title":1,"_id":1})
    if amenitiesData:
        for x in amenitiesData:
            Data['amenities'].append(x["title"])


    code = 200
    status = True
    message = "data got successfully"
    response = output_json(Data,message,status,code)
    #logging.debug('get_accomodation_data: {}'.format(response))
    return response


def save_accomodation(self):
    import datetime;
    code = 201
    status = False
    message = ""
    responseData = {}
    addData = {}
    todayDate = datetime.datetime.now();
    ip_address = socket.gethostbyname(socket.gethostname())
    requestData = dict(request.json)
    fieldsList = {"_id":1,"title":1,"room_type":1,"city":1,"price":1,"max_person":1,"amenities":1}

    addData["outlet_id"] = ObjectId(requestData["outlet_id"])
    addData["title"] = requestData["title"]
    addData["room_type"] = requestData["room_type"]
    addData["city"] = requestData["city"]
    addData["price"] = int(requestData["price"])
    addData["max_person"] = int(requestData["max_person"])
    addData["amenities"] = int(requestData["amenities"])
    addData['created_on'] = todayDate
    addData['created_by'] = ObjectId(requestData["user_id"])
    addData["insert_ip"] = ip_address
    addData["is_delete"] = 0
    if requestData["accomodation_id"] == "":
        act = DB.insert(tbl_v023_accomodation,addData)
        code = 200
        status = True
        message = "Accomodation inserted successfully..!"    
    else:
        act = DB.update_one(tbl_v023_accomodation,{"title":requestData["title"],"room_type":requestData["room_type"],"city":requestData["city"],"price":int(requestData["price"]),"max_person":int(requestData["max_person"]),"amenities":int(requestData["amenities"]),"updated_on":todayDate,"updated_by":ObjectId(requestData["user_id"]),"updated_ip":ip_address},{"_id":ObjectId(requestData['accomodation_id'])})
        code = 200
        status = True
        message = "Accomodation updated successfully..!"
    response = output_json(responseData,message,status,code)
    #logging.debug('add_offer: {}'.format(response))
    return response
    
    
def get_all_accomodation_data(self,outlet_id):
    code = 201
    status = False
    message = ""
    responseData = {}
    addData = {}
    get_all_Data = {}
    fieldsList = {"_id":1,"title":1,"room_type":1,"city":1,"price":1,"max_person":1,"amenities":1}
    get_all_Data = DB.find_using_aggregate(tbl_v023_accomodation,[{"$match":{"outlet_id":ObjectId(outlet_id),"is_delete":0}},{"$sort":{"_id":-1}},{"$project":fieldsList}])
    if(get_all_Data):
            code = 200
            status = True
            message = "Data get Successfully..!"
    else :
        code = 200
        status = False
        message = "technical problem..!"
    response = output_json(get_all_Data,message,status,code)
    #logging.debug('get_all_Data: {}'.format(response))
    return response


def delete_accomodation_data(self): 
    code = 201
    status = False
    message = ""
    responseData = {}
    addData = {}
    requestData = dict(request.json)
    accomodation_id = requestData['accomodation_id']
    code = 201
    delete_accomodation = DB.find_one(tbl_v023_accomodation,{"_id":ObjectId(accomodation_id)})
    if(delete_accomodation):
        updateStatus = DB.update_one(tbl_v023_accomodation,{"is_delete":1},{"_id":ObjectId(accomodation_id)}) 
        if updateStatus:
            code = 200
            status = True
            message = "Data Deleted SuccessFully..!"
        else :
            code = 201
            status = False
            message = "Something Went Wrong..!"
    response = output_json(addData,message,status,code)
    #logging.debug('delete_accomodation_data: {}'.format(response))
    return response