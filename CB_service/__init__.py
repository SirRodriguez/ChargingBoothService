from flask import Flask
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_mail import Mail
from CB_service.config import Config

db = SQLAlchemy()
bcrypt = Bcrypt()
mail = Mail()

limiter = Limiter(
	key_func=get_remote_address,
	default_limits=["10/minute"] # Needs perfecting
)

# os.environ.get('MYSQL_HOST') = 'localhost'
# os.environ.get('MYSQL_USER') = 'root'
# os.environ.get('MYSQL_PASSWORD') = 'CRodPass@123'
# os.environ.get('MYSQL_DATABASE') = 'charging_booth_database'


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