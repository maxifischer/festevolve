import networkx as nx
from networkx.readwrite import json_graph
import json
import time
import datetime
import sys
from collections import deque
import progressbar
import batchrequest
import json
import requests

class RequestException(Exception):
	pass

maxsize = 20000
batchsize = 200
clientid = ""
clientsecret = ""

try:
	for i in range(1,len(sys.argv)):
		params = sys.argv[i].split("=", 1)
		if params[0] == "maxsize":
			maxsize = int(params[1])
		elif params[0] == "batchsize":
			batchsize = int(params[1])
		elif params[0] == "clientid":
			clientid = params[1]
		elif params[0] == "clientsecret":
			clientsecret = params[1]
except:
	print "Error while reading parameters, using defaults"
	maxsize = 20000
	batchsize = 200
	clientid = ""
	clientsecret = ""

# list of artists to add
pq = deque()
all_artists = set()
artists_info = {}
G = nx.Graph()
fetch_artist_info = []

# example set upon Red Hot Chilli Peppers
artist_id = u'0L8ExT028jH3ddEcZwqJJ5'
pq.append(artist_id)
all_artists.add(u'Red Hot Chili Peppers')
count = 0

st = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')
print(st)

progressbar.draw(count, maxsize, 30)

batchrequest.setCredentials(clientid,clientsecret)

try:
	while pq and count < maxsize:
		first = False
		cur_batchsize = 0
		urls = []

		while pq and cur_batchsize < batchsize:
			currentArtist = pq.pop()
			urls.append('https://api.spotify.com/v1/artists/' + currentArtist + '/related-artists')
			cur_batchsize += 1

		# contains tornado HTTPresponses
		# see http://www.tornadoweb.org/en/stable/httpclient.html#tornado.httpclient.HTTPResponse
		all_responses = batchrequest.get(urls)
		
		max_retry = 0
		reauth = False
		for response in all_responses:
			# reconstuct the artist from the url
			currentArtist = response.request.url.split('/')[-2] # -2 means second-last element

			if response.code == 429 or response.code == 401:
				pq.append(currentArtist)
				continue
			elif response.code != 200:
				raise RequestException({"code": response.code, "reason": response.reason})

			count += 1
			
			rjson = json.loads(response.body)
			for artist in rjson['artists']:
				if artist['id'] not in all_artists:
					all_artists.add(artist['id'])
					pq.append(artist['id'])		
					G.add_node(artist['id'])
					fetch_artist_info += artist['id'] + ","
				G.add_edge(currentArtist, artist['id'])
		progressbar.redraw(count, maxsize, 30)

	fetch_queries = []
	api_url = 'https://api.spotify.com/v1/artists'
	while fetch_artist_info:
		fetch_string = ""
		for artistid in fetch_artist_info[:50]:
			fetch_string += artistid + ","
		fetch_string = fetch_string[:-1]
		fetch_queries.append((api_url,{"ids": fetch_string}))
		fetch_artist_info = fetch_artist_info[50:]

	while fetch_queries:
		infos = batchrequest.get(fetch_queries[:batchsize], True)
		fetch_queries = fetch_queries[batchsize:]
		if response.code == 429 or response.code == 401:
			fetch_queries.append((response.request.url, {}))
		elif response.code != 200:
			raise RequestException({"code": response.code, "reason": response.reason})
		for response in infos:
			for artist in json.loads(response.body):
				artists_info[artist.id] = artist

except (KeyboardInterrupt, SystemExit):
	print "Aborting after " + str(count) + " entries"
except RequestException as e:
	details = e.args[0]
	print "Request Error, Status was " + str(details["code"])
	print details["reason"]
except batchrequest.AuthFail as e:
	print e
#print(all_artists)
st = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')
print(st)
print(len(all_artists))
#data = json_graph.adjacency_data(G)
#H = json_graph.adjacency_graph(data)

#file.write(json.dumps(H))
#file.close()
nx.write_adjlist(G, 'graph.txt')

with open('artist.txt', 'wb') as artist_file:
	artist_file.write(str(artists_info))