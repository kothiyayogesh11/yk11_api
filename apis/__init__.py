from flask_restplus import Api
from flask import Blueprint
from .registration.routes import ns as NSregistration
from .login.routes import ns as NSlogin
from .profile.routes import ns as NSprofile
from .outlet.routes import ns as NSoutlet
from .staff.routes import ns as NSstaff
from .services.routes import ns as NSservices
from .settings.routes import ns as NSsettings
from .booking.routes import ns as NSbooking
from .role.routes import ns as NSrole
from .membership.routes import ns as NSmembership
from .feedback.routes import ns as NSfeedback
from .dashboard.routes import ns as NSdashboard
from .offer.routes import ns as NSoffer
from .spotlight.routes import ns as NSspotlight
from .vendor_inquiry.routes import ns as NSvendor_inquiry
from .meditation.routes import ns as NSmeditation
from .naturopathy.routes import ns as NSnaturopathy
from .accomodation.routes import ns as NSaccomodation
from .naturopathy.routes import ns as NSnaturopathy
'''
Refer below link for API metadata
https://flask-restplus.readthedocs.io/en/stable/api.html
'''


bp_api_v1 = Blueprint('api', __name__)
api = Api(
    bp_api_v1,
    title='Vendor APIs',
    version='1.0',
    description='A description',
    doc='/docs',
    validate=True
)

api.add_namespace(NSregistration)
api.add_namespace(NSlogin)
api.add_namespace(NSprofile)
api.add_namespace(NSoutlet)
api.add_namespace(NSstaff)
api.add_namespace(NSservices)
api.add_namespace(NSsettings)
api.add_namespace(NSbooking)
api.add_namespace(NSrole)
api.add_namespace(NSmembership)
api.add_namespace(NSfeedback)
api.add_namespace(NSdashboard)
api.add_namespace(NSoffer)
api.add_namespace(NSspotlight)
api.add_namespace(NSvendor_inquiry)
api.add_namespace(NSmeditation)
api.add_namespace(NSnaturopathy)
api.add_namespace(NSaccomodation)