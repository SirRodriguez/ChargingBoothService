from flask import Blueprint

from flask import request

main = Blueprint('main', __name__)

@main.route("/", methods=['GET', 'POST', 'PATCH', 'PUT', 'DELETE'])
def defaut():
	if request.method == 'GET':
		return "ECHO: GET"

	elif request.method == 'POST':
		return "ECHO: POST"

	elif request.method == 'PATCH':
		return "ECHO: PACTH"

	elif request.method == 'PUT':
		return "ECHO: PUT"

	elif request.method == 'DELETE':
		return "ECHO: DELETE"

	else:
		return "Main - Default"