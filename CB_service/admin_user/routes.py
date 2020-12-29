from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash
from jsonschema import validate
from CB_service import userManager, db, bcrypt, resetLimiter
from CB_service.models import User
from CB_service.admin_user.forms import ResetPasswordForm, SecurityQuestion
from CB_service.admin_user.utils import send_reset_email
import mysql.connector
import os

admin_user = Blueprint('admin_user', __name__)


##########   ############
## Site ##   ## Device ##
##########   ############

# Site and device share the same method endpoint here
@admin_user.route("/device/admin_user/verify_user")
@admin_user.route("/site/admin_user/verify_user")
def verify_user():
	payload = {}
	if request.method == 'GET':
		# Json validation
		schema = {
			"type": "object",
			"properties": {
				"username": {
					"type": "string"
				},
				"password": {
					"type": "string"
				}
			}
		}
		try:
			validate(instance=request.json, schema=schema)
		except:
			resp = jsonify(payload)
			resp.status_code = 400
			return resp


		username = request.json["username"]
		password = request.json["password"]

		admin_key = userManager.verify_user(username, password)
		payload["user_verified"] = admin_key != None
		payload["admin_key"] = admin_key

		resp = jsonify(payload)
		resp.status_code = 200
		return resp

	else:
		resp = jsonify(payload)
		resp.status_code = 405
		return resp

@admin_user.route("/device/admin_user/account_info/<string:admin_key>")
@admin_user.route("/site/admin_user/account_info/<string:admin_key>")
def account_info(admin_key):
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
		sql = "SELECT * FROM user"
		mycursor.execute(sql)
		result = mycursor.fetchall()
		user = result[0]

		payload["username"] = user[1]
		payload["email"] = user[2]

		resp = jsonify(payload)
		resp.status_code = 200
		return resp
	else:
		resp = jsonify(payload)
		resp.status_code = 405
		return resp

@admin_user.route("/device/admin_user/update_account/<string:admin_key>", methods=['PUT'])
@admin_user.route("/site/admin_user/update_account/<string:admin_key>", methods=['PUT'])
def update_account(admin_key):
	payload = {}
	if request.method == 'PUT':
		if not userManager.verify_key(admin_key):
			resp = jsonify(payload)
			resp.status_code = 401
			return resp

		# Verify Json
		# Json validation
		schema = {
			"type": "object",
			"properties": {
				"username": {
					"type": "string"
				},
				"email": {
					"type": "string"
				}
			}
		}
		try:
			validate(instance=request.json, schema=schema)
		except:
			resp = jsonify(payload)
			resp.status_code = 400
			return resp

		mydb = mysql.connector.connect(
			host=os.environ.get('MYSQL_HOST'),
			user=os.environ.get('MYSQL_USER'),
			password=os.environ.get('MYSQL_PASSWORD'),
			database=os.environ.get('MYSQL_DATABASE')
		)
		mycursor = mydb.cursor()
		sql = "UPDATE user SET username = %s, email = %s WHERE id = 1"
		val = (request.json["username"], request.json["email"])

		mycursor.execute(sql, val)

		mydb.commit()

		resp = jsonify(payload)
		resp.status_code = 200
		return resp

	else:
		resp = jsonify(payload)
		resp.status_code = 405
		return resp


@admin_user.route("/device/admin_user/update_password/<string:admin_key>", methods=['PUT'])
@admin_user.route("/site/admin_user/update_password/<string:admin_key>", methods=['PUT'])
def update_password(admin_key):
	payload = {}
	if request.method == 'PUT':
		if not userManager.verify_key(admin_key):
			resp = jsonify(payload)
			resp.status_code = 401
			return resp

		# Json validation
		schema = {
			"type": "object",
			"properties": {
				"hashed_password": {
					"type": "string"
				}
			}
		}
		try:
			validate(instance=request.json, schema=schema)
		except:
			resp = jsonify(payload)
			resp.status_code = 400
			return resp

		mydb = mysql.connector.connect(
			host=os.environ.get('MYSQL_HOST'),
			user=os.environ.get('MYSQL_USER'),
			password=os.environ.get('MYSQL_PASSWORD'),
			database=os.environ.get('MYSQL_DATABASE')
		)
		mycursor = mydb.cursor()
		sql = "UPDATE user SET password = %s WHERE id = %s"
		val = (request.json["hashed_password"], 1)

		mycursor.execute(sql, val)

		mydb.commit()

		resp = jsonify(payload)
		resp.status_code = 200
		return resp
	else:
		resp = jsonify(payload)
		resp.status_code = 405
		return resp

