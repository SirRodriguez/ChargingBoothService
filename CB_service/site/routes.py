from flask import Blueprint, request, json, Response, jsonify, current_app, send_from_directory
import os
from os import listdir
from os.path import isfile, join
import secrets
from CB_service import db
from CB_service.models import User, Device, Settings, Session
from CB_service.site.utils import resize_image, resize_all_images

site = Blueprint('site', __name__)