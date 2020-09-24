# DELETE is pretty easy to understand. It is used to **delete** a resource 
# identified by a URI.

# On successful deletion, return HTTP status 200 (OK) along with a response 
# body, perhaps the representation of the deleted item (often demands too much 
# bandwidth), or a wrapped response (see Return Values below). Either that or 
# return HTTP status 204 (NO CONTENT) with no response body. In other words, a 
# 204 status with no body, or the JSEND-style response and HTTP status 200 are 
# the recommended responses.

# HTTP-spec-wise, DELETE operations are idempotent. If you DELETE a resource, 
# it's removed. Repeatedly calling DELETE on that resource ends up the same: 
# the resource is gone. If calling DELETE say, decrements a counter (within the 
# resource), the DELETE call is no longer idempotent. As mentioned previously, 
# usage statistics and measurements may be updated while still considering the 
# service idempotent as long as no resource data is changed. Using POST for 
# non-idempotent resource requests is recommended.

# There is a caveat about DELETE idempotence, however. Calling DELETE on a 
# resource a second time will often return a 404 (NOT FOUND) since it was already 
# removed and therefore is no longer findable. This, by some opinions, makes 
# DELETE operations no longer idempotent, however, the end-state of the resource 
# is the same. Returning a 404 is acceptable and communicates accurately the status 
# of the call.

from flask import Blueprint

DELETE = Blueprint('DELETE', __name__)

@DELETE.route("/DELETE/")
def defaut():
	return "DELETE - Default"