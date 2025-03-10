from flask_wtf import FlaskForm
from wtforms import SubmitField


class CancelOrderForm(FlaskForm):
    """Форма отмены заказа."""
    submit = SubmitField('Отменить заказ')
