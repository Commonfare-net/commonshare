#!/usr/bin/env python

import sys
import operator
import ast
import networkx as nx
from datetime import datetime
import math
def personalisedPageRank(core_graph,node, type):
    now = datetime.now()
    
 #Do the pagerank calculations 
    surrounding_nodes = {k:10 for k in core_graph.neighbors(node)} 
    core_graph.remove_nodes_from([node])
    core_graph = core_graph.to_directed()
    iter = core_graph.edges(data=True)
    for (u,v,c) in iter:
        last_time_activated = datetime.strptime(c['last_date'],"%Y/%m/%d")
        delta = (now - last_time_activated).days /7.0
        depreciation_factor = math.pow(0.95,delta) #Edge weight depreciates by 5% every week
        if 'edgeweight' in c:
            c['edgeweight'] = ast.literal_eval(c['edgeweight'])[v] * depreciation_factor #Actually swap the in/out weights around for purposes of PageRank
        else:
            c['edgeweight'] = depreciation_factor
    rank_values = nx.pagerank(core_graph,personalization=surrounding_nodes,alpha=0.85,weight='edgeweight')
    for k in rank_values.keys():
       if k in surrounding_nodes.keys():
           del rank_values[k]
       elif core_graph.nodes[k]["type"] != type: #If it's a story, return other stories. If it's a commoner, return other commoners
           del rank_values[k]
    return rank_values
   
def init(filename,nodeid):
    
    G_read = nx.read_gexf(filename)
    type = G_read.nodes[nodeid]['type']
    page_rank_values = personalisedPageRank(G_read,nodeid,type)
    sorted_rank = sorted(page_rank_values.items(), key=operator.itemgetter(1),reverse=True)
    G_untainted = nx.read_gexf(filename)
    list = []
    for i in range(10):
        list.append(sorted_rank[i][0] + ':' + str(nx.shortest_path_length(G_untainted,str(nodeid),sorted_rank[i][0])))
    print list

if __name__ == "__main__":    
    if len(sys.argv) < 3:
        print 'Missing filename or node ID'
        sys.exit()
    filename = sys.argv[1]
    nodeid = sys.argv[2]
    init(filename,nodeid)
    