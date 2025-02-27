from flask_wtf import FlaskForm
from wtforms import FileField, SubmitField


class UploadForm(FlaskForm):
    picture = FileField('Update image')
    submit = SubmitField('Submit')
