from flask import Blueprint, request, jsonify, current_app
from CB_service import db, userManager
from CB_service.models import Device, Session
import os
from os import listdir
from os.path import isfile, join

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

			# Remove all the images that go along with it
			# -----
			# Check if the directory exists
			path = os.path.join(current_app.root_path, 'static', 'picture_files', str(id))
			if os.path.isdir(path):
				# Check if the resized image directory exists
				re_path = os.path.join(current_app.root_path, 'static', 'picture_files', str(id), 'resized')
				if os.path.isdir(re_path):
					# Remove all files here
					all_files = [f for f in listdir(re_path) if isfile(join(re_path, f))]
					for file in all_files:
						file_path = os.path.join(re_path, file)
						os.remove(file_path)

					# Remove the resized directory
					os.rmdir(re_path)

				# Remove all files in the image file directory
				all_files = [f for f in listdir(path) if isfile(join(path, f))]
				for file in all_files:
					file_path = os.path.join(path, file)
					os.remove(file_path)

				# Remove the image file directory
				os.rmdir(path)

			# Remove the sessions of the device
			sessions = devi.sessions
			for sess in sessions:
				db.session.delete(sess)

			# Remove the settings of the device
			db.session.delete(devi.settings)

			# Remove the device
			db.session.delete(devi)

			# Commit
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