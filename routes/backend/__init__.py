from flask import Blueprint

backend_bp = Blueprint('backend', __name__)

# Import and register routes
from routes.backend import team_chat  # noqa: F401,E402
