# use tornado for batchrequests
# see http://www.tornadoweb.org/en/stable/
from tornado import ioloop, httpclient
import requests
import base64

requestcounter = 0
responses = []
token = ""

class AuthFail(Exception):
	pass

def handle_request(response):
    global responses
    global requestcounter
    responses.append(response)
    requestcounter -= 1
    if requestcounter == 0:
        ioloop.IOLoop.instance().stop()

def get(urls):
	global requestcounter
	global responses
	requestcounter = 0
	responses = []
	headers=None
	if token:
		headers = {"Authorization": "Bearer " + token}
	http_client = httpclient.AsyncHTTPClient()
	for url in urls:
	    requestcounter += 1
	    http_client.fetch(httpclient.HTTPRequest(url,headers=headers), handle_request)
	ioloop.IOLoop.instance().start()

	return responses

def getAuth(clientID, clientSecret):
	data = {"grant_type": "client_credentials"}
	headers = {"Authorization": "Basic " + base64.b64encode(clientID + ":" + clientSecret)}
	r = requests.post(r"https://accounts.spotify.com/api/token", data=data, headers=headers)
	if r.status_code != 200:
		raise AuthFail("Could not authenticate with spotify")
	rjson = r.json()
	global token
	token = rjson["access_token"]