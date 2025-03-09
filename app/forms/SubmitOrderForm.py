from datetime import date

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length, ValidationError


class SubmitOrderForm(FlaskForm):
    address = StringField('Адрес', validators=[DataRequired(),
                                               Length(max=60)])
    submit = SubmitField('Оформить заказ')

    def validate_shipment_date(self, shipment_date):
        if shipment_date.data <= date.today():
            raise ValidationError('Мы не можем доставить заказ так скоро.')
