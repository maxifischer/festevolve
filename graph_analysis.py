import networkx as nx
import pylab as plt

spotifygraph = nx.read_edgelist('graph.txt')

in_degrees = spotifygraph.in_degree() # dictionary node:degree
in_values = sorted(set(in_degrees.values()))
in_hist = [in_degrees.values().count(x) for x in in_values]
plt.figure()
plt.plot(in_values,in_hist,'ro-') # in-degree
plt.plot(out_values,out_hist,'bv-') # out-degree
plt.legend(['In-degree','Out-degree'])
plt.xlabel('Degree')
plt.ylabel('Number of nodes')
plt.title('Hartford drug users network')
plt.savefig('hartford_degree_distribution.pdf')
plt.close()
