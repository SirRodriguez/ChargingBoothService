from flask import Blueprint

main = Blueprint('main', __name__)

@main.route("/")
def defaut():
	return "Main - Default"