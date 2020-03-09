from flask import request, Response, make_response, jsonify
from flask_restplus import Resource,Namespace, marshal_with
from bson import json_util
import json
from config import Config
from .model import *
from database import DB


ns = Namespace('feedback', description='Vendor  related operations')

@ns.route('/feedback_data')
class Login(Resource):
    @ns.response(201, 'Vendor Login API.')
    @ns.doc('Vendor - Login')
    def get(self):
        """Vendor Login API """
        outlet_id = ""
        if request.args.get('outlet_id'):
            outlet_id = request.args.get('outlet_id')
        return feedback_data(self,outlet_id)
    
@ns.route('/feedback')
class Login(Resource):
    @ns.response(201, 'Vendor Login API.')
    @ns.doc('Vendor - Login')
    def post(self):
        """Vendor Login API """
        return feedback(self)


