# The HTTP GET method is used to **read** (or retrieve) a representation 
# of a resource. In the “happy” (or non-error) path, GET returns a 
# representation in XML or JSON and an HTTP response code of 200 (OK). 
# In an error case, it most often returns a 404 (NOT FOUND) or 400 
# (BAD REQUEST).

# According to the design of the HTTP specification, GET (along with HEAD) 
# requests are used only to read data and not change it. Therefore, when 
# used this way, they are considered safe. That is, they can be called 
# without risk of data modification or corruption—calling it once has the 
# same effect as calling it 10 times, or none at all. Additionally, GET 
# (and HEAD) is idempotent, which means that making multiple identical 
# requests ends up having the same result as a single request.

# Do not expose unsafe operations via GET—it should never modify any 
# resources on the server.

from flask import Blueprint

GET = Blueprint('GET', __name__)

@GET.route("/GET/")
def defaut():
	return "GET - Default"