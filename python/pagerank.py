#!/usr/bin/env python

import sys
import operator
import ast
import networkx as nx
from datetime import datetime
import math
import xml.etree.ElementTree as ET

def personalisedPageRank(core_graph,node):
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
       elif core_graph.nodes[k]["type"] != "story": #If it's not a story, don't want to know
           del rank_values[k]
    return rank_values
   
def init(filename,storyid,userid):
    
    G_read = nx.read_gexf(filename)
    page_rank_values = personalisedPageRank(G_read,storyid)
    
    
    #How influential is this node (based on kcore)?

    
    sorted_rank = sorted(page_rank_values.items(), key=operator.itemgetter(1),reverse=True)
    G_untainted = nx.read_gexf(filename)
    list = []
    influence = G_untainted.nodes[userid]['kcore']
    
    ET.register_namespace("", "http://www.gexf.net/1.2draft") 
    tree = ET.parse(filename)  
    root = tree.getroot()
    neglected_nodes = root[0].attrib['neglected_nodes'].split(" ")
    
    #neglected_nodes = G_untainted['neglected_nodes'].split(" ")   
    #Based on their influence, throw a few new, unknown stories into the mix
    
    for i in range(min(influence,len(neglected_nodes))):
        list.append(neglected_nodes[i] + ':neglected')
    for j in range(10-influence):
        list.append(sorted_rank[j][0] + ':closematch')
    print list

if __name__ == "__main__":    
    if len(sys.argv) < 4:
        print 'Missing filename or story ID or userid'
        sys.exit()
    filename = sys.argv[1]
    storyid = sys.argv[2]
    userid = sys.argv[3]
    init(filename,storyid,userid)
    