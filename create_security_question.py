import mysql.connector
import os
from flask import Flask
from flask_bcrypt import Bcrypt

bcrypt = Bcrypt(Flask(__name__))

# Grab the security question and response
question = input("Enter the security question: ")
response = input("Enter the security response: ")

# Encript the response
enc_response = bcrypt.generate_password_hash(response).decode('utf-8')

# Execute db sql
mydb = mysql.connector.connect(
	host=os.environ.get('MYSQL_HOST'),
	user=os.environ.get('MYSQL_USER'),
	password=os.environ.get('MYSQL_PASSWORD'),
	database=os.environ.get('MYSQL_DATABASE')
)
mycursor = mydb.cursor()
sql = "UPDATE user SET securityQuestion = %s, securityResponse = %s WHERE id = %s"
val = (question, enc_response, 1)
mycursor.execute(sql, val)

mydb.commit()