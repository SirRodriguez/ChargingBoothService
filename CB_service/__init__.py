from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
# from flask_login import LoginManager
from flask_mail import Mail
from CB_service.config import Config

db = SQLAlchemy()
bcrypt = Bcrypt()
# login_manager = LoginManager()
# login_manager.login_view = 'system_admin.login'
# login_manager.login_message_category = 'info'
mail = Mail()

def create_app(config_class=Config):
	app = Flask(__name__)
	app.config.from_object(Config)

	db.init_app(app)
	bcrypt.init_app(app)
	# login_manager.init_app(app)
	mail.init_app(app)

	from CB_service.main.routes import main
	from CB_service.DELETE.routes import DELETE
	from CB_service.GET.routes import GET
	from CB_service.PATCH.routes import PATCH
	from CB_service.POST.routes import POST
	from CB_service.PUT.routes import PUT

	app.register_blueprint(main)
	app.register_blueprint(DELETE)
	app.register_blueprint(GET)
	app.register_blueprint(PATCH)
	app.register_blueprint(POST)
	app.register_blueprint(PUT)


	return app