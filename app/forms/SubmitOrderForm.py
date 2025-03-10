from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length


class SubmitOrderForm(FlaskForm):
    """Форма оформления заказа."""
    address = StringField('Адрес', validators=[DataRequired(),
                                               Length(max=60)])
    submit = SubmitField('Оформить заказ')
