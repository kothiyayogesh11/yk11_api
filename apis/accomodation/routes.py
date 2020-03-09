from flask import request, Response, make_response, jsonify
from flask_restplus import Resource,Namespace, marshal_with
from bson import json_util
import json
from config import Config
from .model import *
from database import DB
# from .model import addServicesModel, addCategoryModel, CategoryListModel, removeServiceModel, removeServiceCategoryModel, SaveMeditation, getOutLetServicesCategory, saveCategoryServices, category_list_for_service, getServicesByVendor, getServices, removeService, removeServiceCategory, getMasterServiceByCategory, category_data, service_data, getServiceForBookingModel, getServiceListMethod, getAccomodationByOutlet


ns = Namespace('accomodation', description='Naturopathy Related related operations')


# Vendor Services
@ns.route('/')
class Accomodation(Resource):
    # @ns.expect(_addServices, validate=True)
    @ns.response(201, 'Outlet add Services.')
    @ns.doc('Vendor - Outlet add Services')
    def post(self):
        """ Save Accomodation save   """
        return SaveAccomodation(self)

    @ns.doc('Vendor - Outlet get Services')
    @ns.response(201, 'Outlet add Services.')
    def get(self):
        """ Get All Accomodation By Vendor """
        return getAccomodation(self)


@ns.route('/get_amenities')
class getAmenities(Resource):
    @ns.response(201, 'Vendor Login API.')
    @ns.doc('Vendor - Login')
    def get(self):
        """Vendor Login API """
        return getAmenitiesByOutlet(self)
    

@ns.route('/remove_accomodation')
class DeleteAccomodation(Resource):
    @ns.response(201, 'delete meditation.')
    @ns.doc('Vendor - Login')
    def post(self):
        """Vendor Login API """
        return remove_accomodation(self)

@ns.route('/get_all_accomodation')
class GetAllAccomodation(Resource):
    @ns.response(201, 'get all accomodation.')
    @ns.doc('Vendor - Login')
    def get(self):
        """Vendor Login API """
        outlet_id =""
        if request.args.get('outlet_id'):
            outlet_id = request.args.get('outlet_id')
        return accomodation_list(self,outlet_id)    

