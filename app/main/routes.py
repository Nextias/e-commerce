import sqlalchemy as sa
from flask import (abort, current_app, flash, jsonify, redirect,
                   render_template, request, url_for)
from flask_login import current_user, login_required

from app import db
from app.forms import (CancelOrderForm, CheckoutForm, ConfirmOrderForm,
                       EditProfileForm, EditStockForm, FinishOrderForm,
                       ReviewForm, SubmitOrderForm, UploadForm)
from app.main import bp
from app.models import Basket, BasketProduct, Order, Product, Review


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
    """ Отображение информации о товаре по id."""
    product = db.session.get(Product, int(id))
    if product is None:  # Продукт не найден
        abort(404)
    form = UploadForm()
    edit_stock_form = EditStockForm()
    review_form = ReviewForm()
    if review_form.validate_on_submit():  # Если был написан отзыв
        previous_review = db.session.scalar(
            sa.select(Review)
            .where(Review.user_id == current_user.id,
                   Review.product_id == product.id))
        if previous_review:  # Удаление старого отзыва на товар
            db.session.delete(previous_review)
        # Создание нового отзыва
        rating = int(review_form.rating.data)
        review_text = review_form.review.data
        review = Review(user_id=current_user.id, product_id=product.id,
                        rating=rating, review=review_text)
        db.session.add(review)
        product.update_rating()  # Обновление среднего рейтинга товара
        db.session.commit()
    # Получение количества заданного продукта в корзине
    basket = current_user.get_basket()
    basket_item = db.session.scalar(sa.select(BasketProduct).where(
        BasketProduct.basket_id == basket.id,
        BasketProduct.product_id == product.id
    ))
    amount = basket_item.amount if basket_item else 0
    return render_template('main/product.html', product=product,
                           categories=product.categories, amount=amount,
                           form=form, edit_stock_form=edit_stock_form,
                           review_form=review_form, reviews=product.reviews)


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
    cancel_form = CancelOrderForm()
    confirm_form = ConfirmOrderForm()
    finish_form = FinishOrderForm()
    return render_template('main/order.html', order=order,
                           products=basket_items, total_amount=total_amount,
                           cancel_form=cancel_form, confirm_form=confirm_form,
                           finish_form=finish_form)


@bp.route('/explore/', methods=('GET', 'POST'))
def explore():
    """ Отображение главной страницы поиска товаров. """
    page = request.args.get('page', 1, type=int)
    # Проверка наличия товаров в корзине
    if current_user.is_authenticated:
        basket = current_user.get_basket()
        basket_items = basket.get_basket_products()
    else:
        basket_items = {}
    # Если был введён поисковой запрос, то фильтруется результат
    query = sa.select(Product).order_by(Product.id.desc())
    search_query = request.args.get('q', '').strip()
    if search_query:
        query = query.where(
            sa.or_(
                Product.name.ilike(f'%{search_query}%'),
                Product.description.ilike(f'%{search_query}%')
            )
        )
    # Составление списка продуктов
    products = db.paginate(query, page=page,
                           per_page=current_app.config['PAGE_LENGTH'],
                           error_out=False)
    next_url = (url_for('main.explore', page=products.next_num, q=search_query)
                if products.has_next else None)
    prev_url = (url_for('main.explore', page=products.prev_num)
                if products.has_prev else None)
    products = dict.fromkeys(products, 0)
    products.update({product: amount
                     for product, amount in basket_items.items()
                     if product in products})
    return render_template('main/explore.html', products=products,
                           modify_amount=True, next_url=next_url,
                           prev_url=prev_url, search_query=search_query)


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
    form = CheckoutForm()
    if not form.validate_on_submit():  # Форма не прошла проверку
        flash('Ошибка валидации')
        return redirect(url_for('main.basket'))
    # Получение информации об актуальной корзине покупателя
    basket = current_user.get_basket()
    basket_items = basket.get_basket_products()
    if not basket_items:  # Корзина пуста
        flash('Корзина пуста')
        return redirect(url_for('main.basket'))
    total_amount = basket.get_total_amount(basket_items)
    shipment_date = basket.get_shipment_date()
    order_form = SubmitOrderForm()
    order_form.address.data = current_user.address
    return render_template('main/checkout.html', products=basket_items,
                           total_amount=total_amount, form=order_form,
                           shipment_date=shipment_date)


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
    order = Order(shipment_date=basket.get_shipment_date(),
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
@bp.route('/cancel_order/<order_number>', methods=('GET', 'POST'))
def cancel_order(order_number):
    """ Отмена заказа. """
    form = CancelOrderForm()
    if not form.validate_on_submit():
        flash('Ошибка валидации')
        return redirect(url_for('main.index'))
    order = db.session.scalar(sa.select(Order).where(
        Order.order_number == order_number))
    if order is None:  # Заказ не найден
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
    # Возвращение количества товаров в наличие
    basket = order.basket
    basket_items = basket.get_basket_products()
    for product, amount in basket_items.items():
        product.stock += amount
    db.session.commit()
    flash('Заказ был успешно отменён')
    return redirect(url_for('main.index'))
