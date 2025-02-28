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
from app.forms import UploadForm
from app.models import Order, Product, Role, User

ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])


def admin_only(f):
    """ Декоратор проверки, что запрашивающий является админом. """
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
    if product is None:  # Продукт не найден
        flash('There is no such product')
        return redirect(request.url)
    # Проверка наличия файла
    if 'picture' not in request.files:
        flash('No picture part')
        return redirect(request.url)
    file = request.files['picture']
    if file.filename == '':
        flash('No selected file')
        return redirect(request.url)
    # Проверка файла
    if file and allowed_file(file.filename):
        # Сохранение файла в файловой системе и путь в БД
        filename = secure_filename(file.filename)
        file.save(os.path.join(
            current_app.config['UPLOAD_FOLDER'], filename))
        product.photo_path = f'images/products/{filename}'
        db.session.commit()
    flash('success')
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
    """ Отображение списка продуктов в панели администратора. """
    products = db.session.scalars(sa.select(Product))
    return render_template('admin/products.html', products=products)


@bp.route('/admin/create_product', methods=('GET', 'POST'))
@login_required
@admin_only
def create_product():
    """ Отображение страницы создания продукта. """
    return render_template('admin/create_product.html')
