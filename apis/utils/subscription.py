# Create By : Yogesh Kothiya
# Uses : Manage Role

from flask import jsonify, request
import socket
from datetime import datetime, date, time, timedelta
import pymongo
from database import DB
import json
from bson import json_util, ObjectId


class VendorSubscription:
    def __init__(self,vendor_id=None,user_id=None):
        self.todayDate = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.ip_address = socket.gethostbyname(socket.gethostname())
        self.user_id = user_id
        self.vendor_id = vendor_id
        self.tbl_v016_subscription = "v016_subscription"
        self.tbl_v015_membership = "v015_membership"
        self.membership_id       = None

    def getVendorSubscription(self):
        """ Remove payment status condition "payment_status":1, as per jay instruction """
        getSubscription_arr = DB.find_all_where(self.tbl_v016_subscription,{"vendor_id":ObjectId(self.vendor_id),"expiry_date":{"$gte": self.todayDate},"start_date":{"$lte": self.todayDate},"status":1},'ALL','last')
        if getSubscription_arr!=[]:
            getSubscription=getSubscription_arr[-1]
        else:
            getSubscription=[]
            
        if getSubscription:
            getSubscription["subscription_id"] = getSubscription["_id"]["$oid"]
            getSubscription.pop("_id")
            getSubscription["user_id"]   = getSubscription["user_id"]["$oid"]
            getSubscription["vendor_id"] = getSubscription["vendor_id"]["$oid"]
            getSubscription["plan_id"]   = getSubscription["plan_id"]["$oid"]
            self.membership_id           = getSubscription["plan_id"]
            planData = self.getMembershipAccess()
            if planData:
                getSubscription.update(planData)
        else:
            getSubscription = {}
        return getSubscription

    def getMembershipAccess(self):
        planData = DB.find_one(self.tbl_v015_membership,{"_id":ObjectId(self.membership_id)},{"features":0})
        if planData:
            planData["features_id"] = planData["_id"]["$oid"]
            planData.pop("_id")
        return planData

    def addMemberShip(self,subData={}):
        # Get Plan data
        #plan_data = DB.find_one(self.tbl_v015_membership,{"_id":ObjectId(subData["plan_id"])})

        insData = {} 
        
        insData["user_id"]      = ObjectId(subData["user_id"])
        insData["vendor_id"]    = ObjectId(subData["vendor_id"])
        insData["plan_id"]      = ObjectId(subData["plan_id"])
        insData["price"]        = subData["price"]
        insData["tax"]          = subData["tax"]
        insData["tot_price"]    = subData["tot_price"]
        insData["txn_id"]       = subData["txn_id"]
        insData["payment_type"] = subData["payment_type"]
        insData["payment_status"]= subData["payment_status"]
        insData["payment_date"] = subData["payment_date"]
        insData["type"]         = subData["type"]
        insData["expiry_date"]  = subData["expiry_date"]
        insData["start_date"]   = subData["start_date"]
        insData["status"]       = subData["status"]
        insData["created_date"] = subData["created_date"]

        # Set Plan data
        #insData["plan_data"] = plan_data
        
        addPlan = DB.insert(self.tbl_v016_subscription,insData)
        
        return addPlan