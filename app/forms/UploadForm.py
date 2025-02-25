from flask_wtf import FlaskForm
from wtforms import FileField, SubmitField

from app import db
from app.models.models import User


class UploadForm(FlaskForm):
    picture = FileField('Update image')
    submit = SubmitField('Submit')
