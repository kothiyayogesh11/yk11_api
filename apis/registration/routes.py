from flask import request, Response, make_response, jsonify
from flask_restplus import Resource,Namespace, marshal_with
from bson import json_util
import json
from config import Config
from .model import vendorModel, verifyEmail, forgotPassword, contactPersonOtp, save_vendor, verify_email, verify_contact, forgot_password_request, forgot_password, verify_contact_person_number, generate_contact_person_otp, tour_steps, get_tour_steps, insert_newsletter, change_password, delete_account

ns = Namespace('registration', description='Vendor registration related operations')
_vendorModel = vendorModel(object,ns)
_forgot_password = forgotPassword(object,ns)
_contact_person_otp = contactPersonOtp(object, ns)
_verify_email = verifyEmail(object,ns)

@ns.route('/')
class Registration(Resource):
    
    # @ns.expect(_vendorModel, validate=True)
    @ns.response(201, 'User successfully created.')
    @ns.doc('create business')
    def post(self):
        """Creates a new business """
        return save_vendor(self)

# Vendor email verification
@ns.route("/email_verify")
class Email_verify(Resource):
    @ns.doc('verify vendor email')
    @ns.expect(_verify_email, validate=True)
    @ns.response(201, 'User successfully created.')
    def post(self):
        """Verify email address """
        return verify_email(self)



""" @ns.route("/contact_verify/<int:otp>")
class Contact_verify(Resource):
    @ns.doc('verify vendor contact')
    def get(self,otp):
        
        return verify_contact(self,otp) """


@ns.route("/contact_person_number")
class Contact_person_verify(Resource):
    @ns.doc('verify vendor person contact number')
    @ns.response(201, 'Contact number has been verified.')
    def get(self):
        """Verify contact person number """
        return verify_contact_person_number(self)

    @ns.doc('Generate contact person OTP')
    @ns.expect(_contact_person_otp, validate=True)
    @ns.response(201, 'OTP successfully send.')
    def post(self):
        """Generate contact person OTP """
        return generate_contact_person_otp(self)

@ns.route("/forgot_password_request")
class Forgot_password_request(Resource):
    @ns.doc('Forgot password Request')
    @ns.response(201, 'Forgot password Request done.')
    def post(self):
        """Forgot password """
        return forgot_password_request(self)

@ns.route("/forgot_password")
class Forgot_password(Resource):
    @ns.expect(_forgot_password, validate=True)
    @ns.response(201, 'User successfully created.')
    @ns.doc('Forgot password - Process')
    def post(self):
        """Forgot password Save"""
        return forgot_password(self)

@ns.route("/update_vendor_status")
class UpdateVendorStatus(Resource):
    # @ns.expect(_forgot_password, validate=True)
    @ns.response(201, 'Subscription added successfully created.')
    @ns.doc('Subscription update - Process')
    def post(self):
        """Forgot password Save"""
        return tour_steps(self)
    

@ns.route("/get_vendor_status")
class GetVendorStatus(Resource):
    # @ns.expect(_forgot_password, validate=True)
    @ns.response(201, 'Subscription added successfully created.')
    @ns.doc('Subscription update - Process')
    def get(self):
        """Forgot password Save"""
        vendor_id = request.args.get('vendor_id')
        return get_tour_steps(self,vendor_id)
    

@ns.route("/add_newsletter")
class AddNewsLetter(Resource):
    # @ns.expect(_forgot_password, validate=True)
    @ns.response(201, 'Newsletter added successfully created.')
    @ns.doc('newsletter update - Process')
    def post(self):
        """newsletter Save"""
        return insert_newsletter(self)



@ns.route("/change_password")
class changePassword(Resource): 
    @ns.response(201, 'Vendor - change password.')
    @ns.doc('Vendor - change password.')
    def post(self):
        """Vendor - change password. """
        # data = request.json
        return change_password(self)

@ns.route("/delete_user")
class DeleteUser(Resource): 
    @ns.response(201, 'Vendor - delete user.')
    @ns.doc('Vendor - delete user.')
    def post(self):
        """Vendor - delete user."""
        # data = request.json
        return delete_account(self)    
