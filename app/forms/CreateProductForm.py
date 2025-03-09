from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, IntegerField, SelectMultipleField
from wtforms.validators import DataRequired, Length


class CreateProductForm(FlaskForm):
    name = StringField('Название', validators=[DataRequired(),
                                               Length(max=64)])
    price = IntegerField('Стоимость', validators=[DataRequired()])
    stock = IntegerField('В наличии', validators=[DataRequired()])
    brand = StringField('Название бренда', validators=[DataRequired(),
                                                       Length(max=40)])
    description = StringField('Описание', validators=[DataRequired(),
                                                      Length(max=140)])
    categories = SelectMultipleField('Категории')
    submit = SubmitField('Добавить')
