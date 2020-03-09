from flask import request, Response, make_response, jsonify
from flask_restplus import Resource,Namespace, marshal_with, fields
from bson import json_util
import json
from config import Config
# from .model import addSpotlightModel, saveSpotlight, listSpotlightModel, getSpotlight
from .model import *

ns = Namespace('spotlight', description='Spotlight related operations')
_addSpotlight = addSpotlightModel(object,ns)
_listSpotlight = listSpotlightModel(object,ns)

# Vendor Spotlight
@ns.route('/')
class Spotlight(Resource):
    @ns.expect(_addSpotlight, validate=True)
    @ns.response(201, 'Outlet add Spotlight.')
    @ns.doc('Vendor - Outlet add Spotlight')
    def post(self):
        """ Save Spotlight save   """
        return saveSpotlight(self)

@ns.route('/list')
class SpotlightList(Resource):
    @ns.expect(_listSpotlight, validate=True)
    @ns.response(201, 'Outlet add Spotlight.')
    @ns.doc('Vendor - Outlet add Spotlight')
    def post(self):
        """ Save Spotlight save   """
        return getSpotlight(self)
@ns.route('/profile_status')
class Spotlightstatus(Resource):
    @ns.response(201, 'unpublish status')
    @ns.doc('Vendor - unpublish status')
    def post(self):
        """ Save Spotlight save   """
        return Spotlight_status(self)
    
    
@ns.route('/spotlight')
class SpotlighReferalCode(Resource):
    @ns.response(201, 'Get Referal Code')
    @ns.doc('Vendor - Get Referal Code')
    def get(self):
        """ Get Referal Code   """
        vendor_id =""
        if request.args.get('vendor_id'):
            vendor_id = request.args.get('vendor_id')
        return get_referal_code(self,vendor_id)