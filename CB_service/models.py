from flask import current_app
from datetime import datetime
from CB_service import db


class User(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(20), unique=True, nullable=False)
	email = db.Column(db.String(120), unique=True, nullable=False)
	password = db.Column(db.String(60), nullable=False)

class Device(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	id_number = db.Column(db.String(50), unique=True, nullable=False) # Comunication for the device

	# settings_id = db.Column(db.Integer, db.ForeignKey("settings.id"))

	sessions = db.relationship('Session', backref='host', lazy=True)
	# settings = db.relationship('Settings', backref='host', lazy=True, foreign_keys=[settings_id])
	settings = db.relationship('Settings', backref='host', lazy=True)


class Session(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	duration = db.Column(db.Integer) #Seconds
	power_used = db.Column(db.Float) #Watts per second
	amount_paid = db.Column(db.Integer) #Cents
	date_initiated = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
	location = db.Column(db.String(100), default="No Location")
	port = db.Column(db.String(100), default="No Port")
	increment_size = db.Column(db.Integer) #Seconds
	increments = db.Column(db.Integer)

	device_id = db.Column(db.Integer, db.ForeignKey('device.id'), nullable=False)


class Settings(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	toggle_pay = db.Column(db.Boolean, default=True)
	price = db.Column(db.Integer, default=100) #Cents per Session
	charge_time = db.Column(db.Integer, default=60) #Seconds
	time_offset = db.Column(db.String(20), default='UTC') # timezone offset
	location = db.Column(db.String(100)) # Location of the device
	aspect_ratio_width = db.Column(db.Float, default=1.0) # Screen Ratio Width
	aspect_ratio_height = db.Column(db.Float, default=1.0) # Screen Ratio Height

	device_id = db.Column(db.Integer, db.ForeignKey('device.id'), nullable=False)

# Class to count how many devices are using the image.
class Images(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	image_name = db.Column(db.String(50), nullable=False)
	count = db.Column(db.Integer, nullable=False, default=0)