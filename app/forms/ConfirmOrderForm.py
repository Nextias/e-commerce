from flask_wtf import FlaskForm
from wtforms import SubmitField


class ConfirmOrderForm(FlaskForm):
    submit = SubmitField('Подтвердить заказ.')
