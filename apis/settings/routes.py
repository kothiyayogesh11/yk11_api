from flask import request, Response, make_response, jsonify
from flask_restplus import Resource,Namespace, marshal_with
from bson import json_util
import json
from config import Config
from .model import verifyGstModel, vendorProfileModel, searchGst, saveGst, getVendorProfile
from database import DB

ns = Namespace('settings', description='Vendor businss sestting')
_verify_gst = verifyGstModel(object,ns)
_vendor_profile = vendorProfileModel(object, ns)
# Vendor Search GSTN
@ns.route('/gstn_search')
class SettingGSTsearch(Resource):
    @ns.expect(_verify_gst, validate=True)
    @ns.response(201, 'Vendor Login API.')
    @ns.doc('Vendor - Search GST N')
    def post(self):
        """Vendor Login API """
        return searchGst(self)

    
@ns.route('/save_gst')
class SettingGSTsaveGST(Resource):
    @ns.expect(_verify_gst, validate=True)
    @ns.response(201, 'Vendor Login API.')
    @ns.doc('Vendor - Save GST Number')
    def post(self):
        """Vendor Login API """
        return saveGst(self)

@ns.route("/get_vendor_profile")
class SettingVendorProfile(Resource):
    @ns.expect(_vendor_profile, validate=True)
    @ns.response(201, 'Vendor Login API.')
    @ns.doc('Vendor - Save GST Number')
    def post(self):
        """Vendor Login API """
        return getVendorProfile(self)