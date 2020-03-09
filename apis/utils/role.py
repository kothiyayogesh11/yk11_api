# Create By : Yogesh Kothiya
# Uses : Manage Role

from flask import jsonify, request
import socket
import apis.utils.constants as CONST
from datetime import datetime, date, time, timedelta
import pymongo
from database import DB
import json
from bson import json_util, ObjectId
import apis.utils.message_constants as MSG_CONST

class RoleAccess:
    def __init__(self,role_id=None,vendor_id=None,userId=None):
        # self.todayDate = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.todayDate = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.ip_address = socket.gethostbyname(socket.gethostname())
        self.role_id = role_id
        self.user_id = userId
        self.vendor_id = vendor_id
        self.tbl_v005_roles = "v005_roles"
        self.tbl_v018_module_access = "v018_module_access"
        self.tbl_v017_modules = "v017_modules"
        self.tbl_v003_vendor_users = "v003_vendor_users"
        self.roleData = {}
        self.module_ids = []
        
    def getRoleAccess(self):
        res = []
        # roleData = DB.find_one(self.tbl_v005_roles, {"_id":ObjectId(self.role_id)},{"_id":1,"name":1})
        # if roleData:
        #     roleData["_id"] = roleData["_id"]["$oid"]
        #     roleData["name"]= roleData["name"].title()
        #     self.roleData[roleData["_id"]] = roleData["name"]
        moduleAccess = self.getModuleAccess()
        # moduleList   = self.getModuleListByAccess()
        # if moduleList and moduleAccess:
        #     for x in range(len(moduleList)):
        #         if moduleList[x]["_id"] in moduleAccess and moduleAccess[moduleList[x]["_id"]]:
        #             moduleList[x]["access_data"] = moduleAccess[moduleList[x]["_id"]]
        #             res.append(moduleList[x])
        res.append(moduleAccess)
        return res

    def getModuleAccess(self):
        accessList = DB.find_by_key(self.tbl_v018_module_access,{"vendor_id":ObjectId(self.user_id),"is_delete":0})
        accessData = {}
        if accessList:
            accessData = {}
            for x in range(len(accessList)):
                accessList[x]["_id"]        = accessList[x]["_id"]["$oid"]
                accessList[x]["vendor_id"]  = accessList[x]["vendor_id"]["$oid"]
                accessList[x]["module_id"]  = accessList[x]["module_id"]["$oid"]
                # if accessList[x]["access"]:
                #     self.module_ids.append(ObjectId(accessList[x]["module_id"]))
                ModuleName=accessList[x]["module_name"].replace(" ", "_")
                accessData[ModuleName] = accessList[x]
                
        return accessData

    def getModuleListByAccess(self):
        moduleList = DB.find_by_key(self.tbl_v017_modules,{"status":1,"_id":{"$in":self.module_ids}},{},[("index",pymongo.ASCENDING)])
        if moduleList:
            for x in range(len(moduleList)):
                moduleList[x]["_id"] = moduleList[x]["_id"]["$oid"]
        return moduleList

    def getAllModule(self):
        moduleList = DB.find_by_key(self.tbl_v017_modules,{"status":int(1),"is_menu":int(0)},{},[("index",pymongo.ASCENDING)])
        if moduleList:
            for x in range(len(moduleList)):
                moduleList[x]["_id"] = moduleList[x]["_id"]["$oid"]
                moduleList[x]["name"] = moduleList[x]["name"].title()
                if 'parent_id' in moduleList[x]:
                    moduleList[x]["parent_id"] = moduleList[x]["parent_id"]["$oid"]
                else:
                    moduleList[x]["parent_id"] = ""
        return moduleList


    def getAllRole(self):
        roleList = DB.find_by_key(self.tbl_v005_roles,{},{},[("name",pymongo.ASCENDING)])
        if roleList:
            for x in range(len(roleList)):
                roleList[x]["_id"] = roleList[x]["_id"]["$oid"]
                roleList[x]["name"] = roleList[x]["name"].title()
        return roleList
    
    
    # def getRoleById(self):
    #     roleList = DB.find_one(self.tbl_v005_roles,{"_id":ObjectId(self.role_id)})
    #     print("=============================")
    #     print(roleList)
    #     if roleList:
    #         roleList["_id"] = roleList["_id"]["$oid"]
    #         roleList["name"] = roleList["name"].title()
    #     return roleList

    def getModuleAccessByVendor(self):
        accessList = DB.find_by_key(self.tbl_v018_module_access,{"vendor_id":ObjectId(self.vendor_id),"is_delete":0})
        if accessList:
            for x in range(len(accessList)):
                accessList[x]["_id"]        = accessList[x]["_id"]["$oid"]
                accessList[x]["vendor_id"]  = accessList[x]["vendor_id"]["$oid"]
                accessList[x]["module_id"]  = accessList[x]["module_id"]["$oid"]
                accessList[x]["role_id"]    = accessList[x]["role_id"]["$oid"]
        return accessList

    def manageRolePageAPI(self):
        res = {}
        
        res['roleList']    = self.getAllRole()
        moduleList  = self.getAllModule()
        accessList  = self.getModuleAccessByVendor()
        accessListByModule = {}
        if accessList:
            for x in range(len(accessList)):
                if accessList[x]["module_id"] not in accessListByModule:
                    accessListByModule[accessList[x]["module_id"]] = {}
                accessListByModule[accessList[x]["module_id"]][accessList[x]["role_id"]] = accessList[x]

        if moduleList:
            for x in range(len(moduleList)):
                moduleList[x]["access"] = {}
                if moduleList[x]["_id"] in accessListByModule and accessListByModule[moduleList[x]["_id"]]:
                    moduleList[x]["access"] = accessListByModule[moduleList[x]["_id"]]
        res["moduleList"] = moduleList
        return res
    

    def saveRoleAccess(self,reqData):
        vendorId = reqData["vendor_id"]
        module_id = reqData["module_id"]
        role_id = reqData["role_id"]

        getAccess = DB.find_one(self.tbl_v018_module_access,{"vendor_id":ObjectId(vendorId),"module_id":ObjectId(module_id),"role_id":ObjectId(role_id)})
        saveData = {}
        
        saveData["vendor_id"]   = ObjectId(vendorId)
        vendor_email = DB.find_one(self.tbl_v003_vendor_users,{"vendor_id":ObjectId(vendorId)},{'email':1,'_id':0})
        saveData["vendor_email"]=vendor_email['email']
        
        saveData["module_id"]   = ObjectId(module_id)
        module_name = DB.find_one(self.tbl_v017_modules,{"_id":ObjectId(module_id)},{'name':1,'_id':0})
        saveData["module_name"]=module_name['name']
        
        saveData["role_id"]     = ObjectId(role_id)
        role_name = DB.find_one(self.tbl_v005_roles,{"_id":ObjectId(role_id)},{'name':1,'_id':0})
        saveData["role_name"]=role_name['name']
        
        saveData["access_type"] = reqData["access_type"]
        saveData["access"]      = True
        saveData["is_delete"]   = 0

        if getAccess:
            saveData["update_by"] = ObjectId(reqData["user_id"])
            saveData["update_date"] = self.todayDate
            saveData["update_ip"] = self.ip_address
            act = DB.update_one(self.tbl_v018_module_access,saveData,{"vendor_id":ObjectId(vendorId),"module_id":ObjectId(module_id),"role_id":ObjectId(role_id)})
        else:
            saveData["insert_by"] = ObjectId(reqData["user_id"])
            saveData["insert_date"] = self.todayDate
            saveData["insert_ip"] = self.ip_address
            act = DB.insert(self.tbl_v018_module_access,saveData)
        return act

    def addDefaultRolePerminssion(self):
        module = self.getAllModule()
        accessData = {}
        accessData["vendor_id"]     = self.vendor_id
        accessData["role_id"]       = self.role_id
        accessData["user_id"]       = self.user_id
        accessData["access_type"]   = "write"
        status = None
        for x in range(len(module)):
            accessData["module_id"] = module[x]["_id"]
            self.saveRoleAccess(accessData)
        return status