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
G = nx.Graph()

# example set upon Red Hot Chilli Peppers
artist_id = u'0L8ExT028jH3ddEcZwqJJ5'
pq.append(artist_id)
all_artists.add(u'Red Hot Chili Peppers')
count = 0

st = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')
print(st)

progressbar.draw(count, maxsize, 30)

batchrequest.getAuth(clientid,clientsecret)

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
		for response in all_responses:
			# reconstuct the artist from the url
			currentArtist = response.request.url.split('/')[-2] # -2 means second-last element

			if response.code == 429:
				waittime = int(response.headers["Retry-After"])
				if waittime > max_retry:
					max_retry = waittime
				pq.append(currentArtist)
				continue
			elif response.code != 200:
				raise RequestException({"code": response.code, "reason": response.reason})

			count += 1
			
			rjson = json.loads(response.body)
			for artist in rjson['artists']:
				artist_name = artist['name'].encode('ascii','ignore')
				if artist_name not in all_artists:
					pq.append(artist['id'])
					all_artists.add(artist_name)		
					G.add_node(artist['id'])
				G.add_edge(currentArtist, artist['id'])

		if max_retry > 0:
			print "Got 429, waiting for " + str(max_retry) + " seconds"
			time.sleep(max_retry)
			progressbar.clear(1)
			max_retry = 0

		progressbar.redraw(count, maxsize, 30)
except (KeyboardInterrupt, SystemExit):
	print "Aborting after " + str(count) + " entries"
except RequestException as e:
	details = e.args[0]
	print "Request Error, Status was " + str(details["code"])
	print details["reason"]
#print(all_artists)
st = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')
print(st)
print(len(all_artists))
#data = json_graph.adjacency_data(G)
#H = json_graph.adjacency_graph(data)

#file.write(json.dumps(H))
#file.close()
nx.write_adjlist(G, 'graph.txt')
all_artists_sorted = list(all_artists)
all_artists_sorted.sort()

with open('artist.txt', 'wb') as artist_file:
	for artist in all_artists_sorted:
		artist_file.write(artist + "\n")