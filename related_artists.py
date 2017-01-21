import networkx as nx
from networkx.readwrite import json_graph
import json
import requests
import time
import datetime
import sys
from collections import deque
import progressbar

maxsize = 20000 if len(sys.argv) == 1 else int(sys.argv[1])

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

while pq and count < maxsize:
	first = False
	currentArtist = pq.pop()
	r = requests.get('https://api.spotify.com/v1/artists/' + currentArtist + '/related-artists', auth = ())
	
	#print(r)
	for i in r.json()['artists']:
		artist_name = i['name'].encode('ascii','ignore')
		if artist_name not in all_artists:
			#print(i['name'])
			pq.append(i['id'])
			all_artists.add(artist_name)		
			G.add_node(i['id'])
		G.add_edge(currentArtist, i['id'])
	
		#save graph in execution
		#if (count % 100) == 0:
		#	nx.write_adjlist(G, 'graph' + str(count) + '.txt')
	
	count += 1
	progressbar.redraw(count, maxsize, 30)
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