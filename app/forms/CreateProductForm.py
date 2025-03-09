import sqlalchemy as sa
from flask_wtf import FlaskForm
from wtforms import IntegerField, SelectMultipleField, StringField, SubmitField
from wtforms.validators import DataRequired, Length, ValidationError

from app import db
from app.models import Product  # type: ignore[name-defined]


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

    def validate_name(self, name):
        user = db.session.scalar(
            sa.select(Product).where(Product.name == name.data))
        if user is not None:
            raise ValidationError('Используйте другое имя товара.')
