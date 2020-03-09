from flask import request, Response, make_response, jsonify
from flask_restplus import Resource,Namespace, marshal_with
from bson import json_util
import json
from config import Config
from .model import *
from database import DB


ns = Namespace('vendor_inquiry', description='Vendor  related operations')
# _post = AddModel(object,ns)



@ns.route('/add_inquiry')
class AddEmployee(Resource):
    @ns.response(201, 'Vendor update profile API.')
    @ns.doc('Vendor - update profile')
    def post(self):
        """ Save User Profile """
        return vendor_inquiry_data(self)



@ns.route('/get_employee')
class GetEmployee(Resource):
    @ns.response(201, 'Vendor update profile API.')
    @ns.doc('Vendor - update profile')
    def get(self):
        """ Save User Profile """
        inquiry_id=""
        if 'inquiry_id' in request.args:
            inquiry_id = request.args.get('inquiry_id')
        outlet_id=request.args.get('outlet_id')
        return get_vendor_inquiry_data(self,outlet_id,inquiry_id)
    
    
    
@ns.route('/get_all_employee')
class GetAllEmployee(Resource):
    @ns.response(201, 'Vendor update profile API.')
    @ns.doc('Vendor - update profile')
    def get(self):
        """ Save User Profile """

        outlet_id = request.args.get('outlet_id')
        return get_all_vendor_inquiry_data(self,outlet_id)