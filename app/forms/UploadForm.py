from flask_wtf import FlaskForm
from wtforms import FileField, SubmitField


class UploadForm(FlaskForm):
    """Форма загрузки изображения."""
    picture = FileField('Обновить изображение')
    submit = SubmitField('Подтвердить')
