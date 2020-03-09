from flask import request, Response, make_response, jsonify
from flask_restplus import Resource,Namespace, marshal_with
from bson import json_util
import json
from config import Config
from .model import *

ns = Namespace('staff', description='Staff related operations')
_addStaff = addStaffModel(object,ns)
_role_list = roleListModel(object,ns)
_designation_list = designationtModel(object,ns)
_email_verify = emailVerifyModel(object,ns)
_mobile_check = contactVerifyModel(object,ns)
_staff_list   = staffListModel(object,ns)
_remove_staff = removeStaffModel(object,ns)
_outlet_list = outletModel(object,ns)
# _change_passeord = addOutletModel(object,ns)

# Vendor Users
@ns.route('/')
class UserStaff(Resource):
    @ns.expect(_addStaff, validate=True)
    @ns.response(201, 'Vendor - Add staff API')
    @ns.doc('Vendor - Add Staff API')
    def post(self):
        """ Save Users in vendor """
        return saveStaff(self)

    @ns.response(201, 'Vendor - Get User Data')
    @ns.doc('Vendor - Get User DATA')
    def get(self):
        """ Get User Betails By ID """
        return getStaff(self)

@ns.route('/role_list')
class StaffRoleList(Resource):
    @ns.expect(_role_list, validate=True)
    @ns.response(201, 'Vendor - Get All Role')
    @ns.doc('Vendor - Get List Of Role')
    def post(self):
        """ Get Role List """
        return getRoleList(self)

@ns.route("/email_check")
class StaffEmailVerify(Resource):
    @ns.expect(_email_verify, validate=True)
    @ns.response(201, 'Vendor - Check email verify')
    @ns.doc('Vendor - Check email verify')
    def post(self):
        """ Get Role List """
        return emailCheckStaff(self)

@ns.route("/mobile_check")
class StaffContacyVerify(Resource):
    @ns.expect(_mobile_check, validate=True)
    @ns.response(201, 'Vendor - Check mobile verify')
    @ns.doc('Vendor - Check contact verify')
    def post(self):
        """ Get contact List """
        return contactCheckStaff(self)

@ns.route("/staff_list")
class StaffList(Resource):
    @ns.expect(_staff_list, validate=True)
    @ns.response(201, 'Vendor - Get Staff member')
    @ns.doc('Vendor - Vendor get Staff member')
    def post(self):
        """ Vendor get staff member """
        return staff_list(self)

@ns.route("/remove_staff")
class RemoveStaff(Resource):
    @ns.expect(_remove_staff, validate=True)
    @ns.response(201, 'Vendor - Get Staff member')
    @ns.doc('Vendor - Vendor get Staff member')
    def post(self):
        """ Vendor get staff member """
        return remove_staff(self)

@ns.route("/role_access")
class RoleStaff(Resource):
    @ns.response(201, 'Vendor - Get Staff member')
    @ns.doc('Vendor - Vendor get Staff member')
    def post(self):
        """ Vendor get staff member """
        return role_staff(self)


@ns.route('/designation_list_by_managerial')
class StaffDesignationListByManagerial(Resource):
    @ns.expect(_designation_list, validate=True)
    @ns.response(201, 'Vendor - Get All Role')
    @ns.doc('Vendor - Get List Of Role')
    def post(self):
        """ Get Role List """
        return getDesignationListByManagerial(self)
    
    
@ns.route('/designation_list_by_operational')
class StaffDesignationListByOperational(Resource):
    @ns.expect(_designation_list, validate=True)
    @ns.response(201, 'Vendor - Get All Role')
    @ns.doc('Vendor - Get List Of Role')
    def post(self):
        """ Get Role List """
        return getDesignationListByoperational(self)  


@ns.route('/outlet_list')
class StaffOutletList(Resource):
    @ns.expect(_outlet_list, validate=True)
    @ns.response(201, 'Vendor - Get All Role')
    @ns.doc('Vendor - Get List Of Role')
    def post(self):
        """ Get Role List """
        return getOutletList(self) 
   


@ns.route('/addnew_staff')
class AddNewStaff(Resource):
    # @ns.expect(_outlet_list, validate=True)
    @ns.response(201, 'Vendor - Get All Role')
    @ns.doc('Vendor - Get List Of Role')
    def post(self):
        """ Get Role List """
        return add_new_staff(self) 
   

@ns.route('/save_new_role')
class NewSaveRole(Resource):
    # @ns.expect(_outlet_list, validate=True)
    @ns.response(201, 'Vendor - Get All Role')
    @ns.doc('Vendor - Get List Of Role')
    def post(self):
        """ Get Role List """
        return save_new_role(self) 

# @ns.route('/get_all_modules')
# class NewGetRole(Resource):
#     # @ns.expect(_outlet_list, validate=True)
#     @ns.response(201, 'Vendor - Get All Role')
#     @ns.doc('Vendor - Get List Of Role')
#     def get(self):
#         """ Get Role List """
#         print(request.args.get('staff_id'))
#         staff_id =""
#         if request.args.get('staff_id'):
#             staff_id = request.args.get('staff_id')
#         return get_new_role(self,staff_id) 



@ns.route('/get_all_modules')
class GetAllModules(Resource):
    @ns.response(201, 'Vendor - Get All Modules')
    @ns.doc('Vendor - Get List Of Role')
    def get(self):
        """ Get Role List """
        staff_id = ""
        if 'staff_id' in request.args:
            staff_id = request.args.get('staff_id')
        return get_all_module(self,staff_id)




# @ns.route("/staff_assign-mail")
# class EmailVerification(Resource):
#     @ns.response(201, 'Vendor - Send staff assign mail.')
#     @ns.doc('Vendor - Vendor - Send staff assign mail.')
#     def get(self):
#         """ Vendor - Vendor - Send verificatin link. """
#         return sendVerificationLink(self)


@ns.route("/delete_access")
class Deleteaccess(Resource):
    # @ns.expect(_remove_staff, validate=True)
    @ns.response(201, 'Vendor - Get Staff member')
    @ns.doc('Vendor - Vendor get Staff member')
    def post(self):
       
        """ Vendor get staff member """
        return delete_access(self)