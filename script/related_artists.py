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
import ast

def load_file(file, mode=None):
	global folder_prefix

	print "loading " + file
	with open(folder_prefix + file) as f:
		s = f.read()
		if mode == 'json':
			obj = json.loads(s)
		else:
			obj = ast.literal_eval(s)
	return obj

folder_prefix = 'graph_data/'

class RequestException(Exception):
	pass

maxsize = 20000
batchsize = 200
clientid = ""
clientsecret = ""
expand_mode=False

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
		elif params[0] == "expand_mode":
			expand_mode = bool(params[1])
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

# example set upon Red Hot Chilli Peppers
artist_id = u'0L8ExT028jH3ddEcZwqJJ5'
pq.append(artist_id)
all_artists.add(u'Red Hot Chili Peppers')
r = requests.get('https://api.spotify.com/v1/artists/' + artist_id)
artists_info[artist_id] = r.json()

count = 0

if expand_mode:
	print "entering expand mode, restoring state"
	G = nx.read_adjlist(folder_prefix + "graph.txt")
	artists_info = load_file("artist.json", 'json')
	all_artists = load_file("all_artists.set")
	pq = load_file("artist.deque")
	count = len(all_artists)
	print "state restored successfully"

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

			if response.code == 429 or response.code == 401 or response.code == 599:
				pq.append(currentArtist)
				continue
			elif response.code != 200:
				raise RequestException({"code": response.code, "reason": response.reason})
			count += 1
			rjson = json.loads(response.body)
			for artist in rjson['artists']:
				if artist['id'] not in all_artists:
					all_artists.add(artist['id'])
					artists_info[artist['id']] = artist
					pq.append(artist['id'])		
					G.add_node(artist['id'])
				G.add_edge(currentArtist, artist['id'])
		progressbar.redraw(count, maxsize, 30)

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
print "writing graph.txt"
nx.write_adjlist(G, folder_prefix + 'graph.txt')

print "writing artist.json"
with open(folder_prefix + 'artist.json', 'w') as artist_json:
	artist_json.write(json.dumps(artists_info))

print "writing all_artists.set"
with open(folder_prefix + 'all_artists.set') as f:
	f.write(str(all_artists))

print "writing artist.deque"
with open(folder_prefix + 'artist.deque') as f:
	f.write(str(pq))