import os
from functools import wraps

import sqlalchemy as sa
from flask import (abort, current_app, flash, redirect, render_template,
                   request, url_for)
from flask_login import current_user, login_required
from sqlalchemy import func
from werkzeug.utils import secure_filename

from app import db
from app.admin import bp
from app.forms import (CreateCategoryForm, CreateProductForm, EditCategoryForm,
                       EditProductForm, EditStockForm, UploadForm)
from app.models import Category, Order, Product, Role, User

ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])


def admin_only(f):
    """ Декоратор для проверки, что запрашивающий является админом. """
    @wraps(f)
    def wrapper(*args, **kwargs):
        admin_role = db.session.scalar(
            sa.select(Role).where(Role.name == 'admin'))
        if not current_user.role_id == admin_role.id:
            print(current_user.role)
            abort(403)
        return f(*args, **kwargs)
    return wrapper


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@bp.route('/admin/upload/image/product/<id>', methods=('GET', 'POST'))
@admin_only
def upload_product_image(id):
    """ Загрузка изображения продукта. """
    form = UploadForm()
    if not form.validate_on_submit():
        return redirect(url_for('main.product', id=id))
    product = db.session.get(Product, int(id))
    if product is None:  # Товар не найден
        flash(f'Продукт с id {id} не был найден')
        return redirect(request.url)
    # Проверка наличия файла
    if 'picture' not in request.files:
        flash('Отсутствует составляющая UploadForm picture')
        return redirect(request.url)
    file = request.files['picture']
    if file.filename == '':
        flash('Не выбран файл')
        return redirect(request.url)
    # Проверка файла
    if file and allowed_file(file.filename):
        # Сохранение файла в файловой системе и путь в БД
        filename = secure_filename(file.filename)
        file.save(os.path.join(
            current_app.config['UPLOAD_FOLDER'], filename))
        product.photo_path = f'images/products/{filename}'
        db.session.commit()
    flash('Файл был успешно загружен')
    return redirect(request.url)


@bp.route('/admin', methods=('GET', 'POST'))
@login_required
@admin_only
def admin():
    """ Отображение панели администратора. """
    users_amount = db.session.query(func.count(User.id)).scalar()
    products_amount = db.session.query(func.count(Product.id)).scalar()
    orders_amount = db.session.query(func.count(Order.id)).scalar()
    return render_template('admin/admin.html', users_amount=users_amount,
                           products_amount=products_amount,
                           orders_amount=orders_amount)


@bp.route('/admin/products', methods=('GET', 'POST'))
@login_required
@admin_only
def products():
    """Отображение товаров в панели администратора."""
    products = db.session.scalars(
        sa.select(Product).order_by(Product.id.desc()))
    return render_template('admin/products.html', products=products)


@bp.route('/admin/create_product', methods=('GET', 'POST'))
@login_required
@admin_only
def create_product():
    """ Отображение страницы создания товара. """
    form = CreateProductForm()
    # Формирование списка категорий
    categories = db.session.scalars(sa.select(Category).order_by(
        Category.id.desc()))
    form.categories.choices = [category.name for category in categories]
    if form.validate_on_submit():
        # Добавление продукта в базу
        product = Product(name=form.name.data,
                          price=form.price.data,
                          stock=form.stock.data,
                          brand=form.brand.data,
                          description=form.description.data
                          )
        categories = db.session.scalars(
            sa.select(Category).where(
                Category.name.in_(form.categories.data)
            )
        ).all()
        product.categories = categories
        db.session.add(product)
        db.session.commit()
        flash('Товар успешно добавлен')
        return redirect(url_for('admin.products'))
    return render_template('admin/create_product.html', form=form)


@bp.route('/admin/edit_stock/<id>', methods=('GET', 'POST'))
@login_required
@admin_only
def edit_stock(id):
    """ Отображение страницы редактирования продуктов в наличии. """
    form = EditStockForm()
    if form.validate_on_submit():
        product = db.session.get(Product, id)
        product.stock = form.amount.data
        db.session.commit()
        flash('Количество товаров в наличии успешно изменено'
              f' на {product.stock}.')
        return redirect(url_for('main.product', id=id))
    return redirect(url_for('main.product', id=id))


@bp.route('/admin/edit_product/<id>', methods=('GET', 'POST'))
@login_required
@admin_only
def edit_product(id):
    """ Отображение редактирования товара."""
    form = EditProductForm()
    # Формирование списка категорий
    categories = db.session.scalars(sa.select(Category).order_by(
        Category.name))
    form.categories.choices = [category.name for category in categories]
    if form.validate_on_submit():
        # Изменение товара в соответствии с данными из формы
        product = db.session.get(Product, int(id))
        product.name = form.name.data
        product.price = form.price.data
        product.brand = form.brand.data
        product.description = form.description.data
        if product is None:  # Товар не найден
            return redirect(url_for('main.product', id=id))
        categories = db.session.scalars(
            sa.select(Category).where(
                Category.name.in_(form.categories.data)
            )
        ).all()
        product.categories = categories
        db.session.commit()
        flash('Редактирование завершено успешно.')
        return redirect(url_for('main.product', id=id))
    # Получение первоначальных данных для формы
    product = db.session.get(Product, int(id))
    if product is None:  # Товар не найден
        return redirect(url_for('main.product', id=id))
    form.name.data = product.name
    form.price.data = product.price
    form.brand.data = product.brand
    form.description.data = product.description
    form.categories.data = [category.name for category in product.categories]
    return render_template('admin/edit_product.html/', form=form)


