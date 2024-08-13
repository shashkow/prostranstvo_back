from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length

class LoginForm(FlaskForm):
    phone = StringField('Телефон', validators=[DataRequired()],
                        render_kw={"placeholder": "Телефон", "pattern": "8 \(\d{3}\) \d{3}-\d{2}-\d{2}"})
    code = StringField('Код подтверждения', validators=[DataRequired(), Length(min=4, max=4)])
    submit = SubmitField('Войти')

class RegistrationForm(FlaskForm):
    name = StringField('Имя', validators=[DataRequired(), Length(min=2, max=50)])
    company = StringField('Компания')
    phone = StringField('Телефон', validators=[DataRequired(), Length(min=11, max=11)])
    code = StringField('Код подтверждения', validators=[DataRequired(), Length(min=4, max=4)])
    submit = SubmitField('Зарегистрироваться')
