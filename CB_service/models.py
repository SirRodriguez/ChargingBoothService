from flask import current_app
from datetime import datetime, timedelta
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from CB_service import db, bcrypt
import secrets
import threading
import time

##############
## Database ##
##############

class User(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(20), unique=True, nullable=False)
	email = db.Column(db.String(120), unique=True, nullable=False)
	password = db.Column(db.String(60), nullable=False)

	def get_reset_token(self, expires_sec=1800):
		s = Serializer(current_app.config['SECRET_KEY'], expires_sec)
		return s.dumps({'user_id': self.id}).decode('utf-8')

	@staticmethod
	def verify_reset_token(token):
		s = Serializer(current_app.config['SECRET_KEY'])
		try:
			user_id = s.loads(token)['user_id']
		except:
			return None
		return User.query.get(user_id)

class Device(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	id_number = db.Column(db.String(50), unique=True, nullable=False) # Comunication for the device

	sessions = db.relationship('Session', backref='host', lazy=True)
	settings = db.relationship('Settings', backref='host', lazy=True, uselist=False)


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


###########
## Local ##
###########

class ResetLimiter():
	def __init__(self):
		self.limit = 3
		self.decrement_minutes = 10 # how many minutes it takes to decrese the limit by one
		self.reset_count = 0
		self.thread_pool = list()

	def add_count(self):
		if self.reset_count == 0:
			self.reset_count += 1

			# Start a thread
			counter = threading.Thread(target=self.reset_counter, args=[])
			counter.start()
			self.thread_pool.append(counter)
		else:
			self.reset_count += 1

	def reached_limit(self):
		return self.reset_count >= self.limit

	def reset_counter(self):
		running = True
		seconds = 0
		while running:
			# If timer is up
			if seconds >= self.decrement_minutes * 60:
				if self.reset_count > 0:
					self.reset_count -= 1
				else:
					running = False
				seconds = 0
			# timer is not up yet
			else:
				seconds += 1

			# Wait one second
			time.sleep(1)


# Note UserManager will only check one
# The Admin user
class UserManager():
	def __init__(self):
		self.admin_key = "" # Long string to check if this is the admin
		self.last_used = datetime.utcnow() # Time stamp of last valid check in
		self.thread_pool = list()

	def reset_admin_key(self):
		self.admin_key = ""

	def only_verify_user(self, username, password):
		user = User.query.filter_by(username=username).first()
		return user and bcrypt.check_password_hash(user.password, password)

	def verify_user(self, username, password):
		user = User.query.filter_by(username=username).first()
		if user and bcrypt.check_password_hash(user.password, password):
			return self.create_admin_key()
		return None

	def verify_key(self, key):
		if key == "":
			return False
		if self.admin_key == "":
			return False
		return self.admin_key == key

	def create_admin_key(self):
		self.admin_key = secrets.token_hex(50)
		self.last_used = datetime.utcnow()

		# Create a thread to handle the session and terminate when needed
		counter = threading.Thread(target=self.login_counter, args=[])
		counter.start()
		self.thread_pool.append(counter)

		return self.admin_key

	def elapsed_time(self):
		return datetime.utcnow() - self.last_used

	def login_counter(self):
		running = True
		while running:
			time_remain = timedelta(minutes=30) - self.elapsed_time()
			if time_remain < timedelta(seconds=0): # time has run out
				self.admin_key = ""
				running = False

			# Save CPU Time, Check every second.
			time.sleep(1)