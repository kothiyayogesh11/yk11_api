from flask import make_response, jsonify, request
import socket
from random import randint
from bson import ObjectId
from database import DB
import re
import boto3
from botocore.exceptions import ClientError
import random, string
import apis.utils.constants as CONST
import logging
from datetime import datetime, date, time, timedelta
from pytz import timezone
import pytz
india_tz = pytz.timezone('Asia/Kolkata')

tbl_v003_vendor_users =  "v003_vendor_users"
device_list = ['WELNSTVW','WELNSTVA','WELNSTVI']

def validate_token(static_token):
    token = ''
    vendor_user_id = ''
    device_id = ''
    if request.headers.get('Authorization-Token') and request.headers.get('Vendor-User-Id') and request.headers.get('Device-Id'):
        token = request.headers.get('Authorization-Token')
        vendor_user_id = request.headers.get('Vendor-User-Id')
        device_id = request.headers.get('Device-Id')
    else:
        return False

    if device_id not in device_list:
        return False

    # If user not logged in
    if vendor_user_id == '0':
        return True if token == static_token else False

    # If user logged in
    if vendor_user_id != '':
        user_token = DB.find_one(tbl_v003_vendor_users,{"_id":ObjectId(vendor_user_id)},{'security_token':1})
        if user_token != None and user_token != {} and user_token['security_token'] == token:
            return True

    return False


def output_json(data,message,status=True,code=200,headers=None):
    """ 
    code :
        200 : Status ok, success
        201 : Failed opretion
        202 : ALready exists
    """
    datares=jsonify(data=data,status=status,message=message)
    resp = make_response(datares, code)
    resp.headers.extend(headers or {})
    return resp

def random_n_digits(n):
    range_start = 10**(n-1)
    range_end = (10**n)-1
    return randint(range_start, range_end)

# Generate Unique Number
def genOtp(length = 6, collection = "", where={},otp_field="otp"):
    # get unique digits
    OTP = random_n_digits(length)
    where[otp_field] = OTP
    
    result = DB.find_by_key(collection,where)
    if not result:
        return OTP
    else:
        genOtp(length, collection, where)

# Valide Mobile Number
def isMobile(s):
    # 1) Begins with 0 or 91 
    # 2) Then contains 7 or 8 or 9. 
    # 3) Then contains 9 digits 
    Pattern = re.compile(r"^[+]?[0-9]{9}") 
    return bool(Pattern.match(s))


def session_token(collection, where = {}):
    uniqueCode = "".join(random.choices(string.ascii_letters + string.digits, k=30))
    where = {"security_token":str(uniqueCode)}
    result = DB.find_by_key(collection,where)
    if not result:
        return uniqueCode
    else:
        session_token(collection, {})

def upload_file(file_name, bucket, object_name=None):
    """Upload a file to an S3 bucket

    :param file_name: File to upload
    :param bucket: Bucket to upload to
    :param object_name: S3 object name. If not specified then file_name is used
    :return: True if file was uploaded, else False
    """

    # If S3 object_name was not specified, use file_name
    if object_name is None:
        object_name = file_name

    # Upload the file
    s3_client = boto3.client('s3')
    try:
        response = s3_client.upload_file(file_name, bucket, object_name)
    except ClientError as e:
        logging.error(e)
        return False
    return True
      
# Define a function for 
# for validating an Email 
def validEmail(email):
    regex = '^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$'
    if(re.search(regex,email)):
        return True
    else:
        return False

def uniqueString(size=10, chars=string.ascii_letters + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

def convert24(str1): 
      
    # Checking if last two elements of time 
    # is AM and first two elements are 12 
    if str1[-2:] == "AM" and str1[:2] == "12": 
        return "00" + str1[2:-2] 
          
    # remove the AM     
    elif str1[-2:] == "AM": 
        return str1[:-2] 
      
    # Checking if last two elements of time 
    # is PM and first two elements are 12    
    elif str1[-2:] == "PM" and str1[:2] == "12": 
        return str1[:-2] 
          
    else: 
          
        # add 12 to hours and remove PM 
        return str(int(str1[:2]) + 12) + str1[2:8] 

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

def get_device_name(device_id):
    if device_id == device_list[0]:
        return "web"
    elif device_id == device_list[1]:
        return "android"
    elif device_id == device_list[2]:
        return "ios"