from flask import request, Response, make_response, jsonify
from flask_restplus import Resource,Namespace, marshal_with
from bson import json_util
import json
from config import Config
from .model import *
from database import DB


ns = Namespace('booking', description='Vendor  related operations')
_get_available_slot = getAvailableSlotModel(object, ns)
_createOrderModel = createOrderModel(object, ns)
@ns.route('/calendar')
class Calendar(Resource):
    @ns.response(201, 'Vendor Login API.')
    @ns.doc('Vendor - Login')
    def get(self):
        """Vendor Login API """
        outlet_id = ""
        if request.args.get('outlet_id'):
            outlet_id=request.args.get('outlet_id')
        return get_calendar_data(self,outlet_id)
    
@ns.route('/booking_data')
class bookingdata(Resource):
    @ns.response(201, 'Vendor Login API.')
    @ns.doc('Vendor - Login')
    def get(self):
        """Vendor Login API """
        outlet_id = ""
        if request.args.get('outlet_id'):
            outlet_id=request.args.get('outlet_id')
        return get_booking_data(self,outlet_id)

@ns.route('/cal_status')
class booking_status(Resource):
    @ns.response(201, 'Vendor Login API.')
    @ns.doc('Vendor - Login')
    def post(self):
        """Vendor Login API """
        return calendar_status(self)


@ns.route('/get_booking_availability')
class booking_status_availibility(Resource):
    @ns.expect(_get_available_slot, validation=True)
    @ns.response(201, 'Vendor - get slot for booking.')
    @ns.doc('Vendor - get slot for booking')
    def post(self):
        """Vendor Login API """
        return getAvailableSlot(self)

@ns.route('/create_booking')
class create_booking(Resource):
    @ns.expect(_createOrderModel,validation=True)
    @ns.response(201, 'Vendor - Create Order.')
    @ns.doc('Vendor - Create order')
    def post(self):
        """Vendor Login API """
        return createBooking(self)

@ns.route('/get_services')
class get_services(Resource):
    @ns.response(201, 'Vendor Login API.')
    @ns.doc('Vendor - Login')
    def get(self):
        """Vendor Login API """
        outlet_id = ""
        if 'outlet_id' in request.args:
            outlet_id=request.args.get('outlet_id')
        return get_service_data(self,outlet_id)

@ns.route('/validate-qr-code')
class ValidateQrCode(Resource):
    @ns.response(201, 'Validate QR code at vendor outlet.')
    @ns.doc('Vendor - Booking')
    def get(self):
        return validate_qr_code(self)


