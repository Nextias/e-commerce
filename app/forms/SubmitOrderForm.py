from datetime import date

from flask_wtf import FlaskForm
from wtforms import DateField, StringField, SubmitField
from wtforms.validators import DataRequired, ValidationError


class SubmitOrderForm(FlaskForm):
    address = StringField(validators=[DataRequired()])
    shipment_date = DateField(validators=[DataRequired()])
    submit = SubmitField('Submit order')

    def validate_shipment_date(self, shipment_date):
        if shipment_date.data <= date.today():
            raise ValidationError('Cannot be shipped that early.')
