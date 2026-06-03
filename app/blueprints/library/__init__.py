from flask import Blueprint
library_bp = Blueprint("library", __name__, template_folder="../../templates/library")
from app.blueprints.library import routes  # noqa: F401, E402
