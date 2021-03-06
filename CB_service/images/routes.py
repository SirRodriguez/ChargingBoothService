from flask import Blueprint, request, jsonify, current_app, send_from_directory
from CB_service import db, userManager
from CB_service.images.utils import resize_image
import os
from os import listdir
from os.path import isfile, join
import mysql.connector

images = Blueprint('images', __name__)

############
## Device ##
############

# Does not have an admin key because kiosk mode uses this route for not admin purposes
@images.route("/device/img_count/<string:id_number>")
def get_image_count(id_number):
	payload = {}
	if request.method == 'GET':
		mydb = mysql.connector.connect(
			host=os.environ.get('MYSQL_HOST'),
			user=os.environ.get('MYSQL_USER'),
			password=os.environ.get('MYSQL_PASSWORD'),
			database=os.environ.get('MYSQL_DATABASE')
		)
		mycursor = mydb.cursor()

		# Grab device
		sql = "SELECT * FROM device WHERE id_number = %s"
		val = (id_number,)
		mycursor.execute(sql,val)
		result = mycursor.fetchall()

		if len(result) > 0:
			payload["registered"] = True

			devi = result[0]
			id = devi[0]
			path = os.path.join(current_app.root_path, 'static', 'picture_files', str(id))
			count = 0
			if os.path.isdir(path): # If no directory, send 0
				all_files = [f for f in listdir(path) if isfile(join(path, f))]
				for file in all_files:
					count += 1

			payload["image_count"] = count

			# Grab settings
			sql = "SELECT * FROM settings WHERE id = " + str(id)
			mycursor.execute(sql)
			result = mycursor.fetchall()
			devi_settings = result[0]

			# Add the settings to the payload as well
			settings = {}
			settings["toggle_pay"] = devi_settings[1]
			settings["price"] = devi_settings[2]
			settings["charge_time"] = devi_settings[3]
			settings["time_offset"] = devi_settings[4]
			settings["location"] = devi_settings[5]
			settings["aspect_ratio_width"] = devi_settings[6]
			settings["aspect_ratio_height"] = devi_settings[7]

			payload["settings"] = settings

			resp = jsonify(payload)
			resp.status_code = 200
			return resp
		else:
			payload["registered"] = False

			resp = jsonify(payload)
			resp.status_code = 400
			return resp
	else:
		resp = jsonify(payload)
		resp.status_code = 405
		return resp

# Does not have an admin key because kiosk mode uses this route for not admin purposes
@images.route("/device/grab_image/<string:id_number>/<int:img_num>/<random_hex>")
def grab_device_image(id_number, img_num, random_hex):
	payload = {}
	if request.method == 'GET':
		mydb = mysql.connector.connect(
			host=os.environ.get('MYSQL_HOST'),
			user=os.environ.get('MYSQL_USER'),
			password=os.environ.get('MYSQL_PASSWORD'),
			database=os.environ.get('MYSQL_DATABASE')
		)
		mycursor = mydb.cursor()

		# Grab device
		sql = "SELECT * FROM device WHERE id_number = %s"
		val = (id_number,)
		mycursor.execute(sql,val)
		result = mycursor.fetchall()

		if len(result) > 0:
			devi = result[0]
			id = devi[0]

			path = os.path.join(current_app.root_path, 'static', 'picture_files', str(id))

			# Find extention
			all_files = [f for f in listdir(path) if isfile(join(path, f))]
			extention = ""
			for file in all_files:
				f_name, f_ext = os.path.splitext(file)
				if f_name == str(img_num):
					extention = f_ext

			# Send the file
			if os.path.isdir(path):
				return send_from_directory(directory=path, filename=str(img_num) + extention)
			else:
				resp = jsonify(payload)
				resp.status_code = 404
				return resp
		else:
			resp = jsonify(payload)
			resp.status_code = 400
			return resp
	else:
		resp = jsonify(payload)
		resp.status_code = 405
		return resp

# Does not have an admin key because kiosk mode uses this route for not admin purposes
@images.route("/device/grab_re_image/<string:id_number>/<int:img_num>/<random_hex>")
def grab_resized_image(id_number, img_num, random_hex):
	payload = {}
	if request.method == 'GET':
		mydb = mysql.connector.connect(
			host=os.environ.get('MYSQL_HOST'),
			user=os.environ.get('MYSQL_USER'),
			password=os.environ.get('MYSQL_PASSWORD'),
			database=os.environ.get('MYSQL_DATABASE')
		)
		mycursor = mydb.cursor()

		# Grab device
		sql = "SELECT * FROM device WHERE id_number = %s"
		val = (id_number,)
		mycursor.execute(sql,val)
		result = mycursor.fetchall()

		if len(result) > 0:
			devi = result[0]
			id = devi[0]

			path = os.path.join(current_app.root_path, 'static', 'picture_files', str(id), 'resized')

			# Find extention
			all_files = [f for f in listdir(path) if isfile(join(path, f))]
			extention = ""
			for file in all_files:
				f_name, f_ext = os.path.splitext(file)
				if f_name == str(img_num):
					extention = f_ext

			# Send the file
			if os.path.isdir(path):
				return send_from_directory(directory=path, filename=str(img_num) + extention)
			else:
				resp = jsonify(payload)
				resp.status_code = 404
				return resp

		else:
			resp = jsonify(payload)
			resp.status_code = 400
			return resp
	else:
		resp = jsonify(payload)
		resp.status_code = 405
		return resp

