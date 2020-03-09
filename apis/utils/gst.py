import apis.utils.constants as CONST
import socket
from datetime import datetime, date, time, timedelta
import requests
import json
import apis.utils.message_constants as MSG_CONST

class GST:
    def __init__(self,gst_number):
        self.access_token = ""
        self.gst_number = gst_number

    def verifyGst(self):
        res = {}
        token_data = self.gst_access_token()
        if token_data and "access_token" in token_data and token_data["access_token"] != "":
            self.access_token = token_data["access_token"]
            gst_res = self.gst_data()
            if gst_res and "error" in gst_res and gst_res["error"] == False and "data" in gst_res:
                if "sts" in gst_res["data"] and gst_res["data"]["sts"] == "Active":
                    res["error"] = False
                    res["message"] = MSG_CONST.VENDOR_GST_VELIDATE_TRUE
                    res["data"] = gst_res["data"]
                elif "sts" in gst_res["data"] and gst_res["data"]["sts"] != "Active":
                    res["error"] = True
                    res["message"] = MSG_CONST.VENDOR_GST_INVALID
                    res["data"] = gst_res["data"]
                else:
                    res["error"] = True
                    res["message"] = MSG_CONST.VENDOR_GST_VELIDATE_FALSE
                    res["data"] = gst_res["data"]
            else:
                res["error"] = True
                res["message"] = gst_res["data"]["error"]["message"] if "data" in gst_res and "message" in gst_res["data"]["error"] else "Something wrong to make request"
                res["error_type"] = "invalid_gst"
        else:
            res["error"] = True
            res["error_type"] = token_data["error"] if token_data and "error" in token_data else "something_wrong"
            res["message"] = token_data["error_description"] if token_data and "error_description" in token_data else "Something wrong to make request"
        return res

    def gst_access_token(self):
        result = {}
        try:
            crads = {}
            crads["username"] = CONST.GST_USER
            crads["password"] = CONST.GST_PASSWORD
            crads["client_id"] = CONST.GST_CLIENT_ID
            crads["client_secret"] = CONST.GST_CLIENT_SECRET
            crads["grant_type"] = CONST.GST_GRANTTYPE
            res = requests.post(CONST.GST_CLIENT_URL+"oauth/access_token", json=crads)
            result = res.json()
        except requests.exceptions.Timeout:
            result["error"] = True
            result["message"] = "Connection timeout"
            result["data"] = []
        except requests.exceptions.TooManyRedirects:
            result["error"] = True
            result["message"] = "Too many redirects"
            result["data"] = []
        except requests.exceptions.RequestException as e:
            result["error"] = True
            result["message"] = "Request exception"
            result["data"] = []
        return result
        
    def gst_data(self):
        try:
            if self.gst_number == "":
                return {}

            if self.access_token == "":
                return {}
            headerData = {}
            headerData["Content-Type"] = CONST.GST_CONTANTTYPE
            headerData["Authorization"] = CONST.GST_AUTHORIZATION+self.access_token
            headerData["client_id"] = CONST.GST_CLIENT_ID
            headerData["client_secret"] = CONST.GST_CLIENT_SECRET
            headerData["grant_type"] = CONST.GST_GRANTTYPE
            result = requests.get(CONST.GST_CLIENT_URL+"commonapis/searchgstin?gstin="+self.gst_number, headers=headerData)
            result = result.json()
        except requests.exceptions.Timeout:
            result["error"] = True
            result["message"] = "Connection timeout"
            result["data"] = []
        except requests.exceptions.TooManyRedirects:
            result["error"] = True
            result["message"] = "Too many redirects"
            result["data"] = []
        except requests.exceptions.RequestException as e:
            result["error"] = True
            result["message"] = "Request exception"
            result["data"] = []
        return result