from flask import Blueprint, request, jsonify, current_app
from CB_service import db, userManager
import os
from os import listdir
from os.path import isfile, join
import mysql.connector

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

		mydb = mysql.connector.connect(
			host=os.environ.get('MYSQL_HOST'),
			user=os.environ.get('MYSQL_USER'),
			password=os.environ.get('MYSQL_PASSWORD'),
			database=os.environ.get('MYSQL_DATABASE')
		)
		mycursor = mydb.cursor()

		# Grab all devices from database
		sql = "SELECT * FROM device"
		mycursor.execute(sql)
		all_devices = mycursor.fetchall()


		list_id = []
		list_location = []
		count = 0
		for devi in all_devices:
			list_id.append(devi[0])

			# Grab the device settings
			sql = "SELECT * FROM settings WHERE id = " + str(devi[0])
			mycursor.execute(sql)
			result = mycursor.fetchall()
			if len(result) > 0:
				settings = result[0]
				list_location.append(settings[5])
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
# Need to tast if removing the device and settings still correctly correspond to each other
@device.route("/site/remove_device/<int:id>/<string:admin_key>", methods=['DELETE'])
def remove_device(id, admin_key):
	payload = {}
	
	if request.method == 'DELETE':
		if not userManager.verify_key(admin_key):
			resp = jsonify(payload)
			resp.status_code = 401
			return resp

		mydb = mysql.connector.connect(
			host=os.environ.get('MYSQL_HOST'),
			user=os.environ.get('MYSQL_USER'),
			password=os.environ.get('MYSQL_PASSWORD'),
			database=os.environ.get('MYSQL_DATABASE')
		)
		mycursor = mydb.cursor()

		# Grab the device
		sql = "SELECT * FROM device WHERE id = " + str(id)
		mycursor.execute(sql)
		result = mycursor.fetchall()

		if len(result) > 0:
			devi = result[0]

			payload["deleted_id"] = devi[0]
			payload["deleted_num"] = devi[1]

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
			sql = "DELETE FROM session WHERE host_id = " + str(id)
			mycursor.execute(sql)

			# Remove the settings of the device
			sql = "DELETE FROM settings WHERE id = " + str(id)
			mycursor.execute(sql)

			# Remove the device
			sql = "DELETE FROM device WHERE id = " + str(id)
			mycursor.execute(sql)

			# Commit
			mydb.commit()

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

		mydb = mysql.connector.connect(
			host=os.environ.get('MYSQL_HOST'),
			user=os.environ.get('MYSQL_USER'),
			password=os.environ.get('MYSQL_PASSWORD'),
			database=os.environ.get('MYSQL_DATABASE')
		)
		mycursor = mydb.cursor()

		sql = "SELECT * FROM device WHERE id = " + str(id)
		mycursor.execute(sql)
		result = mycursor.fetchall()

		if len(result) > 0:
			# Grab the settings
			sql = "SELECT * FROM settings WHERE id = " + str(id)
			mycursor.execute(sql)
			result = mycursor.fetchall()

			if len(result) > 0:
				payload["location"] = result[0][5]
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