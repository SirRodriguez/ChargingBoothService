from flask import url_for
from CB_service import mail
from CB_service.models import User
from flask_mail import Message

def send_reset_email(user):
	local_user = User.query.first()
	token = local_user.get_reset_token()
	# msg = Message('Password Reset Request', sender='noreply@demo.com', recipients=[user.email])
	msg = Message('Password Reset Request', sender='noreply@demo.com', recipients=[user[2]])


	msg.body = f'''To reset your password, visit the following link:

{url_for('admin_user.reset_token', token=token, _external=True)}

If you did not make this request then simply ignore this email and no change will be made.
'''
	mail.send(msg)