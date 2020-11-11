from flask import Blueprint, request, jsonify
from jsonschema import validate
from CB_service import db, userManager, mysql_host, mysql_user, mysql_password, mysql_database
from CB_service.models import Device
from CB_service.settings.utils import resize_all_images
import mysql.connector

settings = Blueprint('settings', __name__)


############
## Device ##
############

# This route will not use admin key because kisok mode uses this to get settings for non admin use
@settings.route("/device/get_settings/<string:id_number>")
def get_device_settings(id_number):
	payload = {}
	if request.method == 'GET':
		mydb = mysql.connector.connect(
			host=mysql_host,
			user=mysql_user,
			password=mysql_password,
			database=mysql_database
		)
		mycursor = mydb.cursor()

		sql = "SELECT * FROM device WHERE id_number = %s"
		val = (id_number,)
		mycursor.execute(sql,val)
		result = mycursor.fetchall()

		if len(result) > 0:
			payload["registered"] = True

			device_id = result[0][0]

			# Grab the settings
			sql = "SELECT * FROM settings WHERE id = " + str(device_id)
			mycursor.execute(sql)
			result = mycursor.fetchall()
			settings = result[0]


			payload["toggle_pay"] = settings[1]
			payload["price"] = settings[2]
			payload["charge_time"] = settings[3]
			payload["time_offset"] = settings[4]
			payload["location"] = settings[5]
			payload["aspect_ratio_width"] = settings[6]
			payload["aspect_ratio_height"] = settings[7]

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

		mydb = mysql.connector.connect(
			host=mysql_host,
			user=mysql_user,
			password=mysql_password,
			database=mysql_database
		)
		mycursor = mydb.cursor()

		sql = "SELECT * FROM device WHERE id_number = %s"
		val = (id_number,)
		mycursor.execute(sql,val)
		result = mycursor.fetchall()

		if len(result) > 0:
			devi = result[0]
			id = devi[0]

			# Grab the settings
			sql = "SELECT * FROM settings WHERE id = " + str(id)
			mycursor.execute(sql)
			result = mycursor.fetchall()
			settings = result[0]

			# Check if aspect ration is different so that it can resize all images
			resize = False
			if settings[6] != float(request.json["aspect_ratio_width"]) or \
				settings[7] != float(request.json["aspect_ratio_height"]):
				resize = True

			# Update settings
			sql = "UPDATE settings SET toggle_pay = %s, price = %s, charge_time = %s, time_offset = %s, location = %s, aspect_ratio_width = %s, aspect_ratio_height = %s WHERE id = %s"
			val = (
				request.json["toggle_pay"], 
				request.json["price"], 
				request.json["charge_time"], 
				request.json["time_offset"], 
				request.json["location"], 
				request.json["aspect_ratio_width"], 
				request.json["aspect_ratio_height"],
				id
			)
			mycursor.execute(sql, val)

			if resize:
				device_id = result[0][0]
				resize_all_images(request.json["aspect_ratio_width"], request.json["aspect_ratio_height"], device_id)

			mydb.commit()

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

		mydb = mysql.connector.connect(
			host=mysql_host,
			user=mysql_user,
			password=mysql_password,
			database=mysql_database
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
				settings = result[0]
				payload["toggle_pay"] = settings[1]
				payload["price"] = settings[2]
				payload["charge_time"] = settings[3]
				payload["time_offset"] = settings[4]
				payload["location"] = settings[5]
				payload["aspect_ratio_width"] = settings[6]
				payload["aspect_ratio_height"] = settings[7]

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

		mydb = mysql.connector.connect(
			host=mysql_host,
			user=mysql_user,
			password=mysql_password,
			database=mysql_database
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
			settings = result[0]

			# Check if aspect ration is different so that it can resize all images
			resize = False
			if settings[6] != float(request.json["aspect_ratio_width"]) or \
				settings[7] != float(request.json["aspect_ratio_height"]):
				resize = True

			# Update settings
			sql = "UPDATE settings SET toggle_pay = %s, price = %s, charge_time = %s, time_offset = %s, location = %s, aspect_ratio_width = %s, aspect_ratio_height = %s WHERE id = %s"
			val = (
				request.json["toggle_pay"], 
				request.json["price"], 
				request.json["charge_time"], 
				request.json["time_offset"], 
				request.json["location"], 
				request.json["aspect_ratio_width"], 
				request.json["aspect_ratio_height"],
				id
			)
			mycursor.execute(sql, val)

			if resize:
				resize_all_images(settings[6], settings[7], id)

			mydb.commit()

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