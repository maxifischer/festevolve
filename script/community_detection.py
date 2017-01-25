from __future__ import division
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
import community
from collections import Counter
import random


#real data set
#G = nx.read_adjlist('graph1000.txt')
# small data set
G = nx.read_adjlist('graph_report.txt')
# big data set
#G = nx.read_adjlist('graph105315.txt')

def get_genre_of_artists(artist_list):
	req_string = 'https://api.spotify.com/v1/artists'

	genres = {}
	genres['null'] = 0
	# maximum 50 ids
	artist_list = list(artist_list)
	while artist_list:
		artist_batch = ""
		for artist in artist_list[0:50]:
			artist_batch += artist + ","
		artist_batch = artist_batch[:-1]
		r = requests.get(req_string, params={'ids': artist_batch}, auth = ())
		#print(r.json())	
		for artist in r.json()['artists']:
			if artist['genres']:
				for genre in artist['genres']:
					if genre in genres:
						genres[genre] += 1
					else:
						genres[genre] = 1
			else:
				genres['null'] += 1	
		artist_list = artist_list[50:]
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
# lpa_comm = asyn_lpa_communities(G)

# for currPart in lpa_comm:
# 	artists = get_genre_of_artists(currPart)
# 	print(len(currPart), get_genre_tuple(artists))
# print('-----------------------------')


# # Louvain algo
# louvain = []

# print('Louvain algo')
# partition = community.best_partition(G)
# partition_dict = {}
# for key in partition:
# 	if partition[key] in partition_dict:
# 		partition_dict[partition[key]].append(key)
# 	else:
# 		partition_dict[partition[key]] = []
# for part in partition_dict:
# 	artists = get_genre_of_artists(partition_dict[part])
# 	p = (len(partition_dict[part]), get_genre_tuple(artists))
# 	print(p[0], p[1])
# 	louvain.append(p)
# print('-----------------------------')

# kclique = []

# # k-clique_communities
# print('k-clique-communities')
# k_cliques = list(nx.k_clique_communities(G,3))

# for k_clique in k_cliques:
# 	artists = get_genre_of_artists(k_clique)
# 	p = (len(k_clique), get_genre_tuple(artists))
# 	print(p[0], p[1])
# 	kclique.append(p)
# print('-----------------------------')

# with open("graph_communities.txt", 'wb') as output:
# 	output.write("louvain\n")
# 	for c in louvain:
# 		output.write(str(c) + "\n")
# 	output.write("\nkclique\n")
# 	for c in kclique:
# 		output.write(str(c) + "\n")


kclique = []
louvain = []
algo = ''
f = open('graph_communities.txt', 'rb')
for line in f:
	if algo == '':
		algo = 'louvain\n'
	elif algo == 'louvain\n':
		if line == 'kclique\n':
			algo = 'kclique\n'
		else:
			line = line.replace('(', '').replace(')', '').replace('[', '').replace(']', '').replace(' ', '')[:-2].split(',')
			line = filter(None, line)
			line = [int(elem) for elem in line]
			kclique.append(line)
	elif algo == 'kclique\n':
		line = line.replace('(', '').replace(')', '').replace('[', '').replace(']', '').replace(' ', '')[:-2].split(',')
		line = filter(None, line)
		line = [int(elem) for elem in line]
		louvain.append(line)

kclique = kclique[:-1]
print(louvain)
print(kclique)

algos = ['louvain', 'kclique']
for algostr in algos:
	if algostr == 'louvain':
		algo = louvain
	else:
		algo = kclique
	
	null_values = []
	accuracy = []
	for tup in algo:
		if len(tup) > 2:
			accuracy.append(tup[2]/(tup[0] - tup[1]))
			null_values.append(tup[1])
	accuracy = sorted(accuracy, reverse = True)
	values = range(1, len(accuracy) + 1)
	plt.figure()
	plt.plot(values, accuracy, 'ro-') # in-degree
	plt.axis([1, len(accuracy), 0, 1])
	plt.legend(['In-degree','Out-degree'])
	plt.xlabel('Communitites')
	plt.ylabel('Accuracy')
	plt.title('Accuracy of '+ algostr +'-Communities')
	plt.savefig('spotify_acc_'+ algostr +'.pdf')
	plt.close()

	null_values = sorted(null_values, reverse = True)
	values = range(1, len(null_values) + 1)
	plt.figure()
	plt.plot(values, null_values, 'ro-') # in-degree
	plt.axis([1, len(null_values), 0, max(null_values)])
	plt.legend(['In-degree','Out-degree'])
	plt.xlabel('Communitites')
	plt.ylabel('Null Values')
	plt.title('Null Values of '+ algostr +'-Communities')
	plt.savefig('spotify_null_'+ algostr +'.pdf')
	plt.close()


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