@images.route("/device/images/upload/<string:id_number>/<string:admin_key>", methods=['POST'])
def upload_device_images(id_number, admin_key):
	payload = {}

	if request.method == 'POST':
		if not userManager.verify_key(admin_key):
			resp = jsonify(payload)
			resp.status_code = 401
			return resp

		mydb = mysql.connector.connect(
			host=os.environ.get('MYSQL_HOST'),
			user=os.environ.get('MYSQL_USER'),
			password=os.environ.get('MYSQL_PASSWORD'),
			database=os.environ.get('MYSQL_DATABASE')
		)
		mycursor = mydb.cursor()

		# Grab device
		sql = "SELECT * FROM device WHERE id_number = %s"
		val = (id_number,)
		mycursor.execute(sql,val)
		result = mycursor.fetchall()

		if len(result) > 0:
			devi = result[0]
			id = devi[0]

			# Grab settings
			sql = "SELECT * FROM settings WHERE id = " + str(id)
			mycursor.execute(sql)
			result = mycursor.fetchall()
			devi_settings = result[0]

			# From settings get ration width and height
			ratio_width = devi_settings[6]
			ratio_height = devi_settings[7]

			# Check if directory exists for device images
			path = os.path.join(current_app.root_path, 'static', 'picture_files', str(id))
			if not os.path.isdir(path):
				os.mkdir(path)

			# Check if resized image directory exists
			re_path = os.path.join(current_app.root_path, 'static', 'picture_files', str(id), 'resized')
			if not os.path.isdir(re_path):
				os.mkdir(re_path)

			# Count how many images are in the directory
			all_files = [f for f in listdir(path) if isfile(join(path, f))]
			count = 0
			for file in all_files:
				count += 1

			# Save the incomming images
			files = request.files.to_dict(flat=False)
			for image_file in files['image']:
				_, f_ext = os.path.splitext(image_file.filename)
				file_path = os.path.join(path, str(count) + f_ext)
				image_file.save(file_path)

				# Get a resized image
				background_color = 'black'
				re_img = resize_image(image_file, background_color, ratio_width, ratio_height)


				resized_file_path = os.path.join(current_app.root_path, 'static', 'picture_files', str(id), 'resized', str(count) + f_ext)
				re_img.save(resized_file_path)

				count += 1

			resp = jsonify(payload)
			resp.status_code = 200
			return resp

		else:
			resp = jsonify(payload)
			resp.status_code = 400
			return resp

	else:
		resp = jsonify(payload)
		resp.status_code = 405
		return resp

@images.route("/device/remove_images/<string:id_number>/<string:removals>/<string:admin_key>", methods=['DELETE'])
def remove_device_images(id_number, removals, admin_key):
	payload = {}

	if request.method == 'DELETE':
		if not userManager.verify_key(admin_key):
			resp = jsonify(payload)
			resp.status_code = 401
			return resp

		mydb = mysql.connector.connect(
			host=os.environ.get('MYSQL_HOST'),
			user=os.environ.get('MYSQL_USER'),
			password=os.environ.get('MYSQL_PASSWORD'),
			database=os.environ.get('MYSQL_DATABASE')
		)
		mycursor = mydb.cursor()

		# Grab device
		sql = "SELECT * FROM device WHERE id_number = %s"
		val = (id_number,)
		mycursor.execute(sql,val)
		result = mycursor.fetchall()

		if len(result) > 0:
			devi = result[0]
			id = devi[0]

			path = os.path.join(current_app.root_path, 'static', 'picture_files', str(id))
			re_path = os.path.join(current_app.root_path, 'static', 'picture_files', str(id), 'resized')
			if os.path.isdir(path):

				# Parse removals
				rem_list = removals.split(",")
				# fix index and put in a set
				rem_set = set()
				for index, value in enumerate(rem_list):
					rem_set.add(str(int(rem_list[index])-1))

				# Remove the image files in there
				all_files = [f for f in listdir(path) if isfile(join(path, f))]
				for file in all_files:
					f_name, f_ext = os.path.splitext(file)
					if f_name in rem_set:
						file_path = os.path.join(path, file)
						re_file_path = os.path.join(re_path, file) # Resized names are the same as the original
						os.remove(file_path)
						os.remove(re_file_path)

				# readjust the file names
				all_files = [f for f in listdir(path) if isfile(join(path, f))]
				count = 0
				for file in all_files:
					f_name, f_ext = os.path.splitext(file)
					# Original
					src_path = os.path.join(path, file)
					dst_path = os.path.join(path, str(count) + f_ext)
					os.rename(src_path, dst_path)

					# Resized
					src_path = os.path.join(re_path, file)
					dst_path = os.path.join(re_path, str(count) + f_ext)
					os.rename(src_path, dst_path)
					count += 1

				resp = jsonify(payload)
				resp.status_code = 204
				return resp
			else:
				resp = jsonify(payload)
				resp.status_code = 400
				return resp

		else:
			resp = jsonify(payload)
			resp.status_code = 400
			return resp

	else:
		resp = jsonify(payload)
		resp.status_code = 405
		return resp