@admin_user.route("/device/admin_user/logout")
@admin_user.route("/site/admin_user/logout")
def logout():
	payload = {}
	if request.method == 'GET':
		userManager.reset_admin_key()

		resp = jsonify(payload)
		resp.status_code = 200
		return resp
	else:
		resp = jsonify(payload)
		resp.status_code = 405
		return resp


@admin_user.route("/reset_password", methods=['GET', 'POST'])
def reset_password():
	mydb = mysql.connector.connect(
		host=os.environ.get('MYSQL_HOST'),
		user=os.environ.get('MYSQL_USER'),
		password=os.environ.get('MYSQL_PASSWORD'),
		database=os.environ.get('MYSQL_DATABASE')
	)
	mycursor = mydb.cursor()
	sql = "SELECT * FROM user"
	mycursor.execute(sql)
	result = mycursor.fetchall()
	user = result[0]
	security_question = user[4]
	security_response = user[5]

	form = SecurityQuestion()
	if form.validate_on_submit():
		# Check the provided response
		if bcrypt.check_password_hash(security_response, form.response.data):
			flash("You may now change your password", 'success')
			return redirect(url_for("admin_user.change_password", input_security_response=form.response.data))
		else:
			flash("Answer incorrect", 'danger')

		# return render_template('reset_password.html')
	return render_template('security_question.html', form=form, security_question=security_question)

@admin_user.route("/change_password/<string:input_security_response>", methods=['GET', 'POST'])
def change_password(input_security_response):
	# Grab the user from data base
	mydb = mysql.connector.connect(
		host=os.environ.get('MYSQL_HOST'),
		user=os.environ.get('MYSQL_USER'),
		password=os.environ.get('MYSQL_PASSWORD'),
		database=os.environ.get('MYSQL_DATABASE')
	)
	mycursor = mydb.cursor()
	sql = "SELECT * FROM user"
	mycursor.execute(sql)
	result = mycursor.fetchall()
	user = result[0]
	security_question = user[4]
	security_response = user[5]

	# Verify the security response to make sure it is a valid entry
	if bcrypt.check_password_hash(security_response, input_security_response):
		form = ResetPasswordForm()
		if form.validate_on_submit():
			sql = "UPDATE user SET password = %s WHERE id = %s"
			val = (bcrypt.generate_password_hash(form.password.data).decode('utf-8'), 1)
			mycursor.execute(sql, val)
			
			mydb.commit()

			return render_template('reset_done.html')
		return render_template('reset_token.html', form=form)
	else:
		return redirect(url_for('admin_user.reset_password'))


################################
# Old depreciated routes below #
################################

# This will be a web page to reset the password
@admin_user.route("/reset_password_OLD")
def reset_password_OLD():
	# !!!
	# These routes are depreciated because of non-working email
	return redirect(url_for('main.defaut'))

	if not resetLimiter.reached_limit():
		resetLimiter.add_count()
		mydb = mysql.connector.connect(
			host=os.environ.get('MYSQL_HOST'),
			user=os.environ.get('MYSQL_USER'),
			password=os.environ.get('MYSQL_PASSWORD'),
			database=os.environ.get('MYSQL_DATABASE')
		)
		mycursor = mydb.cursor()
		sql = "SELECT * FROM user"
		mycursor.execute(sql)
		result = mycursor.fetchall()
		user = result[0]

		send_reset_email(user=user)

	return render_template('reset_password.html')

@admin_user.route("/reset_token_OLD/<token>", methods=['GET', 'POST'])
def reset_token_OLD(token):
	# !!!
	# These routes are depreciated because of non-working email
	return redirect(url_for('main.defaut'))

	# Verify token
	local_user = User.verify_reset_token(token)
	if local_user is None:
		return render_template('token_denied.html')

	form = ResetPasswordForm()
	if form.validate_on_submit():
		mydb = mysql.connector.connect(
			host=os.environ.get('MYSQL_HOST'),
			user=os.environ.get('MYSQL_USER'),
			password=os.environ.get('MYSQL_PASSWORD'),
			database=os.environ.get('MYSQL_DATABASE')
		)
		mycursor = mydb.cursor()
		sql = "UPDATE user SET password = %s WHERE id = %s"
		val = (bcrypt.generate_password_hash(form.password.data).decode('utf-8'), 1)
		mycursor.execute(sql, val)
		
		mydb.commit()

		return render_template('reset_done.html')
	return render_template('reset_token.html', form=form)