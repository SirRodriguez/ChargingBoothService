from flask import Blueprint, request, jsonify
from jsonschema import validate
from CB_service import db, userManager
from CB_service.models import Device, Session
import datetime

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

		devi = Device.query.filter_by(id_number=id_number).first()
		if devi != None:
			date_initiated=datetime.datetime(
				year=request.json["date_initiated_year"],
				month=request.json["date_initiated_month"],
				day=request.json["date_initiated_day"], 
				hour=request.json["date_initiated_hour"], 
				minute=request.json["date_initiated_minute"],
				second=request.json["date_initiated_second"]
				)

			session = Session(
				duration=request.json["duration"],
				power_used=request.json["power_used"],
				amount_paid=request.json["amount_paid"],
				date_initiated=date_initiated,
				location=request.json["location"],
				port=request.json["port"],
				increment_size=request.json["increment_size"],
				increments=request.json["increments"],
				host=devi
				)

			db.session.add(session)
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

@sessions.route("/device/sessions/<string:id_number>/<int:page>/<string:admin_key>")
def get_deivce_sessions(id_number, page, admin_key):
	payload = {}
	if request.method == 'GET':
		if not userManager.verify_key(admin_key):
			resp = jsonify(payload)
			resp.status_code = 401
			return resp

		devi = Device.query.filter_by(id_number=id_number).first()
		if devi != None:
			payload["registered"] = True

			sessions = Session.query.filter_by(host=devi)\
				.order_by(Session.date_initiated.desc())\
				.paginate(page=page, per_page=10)

			payload["sessions"] = []
			payload["iter_pages"] = []

			for sess in sessions.items:
				sess_items = {}
				sess_items["id"] = sess.id

				sess_items["duration"] = sess.duration
				sess_items["power_used"] = sess.power_used
				sess_items["amount_paid"] = sess.amount_paid

				sess_items["date_initiated_year"] = sess.date_initiated.year
				sess_items["date_initiated_month"] = sess.date_initiated.month
				sess_items["date_initiated_day"] = sess.date_initiated.day
				sess_items["date_initiated_hour"] = sess.date_initiated.hour
				sess_items["date_initiated_minute"] = sess.date_initiated.minute
				sess_items["date_initiated_second"] = sess.date_initiated.second

				sess_items["location"] = sess.location
				sess_items["port"] = sess.port
				sess_items["increment_size"] = sess.increment_size
				sess_items["increments"] = sess.increments

				payload["sessions"].append(sess_items)


			for page_num in sessions.iter_pages(left_edge=1, right_edge=1, left_current=1, right_current=2):
				if page_num:
					payload["iter_pages"].append(page_num)
				else:
					payload["iter_pages"].append(0)

			# Add the settings to the payload as well
			settings = {}
			settings["toggle_pay"] = devi.settings.toggle_pay
			settings["price"] = devi.settings.price
			settings["charge_time"] = devi.settings.charge_time
			settings["time_offset"] = devi.settings.time_offset
			settings["location"] = devi.settings.location
			settings["aspect_ratio_width"] = devi.settings.aspect_ratio_width
			settings["aspect_ratio_height"] = devi.settings.aspect_ratio_height

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

		devi = Device.query.filter_by(id_number=id_number).first()
		if devi != None:
			payload["registered"] = True

			sessions = Session.query.filter_by(host=devi)\
				.order_by(Session.date_initiated.desc())\
				.all()

			payload["sessions"] = []

			for sess in sessions:
				sess_items = {}
				sess_items["id"] = sess.id

				sess_items["duration"] = sess.duration
				sess_items["power_used"] = sess.power_used
				sess_items["amount_paid"] = sess.amount_paid

				sess_items["date_initiated_year"] = sess.date_initiated.year
				sess_items["date_initiated_month"] = sess.date_initiated.month
				sess_items["date_initiated_day"] = sess.date_initiated.day
				sess_items["date_initiated_hour"] = sess.date_initiated.hour
				sess_items["date_initiated_minute"] = sess.date_initiated.minute
				sess_items["date_initiated_second"] = sess.date_initiated.second

				sess_items["location"] = sess.location
				sess_items["port"] = sess.port
				sess_items["increment_size"] = sess.increment_size
				sess_items["increments"] = sess.increments

				payload["sessions"].append(sess_items)

			# Add the settings to the payload as well
			settings = {}
			settings["toggle_pay"] = devi.settings.toggle_pay
			settings["price"] = devi.settings.price
			settings["charge_time"] = devi.settings.charge_time
			settings["time_offset"] = devi.settings.time_offset
			settings["location"] = devi.settings.location
			settings["aspect_ratio_width"] = devi.settings.aspect_ratio_width
			settings["aspect_ratio_height"] = devi.settings.aspect_ratio_height

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
	payload = {}
	if request.method == 'GET':
		if not userManager.verify_key(admin_key):
			resp = jsonify(payload)
			resp.status_code = 401
			return resp

		devi = Device.query.filter_by(id=id).first()
		if devi != None:
			sessions = Session.query.filter_by(host=devi)\
				.order_by(Session.date_initiated.desc())\
				.paginate(page=page, per_page=10)

			payload["sessions"] = []
			payload["iter_pages"] = []

			for sess in sessions.items:
				sess_items = {}
				sess_items["id"] = sess.id

				sess_items["duration"] = sess.duration
				sess_items["power_used"] = sess.power_used
				sess_items["amount_paid"] = sess.amount_paid

				sess_items["date_initiated_year"] = sess.date_initiated.year
				sess_items["date_initiated_month"] = sess.date_initiated.month
				sess_items["date_initiated_day"] = sess.date_initiated.day
				sess_items["date_initiated_hour"] = sess.date_initiated.hour
				sess_items["date_initiated_minute"] = sess.date_initiated.minute
				sess_items["date_initiated_second"] = sess.date_initiated.second

				sess_items["location"] = sess.location
				sess_items["port"] = sess.port
				sess_items["increment_size"] = sess.increment_size
				sess_items["increments"] = sess.increments

				payload["sessions"].append(sess_items)


			for page_num in sessions.iter_pages(left_edge=1, right_edge=1, left_current=1, right_current=2):
				if page_num:
					payload["iter_pages"].append(page_num)
				else:
					payload["iter_pages"].append(0)

			# Add the settings to the payload as well
			settings = {}
			settings["toggle_pay"] = devi.settings.toggle_pay
			settings["price"] = devi.settings.price
			settings["charge_time"] = devi.settings.charge_time
			settings["time_offset"] = devi.settings.time_offset
			settings["location"] = devi.settings.location
			settings["aspect_ratio_width"] = devi.settings.aspect_ratio_width
			settings["aspect_ratio_height"] = devi.settings.aspect_ratio_height

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

		devi = Device.query.filter_by(id=id).first()
		if devi != None:
			sessions = Session.query.filter_by(host=devi)\
				.order_by(Session.date_initiated.desc())\
				.all()

			payload["sessions"] = []

			for sess in sessions:
				sess_items = {}
				sess_items["id"] = sess.id

				sess_items["duration"] = sess.duration
				sess_items["power_used"] = sess.power_used
				sess_items["amount_paid"] = sess.amount_paid

				sess_items["date_initiated_year"] = sess.date_initiated.year
				sess_items["date_initiated_month"] = sess.date_initiated.month
				sess_items["date_initiated_day"] = sess.date_initiated.day
				sess_items["date_initiated_hour"] = sess.date_initiated.hour
				sess_items["date_initiated_minute"] = sess.date_initiated.minute
				sess_items["date_initiated_second"] = sess.date_initiated.second

				sess_items["location"] = sess.location
				sess_items["port"] = sess.port
				sess_items["increment_size"] = sess.increment_size
				sess_items["increments"] = sess.increments

				payload["sessions"].append(sess_items)

			# Add the settings to the payload as well
			settings = {}
			settings["toggle_pay"] = devi.settings.toggle_pay
			settings["price"] = devi.settings.price
			settings["charge_time"] = devi.settings.charge_time
			settings["time_offset"] = devi.settings.time_offset
			settings["location"] = devi.settings.location
			settings["aspect_ratio_width"] = devi.settings.aspect_ratio_width
			settings["aspect_ratio_height"] = devi.settings.aspect_ratio_height

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