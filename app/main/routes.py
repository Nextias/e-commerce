from urllib.parse import urlsplit

import sqlalchemy as sa
from flask import redirect, render_template, request, abort, jsonify, url_for
from flask_login import current_user, login_user, logout_user, login_required

from app import db
from app.main import bp
from app.models.models import (Product, Category, User, Order, order_products,
                               Backet, BacketProduct)


@bp.route('/', methods=('GET', 'POST'))
@bp.route('/index', methods=('GET', 'POST'))
def index():
    if not current_user.is_authenticated:
        return redirect(url_for('main.explore'))
    orders = current_user.user_orders
    return render_template('main/index.html', orders=orders)


@bp.route('/product/<id>', methods=('GET', 'POST'))
def product(id):
    product = db.session.get(Product, int(id))
    if product is None:
        abort(404)
    categories_list = product.categories
    backet = current_user.get_backet()
    backet_item = db.session.scalar(sa.select(BacketProduct).where(
        BacketProduct.backet_id == backet.id,
        BacketProduct.product_id == product.id
    ))
    amount = backet_item.amount or 0
    return render_template('main/product.html', product=product,
                           categories=categories_list, amount=amount)


@bp.route('/profile', methods=('GET', 'POST'))
@login_required
def profile():
    return render_template('main/profile.html')


@login_required
@bp.route('/order/<order_number>/', methods=('GET', 'POST'))
def order(order_number):
    order = db.session.scalar(sa.select(Order).where(
        Order.order_number == order_number))
    if order is None:
        abort(404)
    elif current_user.id != order.user_id:
        abort(403)
    products = order.products
    return render_template('main/order.html', order=order, products=products)


@bp.route('/explore/', methods=('GET', 'POST'))
def explore():
    backet = current_user.get_backet()
    backet_items = backet.get_backet_products()
    products = dict.fromkeys(db.session.scalars(sa.select(Product)), 0)
    products.update(backet_items)
    return render_template('main/explore.html', products=products,
                           backet=backet_items)


@login_required
@bp.route('/backet/', methods=('GET', 'POST'))
def backet():
    backet = current_user.get_backet()
    backet_items = backet.get_backet_products()
    return render_template('main/backet.html', products=backet_items)


@login_required
@bp.route('/backet/add_product/<product_id>', methods=('GET', 'POST'))
def add_item(product_id):
    product = db.session.get(Product, int(product_id))
    if product is None:
        abort(404)
    backets = current_user.user_backets
    if not backets:
        backet = Backet(user_id=current_user.id, active=True)
        db.session.add(backet)
        db.session.commit()
    else:
        backet = backets[0]
    backet_item = db.session.query(BacketProduct).filter_by(
        backet_id=backet.id,
        product_id=product.id).first()
    print(backet_item)
    if backet_item is None:
        backet_item = BacketProduct(backet_id=backet.id,
                                    product_id=product.id,
                                    amount=0)
    backet_item.amount = backet_item.amount + 1
    db.session.add(backet_item)
    db.session.commit()
    print(jsonify(amount=backet_item.amount))
    return jsonify(amount=backet_item.amount)


@login_required
@bp.route('/backet/remove_product/<product_id>', methods=('GET', 'POST'))
def remove_item(product_id):
    product = db.session.get(Product, int(product_id))
    if product is None:
        abort(404)
    backets = current_user.user_backets
    if not backets:
        backet = Backet(user_id=current_user.id, active=True)
        db.session.add(backet)
        db.session.commit()
    else:
        backet = backets[0]
    backet_item = db.session.query(BacketProduct).filter_by(
        backet_id=backet.id,
        product_id=product.id).first()
    print(backet_item)
    backet_item.amount = backet_item.amount - 1
    if backet_item.amount < 1:
        db.session.delete(backet_item)
        db.session.commit()
        return jsonify(amount=0)
    db.session.add(backet_item)
    db.session.commit()
    print(jsonify(amount=backet_item.amount))
    return jsonify(amount=backet_item.amount)
