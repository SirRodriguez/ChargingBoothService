from flask import Blueprint, request, json, Response, jsonify
from CB_service.models import User, Device

main = Blueprint('main', __name__)

@main.route("/")
def defaut():
		return "Main - Default"