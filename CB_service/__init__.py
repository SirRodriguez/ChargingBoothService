from flask import Flask, request
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_mail import Mail
from CB_service.config import Config

db = SQLAlchemy()
bcrypt = Bcrypt()
mail = Mail()

def check_device_id_num():
	print("-----custom key function-----")
	try:
		print(request.view_args['id_number'])
		if request.view_args['id_number'] != None:
			return request.view_args['id_number']
		else:
			return get_remote_address()
	except:
		return get_remote_address()

limiter = Limiter(
	key_func=check_device_id_num,
	default_limits=["10/minute"] # Needs perfecting
)

from CB_service.models import UserManager, ResetLimiter
userManager = UserManager()
resetLimiter = ResetLimiter()

def create_app(config_class=Config):
	app = Flask(__name__)
	app.config.from_object(Config)

	db.init_app(app)
	bcrypt.init_app(app)
	mail.init_app(app)

	limiter.init_app(app)

	from CB_service.main.routes import main
	from CB_service.admin_user.routes import admin_user
	from CB_service.device.routes import device
	from CB_service.register.routes import register
	from CB_service.settings.routes import settings
	from CB_service.sessions.routes import sessions
	from CB_service.images.routes import images

	app.register_blueprint(main)
	app.register_blueprint(admin_user)
	app.register_blueprint(device)
	app.register_blueprint(register)
	app.register_blueprint(settings)
	app.register_blueprint(sessions)
	app.register_blueprint(images)

	return app