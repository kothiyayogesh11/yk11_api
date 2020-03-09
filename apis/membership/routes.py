from flask import request, Response, make_response, jsonify
from flask_restplus import Resource,Namespace, marshal_with
from bson import json_util
import json
from config import Config
from .model import *


ns = Namespace('membership', description='Staff related operations')
_subscription_model = subscriptionModel(object, ns)

# Vendor Membership - Jyoti
@ns.route('/')
class Membership(Resource):
    @ns.response(201, 'Vendor - Outlet membership.')
    @ns.doc('Vendor - Outlet Save membership')
    def get(self):
        vendor_id = request.args.get('vendor-id')
        return get_membership_data(self,vendor_id)


@ns.route('/subscription')
class MembershipSubscription(Resource):
    @ns.expect(_subscription_model, validation= False)
    @ns.response(201, 'Vendor - Outlet membership.')
    @ns.doc('Vendor - Outlet Save membership')
    def post(self):
        return getVendorSubscription(self)

@ns.route('/buy_plan')
class BuyPlan(Resource):
    @ns.response(201, 'Buy Plan click success')
    @ns.doc('Buy Plan click success')
    def post(self):
        data = request.json
        return buy_plan(self,data)
  

@ns.route('/success_plan_payment')
class BuyPlan(Resource):
    @ns.response(201, 'Buy Plan successfully')
    @ns.doc('Buy Plan successfully')
    def post(self):
        data = request.json
        return success_plan_payment(self,data)

@ns.route('/add_plan')
class AddMembership(Resource):
    @ns.response(201, 'Buy Plan successfully')
    @ns.doc('Buy Plan successfully')
    def post(self):
        return AddMembershipPlan(self)
    

@ns.route('/get_membership')
class GetMembership(Resource):
    @ns.response(201, 'get Plan successfully')
    @ns.doc('get Plan successfully')
    def get(self):
        return Getmembership(self)
    
    
@ns.route('/check_gst')
class CheckGst(Resource):
    @ns.response(201, 'GST Verified Successfully')
    @ns.doc('GST Verified Successfully')
    def post(self):
        return check_gst(self)
    
@ns.route('/check_subscription')
class CheckSubscription(Resource):
    @ns.response(201, 'Check Subscription Details')
    @ns.doc('Check Subscription Details')
    def post(self):
        return subscription_details(self)

@ns.route('/get_gst_by_vendor')
class GetGst(Resource):
    @ns.response(201, 'get gst number successfully')
    @ns.doc('get gst number successfully')
    def get(self):
        return get_gst_by_vendor(self)
