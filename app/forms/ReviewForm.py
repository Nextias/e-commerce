from flask_wtf import FlaskForm
from wtforms import TextAreaField, SubmitField, RadioField
from wtforms.validators import DataRequired, Length


class ReviewForm(FlaskForm):
    """Форма добавления отзыва."""
    review = TextAreaField('Отзыв', validators=[DataRequired(),
                                                Length(max=140)])
    rating = RadioField(
        'Рейтинг',
        choices=[(1, '1'), (2, '2'), (3, '3'),
                 (4, '4'), (5, '5')],
        validators=[DataRequired()])
    submit = SubmitField('Оставить отзыв')
