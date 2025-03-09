from flask import Blueprint

bp = Blueprint('auth', __name__)

# import путей для Blueprint в конце(Чтобы избежать circular import)
from app.auth import routes  # noqa
from app.auth.routes import user_activity # noqa


__all__ = ['user_activity']