##########
## Site ##
##########

# Site
@images.route("/site/location_image_count/<int:id>/<string:admin_key>")
def device_location_img_count(id, admin_key):
	payload = {}
	if request.method == 'GET':
		if not userManager.verify_key(admin_key):
			resp = jsonify(payload)
			resp.status_code = 401
			return resp

		mydb = mysql.connector.connect(
			host=os.environ.get('MYSQL_HOST'),
			user=os.environ.get('MYSQL_USER'),
			password=os.environ.get('MYSQL_PASSWORD'),
			database=os.environ.get('MYSQL_DATABASE')
		)
		mycursor = mydb.cursor()

		# Grab device
		sql = "SELECT * FROM device WHERE id = %s"
		val = (str(id),)
		mycursor.execute(sql,val)
		result = mycursor.fetchall()

		if len(result) > 0:
			# Grab the settings
			sql = "SELECT * FROM settings WHERE id = " + str(id)
			mycursor.execute(sql)
			result = mycursor.fetchall()

			# Put the location from settings
			if len(result) > 0:
				payload["location"] = result[0][5]
			else:
				payload["location"] = "No Settings"

			# # Grab image count
			path = os.path.join(current_app.root_path, 'static', 'picture_files', str(id))
			count = 0
			if os.path.isdir(path): # If no directory, send nothing
				all_files = [f for f in listdir(path) if isfile(join(path, f))]
				for file in all_files:
					count += 1

			payload["image_count"] = count

			resp = jsonify(payload)
			resp.status_code = 200
			return resp
		else:
			resp = jsonify(payload)
			resp.status_code = 400
			return resp
	else:
		resp = jsonify(payload)
		resp.status_code = 405
		return resp

# Site
@images.route("/site/image_count/<int:id>/<string:admin_key>")
def device_img_count(id, admin_key):
	payload = {}
	if request.method == 'GET':
		if not userManager.verify_key(admin_key):
			resp = jsonify(payload)
			resp.status_code = 401
			return resp

		mydb = mysql.connector.connect(
			host=os.environ.get('MYSQL_HOST'),
			user=os.environ.get('MYSQL_USER'),
			password=os.environ.get('MYSQL_PASSWORD'),
			database=os.environ.get('MYSQL_DATABASE')
		)
		mycursor = mydb.cursor()

		# Grab device
		sql = "SELECT * FROM device WHERE id = %s"
		val = (str(id),)
		mycursor.execute(sql,val)
		result = mycursor.fetchall()

		if len(result) > 0:
			# Grab image count
			path = os.path.join(current_app.root_path, 'static', 'picture_files', str(id))
			count = 0
			if os.path.isdir(path): # If no directory, send nothing
				all_files = [f for f in listdir(path) if isfile(join(path, f))]
				for file in all_files:
					count += 1

			payload["image_count"] = count

			resp = jsonify(payload)
			resp.status_code = 200
			return resp
		else:
			resp = jsonify(payload)
			resp.status_code = 400
			return resp
	else:
		resp = jsonify(payload)
		resp.status_code = 405
		return resp


# Site
# this will not have an admin key becuase it is used to grab a single image from the service
@images.route("/site/grab_image/<int:id>/<int:img_num>/<random_hex>")
def grab_image(id, img_num, random_hex):
	payload = {}
	if request.method == 'GET':
		path = os.path.join(current_app.root_path, 'static', 'picture_files', str(id))

		# Find extention
		all_files = [f for f in listdir(path) if isfile(join(path, f))]
		extention = ""
		for file in all_files:
			f_name, f_ext = os.path.splitext(file)
			if f_name == str(img_num):
				extention = f_ext


		if os.path.isdir(path):
			return send_from_directory(directory=path, filename=str(img_num) + extention)
		else:
			resp = jsonify(payload)
			resp.status_code = 404
			return resp
	else:
		resp = jsonify(payload)
		resp.status_code = 405
		return resp

