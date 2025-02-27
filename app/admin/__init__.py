from flask import Blueprint


bp = Blueprint('admin', __name__)

# import путей для Blueprint в конце(Чтобы избежать circular import)
from app.admin import routes # noqa
