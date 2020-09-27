from flask import Blueprint, request, json, Response, jsonify
from CB_service.models import User, Device

main = Blueprint('main', __name__)

@main.route("/", methods=['GET', 'POST', 'PATCH', 'PUT', 'DELETE'])
def defaut():
	if request.method == 'GET':
		# devi = Device.query.first()
		payload = {
			"name" : "out",
			"test" : "out2"
		}
		# js = json.dumps(payload)

		# resp = Response(js, status=200, mimetype='application/json')
		# resp.headers['Link'] = 'http://example.com'
		resp = jsonify(payload)
		resp.status_code = 200
		return resp

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