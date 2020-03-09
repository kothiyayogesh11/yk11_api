from flask import request, Response, make_response, jsonify
from flask_restplus import Resource,Namespace, marshal_with
from bson import json_util
import json
from config import Config
from .model import *


ns = Namespace('profile', description='Vendor profile related operations')
_post = updateModel(object,ns)
_change_passeord = changePasseordM(object,ns)
# Vendor Profile
@ns.route('/')
class Profile(Resource):
    @ns.expect(_post, validate=True)
    @ns.response(201, 'Vendor update profile API.')
    @ns.doc('Vendor - update profile')
    def post(self):
        """ Save User Profile """
        return updateProfile(self)

# Vendor get profile
@ns.route('/<vendor_id>')
class Profile(Resource):
    # @ns.expect(_post, validate=True)
    @ns.response(201, 'Vendor get profile API.')
    @ns.doc('Vendor - get profile')
    def get(self,vendor_id=None):
        """Vendor get profile API """
        return getProfile(self,vendor_id)


@ns.route('/change_password')
class Change_password(Resource):
    @ns.response(201, 'Vendor change password API.')
    @ns.expect(_change_passeord, validate=True)
    @ns.doc('Vendor - Change password')
    def post(self,vendor_id=None):
        """ Changes Password API """
        return change_password(self)
    

@ns.route('/update_bank')
class bank_update(Resource):
    @ns.response(201, 'Vendor change password API.')
    # @ns.expect(_change_passeord, validate=True)
    @ns.doc('Vendor - Change password')
    def post(self):
        """ Changes Password API """
        return update_bank_data(self) 

@ns.route('/refer_and_earn')
class refer_and_earn(Resource):
    @ns.response(201, 'refer data get successfully')
    @ns.doc('Vendor - Refereal data')
    def get(self):
        return get_referral_data(self)

@ns.route('/refer_by_email')
class ReferByEmail(Resource):
    @ns.response(201, 'Refer by email.')
    # @ns.expect(_change_passeord, validate=True)
    @ns.doc('Vendor - Refer by email')
    def post(self):
        return refer_by_email(self) 


""" @ns.route('/read_filex')
class ReadFilex(Resource):
    def get(self):
        
        return fx(self) """