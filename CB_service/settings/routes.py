from flask import Blueprint, request, jsonify
from jsonschema import validate
from CB_service import db, userManager
from CB_service.models import Device
from CB_service.settings.utils import resize_all_images

settings = Blueprint('settings', __name__)


############
## Device ##
############

# This route will not use admin key because kisok mode uses this to get settings for non admin use
@settings.route("/device/get_settings/<string:id_number>")
def get_device_settings(id_number):
	payload = {}
	if request.method == 'GET':
		devi = Device.query.filter_by(id_number=id_number).first()
		if devi != None:
			payload["registered"] = True

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
			payload["registered"] = False

			resp = jsonify(payload)
			resp.status_code = 400
			return resp
	else:
		resp = jsonify(payload)
		resp.status_code = 405
		return resp

@settings.route("/device/update_setting/<string:id_number>/<string:admin_key>", methods=['PUT'])
def update_device_settings(id_number, admin_key):
	payload = {}
	if request.method == 'PUT':
		if not userManager.verify_key(admin_key):
			resp = jsonify(payload)
			resp.status_code = 401
			return resp
			
		# Json validation
		schema = {
			"type": "object",
			"properties": {
				"toggle_pay": {
					"type": "boolean"
				},
				"price": {
					"type": "number"
				},
				"charge_time": {
					"type": "number"
				},
				"time_offset": {
					"type": "string"
				},
				"location": {
					"type": "string"
				},
				"aspect_ratio_width": {
					"type": "number"
				},
				"aspect_ratio_height": {
					"type": "number"
				}
			}
		}
		try:
			validate(instance=request.json, schema=schema)
		except:
			resp = jsonify(payload)
			resp.status_code = 400
			return resp

		devi = Device.query.filter_by(id_number=id_number).first()
		if devi != None:

			# Check if aspect ration is different so that it can resize all images
			resize = False
			if devi.settings.aspect_ratio_width != float(request.json["aspect_ratio_width"]) or \
				devi.settings.aspect_ratio_height != float(request.json["aspect_ratio_height"]):
				resize = True

			devi.settings.toggle_pay = request.json["toggle_pay"]
			devi.settings.price = request.json["price"]
			devi.settings.charge_time = request.json["charge_time"]
			devi.settings.time_offset = request.json["time_offset"]
			devi.settings.location = request.json["location"]
			devi.settings.aspect_ratio_width = request.json["aspect_ratio_width"]
			devi.settings.aspect_ratio_height = request.json["aspect_ratio_height"]

			if resize:
				resize_all_images(devi.settings.aspect_ratio_width, devi.settings.aspect_ratio_height, devi.id)

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


##########
## Site ##
##########

# Site
@settings.route("/site/settings/<int:id>/<string:admin_key>")
def device_settings(id, admin_key):
	payload = {}

	if request.method == 'GET':
		if not userManager.verify_key(admin_key):
			resp = jsonify(payload)
			resp.status_code = 401
			return resp

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

# Site
@settings.route("/site/settings/update/<int:id>/<string:admin_key>", methods=["PUT"])
def update_settings(id, admin_key):
	payload = {}

	if request.method == 'PUT':
		if not userManager.verify_key(admin_key):
			resp = jsonify(payload)
			resp.status_code = 401
			return resp

		# Json validation
		schema = {
			"type": "object",
			"properties": {
				"toggle_pay": {
					"type": "boolean"
				},
				"price": {
					"type": "number"
				},
				"charge_time": {
					"type": "number"
				},
				"time_offset": {
					"type": "string"
				},
				"location": {
					"type": "string"
				},
				"aspect_ratio_width": {
					"type": "number"
				},
				"aspect_ratio_height": {
					"type": "number"
				}
			}
		}
		try:
			validate(instance=request.json, schema=schema)
		except:
			resp = jsonify(payload)
			resp.status_code = 400
			return resp

		devi = Device.query.get(id)
		if devi != None:

			# Check if aspect ration is different so that it can resize all images
			resize = False
			if devi.settings.aspect_ratio_width != float(request.json["aspect_ratio_width"]) or \
				devi.settings.aspect_ratio_height != float(request.json["aspect_ratio_height"]):
				resize = True

			devi.settings.toggle_pay = request.json["toggle_pay"]
			devi.settings.price = request.json["price"]
			devi.settings.charge_time = request.json["charge_time"]
			devi.settings.time_offset = request.json["time_offset"]
			devi.settings.location = request.json["location"]
			devi.settings.aspect_ratio_width = request.json["aspect_ratio_width"]
			devi.settings.aspect_ratio_height = request.json["aspect_ratio_height"]

			if resize:
				resize_all_images(devi.settings.aspect_ratio_width, devi.settings.aspect_ratio_height, devi.id)

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