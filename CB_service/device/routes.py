from flask import Blueprint, request, json, Response, jsonify, current_app, send_from_directory
import os
from os import listdir
from os.path import isfile, join
import secrets
from CB_service import db
from CB_service.models import User, Device, Settings

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