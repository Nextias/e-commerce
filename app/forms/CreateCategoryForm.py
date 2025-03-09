from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired


class CreateCategoryForm(FlaskForm):
    name = StringField('Название', validators=[DataRequired()])
    submit = SubmitField('Добавить')
