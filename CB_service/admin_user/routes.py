from flask import Blueprint, request, jsonify
from CB_service import userManager, db
from CB_service.models import User

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

		payload["user_verified"] = userManager.verify_user(username, password)

		resp = jsonify(payload)
		resp.status_code = 200
		return resp

	else:
		resp = jsonify(payload)
		resp.status_code = 405
		return resp

@admin_user.route("/device/admin_user/account_info")
@admin_user.route("/site/admin_user/account_info")
def account_info():
	payload = {}
	if request.method == 'GET':
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