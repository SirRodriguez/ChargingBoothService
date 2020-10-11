from flask import Blueprint, request, jsonify
from CB_service import db
from CB_service.models import Device, Session
import datetime

sessions = Blueprint('sessions', __name__)


############
## Device ##
############

@sessions.route("/device/add_session/<string:id_number>", methods=['PUT'])
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

@sessions.route("/device/sessions/<string:id_number>/<int:page>")
def get_deivce_sessions(id_number, page):
	payload = {}
	if request.method == 'GET':
		devi = Device.query.filter_by(id_number=id_number).first()
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

@sessions.route("/device/all_sessions/<string:id_number>")
def get_all_device_sessions(id_number):
	payload = {}
	if request.method == 'GET':
		devi = Device.query.filter_by(id_number=id_number).first()
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

@sessions.route("/site/sessions/<int:id>/<int:page>")
def get_sessions(id, page):
	payload = {}
	if request.method == 'GET':
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

@sessions.route("/site/all_sessions/<int:id>")
def all_sessions(id):
	payload = {}
	if request.method == 'GET':
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