from __future__ import division
from networkx.readwrite import json_graph
from operator import itemgetter
from collections import Counter
import networkx as nx
import cProfile
import community
import json
import requests
import time
import datetime
import matplotlib.pyplot as plt
import operator
import random
import pickle


def get_genre_of_artists(artist_list):
	# req_string = 'https://api.spotify.com/v1/artists'

	# genres = {}
	# genres['null'] = 0
	# # maximum 50 ids
	# artist_list = list(artist_list)
	# while artist_list:
	# 	artist_batch = ""
	# 	for artist in artist_list[0:50]:
	# 		artist_batch += artist + ","
	# 	artist_batch = artist_batch[:-1]
	# 	r = requests.get(req_string, params={'ids': artist_batch}, auth = ())
	# 	#print(r.json())	
	# 	for artist in r.json()['artists']:
	# 		if artist['genres']:
	# 			for genre in artist['genres']:
	# 				if genre in genres:
	# 					genres[genre] += 1
	# 				else:
	# 					genres[genre] = 1
	# 		else:
	# 			genres['null'] += 1	
	# 	artist_list = artist_list[50:]
	global artist_info

	genres = {}
	genres['null'] = 0
	artist_list = list(artist_list)

	for artist in artist_list:
		if artist_info[artist]['genres']:
			for genre in artist_info[artist]['genres']:
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

	for i in sorted_genres[:3]:
		genre_list.append(genres[i])
	return genre_list

def asyn_lpa_communities(G, weight=None):
    labels = {n: i for i, n in enumerate(G)}
    cont = True
    while cont:
        cont = False
        nodes = list(G)
        random.shuffle(nodes)
        # Calculate the label for each node
        for node in nodes:
            if len(G[node]) < 1:
                continue

            # Get label frequencies. Depending on the order they are processed
            # in some nodes with be in t and others in t-1, making the
            # algorithm asynchronous.
            label_freq = Counter()
            for v in G[node]:
                label_freq.update({labels[v]: G.edge[v][node][weight]
                                    if weight else 1})
            # Choose the label with the highest frecuency. If more than 1 label
            # has the highest frecuency choose one randomly.
            max_freq = max(label_freq.values())
            best_labels = [label for label, freq in label_freq.items()
                           if freq == max_freq]
            new_label = random.choice(best_labels)
            labels[node] = new_label
            # Continue until all nodes have a label that is better than other
            # neighbour labels (only one label has max_freq for each node).
            cont = cont or len(best_labels) > 1

    # TODO In Python 3.3 or later, this should be `yield from ...`.
    return iter(groups(labels).values())

spotifygraph = nx.read_adjlist('graph.txt')
artist_info = {}
with open('artist.json', 'r') as f:
	s = f.read()
	artist_info = json.loads(s)

# number of nodes and edges
#print(spotifygraph.number_of_nodes())
#print(spotifygraph.number_of_edges())

# degree histogram
# degrees = spotifygraph.degree() # dictionary node:degree
# values = sorted(set(degrees.values()))
# hist = [degrees.values().count(x) for x in values]
# plt.figure()
# plt.plot(values,hist,'ro-') # in-degree
# plt.legend(['In-degree','Out-degree'])
# plt.xlabel('Degree')
# plt.ylabel('Number of nodes')
# plt.title('Spotify related artist network')
# plt.savefig('spotify_degree_distribution.pdf')
# plt.close()

# diameter
#print(nx.diameter(spotifygraph))

# triangles
#print(sum(list(nx.triangles(spotifygraph).values())))

# avg clustering coefficient
#print(nx.average_clustering(spotifygraph))

# Louvain algo
profile = cProfile.Profile()

louvain = []

print('Louvain algo')
profile.enable()
partition = community.best_partition(spotifygraph)
partition_dict = {}
for key in partition:
	if partition[key] in partition_dict:
		partition_dict[partition[key]].append(key)
	else:
		partition_dict[partition[key]] = []
for part in partition_dict:
	artists = get_genre_of_artists(partition_dict[part])
	p = (len(partition_dict[part]), get_genre_tuple(artists))
	print(p[0], p[1])
	louvain.append(p)
profile.create_stats()
print('-----------------------------')
profile.print_stats()

kclique = []

# k-clique_communities
profile = cProfile.Profile()

print('k-clique-communities')
profile.enable()
k_cliques = list(nx.k_clique_communities(spotifygraph,3))

for k_clique in k_cliques:
	artists = get_genre_of_artists(k_clique)
	p = (len(k_clique), get_genre_tuple(artists))
	print(p[0], p[1])
	kclique.append(p)
profile.create_stats()
print('-----------------------------')
profile.print_stats()

with open("graph_communities.txt", 'wb') as output:
	output.write("louvain\n")
	for c in louvain:
		output.write(str(c) + "\n")
	output.write("\nkclique\n")
	for c in kclique:
		output.write(str(c) + "\n")