from flask import request, Response, make_response, jsonify
from flask_restplus import Resource,Namespace, marshal_with
from bson import json_util
import json
from config import Config
#from .model import dto, loginOtpModel, verificationCodeModel, login, generateLoginOtp, checkUserLogin, sendVerificationLink, vendorEmailVarification, change_password
from database import DB
from .model import *


ns = Namespace('login', description='Vendor login related operations')
_post = dto(object,ns)
_login_otp = loginOtpModel(object,ns)
_verification_code = verificationCodeModel(object,ns)
# Vendor Login
@ns.route('/')
class Login(Resource):
    @ns.expect(_post, validate=True)
    @ns.response(201, 'Vendor Login API.')
    @ns.doc('Vendor - Login')
    def post(self):
        """Vendor Login API """
        return login(self)

@ns.route('/logout')
class Logout(Resource):
    @ns.response(201, 'Vendor logout API.')
    @ns.doc('Vendor - update logout')
    def get(self):
        """ Save User Profile """
        return logout_request(self)

# Generate Login OTP
@ns.route('/otp')
class LoginOTP(Resource):
    @ns.expect(_login_otp, validate=True)
    @ns.response(201, 'Vendor - Login OTP successfully Generated.')
    @ns.doc('Vendor - Login OTP Generate')
    def post(self):
        """Vendor - Login OTP Generate """
        # data = request.json
        return generateLoginOtp(self)

@ns.route("/check_email_contact")
class checkLoginUser(Resource):
    
    @ns.response(201, 'Vendor - Login Email Or Contact Check.')
    @ns.doc('Vendor - Login Email Or Contact Check.')
    def post(self):
        """Vendor - Login Email Or Contact Check. """
        # data = request.json
        return checkUserLogin(self)

@ns.route("/email_verification_link")
class EmailVerification(Resource):
    @ns.response(201, 'Vendor - Send vedor verification link.')
    @ns.doc('Vendor - Vendor - Send verificatin link.')
    def get(self):
        """ Vendor - Vendor - Send verificatin link. """
        return sendVerificationLink(self)

    @ns.response(201, 'Vendor - Verify vendor email address.')
    @ns.doc('Vendor - Verify vendor email address')
    @ns.expect(_verification_code, validate=True)
    def post(self):
        # print("route")
        """ Vendor - Vendor - Send verificatin link. """
        return vendorEmailVarification(self)

