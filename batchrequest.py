# use tornado for batchrequests
# see http://www.tornadoweb.org/en/stable/
from tornado import ioloop, httpclient
import requests
import base64
import progressbar
import time

requestcounter = 0
responses = []
token = ""
max_waittime = 0
need_reauth = True
clientid = ""
clientsecret = ""

class AuthFail(Exception):
	pass

def handle_request(response):
	global responses
	global requestcounter
	global max_waittime
	global need_reauth
	responses.append(response)
	requestcounter -= 1

	if response.code == 429:
		waittime = int(response.headers["Retry-After"])
		if waittime > max_waittime:
			max_waittime = waittime

	if response.code == 401:
		need_reauth = True

	if requestcounter == 0:
		ioloop.IOLoop.instance().stop()

def get(urls, params=False):
	global requestcounter
	global responses
	global token
	global max_waittime
	global need_reauth
	global clientid
	global clientsecret

	if max_waittime > 0:
		print "Got 429, waiting for " + str(max_waittime) + " seconds"
		time.sleep(max_waittime)
		progressbar.clear(1)
		max_waittime = 0

	if need_reauth:
		getAuth()
		need_reauth = False

	requestcounter = 0
	responses = []
	headers=None
	if token:
		headers = {"Authorization": "Bearer " + token}
	http_client = httpclient.AsyncHTTPClient()

	for url in urls:
		requestcounter += 1
		url_string = url
		if params:
			url_string = url[0] + "?"
			for param in url[1]:
				url_string += str(param) + "=" + url[1][param] + "&"
			if url[1]:
				url_string = url_string[:-1]
		http_client.fetch(httpclient.HTTPRequest(url_string,headers=headers), handle_request)
	ioloop.IOLoop.instance().start()

	return responses

def getAuth():
	global clientid
	global clientsecret
	data = {"grant_type": "client_credentials"}
	headers = {"Authorization": "Basic " + base64.b64encode(clientid + ":" + clientsecret)}
	r = requests.post(r"https://accounts.spotify.com/api/token", data=data, headers=headers)
	if r.status_code != 200:
		raise AuthFail("Could not authenticate with spotify")
	rjson = r.json()
	global token
	token = rjson["access_token"]

def setCredentials(ID, secret):
	global clientid
	global clientsecret
	clientid = ID
	clientsecret = secret

def getWithParams(url, params):
	global token
	if token:
		headers = {"Authorization": "Bearer " + token}
	r = requests.get(url, params=params, headers=headers)

	while r.status_code == 429:
		waittime = int(r.headers["Retry-After"])
		time.sleep(waittime)
		r = requests.get(url, params=params, headers=headers)

	if r.status_code == 401:
		getAuth()
		r = requests.get(url, params=params, headers=headers)

	return r