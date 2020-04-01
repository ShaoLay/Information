from flask import Blueprint

admin_blu = Blueprint("admin", __name__, url_prefix='/admin')

from . import views