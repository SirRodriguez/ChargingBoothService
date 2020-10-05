from flask import Blueprint, request, json, Response, jsonify, current_app, send_from_directory
import datetime
# from datetime import datetime
import os
from os import listdir
from os.path import isfile, join
import secrets
from CB_service import db
from CB_service.models import User, Device, Settings, Session

device = Blueprint('device', __name__)

# Device
@device.route("/device/register")
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

# Device
@device.route("/device/is_registered/<string:id_number>")
def is_registered(id_number):
	payload = {}
	if request.method == 'GET':
		devi = Device.query.filter_by(id_number=id_number).first()
		if devi == None:
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

@device.route("/device/get_settings/<string:id_number>")
def settings(id_number):
	payload = {}
	if request.method == 'GET':
		devi = Device.query.filter_by(id_number=id_number).first()
		if devi != None:
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
			resp.status_code = 400
			return resp
	else:
		resp = jsonify(payload)
		resp.status_code = 405
		return resp

@device.route("/device/update_setting/<string:id_number>", methods=['PUT'])
def update_settings(id_number):
	payload = {}
	if request.method == 'PUT':
		devi = Device.query.filter_by(id_number=id_number).first()
		if devi != None:
			devi.settings.toggle_pay = request.json["toggle_pay"]
			devi.settings.price = request.json["price"]
			devi.settings.charge_time = request.json["charge_time"]
			devi.settings.time_offset = request.json["time_offset"]
			devi.settings.location = request.json["location"]
			devi.settings.aspect_ratio_width = request.json["aspect_ratio_width"]
			devi.settings.aspect_ratio_height = request.json["aspect_ratio_height"]

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


@device.route("/device/add_session/<string:id_number>", methods=['PUT'])
def add_session(id_number):
	payload = {}
	if request.method == 'PUT':
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

# payload_send["date_initiated_year"] = self.local_sessions[index].date_initiated.year
# 					payload_send["date_initiated_month"] = self.local_sessions[index].date_initiated.month
# 					payload_send["date_initiated_day"] = self.local_sessions[index].date_initiated.day
# 					payload_send["date_initiated_hour"] = self.local_sessions[index].date_initiated.hour
# 					payload_send["date_initiated_minute"] = self.local_sessions[index].date_initiated.minute
# 					payload_send["date_initiated_second"] = self.local_sessions[index].date_initiated.second


@device.route("/device/sessions/<string:id_number>/<int:page>")
def get_sessions(id_number, page):
	payload = {}
	if request.method == 'GET':
		devi = Device.query.filter_by(id_number=id_number).first()
		if devi != None:
			# sessions = Session.query.order_by(Session.date_initiated.desc()).paginate(page=page, per_page=10)

			sessions = Session.query.order_by(Session.date_initiated.desc()).paginate(page=page, per_page=10)

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

			# {% for page_num in sessions.iter_pages(left_edge=1, right_edge=1, left_current=1, right_current=2) %}
		 #      {% if page_num %}
		 #        {% if sessions.page == page_num %}
		 #          <a class="btn btn-info mb-4" href="{{ url_for('system_admin.view_data', page=page_num) }}">{{ page_num }}</a>
		 #        {% else %}
		 #          <a class="btn btn-outline-info mb-4" href="{{ url_for('system_admin.view_data', page=page_num) }}">{{ page_num }}</a>
		 #        {% endif %}
		 #      {% else %}
		 #        ...
		 #      {% endif %}
		 #    {% endfor %}

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