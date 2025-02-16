from urllib.parse import urlsplit

import sqlalchemy as sa
from flask import flash, redirect, render_template, request, url_for, abort
from flask_login import current_user, login_user, logout_user, login_required

from app import db
from app.main import bp
from app.models.models import Product, Category


@bp.route('/', methods=('GET', 'POST'))
@bp.route('/index', methods=('GET', 'POST'))
def index():
    return render_template('main/index.html')


@bp.route('/product/<id>', methods=('GET', 'POST'))
def product(id):
    product = db.session.get(Product, int(id))
    if product is None:
        abort(404)
    categories_list = product.get_categories()
    return render_template('main/product.html', product=product,
                           categories=categories_list)
