from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_mail import Mail
from CB_service.config import Config
# import mysql.connector

db = SQLAlchemy()
bcrypt = Bcrypt()
mail = Mail()

# MYSQL database
# mydb = mysql.connector.connect(
# 	host='localhost',
# 	user='root',
# 	password='CRodPass@123',
# 	database='charging_booth_database'
# )
mysql_host = 'localhost'
mysql_user = 'root'
mysql_password = 'CRodPass@123'
mysql_database = 'charging_booth_database'


from CB_service.models import UserManager, ResetLimiter
userManager = UserManager()
resetLimiter = ResetLimiter()

def create_app(config_class=Config):
	app = Flask(__name__)
	app.config.from_object(Config)

	db.init_app(app)
	bcrypt.init_app(app)
	mail.init_app(app)

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