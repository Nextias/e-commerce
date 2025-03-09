from flask_wtf import FlaskForm
from wtforms import SubmitField


class FinishOrderForm(FlaskForm):
    submit = SubmitField('Завершить заказ')
