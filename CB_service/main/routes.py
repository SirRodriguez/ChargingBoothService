from flask import Blueprint
# from CB_service import mydb

main = Blueprint('main', __name__)

@main.route("/")
def defaut():
		# mycursor = mydb.cursor()

		# # mycursor.execute("SELECT * FROM user")
		# # myresult = mycursor.fetchall()
		# # user = myresult[0]

		# sql = "UPDATE user SET username = 'admin' WHERE id = 1"

		# mycursor.execute(sql)
		# mydb.commit()

		return "Main - Default"