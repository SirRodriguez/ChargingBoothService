from flask import Blueprint, request, jsonify
from jsonschema import validate
from CB_service import db, userManager, mysql_host, mysql_user, mysql_password, mysql_database
from CB_service.models import Device, Settings
import secrets
import mysql.connector

register = Blueprint('register', __name__)

# Device
@register.route("/device/register")
def register_device():
	payload = {}
	if request.method == 'GET':
		# Json validation
		schema = {
			"type": "object",
			"properties": {
				"username": {
					"type": "string"
				},
				"password": {
					"type": "string"
				}
			}
		}
		try:
			validate(instance=request.json, schema=schema)
		except:
			resp = jsonify(payload)
			resp.status_code = 400
			return resp

		# User verification
		username = request.json["username"]
		password = request.json["password"]
		if not userManager.only_verify_user(username, password):
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



		# Create a random hex that will be used to 
		# keep track of what device is being talked to
		random_hex = secrets.token_hex(25)

		# Add device to the database
		sql = "INSERT INTO device (id_number) VALUES ('" + random_hex + "')"
		mycursor.execute(sql)
		mydb.commit()

		# Grab the device from database for info
		sql = "SELECT * FROM device WHERE id_number = '" + random_hex + "'"
		mycursor.execute(sql)
		result = mycursor.fetchall()
		device = result[0]
		device_id = device[0]

		# Add settings to data base for corresponding device
		sql = "INSERT INTO settings (location) VALUES ('" + str(device_id) + "')"
		mycursor.execute(sql)

		mydb.commit()

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

# Device
@register.route("/device/is_registered/<string:id_number>")
def is_registered(id_number):
	payload = {}
	if request.method == 'GET':
		mydb = mysql.connector.connect(
			host=mysql_host,
			user=mysql_user,
			password=mysql_password,
			database=mysql_database
		)
		mycursor = mydb.cursor()
		sql = "SELECT * FROM device WHERE id_number = %s%s"
		val = (id_number, '')
		mycursor.execute(sql, val)
		result = mycursor.fetchall()
		if len(result) == 0:
			payload["registered"] = False
		else:
			payload["registered"] = True

		resp = jsonify(payload)
		resp.status_code = 200
		return resp

	else:
		resp = jsonify(payload)
		resp.status_code = 405
		return resp