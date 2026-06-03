from flask import Blueprint
scan_bp = Blueprint("scan", __name__, template_folder="../../templates/scan")
from app.blueprints.scan import routes  # noqa: F401, E402
