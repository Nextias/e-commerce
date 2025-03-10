import sqlalchemy as sa
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length, ValidationError

from app import db
from app.models import Category  # type: ignore[name-defined]


class CreateCategoryForm(FlaskForm):
    """Форма создания категории."""
    name = StringField('Название', validators=[DataRequired(),
                                               Length(max=64)])
    submit = SubmitField('Добавить')

    def validate_name(self, name):
        user = db.session.scalar(
            sa.select(Category).where(Category.name == name.data))
        if user is not None:
            raise ValidationError('Используйте другое название категории.')
