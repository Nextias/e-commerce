from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, IntegerField
from wtforms.validators import DataRequired


class AddProductForm(FlaskForm):
    name = StringField('Название', validators=[DataRequired()])
    price = IntegerField('Стоимость', validators=[DataRequired()])
    stock = IntegerField('В наличии', validators=[DataRequired()])
    brand = StringField('Название бренда', validators=[DataRequired()])
    description = StringField('Описание', validators=[DataRequired()])
    submit = SubmitField('Добавить')

    def validate_brand(self, brand_name):
        # Реализовать после появления таблицы брендов, убедится,
        #  что бренд существует
        return True
