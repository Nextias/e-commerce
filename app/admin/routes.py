from urllib.parse import urlsplit

import sqlalchemy as sa
from flask import flash, redirect, render_template, request, url_for, abort
from flask_login import current_user, login_required, login_user, logout_user

from app import db
from app.admin import bp
from app.forms import LoginForm, RegistrationForm
from app.models import User, Role


def admin_only(f):
    def wrapper(*args, **kwargs):
        admin_role = db.session.scalar(
            sa.select(Role).where(Role.name == 'admin'))
        if not current_user.role_id == admin_role.id:
            print(current_user.role)
            abort(403)
        return f(*args, **kwargs)
    return wrapper


@bp.route('/admin', methods=('GET', 'POST'))
@login_required
@admin_only
def admin():
    return 'heeeey'
