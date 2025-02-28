from flask_wtf import FlaskForm
from wtforms import FileField, SubmitField


class UploadForm(FlaskForm):
    picture = FileField('Обновить изображение')
    submit = SubmitField('Подтвердить')
