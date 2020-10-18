from flask import Blueprint, request, jsonify
from CB_service import userManager, db
from CB_service.models import User

admin_user = Blueprint('admin_user', __name__)

@admin_user.route("/site/admin_user/verify_user/<string:username>/<string:password>")
def verify_user(username, password):
	payload = {}
	if request.method == 'GET':

		payload["user_verified"] = userManager.verify_user(username, password)

		resp = jsonify(payload)
		resp.status_code = 200
		return resp

	else:
		resp = jsonify(payload)
		resp.status_code = 405
		return resp

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
