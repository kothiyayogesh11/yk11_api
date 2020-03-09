from flask import request, Response, make_response, jsonify
from flask_restplus import Resource,Namespace, marshal_with, fields
from bson import json_util
import json
from config import Config

from .model import addServicesModel, addCategoryModel, CategoryListModel, removeServiceModel, removeServiceCategoryModel, saveServices, getOutLetServicesCategory, saveCategoryServices, category_list_for_service, getServicesByVendor, getServices, removeService, removeServiceCategory, getMasterServiceByCategory, category_data, service_data, getServiceForBookingModel, getServiceListMethod, save_accomodation, get_accomodation_data, get_all_accomodation_data, delete_accomodation_data


ns = Namespace('services', description='Services related operations')
_addServices = addServicesModel(object,ns)
_category    = addCategoryModel(object, ns)
_category_list_model = CategoryListModel(object, ns) 
_remove_service_model = removeServiceModel(object, ns)
_categoty_remove_model = removeServiceCategoryModel(object, ns)
_getServiceForBooking = getServiceForBookingModel(object, ns)

# Vendor Services
@ns.route('/')
class Services(Resource):
    # @ns.expect(_addServices, validate=True)
    @ns.response(201, 'Outlet add Services.')
    @ns.doc('Vendor - Outlet add Services')
    def post(self):
        """ Save Services save   """
        return saveServices(self)

    @ns.doc('Vendor - Outlet get Services')
    @ns.response(201, 'Outlet add Services.')
    def get(self):
        """ Get All Services By Vendor """
        return getServices(self)

@ns.route('/category')
class ServicesCategory(Resource):
    @ns.response(201, 'Get outlet services.')
    @ns.doc('Vendor - Get outlet services')
    def get(self):
        """ Get All Services By Vendor """
        return getOutLetServicesCategory(self)

    @ns.expect(_category, validate=True)
    @ns.response(201, 'Outlet add Category Services.')
    @ns.doc('Vendor - Outlet add Category Services')
    def post(self):
        """ Save Category """
        return saveCategoryServices(self)

@ns.route('/category_list_for_service')
class CategoryList(Resource):
    @ns.expect(_category_list_model, validate=True)
    @ns.response(201, 'Get All sevices category list.')
    @ns.doc('Vendor - Get sevices category list')
    def post(self):
        """ Get Category List """
        return category_list_for_service(self)

@ns.route('/service_list_by_vendor')
class ServciesListByVendor(Resource):
    @ns.response(201, 'Get All vendor sevices list.')
    @ns.doc('Vendor - Get vendor sevices list')
    def get(self):
        """ Get Services By Vendor """
        return getServicesByVendor(self)
_getServiceForBooking
@ns.route('/remove_service')
class RemoveService(Resource):
    @ns.expect(_remove_service_model, validate=True)
    @ns.response(201, 'Service remove done.')
    @ns.doc('Vendor - Remove sevices')
    def post(self):
        """ Remove Service """
        return removeService(self)
        
@ns.route('/category_remove')
class RemoveCategory(Resource):
    @ns.expect(_categoty_remove_model, validate=True)
    @ns.response(201, 'Service remove done.')
    @ns.doc('Vendor - Remove sevices category list')
    def post(self):
        """ Remove Service Category """
        return removeServiceCategory(self)

@ns.route("/get_master_service_by_category")
class GetServiceMasterByCat(Resource):
    @ns.response(201, 'Service remove done.')
    @ns.doc('Vendor - Remove sevices category list')
    def post(self):
        """ Remove Service Category """
        return getMasterServiceByCategory(self)

        
@ns.route("/get_services_list")
class getServiceList(Resource):
    @ns.expect(_getServiceForBooking, validate=True)
    @ns.response(201, 'Service remove done.')
    @ns.doc('Vendor - Get all outlet services')
    def post(self):
        """ Get all outlet services """
        return getServiceListMethod(self)
    
    
@ns.route('/category_data')
class catgory(Resource):
    @ns.response(201, 'Vendor Login API.')
    @ns.doc('Vendor - Login')
    def get(self):
        """Vendor Login API """
        return category_data(self)
    
    
@ns.route('/service_names')
class service_datas(Resource):
    @ns.response(201, 'Vendor Login API.')
    @ns.doc('Vendor - Login')
    def post(self):
        """Vendor Login API """
        return service_data(self)

@ns.route('/save_accomodation')
class save_accomo_dation(Resource):
    @ns.response(201, 'Vendor Login API.')
    @ns.doc('Vendor - Login')
    def post(self):
        """Vendor Login API """
        return save_accomodation(self)
    
    
@ns.route('/get_accomodation')
class get_accomo_dation(Resource):
    @ns.response(201, 'Vendor update profile API.')
    @ns.doc('Vendor - update profile')
    def get(self):
        """ Save User Profile """
        accomodation_id=""
        if 'accomodation_id' in request.args:
            accomodation_id = request.args.get('accomodation_id')
        outlet_id=request.args.get('outlet_id')
        return get_accomodation_data(self,outlet_id,accomodation_id)
    
@ns.route('/get_all_accomodation')
class get_accomo_dation(Resource):
    @ns.response(201, 'Vendor update profile API.')
    @ns.doc('Vendor - update profile')
    def get(self):
        """ Save User Profile """
        outlet_id = request.args.get('outlet_id')
        return get_all_accomodation_data(self,outlet_id)
    
    
@ns.route('/delete_accomodation')
class delete_accomo_dation(Resource):
    @ns.response(201, 'Vendor update profile API.')
    @ns.doc('Vendor - update profile')
    def post(self):
        """ Save User Profile """
        return delete_accomodation_data(self)