import networkx as nx
from networkx.readwrite import json_graph
import json
import requests
import time
import datetime
import matplotlib.pyplot as plt
from operator import itemgetter

# small data set
G = nx.read_adjlist('graph1000.txt')
# big data set
#G = nx.read_adjlist('graph105315.txt')

# find communities base on k-cliques
#k_cliques = list(nx.k_clique_communities(G, 13))

# ask for all artist names of clique/community & print it
def print_community(k_cliques):
	for elem in k_cliques:
		req_string = 'https://api.spotify.com/v1/artists?ids='
		for node in elem:
			req_string = req_string + node + ','
		req_string = req_string[:-1]
		r = requests.get(req_string, auth = ())
		genres = {}
		for artist in r.json()['artists']:
			if len(artist['genres']) != 0:
				for genre in artist['genres']:
					if genre in genres:
						genres[genre] += 1
					else:
						genres[genre] = 1
		print(genres)
		print('-----------------------------')

# example code for extracting biggest hub for an egonet (node with all neighbors and edges between them)
#node_and_degree=G.degree()
#(largest_hub,degree)=sorted(node_and_degree.items(),key=itemgetter(1))[-100]
# Create ego graph of main hub
#hub_ego=nx.ego_graph(G,largest_hub)
# Draw graph
#pos=nx.spring_layout(hub_ego)
#nx.draw(hub_ego,pos,node_color='b',node_size=50,with_labels=False)
# Draw ego as large and red
#nx.draw_networkx_nodes(hub_ego,pos,nodelist=[largest_hub],node_size=300,node_color='r')
#plt.savefig('ego_graph.png')
#plt.show()


# graph of egonets without the ego, so just the edges between the neighbors
E = nx.Graph()
degrees = sorted(node_and_degree.items(),key=itemgetter(1))
for i in range(len(degrees)):
	(hub, degree) = degrees[i]
	E = nx.compose(E, nx.ego_graph(G, hub))

cliques = list(nx.find_cliques(E))
print_community(cliques)

# some stumps of finding max cliques in max cliques
#H = nx.make_max_clique_graph(E)
#print(len(cc))
#I = nx.make_max_clique_graph(H)

#nx.draw(E)
#plt.savefig('ego_graphs.png')
#plt.show()

#nx.draw(H)
#plt.savefig('max_clique.png')
#plt.show()

#nx.draw(I)
#plt.savefig('max_clique2.png')
#plt.show()


# similarity measure for two nodes
def friendship_score(G, v, w):
	sum = 0
	for u in nx.nodes(G):
		neighbors = nx.all_neighbors(G, u)
		if ((v in neighbors) and (w in neighbors)):
			Z_u = nx.ego_graph(G, u, center=False)
			if ((v in nx.nodes(Z_u)) and (w in nx.nodes(Z_u))):
				sum += 1
	return sum

# first attempt to use friendship score for clustering (just an array of scores right now)
# takes time even for the small data set
#all_nodes = list(nx.nodes(G))
#friendship_scores = [ [0 for i in range(len(all_nodes))] for i in range(len(all_nodes))]

#ego = nx.ego_graph(G, all_nodes[6], center = False)
#nx.draw(ego)
#plt.savefig('ego.png')
#plt.show()
#for i in range(len(all_nodes)):
#	for j in range(len(all_nodes)):
#		if i != j:
#			if friendship_scores[i][j] == 0: 
#				score = friendship_score(G, all_nodes[i], all_nodes[j])
#				friendship_scores[i][j] = score
#				friendship_scores[j][i] = score
#print(friendship_scores)