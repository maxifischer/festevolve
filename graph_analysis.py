import networkx as nx
import pylab as plt

spotifygraph = nx.read_adjlist('graph.txt')

degrees = spotifygraph.degree() # dictionary node:degree
values = sorted(set(degrees.values()))
hist = [degrees.values().count(x) for x in values]
plt.figure()
plt.plot(values,hist,'ro-') # in-degree
plt.legend(['In-degree','Out-degree'])
plt.xlabel('Degree')
plt.ylabel('Number of nodes')
plt.title('Spotify related artist network')
plt.savefig('spotify_degree_distribution.pdf')
plt.close()
