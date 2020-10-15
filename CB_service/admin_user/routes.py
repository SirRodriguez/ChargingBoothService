from flask import Blueprint, request, jsonify
from CB_service import userManager

admin_user = Blueprint('admin_user', __name__)

@admin_user.route("/site/admin_user/login/<string:username>/<string:password>")
def login(username, password):
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