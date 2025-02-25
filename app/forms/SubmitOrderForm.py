import sqlalchemy as sa
from flask_wtf import FlaskForm
from wtforms import BooleanField, DateField, StringField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError
from datetime import date

from app import db
from app.models.models import User


class SubmitOrderForm(FlaskForm):
    address = StringField(validators=[DataRequired()])
    shipment_date = DateField(validators=[DataRequired()])
    submit = SubmitField('Submit order')

    def validate_shipment_date(self, shipment_date):
        if shipment_date.data <= date.today():
            raise ValidationError('Cannot be shipped that early.')