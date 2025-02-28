from urllib.parse import urlsplit

import sqlalchemy as sa
from flask import flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user

from app import db
from app.auth import bp
from app.forms import LoginForm, RegistrationForm
from app.models import User


@bp.route('/login', methods=('GET', 'POST'))
def login():
    """ Отображение страницы логина. """
    if current_user.is_authenticated:  # Пользователь уже залогинен
        return redirect(url_for('main.index'))
    form = LoginForm()
    if form.validate_on_submit():
        # Получение объекта записи User из БД
        user = db.session.scalar(
            sa.select(User).where(User.username == form.username.data))
        if user is None or not user.check_password(form.password.data):
            flash('Неверные имя пользователя или пароль')
            return redirect(url_for('auth.login'))
        login_user(user, remember=form.remember_me.data)  # Логин пользователя
        # Перенаправление после аутентификации
        next_page = request.args.get('next')
        if not next_page or urlsplit(next_page).netloc != '':
            next_page = url_for('main.index')
        return redirect(next_page)
    return render_template('auth/login.html', form=form)


@bp.route('/register', methods=('GET', 'POST'))
def register():
    """ Отображение страницы регистрации пользователя. """
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        # Создание пользователя
        user = User(
            username=form.username.data,
            email=form.email.data,
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Вы успешно зарегистрированы!')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', form=form)


@bp.route('/logout')
@login_required
def logout():
    """ Выход из сессии пользователя. """
    logout_user()
    return redirect(url_for('main.index'))
