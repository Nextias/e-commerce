import os
from urllib.parse import urlsplit

import sqlalchemy as sa
from flask import (abort, current_app, flash, jsonify, redirect,
                   render_template, request, url_for, g, session)
from flask_login import current_user, login_required, login_user, logout_user
from app.forms import (UploadForm, EditProfileForm, CheckoutForm,
                       SubmitOrderForm)

from app import db
from app.main import bp
from app.models.models import (Backet, BacketProduct, Category, Order, Product,
                               User, order_products)


@bp.route('/', methods=('GET', 'POST'))
@bp.route('/index', methods=('GET', 'POST'))
@login_required
def index():
    orders = current_user.user_orders
    return render_template('main/index.html', orders=orders)


@bp.route('/product/<id>', methods=('GET', 'POST'))
@login_required
def product(id):
    form = UploadForm()
    print(form)
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
                           categories=categories_list, amount=amount,
                           form=form)


@bp.route('/profile', methods=('GET', 'POST'))
@login_required
def profile():
    return render_template('main/profile.html')


@bp.route('/edit_profile/', methods=('GET', 'POST'))
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.first_name = form.first_name.data
        current_user.last_name = form.last_name.data
        current_user.phone_number = form.phone_number.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        return redirect(url_for('main.profile'))
    form.first_name.data = current_user.first_name
    form.last_name.data = current_user.last_name
    form.phone_number.data = current_user.phone_number
    form.about_me.data = current_user.about_me
    return render_template('main/edit_profile.html/', form=form)


@bp.route('/order/<order_number>/', methods=('GET', 'POST'))
@login_required
def order(order_number):
    order = db.session.scalar(sa.select(Order).where(
        Order.order_number == order_number))
    if order is None:
        abort(404)
    elif current_user.id != order.user_id:
        abort(403)
    backet = db.session.get(Backet, order.backet_id)
    backet_items = backet.get_backet_products()
    total_amount = backet.get_total_amount(backet_items)
    return render_template('main/order.html', order=order,
                           products=backet_items, total_amount=total_amount)


@bp.route('/explore/', methods=('GET', 'POST'))
def explore():
    if current_user.is_authenticated:
        backet = current_user.get_backet()
        backet_items = backet.get_backet_products()
    else:
        backet_items = {}
    products = dict.fromkeys(db.session.scalars(sa.select(Product)), 0)
    products.update(backet_items)
    return render_template('main/explore.html', products=products,
                           backet=backet_items)


@login_required
@bp.route('/backet/', methods=('GET', 'POST'))
def backet():
    form = CheckoutForm()
    backet = current_user.get_backet()
    backet_items = backet.get_backet_products()
    total_amount = backet.get_total_amount(backet_items)
    return render_template('main/backet.html', products=backet_items,
                           total_amount=total_amount, form=form, backet=backet)


@login_required
@bp.route('/backet/add_product/<product_id>', methods=('GET', 'POST'))
def add_item(product_id):
    product = db.session.get(Product, int(product_id))
    if product is None:
        abort(404)
    backet = current_user.get_backet()
    backet_item = db.session.query(BacketProduct).filter_by(
        backet_id=backet.id,
        product_id=product.id).first()
    if backet_item is None:
        backet_item = BacketProduct(backet_id=backet.id,
                                    product_id=product.id,
                                    amount=0)
    backet_item.amount = backet_item.amount + 1
    db.session.add(backet_item)
    db.session.commit()
    total_amount = (backet.get_total_amount()
                    if 'backet' in request.headers.get('Referer') else 0)
    return jsonify(amount=backet_item.amount, total_amount=total_amount)


@login_required
@bp.route('/backet/remove_product/<product_id>', methods=('GET', 'POST'))
def remove_item(product_id):
    product = db.session.get(Product, int(product_id))
    if product is None:
        abort(404)
    backet = current_user.get_backet()
    backet_item = db.session.query(BacketProduct).filter_by(
        backet_id=backet.id,
        product_id=product.id).first()
    backet_item.amount = backet_item.amount - 1
    total_amount = (backet.get_total_amount()
                    if 'backet' in request.headers.get('Referer') else 0)
    if backet_item.amount < 1:
        db.session.delete(backet_item)
        db.session.commit()
        return jsonify(amount=0, total_amount=total_amount)
    db.session.add(backet_item)
    db.session.commit()
    return jsonify(amount=backet_item.amount, total_amount=total_amount)


@login_required
@bp.route('/checkout/', methods=('GET', 'POST'))
def checkout():
    form = CheckoutForm()
    if not form.validate_on_submit():
        return redirect(url_for('main.backet'))
    order_form = SubmitOrderForm()
    order_form.address.data = current_user.address
    backet = current_user.get_backet()
    backet_items = backet.get_backet_products()
    total_amount = backet.get_total_amount(backet_items)
    return render_template('main/checkout.html', products=backet_items,
                           total_amount=total_amount, form=order_form)


@login_required
@bp.route('/submit_order/', methods=('GET', 'POST'))
def submit_order():
    form = SubmitOrderForm()
    if not form.validate_on_submit():
        flash('Error')
        return redirect(url_for('main.checkout'))
    backet = current_user.get_backet()
    total_amount = backet.get_total_amount()
    order = Order(order_number=backet.id,
                  status='created',
                  shipment_date=form.shipment_date.data,
                  total_amount=total_amount,
                  user_id=current_user.id,
                  address=form.address.data,
                  backet_id=backet.id)
    db.session.add(order)
    db.session.commit()
    backet.active = False
    flash('Your order was created')
    return redirect(url_for('main.index'))
