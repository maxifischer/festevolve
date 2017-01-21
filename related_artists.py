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

maxsize = 20000 if len(sys.argv) == 1 else int(sys.argv[1])
batchsize = 200 if len(sys.argv) < 3 else int(sys.argv[2])

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
		
		for response in all_responses:
			if response.code != 200:
				raise RequestException({"code": response.code, "reason": response.reason})
			# reconstuct the artist from the url
			currentArtist = response.request.url.split('/')[-2] # -2 means second-last element
			rjson = json.loads(response.body)
			for artist in rjson['artists']:
				artist_name = artist['name'].encode('ascii','ignore')
				if artist_name not in all_artists:
					pq.append(artist['id'])
					all_artists.add(artist_name)		
					G.add_node(artist['id'])
				G.add_edge(currentArtist, artist['id'])
	
		count += 1
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