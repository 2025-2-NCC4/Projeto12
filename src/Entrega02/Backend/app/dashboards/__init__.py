from flask import Blueprint
dash_bp = Blueprint("dashboards", __name__, url_prefix="/api")
from . import ceo, cfo  