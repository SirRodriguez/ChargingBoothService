from flask import Blueprint, request, json, Response, jsonify
import secrets
from CB_service import db
from CB_service.models import User, Device, Settings

device_module = Blueprint('device_module', __name__)

@device_module.route("/device_module/register")
def register():
	payload = {}
	if request.method == 'GET':
		# Create a random hex that will be used to 
		# keep track of what device is being talked to
		random_hex = secrets.token_hex(25)

		# Add device to the database
		devi = Device(id_number=random_hex)
		db.session.add(devi)
		db.session.commit()

		# Grab the device from database for info
		db_device = Device.query.filter_by(id_number=random_hex).first()
		device_id = str(db_device.id)

		# Add settings to data base for corresponding device
		sett = Settings(location=device_id, host=db_device)
		db.session.add(sett)
		db.session.commit()

		# Describe the device currently added
		payload["device_id"] = random_hex
		payload["id"] = device_id

		resp = jsonify(payload)
		resp.status_code = 200
		return resp

	else:
		resp = jsonify(payload)
		resp.status_code = 405
		return resp

@device_module.route("/device_module/get_all")
def all_devices():
	payload = {}
	if request.method == 'GET':
		all_devices = Device.query.order_by(Device.id.asc())

		# list_dev_num = []
		list_id = []
		list_location = []
		count = 0
		for devi in all_devices:
			# list_dev_num.append(devi.id_number)
			list_id.append(devi.id)
			if(devi.settings != None):
				list_location.append(devi.settings.location)
			else:
				list_location.append("No Settings")
			count += 1

		# payload["device_num"] = list_dev_num
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

@device_module.route("/device_module/location/<int:id>")
def device_location(id):
	payload = {}
	if request.method == 'GET':
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


@device_module.route("/device_module/remove_device/<int:id>", methods=['DELETE'])
def remove_device(id):
	payload = {}
	if request.method == 'DELETE':
		devi = Device.query.get(id)

		if devi != None:
			payload["deleted_id"] = devi.id
			payload["deleted_num"] = devi.id_number

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