# Site
@images.route("/site/remove_images/<int:id>/<string:removals>/<string:admin_key>", methods=['DELETE'])
def remove_images(id, removals, admin_key):
	payload = {}

	if request.method == 'DELETE':
		if not userManager.verify_key(admin_key):
			resp = jsonify(payload)
			resp.status_code = 401
			return resp

		path = os.path.join(current_app.root_path, 'static', 'picture_files', str(id))
		re_path = os.path.join(current_app.root_path, 'static', 'picture_files', str(id), 'resized')
		if os.path.isdir(path):

			# Parse removals
			rem_list = removals.split(",")
			# fix index and put in a set
			rem_set = set()
			for index, value in enumerate(rem_list):
				rem_set.add(str(int(rem_list[index])-1))

			# Remove the image files in there
			all_files = [f for f in listdir(path) if isfile(join(path, f))]
			for file in all_files:
				f_name, f_ext = os.path.splitext(file)
				if f_name in rem_set:
					file_path = os.path.join(path, file)
					re_file_path = os.path.join(re_path, file) # Resized names are the same as the original
					os.remove(file_path)
					os.remove(re_file_path)

			# readjust the file names
			all_files = [f for f in listdir(path) if isfile(join(path, f))]
			count = 0
			for file in all_files:
				f_name, f_ext = os.path.splitext(file)
				# Original
				src_path = os.path.join(path, file)
				dst_path = os.path.join(path, str(count) + f_ext)
				os.rename(src_path, dst_path)

				# Resized
				src_path = os.path.join(re_path, file)
				dst_path = os.path.join(re_path, str(count) + f_ext)
				os.rename(src_path, dst_path)
				count += 1

			resp = jsonify(payload)
			resp.status_code = 204
			return resp
		else:
			resp = jsonify(payload)
			resp.status_code = 400
			return resp
	else:
		resp = jsonify(payload)
		resp.status_code = 405
		return resp


# Site
@images.route("/site/images/upload/<int:id>/<string:admin_key>", methods=['POST'])
def upload_images(id, admin_key):
	payload = {}

	if request.method == 'POST':
		if not userManager.verify_key(admin_key):
			resp = jsonify(payload)
			resp.status_code = 401
			return resp
			
		mydb = mysql.connector.connect(
			host=os.environ.get('MYSQL_HOST'),
			user=os.environ.get('MYSQL_USER'),
			password=os.environ.get('MYSQL_PASSWORD'),
			database=os.environ.get('MYSQL_DATABASE')
		)
		mycursor = mydb.cursor()

		# Grab device
		sql = "SELECT * FROM device WHERE id = %s"
		val = (str(id),)
		mycursor.execute(sql,val)
		result = mycursor.fetchall()

		if len(result) > 0:
			# Grab settings
			sql = "SELECT * FROM settings WHERE id = " + str(id)
			mycursor.execute(sql)
			result = mycursor.fetchall()
			devi_settings = result[0]

			# From settings get ration width and height
			ratio_width = devi_settings[6]
			ratio_height = devi_settings[7]

			# Check if directory exists for device images
			path = os.path.join(current_app.root_path, 'static', 'picture_files', str(id))
			if not os.path.isdir(path):
				os.mkdir(path)

			# Check if resized image directory exists
			re_path = os.path.join(current_app.root_path, 'static', 'picture_files', str(id), 'resized')
			if not os.path.isdir(re_path):
				os.mkdir(re_path)

			# Count how many images are in the directory
			all_files = [f for f in listdir(path) if isfile(join(path, f))]
			count = 0
			for file in all_files:
				count += 1

			# Save the incomming images
			files = request.files.to_dict(flat=False)
			for image_file in files['image']:
				# Save the original file
				_, f_ext = os.path.splitext(image_file.filename)
				file_path = os.path.join(path, str(count) + f_ext)
				image_file.save(file_path)

				# Get a resized image
				background_color = 'black'
				re_img = resize_image(image_file, background_color, ratio_width, ratio_height)

				# Save the resized image
				resized_file_path = os.path.join(current_app.root_path, 'static', 'picture_files', str(id), 'resized', str(count) + f_ext)
				re_img.save(resized_file_path)

				count += 1

			resp = jsonify(payload)
			resp.status_code = 200
			return resp
		else:
			resp = jsonify(payload)
			resp.status_code = 400
			return resp
	else:
		resp = jsonify(payload)
		resp.status_code = 405
		return resp
