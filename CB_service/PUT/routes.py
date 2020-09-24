# PUT is most-often utilized for **update** capabilities, PUT-ing to a 
# known resource URI with the request body containing the newly-updated 
# representation of the original resource.

# However, PUT can also be used to create a resource in the case where the 
# resource ID is chosen by the client instead of by the server. In other 
# words, if the PUT is to a URI that contains the value of a non-existent 
# resource ID. Again, the request body contains a resource representation. 
# Many feel this is convoluted and confusing. Consequently, this method of 
# creation should be used sparingly, if at all.

# Alternatively, use POST to create new resources and provide the client-defined 
# ID in the body representation—presumably to a URI that doesn't include the ID 
# of the resource (see POST below).

# On successful update, return 200 (or 204 if not returning any content in 
# the body) from a PUT. If using PUT for create, return HTTP status 201 on 
# successful creation. A body in the response is optional—providing one consumes 
# more bandwidth. It is not necessary to return a link via a Location header in 
# the creation case since the client already set the resource ID.

# PUT is not a safe operation, in that it modifies (or creates) state on the server, 
# but it is idempotent. In other words, if you create or update a resource using PUT 
# and then make that same call again, the resource is still there and still has the 
# same state as it did with the first call.

# If, for instance, calling PUT on a resource increments a counter within the resource, 
# the call is no longer idempotent. Sometimes that happens and it may be enough to 
# document that the call is not idempotent. However, it's recommended to keep PUT 
# requests idempotent. It is strongly recommended to use POST for non-idempotent requests.

from flask import Blueprint

PUT = Blueprint('PUT', __name__)

@PUT.route("/PUT/")
def defaut():
	return "PUT - Default"