from urllib.parse import urlsplit

import sqlalchemy as sa
from flask import flash, redirect, render_template, request, abort, jsonify
from flask_login import current_user, login_user, logout_user, login_required

from app import db
from app.main import bp
from app.models.models import Product, Category, User, Order, order_products


@bp.route('/', methods=('GET', 'POST'))
@bp.route('/index', methods=('GET', 'POST'))
def index():
    orders = current_user.user_orders
    print(orders)
    return render_template('main/index.html', orders=orders)


@bp.route('/product/<id>', methods=('GET', 'POST'))
def product(id):
    product = db.session.get(Product, int(id))
    if product is None:
        abort(404)
    categories_list = product.categories
    return render_template('main/product.html', product=product,
                           categories=categories_list)


@login_required
@bp.route('/profile', methods=('GET', 'POST'))
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
    print(order)
    products = order.products
    print(products)
    return render_template('main/order.html', order=order, products=products)


@bp.route('/explore/', methods=('GET', 'POST'))
def explore():
    products = db.session.scalars(sa.select(Product))
    return render_template('main/explore.html', products=products)


@bp.route('/add_item/', methods=['POST'])
def add_item():
    new_item = Product()
    cart_items.append(new_item)
    return jsonify(success=True, item=new_item)

@bp.route('/remove_item/<int:item_id>', methods=['POST'])
def remove_item(item_id):
    global cart_items
    cart_items = [item for item in cart_items if item['id'] != item_id]
    return jsonify(success=True, item_id=item_id)