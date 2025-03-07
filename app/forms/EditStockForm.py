from flask_wtf import FlaskForm
from wtforms import SubmitField, IntegerField
from wtforms.validators import ValidationError


class EditStockForm(FlaskForm):
    amount = IntegerField('Количество', default=0)
    submit = SubmitField('Изменить')

    def validate_amount(self, field):
        if field.data < 0:
            raise ValidationError('Количество не может быть меньше')
