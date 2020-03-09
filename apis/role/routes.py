from flask import request, Response, make_response, jsonify
from flask_restplus import Resource,Namespace, marshal_with
from bson import json_util
import json
from config import Config
from .model import *

ns = Namespace('role', description='Role related operations')
_role_list_model = roleListModel(object,ns)
_role_access_save = roleAccessSaveModel(object,ns)
# Vendor Role
@ns.route('/list')
class RoleList(Resource):
    @ns.expect(_role_list_model, validate=True)
    @ns.response(201, 'Vendor - Roe list API')
    @ns.doc('Vendor - Role list API')
    def post(self):
        """ Role list """
        return roleList(self)


@ns.route('/module_access')
class RoleModuleAccess(Resource):
    @ns.expect(_role_list_model, validate=True)
    @ns.response(201, 'Vendor - Roe list API')
    @ns.doc('Vendor - Role list API')
    def post(self):
        """ Role list """
        return manageRolePageAPI(self)

@ns.route('/save_access')
class RoleModuleAccessSave(Resource):
    @ns.expect(_role_access_save, validate=True)
    @ns.response(201, 'Vendor - Roe save API')
    @ns.doc('Vendor - Role save API')
    def post(self):
        """ Role save """
        return saveRoleAccess(self)

@ns.route('/get_user_module_access')
class GetUserModuleAccess(Resource):
    @ns.expect(_role_list_model, validate=True)
    @ns.response(200, 'Vendor - Role save API')
    @ns.doc('Vendor - Role save API')
    def post(self):
        """ Role save """
        return getRoleAccess(self)
    
    
@ns.route('/addnew_role')
class CreateRole(Resource):
    # @ns.expect(_outlet_list, validate=True)
    @ns.response(201, 'Vendor - Get All Role')
    @ns.doc('Vendor - Get List Of Role')
    def post(self):
        """ Get Role List """
        return create_new_role(self) 

@ns.route('/get_all_modules')
class GetAllModules(Resource):
    @ns.response(201, 'Vendor - Get All Modules')
    @ns.doc('Vendor - Get List Of Role')
    def get(self):
        """ Get Role List """
        role_id = ""
        user_id = request.args.get('user_id')
        if 'role_id' in request.args:
            role_id = request.args.get('role_id')
        return get_all_module(self,user_id,role_id)
    
    