@bp.route('/admin/delete_product/<id>', methods=('GET', 'POST'))
@login_required
@admin_only
def delete_product(id):
    """Удаление товара по id. """
    product = db.session.get(Product, int(id))
    if product is None:
        return redirect(url_for('admin.products'))
    db.session.delete(product)
    db.session.commit()
    flash('Удаление успешно завершено.')
    return redirect(url_for('admin.products'))


@bp.route('/admin/orders', methods=('GET', 'POST'))
@login_required
@admin_only
def orders():
    """Отображение заказов в панели администратора. """
    orders = db.session.scalars(sa.select(Order).order_by(Order.id.desc()))
    orders_dict = {order: order.customer for order in orders}
    return render_template('admin/orders.html', orders=orders_dict)


@bp.route('/admin/confirm_order/<order_number>/', methods=('GET', 'POST'))
@login_required
@admin_only
def confirm_order(order_number):
    """Подтверждение заказа."""
    order = db.session.scalar(sa.select(Order).where(
        Order.order_number == order_number))
    if order is None:  # Заказ не найден
        abort(404)
    if order.status.name == 'Подтверждён':  # Заказ уже был подтверждён
        flash('Заказ уже был ранее подтверждён')
        return redirect(url_for('admin.orders'))
    # Смена статуса заказа
    order.set_status('Подтверждён')
    db.session.commit()
    flash('Заказ был успешно подтверждён')
    return redirect(url_for('admin.orders'))


@bp.route('/admin/finish_order/<order_number>/', methods=('GET', 'POST'))
@login_required
@admin_only
def finish_order(order_number):
    """Завершение заказа."""
    order = db.session.scalar(sa.select(Order).where(
        Order.order_number == order_number))
    if order is None:  # Заказ не найден
        abort(404)
    if order.status.name != 'Подтверждён':  # Заказ не был подтверждён
        flash('Можно завершить лишь подтверждённый заказ')
        return redirect(url_for('admin.orders'))
    # Смена статуса заказа
    order.set_status('Завершён')
    db.session.commit()
    flash('Заказ был успешно завершён')
    return redirect(url_for('admin.orders'))


@bp.route('/admin/users', methods=('GET', 'POST'))
@login_required
@admin_only
def users():
    """Отображение пользователей в панели администратора. """
    users = db.session.scalars(sa.select(User).order_by(User.username))
    return render_template('admin/users.html', users=users)


@bp.route('/admin/ban_user/<id>', methods=('GET', 'POST'))
@login_required
@admin_only
def ban_user(id):
    """Блокировать пользователя по id."""
    user = db.session.get(User, int(id))
    if user is None:  # Пользователь не найден
        flash('Пользователь не найден')
        return redirect(url_for('admin.users'))
    if user.banned:  # Пользователь уже в бане
        flash('Пользователь был ранее заблокирован')
        return redirect(url_for('admin.users'))
    user.banned = True
    db.session.commit()
    flash(f'Пользователь {user.username} был успешно заблокирован')
    return redirect(url_for('admin.users'))


@bp.route('/admin/unban_user/<id>', methods=('GET', 'POST'))
@login_required
@admin_only
def unban_user(id):
    """Разблокировать пользователя по id."""
    user = db.session.get(User, int(id))
    if user is None:  # Пользователь не найден
        flash('Пользователь не найден')
        return redirect(url_for('admin.users'))
    if not user.banned:  # Пользователь не в бане
        flash('Пользователь не заблокирован')
        return redirect(url_for('admin.users'))
    user.banned = False
    db.session.commit()
    flash(f'Пользователь {user.username} был успешно разблокирован')
    return redirect(url_for('admin.users'))


@bp.route('/admin/categories', methods=('GET', 'POST'))
@login_required
@admin_only
def categories():
    """Отображение категорий в панели администратора."""
    categories = db.session.scalars(sa.select(Category).order_by(
        Category.name))
    return render_template('admin/categories.html', categories=categories)


@bp.route('/admin/create_category', methods=('GET', 'POST'))
@login_required
@admin_only
def create_category():
    """ Отображение страницы создания категории. """
    form = CreateCategoryForm()
    if form.validate_on_submit():
        # Добавление категории в базу
        category = Category(name=form.name.data)
        db.session.add(category)
        db.session.commit()
        flash('Категория успешно добавлена')
        return redirect(url_for('admin.categories'))
    return render_template('admin/create_category.html', form=form)


@bp.route('/admin/edit_category/<id>', methods=('GET', 'POST'))
@login_required
@admin_only
def edit_category(id):
    """ Отображение редактирования категории."""
    form = EditCategoryForm()
    # Формирование списка категорий
    if form.validate_on_submit():
        # Изменение товара в соответствии с данными из формы
        category = db.session.get(Category, int(id))
        category.name = form.name.data
        db.session.commit()
        flash('Редактирование завершено успешно.')
        return redirect(url_for('admin.categories'))
    # Получение первоначальных данных для формы
    category = db.session.get(Category, int(id))
    if category is None:  # Категория не найдена
        return redirect(url_for('admin.categories'))
    form.name.data = category.name
    return render_template('admin/edit_category.html/', form=form)


@bp.route('/admin/delete_category/<id>', methods=('GET', 'POST'))
@login_required
@admin_only
def delete_category(id):
    """Удаление категории по id."""
    category = db.session.get(Category, int(id))
    if category is None:
        return redirect(url_for('admin.categories'))
    db.session.delete(category)
    db.session.commit()
    flash('Удаление успешно завершено.')
    return redirect(url_for('admin.categories'))
