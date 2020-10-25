from flask import Blueprint, request, jsonify
from CB_service import db, userManager
from CB_service.models import Device

device = Blueprint('device', __name__)


# Site
@device.route("/site/get_all/<string:admin_key>")
def all_devices(admin_key):
	payload = {}
	if request.method == 'GET':
		if not userManager.verify_key(admin_key):
			resp = jsonify(payload)
			resp.status_code = 401
			return resp

		all_devices = Device.query.order_by(Device.id.asc())

		list_id = []
		list_location = []
		count = 0
		for devi in all_devices:
			list_id.append(devi.id)
			if(devi.settings != None):
				list_location.append(devi.settings.location)
			else:
				list_location.append("No Settings")
			count += 1

		payload["device_id"] = list_id
		payload["location"] = list_location
		payload["count"] = count

		resp = jsonify(payload)
		resp.status_code = 200
		return resp
	else:
		resp = jsonify(payload)
		resp.status_code = 405
		return resp

# Site
@device.route("/site/remove_device/<int:id>/<string:admin_key>", methods=['DELETE'])
def remove_device(id, admin_key):
	payload = {}
	
	if request.method == 'DELETE':
		if not userManager.verify_key(admin_key):
			resp = jsonify(payload)
			resp.status_code = 401
			return resp

		devi = Device.query.get(id)
		if devi != None:
			payload["deleted_id"] = devi.id
			payload["deleted_num"] = devi.id_number

			# Settings must be seleted along with it
			# Later all the session that go along with it
			# And also all the image files that go along with it
			db.session.delete(devi.settings)
			db.session.delete(devi)
			db.session.commit()

			resp = jsonify(payload)
			resp.status_code = 204
			return resp

		else:
			resp = jsonify(payload)
			resp.status_code = 400
			return resp

	else:
		resp = jsonify(payload)
		resp.status_code = 405
		return resp

# Site
@device.route("/site/location/<int:id>/<string:admin_key>")
def device_location(id, admin_key):
	payload = {}
	if request.method == 'GET':
		if not userManager.verify_key(admin_key):
			resp = jsonify(payload)
			resp.status_code = 401
			return resp

		devi = Device.query.get(id)

		if devi != None:
			if(devi.settings != None):
				payload["location"] = devi.settings.location
			else:
				payload["location"] = "No Settings"

			resp = jsonify(payload)
			resp.status_code = 200
			return resp
		else:
			resp = jsonify(payload)
			resp.status_code = 400
			return resp
	else:
		resp = jsonify(payload)
		resp.status_code = 405
		return resp