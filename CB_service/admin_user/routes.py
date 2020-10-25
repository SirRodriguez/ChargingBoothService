from flask import Blueprint, request, jsonify, render_template
from CB_service import userManager, db, bcrypt
from CB_service.models import User
from CB_service.admin_user.forms import ResetPasswordForm
from CB_service.admin_user.utils import send_reset_email

admin_user = Blueprint('admin_user', __name__)


##########   ############
## Site ##   ## Device ##
##########   ############

# Site and device share the same method endpoint here
@admin_user.route("/device/admin_user/verify_user")
@admin_user.route("/site/admin_user/verify_user")
def verify_user():
	payload = {}
	if request.method == 'GET':
		username = request.json["username"]
		password = request.json["password"]

		admin_key = userManager.verify_user(username, password)
		payload["user_verified"] = admin_key != None
		payload["admin_key"] = admin_key

		resp = jsonify(payload)
		resp.status_code = 200
		return resp

	else:
		resp = jsonify(payload)
		resp.status_code = 405
		return resp
## TODO!!!
@admin_user.route("/device/admin_user/account_info/<string:admin_key>")
@admin_user.route("/site/admin_user/account_info/<string:admin_key>")
def account_info(admin_key):
	payload = {}
	if request.method == 'GET':
		if not userManager.verify_key(admin_key):
			resp = jsonify(payload)
			resp.status_code = 401
			return resp

		user = User.query.first()

		payload["username"] = user.username
		payload["email"] = user.email

		resp = jsonify(payload)
		resp.status_code = 200
		return resp
	else:
		resp = jsonify(payload)
		resp.status_code = 405
		return resp

@admin_user.route("/device/admin_user/update_account/", methods=['PUT'])
@admin_user.route("/site/admin_user/update_account/", methods=['PUT'])
def update_account():
	payload = {}
	if request.method == 'PUT':
		user = User.query.first()

		user.username = request.json["username"]
		user.email = request.json["email"]

		db.session.commit()

		resp = jsonify(payload)
		resp.status_code = 200
		return resp

	else:
		resp = jsonify(payload)
		resp.status_code = 405
		return resp


@admin_user.route("/site/admin_user/update_password/", methods=['PUT'])
@admin_user.route("/device/admin_user/update_password/", methods=['PUT'])
def update_password():
	payload = {}
	if request.method == 'PUT':
		user = User.query.first()

		user.password = request.json["hashed_password"]

		db.session.commit()

		resp = jsonify(payload)
		resp.status_code = 200
		return resp
	else:
		resp = jsonify(payload)
		resp.status_code = 405
		return resp


# This will be a web page to reset the password
@admin_user.route("/reset_password")
def reset_password():
	user = User.query.first()

	send_reset_email(user=user)

	return render_template('reset_password.html')

@admin_user.route("/reset_token/<token>", methods=['GET', 'POST'])
def reset_token(token):
	# Verify token
	user = User.verify_reset_token(token)
	if user is None:
		return render_template('token_denied.html')

	form = ResetPasswordForm()
	if form.validate_on_submit():
		user = User.query.first()
		user.password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')

		db.session.commit()

		return render_template('reset_done.html')
	return render_template('reset_token.html', form=form)