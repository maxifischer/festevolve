import networkx as nx
from networkx.readwrite import json_graph
import json
import requests
import time
import datetime
import matplotlib.pyplot as plt
from operator import itemgetter
import operator
import random
import pickle
#sudo pip install python-louvain
import community

#real data set
#G = nx.read_adjlist('graph_report.txt')
# small data set
G = nx.read_adjlist('graph1000.txt')
# big data set
#G = nx.read_adjlist('graph105315.txt')

def get_genre_of_artists(artist_list):
	req_string = 'https://api.spotify.com/v1/artists'
	#for artist in artist_list:
	#	req_string = req_string + artist + ','
	#req_string = req_string[:-1]
	genres = {}
	genres['null'] = 0
	# maximum 50 ids
	artist_list = list(artist_list)
	while len(artist_list) > 51:
		for artist in artist_list[0:50]:
			r = requests.get(req_string, params={'ids': artist}, auth = ())
			#print(r.json())	
			for artist in r.json()['artists']:
				if len(artist['genres']) > 0:
					for genre in artist['genres']:
						if genre in genres:
							genres[genre] += 1
						else:
							genres[genre] = 1
				else:
					genres['null'] += 1	
		artist_list = artist_list[50:-1] 	
	for artist in artist_list:
		r = requests.get(req_string, params={'ids': artist}, auth = ())
		#print(r.json())
		for artist in r.json()['artists']:
			if len(artist['genres']) > 0:
				for genre in artist['genres']:
					if genre in genres:
						genres[genre] += 1
					else:
						genres[genre] = 1
			else:
				genres['null'] += 1	
	return genres

def print_community(k_cliques):
	for elem in k_cliques:
		inp = [elem]
		genres = get_genre_of_artists(inp)
		for genre in genres:
			if genre in genres:
				genres[genre] += 1
			else:
				genres[genre] = 1
		print(genres)
		print('-----------------------------')

def print_genres(genres):
	for genre in genres:
		print(genre, genres[genre])
	print('-----------------------------')

# tuple consists of (null_values, max_genre1, max_genre2, max_genre3)
def get_genre_tuple(genres):
	genre_list = []
	null_genre = genres['null']
	genre_list.append(null_genre)
	del genres['null']
	sorted_genres = sorted(genres, key = lambda genre : genres[genre], reverse = True)
	if len(sorted_genres) < 3:
		genre_list.append(sorted_genres)
	else:
		for i in sorted_genres[:3]:
			genre_list.append(genres[i])
	return genre_list
	

# find communities base on k-cliques
# TODO: more community algos

# Girvan-Newman
# print('girvan-newman')
# path_graph = nx.path_graph(nx.nodes(G))
# girvan_iter = nx.girvan_newman(path_graph)

# for currPart in girvan_iter:
# 	artists = get_genre_of_artists(currPart)
# 	print(len(currPart), get_genre_tuple(artists))
# print('-----------------------------')


# Asynchronous LPA communities
# print('asynchronous LPA communities')
# lpa_comm = nx.asyn_lpa_communities(G)

# for currPart in lpa_comm:
# 	artists = get_genre_of_artists(currPart)
# 	print(len(currPart), get_genre_tuple(artists))
# print('-----------------------------')


# Louvain algo
print('Louvain algo')
partition = community.best_partition(G)
partition_dict = {}
for key in partition:
	if partition[key] in partition_dict:
		partition_dict[partition[key]].append(key)
	else:
		partition_dict[partition[key]] = []
for part in partition_dict:
	artists = get_genre_of_artists(partition_dict[part])
	print(len(partition_dict[part]), get_genre_tuple(artists))
print('-----------------------------')

# k-clique_communities
print('k-clique-communities')
k_cliques = list(nx.k_clique_communities(G,3))

for k_clique in k_cliques:
	artists = get_genre_of_artists(k_clique)
	print(len(k_clique), get_genre_tuple(artists))
print('-----------------------------')





# dumb genre prediction per max count of genres in neighborhood
# queue = []
# genre_artist = {}
# for elem in nx.nodes(G):
# 	inp = []
# 	inp.append(elem)
# 	genre =  getGenreOfArtists(inp)
# 	if genre:
# 		genre_artist[elem] = genre
# 	else:
# 		neighbors = G.neighbors(elem)
# 		genres = getGenreOfArtists(neighbors)
# 		if genres:
# 			genre_artist[elem] = max(genres.iteritems(), key=operator.itemgetter(1))[0]
# 		else:
# 			queue.append(elem)
# count = 0
# while queue and count < 100:
# 	elem = random.choice(queue)
# 	inp = []
# 	inp.append(elem)
# 	genre =  getGenreOfArtists(inp)
# 	if genre:
# 		genre_artist[elem] = genre
# 		queue.remove(elem)
# 		count = 0
# 	else:
# 		neighbors = G.neighbors(elem)
# 		genres = getGenreOfArtists(neighbors)
# 		if genres:
# 			genre_artist[elem] = max(genres.iteritems(), key=operator.itemgetter(1))[0]
# 			queue.remove(elem)
# 			count = 0
# 		else:
# 			count += 1
# 			print(count)
# # delete elements when there are no neighbors with genres
# if count == 100:
# 	for i in queue:
# 		G.remove_node(i)
# with open('genres.pkl', 'wb') as f:
#     pickle.dump(genre_artist, f, pickle.HIGHEST_PROTOCOL)

# with open('obj/' + name + '.pkl', 'rb') as f:
#     artistsWithGenres = pickle.load(f)
# print(artistsWithGenres[artistsWithGenres.keys()[0]])
# print(artistsWithGenres.iterkeys().next())



# ask for all artist names of clique/community & print it


# example code for extracting biggest hub for an egonet (node with all neighbors and edges between them)
node_and_degree=G.degree()
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
#E = nx.Graph()
#degrees = sorted(node_and_degree.items(),key=itemgetter(1))
#for i in range(len(degrees)):
#	(hub, degree) = degrees[i]
#	E = nx.compose(E, nx.ego_graph(G, hub))
#cliques = list(nx.find_cliques(E))
#print_community(cliques)

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
	V = nx.ego_graph(G, v)
	V = nx.compose(V, nx.ego_graph(G, w))
	for u in nx.nodes(V):
		Z_u = nx.ego_graph(V, u, center=False)
		cc = nx.connected_components(Z_u)
		for comp in cc:
			if v in comp:
				if w in comp:
					sum += 1
	return sum

# first attempt to use friendship score for clustering (just an array of scores right now)
# takes time even for the small data set
# all_nodes = list(nx.nodes(G))
# friendship_scores = [ [i for i in all_nodes] for j in all_nodes]
# all_edges = list(nx.edges(G))

#ego = nx.ego_graph(G, all_nodes, center = False)
#nx.draw(ego)
#plt.savefig('ego.png')
#plt.show()
# for i, j in all_edges:
# 	if friendship_scores[i][j] == 0: 
# 		score = friendship_score(G, i, j)
# 		friendship_scores[i][j] = score
# 		friendship_scores[j][i] = score
# print(friendship_scores)