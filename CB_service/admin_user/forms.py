from flask_wtf import FlaskForm
from wtforms import PasswordField, SubmitField, StringField
from wtforms.validators import DataRequired, EqualTo

# Reset Password
class ResetPasswordForm(FlaskForm):
	password = PasswordField('Password', validators=[DataRequired()])
	confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
	submit = SubmitField('Reset Password')

# Security Question
class SecurityQuestion(FlaskForm):
	response = StringField('Response', validators=[DataRequired()])
	submit = SubmitField('Enter Response')