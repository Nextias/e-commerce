from flask_wtf import FlaskForm
from wtforms import SubmitField


class CheckoutForm(FlaskForm):
    """Форма подтверждения корзины заказа."""
    submit = SubmitField('Перейти к подтверждению')
