from flask import Blueprint

bp = Blueprint('errors', __name__)

# import путей для Blueprint в конце(Чтобы избежать circular import)
from app.errors import routes  # noqa
