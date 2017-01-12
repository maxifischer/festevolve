import networkx as nx
from networkx.readwrite import json_graph
import json
import requests
import time
import datetime

# list of artists to add
pq = []
all_artists = []
G = nx.Graph()
artist_file = open('artist16.txt', 'wb')

# example set upon Red Hot Chilli Peppers
artist_id = u'0L8ExT028jH3ddEcZwqJJ5'
pq.append(artist_id)
all_artists.append(u'Red Hot Chili Peppers')
count = 0

st = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')
print(st)


while len(pq) > count:
	first = False
	currentArtist = pq[0]
	del pq[0]
	r = requests.get('https://api.spotify.com/v1/artists/' + currentArtist + '/related-artists', auth = ())
	
	#print(r)
	for i in r.json()['artists']:
		if i['name'].encode('ascii','ignore') not in all_artists:
			#print(i['name'])
			pq.append(i['id'])
			all_artists.append(i['name'].encode('ascii','ignore'))
			artist_file.write(i['name'].encode('ascii', 'ignore') + "\n")		
			G.add_node(i['id'])
		G.add_edge(currentArtist, i['id'])
	
		#save graph in execution
		#if (count % 100) == 0:
		#	nx.write_adjlist(G, 'graph' + str(count) + '.txt')
	
	# variable to cut the last items in priority queue, under 5 is time critical 
	count += 4
#print(all_artists)
st = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')
print(st)
print(len(all_artists))
#data = json_graph.adjacency_data(G)
#H = json_graph.adjacency_graph(data)

#file.write(json.dumps(H))
#file.close()
nx.write_adjlist(G, 'graph16.txt')
artist_file.close()