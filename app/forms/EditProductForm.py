from flask_wtf import FlaskForm
from wtforms import IntegerField, SelectMultipleField, StringField, SubmitField
from wtforms.validators import DataRequired, Length


class EditProductForm(FlaskForm):
    """Форма редактирования товара."""
    name = StringField('Название', validators=[DataRequired(),
                                               Length(max=64)])
    price = IntegerField('Стоимость', validators=[DataRequired()])
    brand = StringField('Название бренда', validators=[DataRequired(),
                                                       Length(max=40)])
    description = StringField('Описание', validators=[DataRequired(),
                                                      Length(max=140)])
    categories = SelectMultipleField('Категории')
    submit = SubmitField('Сохранить')
