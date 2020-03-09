from flask import request, Response, make_response, jsonify
from flask_restplus import Resource,Namespace, marshal_with
from bson import json_util
import json
from config import Config
from .model import *
from database import DB


ns = Namespace('offer', description='Vendor  related operations')
# _post = AddModel(object,ns)



@ns.route('/add_offer')
class offer(Resource):
    # @ns.expect(_post, validate=True)
    @ns.response(201, 'Vendor update profile API.')
    @ns.doc('Vendor - update profile')
    def post(self):
        """ Save User Profile """
        return offer_data(self)
        # return updateProfile(self)
        
@ns.route('/get_offer')
class get_offer(Resource):
    @ns.response(201, 'Vendor update profile API.')
    @ns.doc('Vendor - update profile')
    def get(self):
        """ Save User Profile """
        offer_id=""
        outlet_id = ""
        if 'offer_id' in request.args:
            offer_id = request.args.get('offer_id')
        if 'outlet_id' in request.args:
            outlet_id=request.args.get('outlet_id')
        vendor_id=request.args.get('vendor_id')
        return get_offer_data(self,outlet_id,offer_id,vendor_id)
    
    
@ns.route('/get_all_offer')
class get_all_offer(Resource):
    @ns.response(201, 'Vendor update profile API.')
    @ns.doc('Vendor - update profile')
    def get(self):
        """ Save User Profile """
        outlet_id =""
        if request.args.get('outlet_id'):
            outlet_id = request.args.get('outlet_id')
        return get_all_offer_data(self,outlet_id)
    
      
@ns.route('/delete_offer')
class delete_offer(Resource):
    @ns.response(201, 'Vendor update profile API.')
    @ns.doc('Vendor - update profile')
    def post(self):
        """ Save User Profile """
        return delete_offer_data(self)

@ns.route('/get_services')
class GetServicesbyOutlets(Resource):
    @ns.response(201, 'Vendor update profile API.')
    @ns.doc('Vendor - update profile')
    def post(self):
        """ Save User Profile """
        return get_services_data(self)

@ns.route('/apply_barter_offer')
class ApplyBarterOffer(Resource):
    @ns.response(201, 'Apply for barter offer.')
    @ns.doc('Vendor - Barter Offer')
    def post(self):
        return apply_barter_offer(self)