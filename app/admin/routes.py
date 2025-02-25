import os
from functools import wraps
from urllib.parse import urlsplit

import sqlalchemy as sa
from flask import (abort, current_app, flash, redirect, render_template,
                   request, url_for)
from flask_login import current_user, login_required, login_user, logout_user
from werkzeug.utils import secure_filename

from app import db
from app.admin import bp
from app.forms import LoginForm, RegistrationForm, UploadForm
from app.models import Role, User, Product

ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

def admin_only(f):
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
    form = UploadForm()
    print(form, form.validate_on_submit())
    if not form.validate_on_submit():
        return redirect(url_for('main.product', id=id))
    # check if the post request has the file part
    print(request.files)
    product = db.session.get(Product, int(id))
    if product is None:
        flash('There is no such product')
        return redirect(request.url)
    if 'picture' not in request.files:
        flash('No picture part')
        return redirect(request.url)
    file = request.files['picture']
    # if user does not select file, browser also
    # submit a empty part without filename
    if file.filename == '':
        flash('No selected file')
        return redirect(request.url)
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(
            current_app.config['UPLOAD_FOLDER'], filename))
        print(current_user)
        product.photo_path = f'images/products/{filename}'
        print(product.photo_path)
        db.session.commit()
    flash('success')
    return redirect(request.url)


@bp.route('/admin', methods=('GET', 'POST'))
@login_required
@admin_only
def admin():
    return render_template('admin/admin.html')
