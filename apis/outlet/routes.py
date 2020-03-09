from flask import request, Response, make_response, jsonify
from flask_restplus import Resource,Namespace, marshal_with, fields
from bson import json_util
import json
from config import Config
from .model import addBusinessModel,addgellaryModel, addDetailsModel, billing, addServiceModel,upload_documents, outletImagesModel, outletGstModel,outletListModel,saveGellary, removeListingModel, saveBusiness, getDetails, businessDetails, servicesDetails, addImages, allOutletList, saveGST, getOutLetForServices, amenities_list, removeListing, branch


ns = Namespace('outlet', description='Branch ( Outlet related operation )')
_addBusiness = addBusinessModel(object,ns)
# _outlet_address = addressModel(object, ns)
_outlet_gellary = addgellaryModel(object,ns)
_business_details = addDetailsModel(object, ns)
_service_details = addServiceModel(object, ns)
_outlet_images = outletImagesModel(object, ns)
_outlet_list   = outletListModel(object,ns)
_outlet_gst = outletGstModel(object, ns)
_remove_listing_model = removeListingModel(object, ns)

# Vendor Profile
@ns.route('/outlet_details')
class Outlet(Resource):
    # @ns.expect(_addBusiness, validate=True)
    @ns.response(201, 'Outlet add outlet.')
    @ns.doc('Vendor - update profile')
    def post(self):
        """ Save Bussines """
        return saveBusiness(self)

    @ns.response(201, 'get outlet details.')
    @ns.doc('Vendor - get outlet details')
    def get(self):
        return getDetails(self)

@ns.route('/savegellary')
class Gellary(Resource):
    @ns.expect(_outlet_gellary, validate=True)
    @ns.response(201, 'Outlet add outlet.')
    @ns.doc('Vendor - update profile')
    def post(self):
        """ Save Location"""
        return saveGellary(self)

@ns.route("/business_details")
class BusinessDetais(Resource):
    @ns.expect(_business_details, validation= False)
    @ns.response(201, 'Vendor - Save outlet details.')
    @ns.doc('Vendor - Vendor Save outlet details')
    def post(self):
        """ Save Bussiness details """
        return businessDetails(self)


@ns.route("/service_details")
class BserviceDetais(Resource):
    @ns.expect(_service_details, validation= False)
    @ns.response(201, 'Vendor - Outlet Save services.')
    @ns.doc('Vendor - Outlet Save Services details')
    def post(self):
        """ Save Service details """
        return servicesDetails(self)

@ns.route("/outlet_images")
class Images(Resource):
    @ns.expect(_outlet_images, validation= False)
    @ns.response(201, 'Vendor - Outlet Save Images.')
    @ns.doc('Vendor - Outlet Save Images')
    def post(self):
        """ Save Outlet Images """
        return addImages(self)

@ns.route("/outlet_list")
class outletList(Resource):
    @ns.expect(_outlet_list, validation= True)
    @ns.response(201, 'Vendor - Outlet List.')
    @ns.doc('Vendor - Outlet List')
    def post(self):
        """ Get All Outlet List """
        return allOutletList(self)

@ns.route("/outlet_gst_details")
class outletGst(Resource):
    @ns.expect(_outlet_gst, validation= False)
    @ns.response(201, 'Vendor - Outlet Save Images.')
    @ns.doc('Vendor - Outlet Save Images')
    def post(self):
        """ Save GST """
        return saveGST(self)

@ns.route("/outlet_list_services")
class outletForServices(Resource):
    @ns.expect(_outlet_list, validation= False)
    @ns.response(201, 'Vendor - Outlet List for services')
    @ns.doc('Vendor - Outlet List for services')
    def post(self):
        """ Get Outlet Details For Services """
        return getOutLetForServices(self)

@ns.route("/amenities_list")
class outlett(Resource):
    @ns.response(201, 'Vendor - Outlet amenities_list.')
    @ns.doc('Vendor - Outlet Save amenities_list')
    def get(self):
        """ Get All Aminities List """
        return amenities_list(self)

@ns.route("/remove_listing")
class RemoveListing(Resource):
    @ns.expect(_remove_listing_model, validation= False)
    @ns.response(201, 'Vendor - Outlet amenities_list.')
    @ns.doc('Vendor - Outlet Save amenities_list')
    def post(self):
        """ Get All Aminities List """
        return removeListing(self)


@ns.route("/branch")
class Branch_outlet(Resource):
    @ns.response(201, 'Vendor - Outlet branch.')
    @ns.doc('Vendor - Outlet Save branch')
    def get(self):
        id = request.args.get('id')
        vendor_id = request.headers.get('vendor_id')
        outlet_id = request.headers.get('outlet_id')
        """ Get All branch List """
        return branch(self,id,vendor_id,outlet_id)

@ns.route('/upload_docs')
class Document(Resource):
    # @ns.expect(_post, validate=True)
    @ns.response(201, 'Document update profile API.')
    @ns.doc('Outlet - update document')
    def post(self):
        """ Save User Document """
        return upload_documents(self)

# @ns.route("/get_outlet_docs")
# class get_documents(Resource):
#     # @ns.expect(_vendor_profile, validate=True)
#     @ns.response(201, 'Vendor Login API.')
#     @ns.doc('outlet - GET Documents')
#     def post(self):
#         """Outlet DOcuments """
#         return getDocs(self)


@ns.route("/billing")
class Billing_outlet(Resource):
    @ns.response(201, 'Vendor - Outlet billing.')
    @ns.doc('Vendor - Outlet Save billing')
    def get(self):
        vendor_id = request.args.get('vendor_id')
        return billing(self,vendor_id)
    
    
# @ns.route("/dashboard_count")
# class data_count(Resource):
#     @ns.response(201, 'Vendor - Outlet billing.')
#     @ns.doc('Vendor - Outlet Save billing')
#     def post(self):
#         print("==============================================")
#         outlet_id = request.headers.get('outlet_id')
#         vendor_id = request.headers.get('vendor_id')
#         return get_count_data(self,outlet_id,vendor_id)