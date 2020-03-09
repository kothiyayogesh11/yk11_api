from flask import request, Response, make_response, jsonify
from flask_restplus import Resource,Namespace, marshal_with, fields
from bson import json_util
import json
from config import Config
from .model import *


ns = Namespace('dashboard', description='Branch ( Outlet related operation )')


@ns.route("/dashboard_count")
class data_count(Resource):
    @ns.response(201, 'Vendor - Outlet billing.')
    @ns.doc('Vendor - Outlet Save billing')
    def get(self):
        outlet_id = ""
        if request.headers.get('outlet_id'):
            outlet_id = request.headers.get('outlet_id')
        vendor_id = request.headers.get('vendor_id')
        return get_count_data(self,outlet_id,vendor_id)

@ns.route("/")
class get_analytics_all(Resource):
    @ns.response(201, 'all analytics')
    @ns.doc('Vendor - all analytics')
    def get(self):
        vendor_id = request.args.get('vendor_id')
        outlet_id = request.args.get('outlet_id')
        return get_analytics(self,vendor_id,outlet_id)

# @ns.route("/dashboard_total_count")
# class total_count(Resource):
#     @ns.response(201, 'Vendor - Outlet billing.')
#     @ns.doc('Vendor - Outlet Save billing')
#     def post(self):
#         request_type = request.headers.get('request_type')
#         outlet_id = request.headers.get('outlet_id')
#         return total_count_data(self,request_type,outlet_id)
    
# @ns.route("/dashboard_button_data")
# class total_count(Resource):
#     @ns.response(201, 'Vendor - Outlet billing.')
#     @ns.doc('Vendor - Outlet Save billing')
#     def post(self):
#         return button_data(self)
    