from flask_wtf import FlaskForm
from wtforms import SubmitField


class FinishOrderForm(FlaskForm):
    """Форма завершения заказа."""
    submit = SubmitField('Завершить заказ')
