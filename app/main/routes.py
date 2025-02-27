import os
from urllib.parse import urlsplit

import sqlalchemy as sa
from flask import (abort, current_app, flash, jsonify, redirect,
                   render_template, request, url_for, g, session)
from flask_login import current_user, login_required, login_user, logout_user
from app.forms import (UploadForm, EditProfileForm, CheckoutForm,
                       SubmitOrderForm, CancelOrderForm)

from app import db
from app.main import bp
from app.models.models import (Basket, BasketProduct, Category, Order, Product,
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
    product = db.session.get(Product, int(id))
    if product is None:
        abort(404)
    categories_list = product.categories
    basket = current_user.get_basket()
    basket_item = db.session.scalar(sa.select(BasketProduct).where(
        BasketProduct.basket_id == basket.id,
        BasketProduct.product_id == product.id
    ))
    amount = basket_item.amount if basket_item else 0
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
        current_user.address = form.address.data
        db.session.commit()
        return redirect(url_for('main.profile'))
    form.first_name.data = current_user.first_name
    form.last_name.data = current_user.last_name
    form.phone_number.data = current_user.phone_number
    form.about_me.data = current_user.about_me
    form.address.data = current_user.address
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
    basket = db.session.get(Basket, order.basket_id)
    basket_items = basket.get_basket_products()
    total_amount = basket.get_total_amount(basket_items)
    form = CancelOrderForm()
    return render_template('main/order.html', order=order,
                           products=basket_items, total_amount=total_amount,
                           form=form)


@bp.route('/explore/', methods=('GET', 'POST'))
def explore():
    if current_user.is_authenticated:
        basket = current_user.get_basket()
        basket_items = basket.get_basket_products()
    else:
        basket_items = {}
    products = dict.fromkeys(db.session.scalars(sa.select(Product)), 0)
    products.update(basket_items)
    return render_template('main/explore.html', products=products,
                           modify_amount=True)


@login_required
@bp.route('/basket/', methods=('GET', 'POST'))
def basket():
    basket = current_user.get_basket()
    basket_items = basket.get_basket_products()
    total_amount = basket.get_total_amount(basket_items)
    form = CheckoutForm()
    return render_template('main/basket.html', products=basket_items,
                           total_amount=total_amount, form=form,
                           modify_amount=True)


@login_required
@bp.route('/basket/add_product/<product_id>', methods=('GET', 'POST'))
def add_item(product_id):
    product = db.session.get(Product, int(product_id))
    if product is None:
        abort(404)
    basket = current_user.get_basket()
    basket_item = db.session.scalar(sa.select(BasketProduct).where(
        BasketProduct.basket_id == basket.id,
        BasketProduct.product_id == product.id
    ))
    if basket_item is None:
        basket_item = BasketProduct(basket_id=basket.id,
                                    product_id=product.id,
                                    amount=0)
    if basket_item.amount < product.stock:
        basket_item.amount = basket_item.amount + 1
    db.session.add(basket_item)
    db.session.commit()
    total_amount = (basket.get_total_amount()
                    if 'basket' in request.headers.get('Referer') else None)
    return jsonify(amount=basket_item.amount, total_amount=total_amount)


@login_required
@bp.route('/basket/remove_product/<product_id>', methods=('GET', 'POST'))
def remove_item(product_id):
    product = db.session.get(Product, int(product_id))
    if product is None:
        abort(404)
    basket = current_user.get_basket()
    basket_item = db.session.scalar(sa.select(BasketProduct).where(
        BasketProduct.basket_id == basket.id,
        BasketProduct.product_id == product.id
    ))
    basket_item.amount = basket_item.amount - 1
    total_amount = (basket.get_total_amount()
                    if 'basket' in request.headers.get('Referer') else 0)
    if basket_item.amount < 1:
        db.session.delete(basket_item)
        db.session.commit()
        return jsonify(amount=0, total_amount=total_amount)
    db.session.add(basket_item)
    db.session.commit()
    return jsonify(amount=basket_item.amount, total_amount=total_amount)


@login_required
@bp.route('/checkout/', methods=('GET', 'POST'))
def checkout():
    form = CheckoutForm()
    if not form.validate_on_submit():
        return redirect(url_for('main.basket'))
    basket = current_user.get_basket()
    basket_items = basket.get_basket_products()
    if not basket_items:
        flash('Basket is empty')
        return redirect(url_for('main.basket'))
    total_amount = basket.get_total_amount(basket_items)
    order_form = SubmitOrderForm()
    order_form.address.data = current_user.address
    return render_template('main/checkout.html', products=basket_items,
                           total_amount=total_amount, form=order_form)


@login_required
@bp.route('/submit_order/', methods=('GET', 'POST'))
def submit_order():
    form = SubmitOrderForm()
    if not form.validate_on_submit():
        flash('Error')
        return redirect(url_for('main.basket'))
    basket = current_user.get_basket()
    basket_items = basket.get_basket_products()
    total_amount = basket.get_total_amount(basket_items)
    for product, amount in basket_items.items():
        if product.stock < amount:
            flash('Error')
            return redirect(url_for('main.basket'))
        product.stock -= amount

    order = Order(order_number=basket.id,
                  status='created',
                  shipment_date=form.shipment_date.data,
                  total_amount=total_amount,
                  user_id=current_user.id,
                  address=form.address.data,
                  basket_id=basket.id)
    db.session.add(order)
    basket.active = False
    db.session.commit()
    flash('Your order was created')
    return redirect(url_for('main.index'))


@login_required
@bp.route('/cancel_order/<id>', methods=('GET', 'POST'))
def cancel_order(id):
    print(id)
    form = CancelOrderForm()
    if not form.validate_on_submit():
        flash('Error')
        return redirect(url_for('main.index'))
    order = db.session.get(Order, int(id))
    if not order or not order.user_id == current_user.id:
        abort(404)
    if order.status == 'canceled':
        flash('Error')
        return redirect(url_for('main.index'))
    order.status = 'canceled'
    db.session.commit()
    flash('order cancelled successfully')
    return redirect(url_for('main.index'))
