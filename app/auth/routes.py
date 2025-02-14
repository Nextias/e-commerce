from flask import render_template, redirect, url_for, flash, request
from urllib.parse import urlsplit
from flask_login import login_user, logout_user, current_user
from app.auth import bp
from app.forms import LoginForm
from app.models import user


@bp.route('/login', methods=('GET', 'POST'))
def login():
    form = LoginForm()
    if form.validate_on_submit():
        login_user(user)
        flash('Logged in successfully.')
        next = request.args.get('next')
        if not next or urlsplit(next).netloc != '':
            next = url_for('main.index')

        return redirect(next or url_for('index'))
    return render_template('login.html', form=form)