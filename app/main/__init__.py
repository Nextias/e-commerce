from flask import Blueprint


bp = Blueprint('main', __name__)

# import путей для Blueprint в конце(Чтобы избежать circular import)
from app.main import routes # noqa
