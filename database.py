import pymongo
from flask import Flask
from bson import json_util, ObjectId
import json
import random, string
from flask_restplus import fields, marshal
from datetime import datetime, date, time, timedelta
from pytz import timezone
import pytz
india_tz = pytz.timezone('Asia/Kolkata')


class DB(object):
    def __init__(self):
        pass
            
    @staticmethod
    def init(app):
        """ client = pymongo.MongoClient(app.config["MONGO_URI"])
        DB.DATABASE = client[app.config["DB_NAME"]] """

    @staticmethod
    def insert(collection, data):
        insertId = DB.DATABASE[collection].insert(data)
        return str(insertId)

    @staticmethod
    def find_one(collection, query,fields='ALL', sorts=None):
        if fields == "ALL":
            data = DB.DATABASE[collection].find_one(query)
        else:
            data = DB.DATABASE[collection].find_one(query,fields)
        if sorts:
            data.sort(sorts)

        page_sanitized = json.loads(json_util.dumps(data))
        return page_sanitized

    @staticmethod
    def find_all(collection,fields={}):
        if fields:
            page_sanitized = json.loads(json_util.dumps(DB.DATABASE[collection].find({},fields)))
        else:
            page_sanitized = json.loads(json_util.dumps(DB.DATABASE[collection].find()))
        return page_sanitized

    # @staticmethod
    # def find_all_where(collection,query,fields='ALL',sorts=None):
    #     if fields == "ALL":
    #         page_sanitized = json.loads(json_util.dumps(DB.DATABASE[collection].find(query)))
    #     else:
    #         page_sanitized = json.loads(json_util.dumps(DB.DATABASE[collection].find(query,fields)))
    #     return page_sanitized       
    
    @staticmethod
    def find_all_where(collection,query,fields='ALL',sorts=None,limit=None):
        
        if fields == "ALL":
            data = DB.DATABASE[collection].find(query)
        else:
            data = DB.DATABASE[collection].find(query,fields)
        if sorts:
            data = data.sort(sorts)
        if limit:
            data = data.sort(sorts).limit(int(limit))    
        page_sanitized = json.loads(json_util.dumps(data))
        return page_sanitized  

    @staticmethod
    def find_by_key(collection,key={},fields={},sorts=[]):
        if fields:
            data=DB.DATABASE[collection].find(key,fields)
        else:
            data=DB.DATABASE[collection].find(key)
        if sorts:
            page_sanitized = json.loads(json_util.dumps(data.sort(sorts)))
        else:
            page_sanitized = json.loads(json_util.dumps(data))
        return page_sanitized

    @staticmethod
    def find_max_by_key(collection,key):
        data = DB.DATABASE[collection].find_one(sort=[(key, -1)])
        return data

    @staticmethod
    def update_one(collection, setVal, where = {}):
        if not setVal or not where:
            return False
        else:
            rs = DB.DATABASE[collection].update_one(where, {"$set":setVal}).matched_count
            return rs
    @staticmethod
    def find_max_id(collection,key):
        maxKey = DB.DATABASE[collection].find_one(sort=[(key, -1)])
        max_id = 1
        if not maxKey:
            max_id = 1
        elif key in maxKey:
            max_id = (int(maxKey[key]) + 1)
        else:
            max_id = 1
        return max_id

    @staticmethod
    def insert_many(collection, data):
        insertId = DB.DATABASE[collection].insert_many(data, ordered=True).inserted_ids
        return insertId

    @staticmethod
    def count_by_key(collection, data):
        insertId = DB.DATABASE[collection].find(data).count(True)
        return insertId
    
    @staticmethod
    def update_many(collection, setVal, where = {}):
        rs = DB.DATABASE[collection].update_many(where, {"$set":setVal})
        return str(rs.modified_count)

    @staticmethod
    def delete_many(collection,where = {}):
        rs = DB.DATABASE[collection].delete_many(where)
        return str(rs.deleted_count)    

    # @staticmethod
    # def find_using_aggregrat(collection):
    #     data=DB.DATABASE[collection].aggregate([{ "$lookup":{"from": 'v006_service_category',"localField": "category_id","foreignField": "_id","as": 'orderdetails'}}])
    #     page_sanitized = json.loads(json_util.dumps(data))
    #     return page_sanitized
    
    @staticmethod
    def find_using_aggregate(collection,fields):
        data=DB.DATABASE[collection].aggregate(fields)
        page_sanitized = json.loads(json_util.dumps(data))
        return page_sanitized

    # @staticmethod
    # def randomDigits(stringLength=3):
    #     """Generate a random string of letters and digits """
    #     lettersAndDigits = string.digits
    #     return ''.join(random.choice(lettersAndDigits) for i in range(stringLength))
    
    
    @staticmethod
    def randomStringDigits(stringLength=3):
        """Generate a random string of letters and digits """
        lettersAndDigits = string.ascii_letters + string.digits
        return ''.join(random.choice(lettersAndDigits) for i in range(stringLength))
    
    @staticmethod
    def aggregateQuery(collection,aggregate):
        data= DB.DATABASE[collection].aggregate(aggregate)
        return json.loads(json_util.dumps(data))

    def get_timestamp_from_date(date):
        return int(datetime.timestamp(india_tz.localize(date)))

    def convert_timestamp_in_datetime(timestamp_received):
        return datetime.fromtimestamp(timestamp_received, india_tz)
        #dt_local.astimezone(india_tz)

    def convert_timestamp_in_datetime_string(timestamp_received):
        date = datetime.fromtimestamp(timestamp_received, india_tz)
        return date.strftime("%Y-%m-%d %H:%M:%S")


    def get_current_date():
        return datetime.now(india_tz)

    def get_current_timestamp():
        return int(datetime.timestamp(datetime.now(india_tz)))