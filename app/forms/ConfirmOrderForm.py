from flask_wtf import FlaskForm
from wtforms import SubmitField


class ConfirmOrderForm(FlaskForm):
    """Форма подтверждения заказа."""
    submit = SubmitField('Подтвердить заказ')
