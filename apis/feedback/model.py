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

#logging.basicConfig(filename='vendor.log', level=logging.DEBUG)   

tbl_v013_feedback = "v013_feedback"
tbl_v004_outlets = "v004_outlets"
# tbl_u001_users = "u001_users"

def feedback_data(slef,outlet_id):
    if outlet_id != "":
        get_feedback=DB.find_all_where(tbl_v013_feedback,{"outlet_id":ObjectId(outlet_id),"status":1},"ALL")
    else:
        get_feedback = []
    return output_json(get_feedback, True, 200)


def feedback(self):
    requestData = dict(request.json)
    feedback_id = requestData['feedback_id']
    feedback=DB.find_one(tbl_v013_feedback,{"_id":ObjectId(feedback_id)},"ALL")
    return output_json(feedback, True, 200)