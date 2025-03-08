from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, IntegerField, SelectMultipleField
from wtforms.validators import DataRequired


class EditProductForm(FlaskForm):
    name = StringField('Название', validators=[DataRequired()])
    price = IntegerField('Стоимость', validators=[DataRequired()])
    brand = StringField('Название бренда', validators=[DataRequired()])
    description = StringField('Описание', validators=[DataRequired()])
    categories = SelectMultipleField('Категории')
    submit = SubmitField('Сохранить')
