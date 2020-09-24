# PATCH is used for **modify** capabilities. The PATCH request only needs 
# to contain the changes to the resource, not the complete resource.

# This resembles PUT, but the body contains a set of instructions describing 
# how a resource currently residing on the server should be modified to 
# produce a new version. This means that the PATCH body should not just be a 
# modified part of the resource, but in some kind of patch language like JSON 
# Patch or XML Patch.

# PATCH is neither safe nor idempotent. However, a PATCH request can be issued 
# in such a way as to be idempotent, which also helps prevent bad outcomes from 
# collisions between two PATCH requests on the same resource in a similar time 
# frame. Collisions from multiple PATCH requests may be more dangerous than PUT 
# collisions because some patch formats need to operate from a known base-point 
# or else they will corrupt the resource. Clients using this kind of patch 
# application should use a conditional request such that the request will fail 
# if the resource has been updated since the client last accessed the resource. 
# For example, the client can use a strong ETag in an If-Match header on the 
# PATCH request.

from flask import Blueprint

PATCH = Blueprint('PATCH', __name__)

@PATCH.route("/PATCH/")
def defaut():
	return "PATCH - Default"