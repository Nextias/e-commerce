from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length


class EditCategoryForm(FlaskForm):
    name = StringField('Название', validators=[DataRequired(),
                                               Length(max=64)])
    submit = SubmitField('Сохранить')
