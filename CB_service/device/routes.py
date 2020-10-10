from flask import Blueprint, request, json, Response, jsonify, current_app, send_from_directory
import datetime
# from datetime import datetime
import os
from os import listdir
from os.path import isfile, join
import secrets
from CB_service import db
from CB_service.models import User, Device, Settings, Session
from CB_service.device.utils import resize_image, resize_all_images

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

@device.route("/device/sessions/<string:id_number>/<int:page>")
def get_sessions(id_number, page):
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

@device.route("/device/all_sessions/<string:id_number>")
def get_all_sessions(id_number):
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

@device.route("/device/img_count/<string:id_number>")
def get_image_count(id_number):
	payload = {}
	if request.method == 'GET':
		devi = Device.query.filter_by(id_number=id_number).first()
		if devi != None:

			id = devi.id
			path = os.path.join(current_app.root_path, 'static', 'picture_files', str(id))
			count = 0
			if os.path.isdir(path): # If no directory, send 0
				all_files = [f for f in listdir(path) if isfile(join(path, f))]
				for file in all_files:
					count += 1

			payload["image_count"] = count

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

@device.route("/device/grab_image/<string:id_number>/<int:img_num>/<random_hex>")
def grab_image(id_number, img_num, random_hex):
	payload = {}
	if request.method == 'GET':

		devi = Device.query.filter_by(id_number=id_number).first()

		if devi != None:
			id = devi.id

			path = os.path.join(current_app.root_path, 'static', 'picture_files', str(id))

			# Find extention
			all_files = [f for f in listdir(path) if isfile(join(path, f))]
			extention = ""
			for file in all_files:
				f_name, f_ext = os.path.splitext(file)
				if f_name == str(img_num):
					extention = f_ext


			if os.path.isdir(path):
				return send_from_directory(directory=path, filename=str(img_num) + extention)
			else:
				resp = jsonify(payload)
				resp.status_code = 404
				return resp
		else:
			resp = jsonify(payload)
			resp.status_code = 400
			return resp
	else:
		resp = jsonify(payload)
		resp.status_code = 405
		return resp

@device.route("/device/images/upload/<string:id_number>", methods=['POST'])
def upload_image(id_number):
	payload = {}

	if request.method == 'POST':

		devi = Device.query.filter_by(id_number=id_number).first()
		if devi != None:

			id = devi.id
			# From settings get ration width and height
			ratio_width = devi.settings.aspect_ratio_width
			ratio_height = devi.settings.aspect_ratio_height

			# Check if directory exists for device images
			path = os.path.join(current_app.root_path, 'static', 'picture_files', str(id))
			if not os.path.isdir(path):
				os.mkdir(path)

			# Check if resized image directory exists
			re_path = os.path.join(current_app.root_path, 'static', 'picture_files', str(id), 'resized')
			if not os.path.isdir(re_path):
				os.mkdir(re_path)

			# Count how many images are in the directory
			all_files = [f for f in listdir(path) if isfile(join(path, f))]
			count = 0
			for file in all_files:
				count += 1

			# Save the incomming images
			files = request.files.to_dict(flat=False)
			for image_file in files['image']:
				print(image_file.filename)
				_, f_ext = os.path.splitext(image_file.filename)
				file_path = os.path.join(path, str(count) + f_ext)
				image_file.save(file_path)

				# Get a resized image
				background_color = 'black'
				re_img = resize_image(image_file, background_color, ratio_width, ratio_height)


				resized_file_path = os.path.join(current_app.root_path, 'static', 'picture_files', str(id), 'resized', str(count) + f_ext)
				re_img.save(resized_file_path)

				count += 1

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

@device.route("/device/remove_images/<string:id_number>/<string:removals>", methods=['DELETE'])
def remove_images(id_number, removals):
	payload = {}

	if request.method == 'DELETE':
		devi = Device.query.filter_by(id_number=id_number).first()

		if devi != None:
			id = devi.id

			path = os.path.join(current_app.root_path, 'static', 'picture_files', str(id))
			re_path = os.path.join(current_app.root_path, 'static', 'picture_files', str(id), 'resized')
			if os.path.isdir(path):

				# Parse removals
				rem_list = removals.split(",")
				# fix index and put in a set
				rem_set = set()
				for index, value in enumerate(rem_list):
					rem_set.add(str(int(rem_list[index])-1))

				# Remove the image files in there
				all_files = [f for f in listdir(path) if isfile(join(path, f))]
				for file in all_files:
					f_name, f_ext = os.path.splitext(file)
					if f_name in rem_set:
						file_path = os.path.join(path, file)
						re_file_path = os.path.join(re_path, file) # Resized names are the same as the original
						os.remove(file_path)
						os.remove(re_file_path)

				# readjust the file names
				all_files = [f for f in listdir(path) if isfile(join(path, f))]
				count = 0
				for file in all_files:
					f_name, f_ext = os.path.splitext(file)
					# Original
					src_path = os.path.join(path, file)
					dst_path = os.path.join(path, str(count) + f_ext)
					os.rename(src_path, dst_path)

					# Resized
					src_path = os.path.join(re_path, file)
					dst_path = os.path.join(re_path, str(count) + f_ext)
					os.rename(src_path, dst_path)
					count += 1

				resp = jsonify(payload)
				resp.status_code = 204
				return resp
			else:
				resp = jsonify(payload)
				resp.status_code = 400
				return resp

		else:
			resp = jsonify(payload)
			resp.status_code = 400
			return resp

	else:
		resp = jsonify(payload)
		resp.status_code = 405
		return resp