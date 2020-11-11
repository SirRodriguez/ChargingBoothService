from flask import Blueprint, request, jsonify
from jsonschema import validate
from CB_service import db, userManager, mysql_host, mysql_user, mysql_password, mysql_database
from CB_service.models import Device, Session
from CB_service.sessions.utils import ceildiv, get_iter_pages
import datetime
import mysql.connector

sessions = Blueprint('sessions', __name__)


############
## Device ##
############

# This will not have an admin key because it is not used by admin route
@sessions.route("/device/add_session/<string:id_number>", methods=['PUT'])
def add_session(id_number):
	payload = {}
	if request.method == 'PUT':
		# Json validation
		schema = {
			"type": "object",
			"properties": {
				"date_initiated_year": {
					"type": "number"
				},
				"date_initiated_month": {
					"type": "number"
				},
				"date_initiated_day": {
					"type": "number"
				},
				"date_initiated_hour": {
					"type": "number"
				},
				"date_initiated_minute": {
					"type": "number"
				},
				"date_initiated_second": {
					"type": "number"
				},
				"duration": {
					"type": "number"
				},
				"power_used": {
					"type": "number"
				},
				"amount_paid": {
					"type":"number"
				},
				"location": {
					"type": "string"
				},
				"port": {
					"type": "string"
				},
				"increment_size": {
					"type": "number"
				},
				"increments": {
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

		# if devi != None:
		if len(result) > 0:
			device_id = result[0][0]

			date_initiated=datetime.datetime(
				year=request.json["date_initiated_year"],
				month=request.json["date_initiated_month"],
				day=request.json["date_initiated_day"], 
				hour=request.json["date_initiated_hour"], 
				minute=request.json["date_initiated_minute"],
				second=request.json["date_initiated_second"]
				)

			# Add a session to the DB
			sql = "INSERT INTO session (duration, power_used, amount_paid, date_initiated, location, port, increment_size, increments, host_id) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
			val = (
				request.json["duration"], 
				request.json["power_used"], 
				request.json["amount_paid"], 
				date_initiated, 
				request.json["location"], 
				request.json["port"], 
				request.json["increment_size"], 
				request.json["increments"], 
				device_id
			)
			mycursor.execute(sql, val)
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

# Could use more testing
@sessions.route("/device/sessions/<string:id_number>/<int:page>/<string:admin_key>")
def get_deivce_sessions(id_number, page, admin_key):
	items_per_page = 25

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

		sql = "SELECT * FROM device WHERE id_number = %s"
		val = (id_number,)
		mycursor.execute(sql,val)
		result = mycursor.fetchall()

		if len(result) > 0:
			payload["registered"] = True

			device_id = result[0][0]

			# Get the number of rows in sessions
			sql = "SELECT COUNT(*) FROM session"
			mycursor.execute(sql)
			result = mycursor.fetchall()
			num_of_sessions = result[0][0]
			num_pages = ceildiv(num_of_sessions, items_per_page)

			# Grab the sessions
			offset = (page - 1) * items_per_page
			sql = "SELECT * FROM session WHERE host_id = %s ORDER BY date_initiated LIMIT %s OFFSET %s"
			val = (device_id, items_per_page, offset)
			mycursor.execute(sql, val)
			result = mycursor.fetchall()

			payload["sessions"] = []
			payload["iter_pages"] = []

			for sess in result:
				sess_items = {}
				sess_items["id"] = sess[0]

				sess_items["duration"] = sess[1]
				sess_items["power_used"] = sess[2]
				sess_items["amount_paid"] = sess[3]

				sess_items["date_initiated_year"] = sess[4].year
				sess_items["date_initiated_month"] = sess[4].month
				sess_items["date_initiated_day"] = sess[4].day
				sess_items["date_initiated_hour"] = sess[4].hour
				sess_items["date_initiated_minute"] = sess[4].minute
				sess_items["date_initiated_second"] = sess[4].second

				sess_items["location"] = sess[5]
				sess_items["port"] = sess[6]
				sess_items["increment_size"] = sess[7]
				sess_items["increments"] = sess[8]

				payload["sessions"].append(sess_items)

			for page_num in get_iter_pages(left_edge=2, right_edge=2, left_current=2, right_current=5, pages=num_pages, page=page):
				if page_num:
					payload["iter_pages"].append(page_num)
				else:
					payload["iter_pages"].append(0)

			# Grab the settings
			sql = "SELECT * FROM settings WHERE id = " + str(device_id)
			mycursor.execute(sql)
			result = mycursor.fetchall()
			device_settings = result[0]

			# Add the settings to the payload as well
			settings = {}
			settings["toggle_pay"] = device_settings[1]
			settings["price"] = device_settings[2]
			settings["charge_time"] = device_settings[3]
			settings["time_offset"] = device_settings[4]
			settings["location"] = device_settings[5]
			settings["aspect_ratio_width"] = device_settings[6]
			settings["aspect_ratio_height"] = device_settings[7]

			payload["settings"] = settings

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

@sessions.route("/device/all_sessions/<string:id_number>/<string:admin_key>")
def get_all_device_sessions(id_number, admin_key):
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

		sql = "SELECT * FROM device WHERE id_number = %s"
		val = (id_number,)
		mycursor.execute(sql,val)
		result = mycursor.fetchall()

		if len(result) > 0:
			payload["registered"] = True

			device_id = result[0][0]

			# Grab the sessions
			sql = "SELECT * FROM session WHERE host_id = " + str(device_id)
			mycursor.execute(sql)
			all_sessions = mycursor.fetchall()

			payload["sessions"] = []

			for sess in all_sessions:
				sess_items = {}
				sess_items["id"] = sess[0]

				sess_items["duration"] = sess[1]
				sess_items["power_used"] = sess[2]
				sess_items["amount_paid"] = sess[3]

				sess_items["date_initiated_year"] = sess[4].year
				sess_items["date_initiated_month"] = sess[4].month
				sess_items["date_initiated_day"] = sess[4].day
				sess_items["date_initiated_hour"] = sess[4].hour
				sess_items["date_initiated_minute"] = sess[4].minute
				sess_items["date_initiated_second"] = sess[4].second

				sess_items["location"] = sess[5]
				sess_items["port"] = sess[6]
				sess_items["increment_size"] = sess[7]
				sess_items["increments"] = sess[8]

				payload["sessions"].append(sess_items)

			# Grab the settings
			sql = "SELECT * FROM settings WHERE id = " + str(device_id)
			mycursor.execute(sql)
			result = mycursor.fetchall()
			device_settings = result[0]

			# Add the settings to the payload as well
			settings = {}
			settings["toggle_pay"] = device_settings[1]
			settings["price"] = device_settings[2]
			settings["charge_time"] = device_settings[3]
			settings["time_offset"] = device_settings[4]
			settings["location"] = device_settings[5]
			settings["aspect_ratio_width"] = device_settings[6]
			settings["aspect_ratio_height"] = device_settings[7]

			payload["settings"] = settings

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


##########
## Site ##
##########

@sessions.route("/site/sessions/<int:id>/<int:page>/<string:admin_key>")
def get_sessions(id, page, admin_key):
	items_per_page = 25

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

		sql = "SELECT * FROM device WHERE id = %s"
		val = (id,)
		mycursor.execute(sql,val)
		result = mycursor.fetchall()

		if len(result) > 0:
			device_id = result[0][0]

			# Get the number of rows in sessions
			sql = "SELECT COUNT(*) FROM session"
			mycursor.execute(sql)
			result = mycursor.fetchall()
			num_of_sessions = result[0][0]
			num_pages = ceildiv(num_of_sessions, items_per_page)

			# Grab the sessions
			offset = (page - 1) * items_per_page
			sql = "SELECT * FROM session WHERE host_id = %s ORDER BY date_initiated LIMIT %s OFFSET %s"
			val = (device_id, items_per_page, offset)
			mycursor.execute(sql, val)
			result = mycursor.fetchall()

			payload["sessions"] = []
			payload["iter_pages"] = []

			for sess in result:
				sess_items = {}
				sess_items["id"] = sess[0]

				sess_items["duration"] = sess[1]
				sess_items["power_used"] = sess[2]
				sess_items["amount_paid"] = sess[3]

				sess_items["date_initiated_year"] = sess[4].year
				sess_items["date_initiated_month"] = sess[4].month
				sess_items["date_initiated_day"] = sess[4].day
				sess_items["date_initiated_hour"] = sess[4].hour
				sess_items["date_initiated_minute"] = sess[4].minute
				sess_items["date_initiated_second"] = sess[4].second

				sess_items["location"] = sess[5]
				sess_items["port"] = sess[6]
				sess_items["increment_size"] = sess[7]
				sess_items["increments"] = sess[8]

				payload["sessions"].append(sess_items)

			for page_num in get_iter_pages(left_edge=2, right_edge=2, left_current=2, right_current=5, pages=num_pages, page=page):
				if page_num:
					payload["iter_pages"].append(page_num)
				else:
					payload["iter_pages"].append(0)

			# Grab the settings
			sql = "SELECT * FROM settings WHERE id = " + str(device_id)
			mycursor.execute(sql)
			result = mycursor.fetchall()
			device_settings = result[0]

			# Add the settings to the payload as well
			settings = {}
			settings["toggle_pay"] = device_settings[1]
			settings["price"] = device_settings[2]
			settings["charge_time"] = device_settings[3]
			settings["time_offset"] = device_settings[4]
			settings["location"] = device_settings[5]
			settings["aspect_ratio_width"] = device_settings[6]
			settings["aspect_ratio_height"] = device_settings[7]

			payload["settings"] = settings

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

@sessions.route("/site/all_sessions/<int:id>/<string:admin_key>")
def all_sessions(id, admin_key):
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

		sql = "SELECT * FROM device WHERE id = %s"
		val = (id,)
		mycursor.execute(sql,val)
		result = mycursor.fetchall()

		if len(result) > 0:
			device_id = result[0][0]

			# Grab the sessions
			sql = "SELECT * FROM session WHERE host_id = " + str(device_id)
			mycursor.execute(sql)
			all_sessions = mycursor.fetchall()

			payload["sessions"] = []

			for sess in all_sessions:
				sess_items = {}
				sess_items["id"] = sess[0]

				sess_items["duration"] = sess[1]
				sess_items["power_used"] = sess[2]
				sess_items["amount_paid"] = sess[3]

				sess_items["date_initiated_year"] = sess[4].year
				sess_items["date_initiated_month"] = sess[4].month
				sess_items["date_initiated_day"] = sess[4].day
				sess_items["date_initiated_hour"] = sess[4].hour
				sess_items["date_initiated_minute"] = sess[4].minute
				sess_items["date_initiated_second"] = sess[4].second

				sess_items["location"] = sess[5]
				sess_items["port"] = sess[6]
				sess_items["increment_size"] = sess[7]
				sess_items["increments"] = sess[8]

				payload["sessions"].append(sess_items)

			# Grab the settings
			sql = "SELECT * FROM settings WHERE id = " + str(device_id)
			mycursor.execute(sql)
			result = mycursor.fetchall()
			device_settings = result[0]

			# Add the settings to the payload as well
			settings = {}
			settings["toggle_pay"] = device_settings[1]
			settings["price"] = device_settings[2]
			settings["charge_time"] = device_settings[3]
			settings["time_offset"] = device_settings[4]
			settings["location"] = device_settings[5]
			settings["aspect_ratio_width"] = device_settings[6]
			settings["aspect_ratio_height"] = device_settings[7]

			payload["settings"] = settings

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