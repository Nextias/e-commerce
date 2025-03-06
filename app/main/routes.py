import sqlalchemy as sa
from flask import (abort, flash, jsonify, redirect, render_template, request,
                   url_for)
from flask_login import current_user, login_required

from app import db
from app.forms import (CancelOrderForm, CheckoutForm, EditProfileForm,
                       SubmitOrderForm, UploadForm)
from app.main import bp
from app.models import Basket, BasketProduct, Order, Product


@bp.route('/', methods=('GET', 'POST'))
@bp.route('/index', methods=('GET', 'POST'))
@login_required
def index():
    """ Отображение стартовой страницы. """
    orders = current_user.user_orders
    return render_template('main/index.html', orders=orders)


@bp.route('/product/<id>', methods=('GET', 'POST'))
@login_required
def product(id):
    """ Отображение информации о товаре по id. """
    form = UploadForm()
    product = db.session.get(Product, int(id))
    if product is None:  # Продукт не найден
        abort(404)
    categories_list = product.categories
    # Получение количества заданного продукта в корзине
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
    """ Отображение страницы профиля. """
    return render_template('main/profile.html')


@bp.route('/edit_profile/', methods=('GET', 'POST'))
@login_required
def edit_profile():
    """ Отображение страницы редактирования профиля. """
    form = EditProfileForm()
    if form.validate_on_submit():
        # Изменение пользователя в соответствии с данными из формы
        current_user.first_name = form.first_name.data
        current_user.last_name = form.last_name.data
        current_user.phone_number = form.phone_number.data
        current_user.about_me = form.about_me.data
        current_user.address = form.address.data
        db.session.commit()
        return redirect(url_for('main.profile'))
    # Получение первоначальных данных для формы
    form.first_name.data = current_user.first_name
    form.last_name.data = current_user.last_name
    form.phone_number.data = current_user.phone_number
    form.about_me.data = current_user.about_me
    form.address.data = current_user.address
    return render_template('main/edit_profile.html/', form=form)


@bp.route('/order/<order_number>/', methods=('GET', 'POST'))
@login_required
def order(order_number):
    """ Отображение информации о заказе по order_number. """
    order = db.session.scalar(sa.select(Order).where(
        Order.order_number == order_number))
    if order is None:  # Заказ не найден
        abort(404)
    # Пользователь не владелец заказа и не админ
    elif (current_user.role.name != 'admin'
          and current_user.id != order.user_id):
        abort(404)  # Посторонний не получает информацию о наличии заказа
    # Получение информации о корзине по заказу
    basket = db.session.get(Basket, order.basket_id)
    basket_items = basket.get_basket_products()
    total_amount = basket.get_total_amount(basket_items)
    form = CancelOrderForm()
    return render_template('main/order.html', order=order,
                           products=basket_items, total_amount=total_amount,
                           form=form)


@bp.route('/explore/', methods=('GET', 'POST'))
def explore():
    """ Отображение главной страницы поиска товаров. """
    # Проверка наличия товаров в корзине
    if current_user.is_authenticated:
        basket = current_user.get_basket()
        basket_items = basket.get_basket_products()
    else:
        basket_items = {}
    # Составление списка продуктов
    products = dict.fromkeys(db.session.scalars(sa.select(Product)), 0)
    products.update(basket_items)
    return render_template('main/explore.html', products=products,
                           modify_amount=True)


@login_required
@bp.route('/basket/', methods=('GET', 'POST'))
def basket():
    """ Отображение корзины. """
    # Получение информации об актуальной корзине покупателя
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
    """ Добавление единицы продукта в корзину, с последующим возвращением
    актуального количества товара и полной стоимости по корзине в формате json.
    Функция предназначена для AJAX вызова.
    """
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
                    if request.headers.get('Referer')
                    and 'basket' in request.headers.get('Referer')
                    else None
                    )
    return jsonify(amount=basket_item.amount, total_amount=total_amount)


@login_required
@bp.route('/basket/remove_product/<product_id>', methods=('GET', 'POST'))
def remove_item(product_id):
    """ Удаление единицы продукта из корзины, с последующим возвращением
    актуального количества товара и полной стоимости по корзине в формате json.
    Функция предназначена для AJAX вызова.
    """
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
                    if request.headers.get('Referer')
                    and 'basket' in request.headers.get('Referer')
                    else None
                    )
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
    """ Отображение страницы подтверждения заказа. """
    form = CheckoutForm()  # Форма не прошла проверку
    if not form.validate_on_submit():
        flash('Ошибка валидации')
        return redirect(url_for('main.basket'))
    # Получение информации об актуальной корзине покупателя
    basket = current_user.get_basket()
    basket_items = basket.get_basket_products()
    if not basket_items:  # Корзина пуста
        flash('Корзина пуста')
        return redirect(url_for('main.basket'))
    total_amount = basket.get_total_amount(basket_items)
    order_form = SubmitOrderForm()
    order_form.address.data = current_user.address
    return render_template('main/checkout.html', products=basket_items,
                           total_amount=total_amount, form=order_form)


@login_required
@bp.route('/submit_order/', methods=('GET', 'POST'))
def submit_order():
    """ Формирование заказа. """
    form = SubmitOrderForm()
    if not form.validate_on_submit():
        flash('Ошибка валидации')
        return redirect(url_for('main.basket'))
    # Получение информации об актуальной корзине покупателя
    basket = current_user.get_basket()
    basket_items = basket.get_basket_products()
    total_amount = basket.get_total_amount(basket_items)
    # Подготовка к списанию товаров из доступных к продаже
    for product, amount in basket_items.items():
        # Если товаров не хватает для оформления заказов
        if product.stock < amount:
            flash('В наличии недостаточно товаров для оформления заказа')
            return redirect(url_for('main.basket'))
        product.stock -= amount
    # Формирование заказа
    order = Order(order_number=basket.id,
                  shipment_date=form.shipment_date.data,
                  total_amount=total_amount,
                  user_id=current_user.id,
                  address=form.address.data,
                  basket_id=basket.id)
    db.session.add(order)
    basket.active = False  # Смена статуса корзины с актуальной на архивную
    db.session.commit()  # Подтверждение всех действий с БД в рамках транзакции
    flash('Ваш заказ был успешно оформлен')
    return redirect(url_for('main.order', order_number=order.order_number))


@login_required
@bp.route('/cancel_order/<id>', methods=('GET', 'POST'))
def cancel_order(id):
    """ Отмена заказа. """
    form = CancelOrderForm()
    if not form.validate_on_submit():
        flash('Ошибка валидации')
        return redirect(url_for('main.index'))
    order = db.session.get(Order, int(id))
    if not order:  # Заказ не найден
        abort(404)
    # Пользователь не владелец заказа и не админ
    elif (current_user.role.name != 'admin'
          and current_user.id != order.user_id):
        abort(404)  # Посторонний не получает информацию о наличии заказа
    if order.status.name == 'Отменён':  # Заказ уже был отменён
        flash('Заказ уже был ранее отменён')
        return redirect(url_for('main.index'))
    # Смена статуса заказа
    order.set_status('Отменён')
    db.session.commit()
    flash('Заказ был успешно отменён')
    return redirect(url_for('main.index'))
