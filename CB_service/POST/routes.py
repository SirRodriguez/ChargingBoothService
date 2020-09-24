# The POST verb is most-often utilized to **create** new resources. 
# In particular, it's used to create subordinate resources. That is, 
# subordinate to some other (e.g. parent) resource. In other words, 
# when creating a new resource, POST to the parent and the service 
# takes care of associating the new resource with the parent, assigning 
# an ID (new resource URI), etc.

# On successful creation, return HTTP status 201, returning a Location 
# header with a link to the newly-created resource with the 201 HTTP status.

# POST is neither safe nor idempotent. It is therefore recommended for 
# non-idempotent resource requests. Making two identical POST requests 
# will most-likely result in two resources containing the same information.

from flask import Blueprint

POST = Blueprint('POST', __name__)

@POST.route("/POST/")
def defaut():
	return "POST - Default"