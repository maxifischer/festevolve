# use tornado for batchrequests
# see http://www.tornadoweb.org/en/stable/
from tornado import ioloop, httpclient
import requests

requestcounter = 0
responses = []

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

	http_client = httpclient.AsyncHTTPClient()
	for url in urls:
	    requestcounter += 1
	    http_client.fetch(url, handle_request)
	ioloop.IOLoop.instance().start()

	return responses

def getAuth(clientID, clientSecret):
	data = {}
	r = requests.post(url, data=data, headers=headers)