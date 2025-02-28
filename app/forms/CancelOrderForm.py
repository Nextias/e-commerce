from flask_wtf import FlaskForm
from wtforms import SubmitField


class CancelOrderForm(FlaskForm):
    submit = SubmitField('Отмена заказа')
