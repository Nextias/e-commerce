import phonenumbers
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, ValidationError


class EditProfileForm(FlaskForm):
    first_name = StringField('Name', validators=[DataRequired()])
    last_name = StringField('Last name', validators=[DataRequired()])
    phone_number = StringField('Phone')
    about_me = StringField('About me')
    address = StringField('Address')
    submit = SubmitField('Confirm')

    def validate_phone_number(form, field):
        if len(field.data) > 16:
            raise ValidationError('Invalid phone number.')
        try:
            input_number = phonenumbers.parse(field.data)
            if not (phonenumbers.is_valid_number(input_number)):
                raise ValidationError('Invalid phone number.')
        except ValidationError:
            input_number = phonenumbers.parse("+1"+field.data)
            if not (phonenumbers.is_valid_number(input_number)):
                raise ValidationError('Invalid phone number.')
