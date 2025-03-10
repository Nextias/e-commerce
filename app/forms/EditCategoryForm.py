import sqlalchemy as sa
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length, ValidationError

from app import db
from app.models import Product  # type: ignore[name-defined]


class EditCategoryForm(FlaskForm):
    name = StringField('Название', validators=[DataRequired(),
                                               Length(max=64)])
    submit = SubmitField('Сохранить')

    def validate_name(self, name):
        user = db.session.scalar(
            sa.select(Product).where(Product.name == name.data))
        if user is not None:
            raise ValidationError('Используйте другое имя товара.')
