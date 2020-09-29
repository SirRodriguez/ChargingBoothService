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
	print(id)
	if request.method == 'DELETE':
		devi = Device.query.get(id)

		# print(devi.id)
		# print(devi.id_number)

		if devi != None:
			payload["deleted_id"] = devi.id
			payload["deleted_num"] = devi.id_number

			# Settings must be seleted along with it
			# Later all the session that go along with it
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

@device_module.route("/device_module/settings/<int:id>")
def device_settings(id):
	payload = {}

	if request.method == 'GET':
		devi = Device.query.get(id)

		if devi != None:
			if(devi.settings != None):
				payload["toggle_pay"] = devi.settings.toggle_pay
				payload["price"] = devi.settings.price
				payload["charge_time"] = devi.settings.charge_time
				payload["time_offset"] = devi.settings.time_offset
				payload["location"] = devi.settings.location
				payload["aspect_ratio_width"] = devi.settings.aspect_ratio_width
				payload["aspect_ratio_height"] = devi.settings.aspect_ratio_height

				resp = jsonify(payload)
				resp.status_code = 200
				return resp

			else:
				resp = jsonify(payload)
				resp.status_code = 500
				return resp

		else:
			resp = jsonify(payload)
			resp.status_code = 400
			return resp

	else:
		resp = jsonify(payload)
		resp.status_code = 405
		return resp

@device_module.route("/device_module/settings/update/<int:id>", methods=["PUT"])
def update_settings(id):
	payload = {}

	if request.method == 'PUT':
		devi = Device.query.get(id)
		if devi != None:

			# Check if aspect ration is different so that it can resize all images
			# resize = False
			# if Settings.query.first().aspect_ratio_width != float(form.aspect_ratio.data.split(":")[0]) and \
			# 	Settings.query.first().aspect_ratio_height != float(form.aspect_ratio.data.split(":")[1]):
			# 	resize = True

			devi.settings.toggle_pay = request.json["toggle_pay"]
			devi.settings.price = request.json["price"]
			devi.settings.charge_time = request.json["charge_time"]
			devi.settings.time_offset = request.json["time_offset"]
			devi.settings.location = request.json["location"]
			devi.settings.aspect_ratio_width = request.json["aspect_ratio_width"]
			devi.settings.aspect_ratio_height = request.json["aspect_ratio_height"]

			# if resize:
			# 	pic_files = PFI()
			# 	pic_files.resize_all(Settings.query.first().aspect_ratio_width, Settings.query.first().aspect_ratio_height)

			db.session.commit()

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