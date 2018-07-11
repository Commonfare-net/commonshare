import networkx as nx
import dynetworkx as dx
import time
import math
import random
from datetime import datetime
import config as cf
import json
from networkx.readwrite import json_graph
from collections import Counter
import os
import copy
import ast
import xml.etree.ElementTree as ET
from dateutil.relativedelta import *
'''
This module does the necessary k-core calculations and appends the results to each node in the Graph.
Plotly functions now exist in 'kcoreplotly.py' as this generates data to be used in a D3 visualisation instead
'''

def getNodeStats(G,node_id):
    edges = G.edges(node_id,data=True)
    
    stats = {}
    for (u,v,c) in edges:
        for action_key in cf.interaction_keys:
            if action_key in c:
                meta = cf.meta[action_key]
                if meta not in stats:
                    stats[meta] = {}
                if action_key not in stats[meta]:
                    stats[meta][action_key] = []
                    stats[meta]["r"+action_key] = [] #This is the inverse (i.e. comment received, like received)
                for action in c[action_key]:
                    if str(ast.literal_eval(action[0])[0]) == str(node_id)or action_key in cf.mutual_interactions:
                        stats[meta][action_key].append(action)
                        if action[1] not in stats:
                            stats[action[1]] = {}
                        if meta not in stats[action[1]]:
                            stats[action[1]][meta] = {}                            
                        if action_key not in stats[action[1]][meta]:
                            stats[action[1]][meta][action_key] = [1,cf.weights[action_key][0]]
                        else:
                            stats[action[1]][meta][action_key][0] += 1 #Number of actions
                            stats[action[1]][meta][action_key][1] += cf.weights[action_key][0] #Weight of actions
                    elif action_key in cf.indirect_interactions:
                        stats[meta]["r"+action_key].append(action)
                        if action[1] not in stats:
                            stats[action[1]] = {}
                        if meta not in stats[action[1]]:
                            stats[action[1]][meta] = {}
                        if ("r" + action_key) not in stats[action[1]][meta]:
                            stats[action[1]][meta]["r"+action_key] = [1,cf.weights[action_key][1]]
                        else:
                            stats[action[1]][meta]["r"+action_key][0] += 1 #Number of actions
                            stats[action[1]][meta]["r"+action_key][1] += cf.weights[action_key][1] #Weight of actions
                    else:
                        stats[meta][action_key].append(action)                    

    return stats

    
def calculate(G,startdate,enddate):  
    user_id = 0
    
    if not os.path.exists("../json"):
        os.makedirs("../json")
        
    windowstart = startdate
    windowend = windowstart+ relativedelta(months=+1)
    loopcount = 0
    
    
    node_data_dict = {}
    nodeiter = G.nodes(data=True)      
    for (n,c) in nodeiter:
        node_data_dict[n] = []
  
    while(windowend < enddate):
        #Find edges which have a spell that started or ended within the bounds of a given hour/day
        #For those edges that didn't, remove them, then calculate the k-core
        ebunch = []
        tagedges = []
        
        #GCopy = SimpleGraph.copy()
        #Apparently the above doesn't deep copy node attributes that are lists. The documentation on this is confusing
        #as, supposedly, it's meant to be a deep copy of the graph by default. Instead, the below works just fine
        GCopy = copy.deepcopy(G)
        iter = GCopy.edges(data=True)
      
        for (u,v,c) in iter:
            edgeexists = False
            for intervals in c['spells']:
                if (windowstart < datetime.strptime(intervals[0],"%Y/%m/%d") < windowend):
                    edgeexists = True
                    break
            if edgeexists == False:
               
                ebunch.append((u,v,c))
            elif GCopy.nodes[u]["type"] == "tag" or GCopy.nodes[v]["type"] == "tag":
                tagedges.append((u,v,c))
                
        GCopy.remove_edges_from(ebunch)
        GCopy.remove_edges_from((tagedges))
        #Here a similar operation is done to remove nodes that do not exist at this point in time
        nbunch = []
        nodeiter = GCopy.nodes(data=True)
        for (n,c) in nodeiter:
            nodeexists = False
            c['date'] = datetime.strftime(windowstart,"%Y/%m/%d")
            if 'spells' in c:
                for intervals in c['spells']:
                    if (windowstart < datetime.strptime(intervals[0],"%Y/%m/%d") < windowend):
                        nodeexists = True
                        break
            if nodeexists == False:
                nbunch.append(n)
        GCopy.remove_nodes_from(nbunch)
            

        #Go through them again, remove unnecessary actions and add 'meta-data' to nodes based on their remaining actions
        
        nodeiter = GCopy.nodes(data=True)      
        for (n,c) in nodeiter:
            nodemeta = []
            for action_key in cf.interaction_keys:
                if action_key in c:
                    actions_to_keep = []
                    for action in c[action_key]:
                        if (windowstart < datetime.strptime(action[1],"%Y/%m/%d") < windowend):
                            actions_to_keep.append(action)
                    c[action_key] = actions_to_keep
                    if len(actions_to_keep) == 0:
                        continue
                    if action_key not in cf.indirect_interactions:
                        nodemeta.append(cf.meta[action_key])
                    #If the user has left a comment and they are the commenter (user to resource) rather than the receiver (user to user)...
                    #...then this node is active in the story/discussion network too                    
                    if action_key in cf.indirect_interactions and n in list(map(lambda x: str(ast.literal_eval(x[0])[0]), c[action_key])): 
                        nodemeta.append(cf.meta[action_key])
            if c['type'] == 'story':
                nodemeta.append('story')
            elif c['type'] == 'listing':
                nodemeta.append('listing')
            c['nodemeta'] = nodemeta
                
                
        #Have to remove the self-loops that have cropped up
        GCopy.remove_edges_from(GCopy.selfloop_edges())
        (ReducedGraph,D) = dx.core_number_weighted(GCopy,windowstart,windowend,True,False)
        d1 = Counter(D.values())
        ReducedGraph.add_edges_from(tagedges)
        tag_globals = {}
        nodeiter = ReducedGraph.nodes(data=True)
        #This adds the kcore value back into the GEXF
        for (n,c) in nodeiter:
            if n not in D:
                c['kcore'] = 0
                c['stats'] = {}
                node_data_dict[n].append(c)
            elif D[n] == 0:
                c['kcore'] = 0
                c['stats'] = {}
                node_data_dict[n].append(c)                
            else:
                c['kcore'] = D[n]
                c['cumu_totals'] = {k:(v*D[n]) for k,v in c['cumu_totals'].items()}
                c['avg_totals'] = {k:(v*D[n]) for k,v in c['avg_totals'].items()}
                c['stats'] = getNodeStats(ReducedGraph,n)
                node_data_dict[n].append(c)
        
        
        network_globals = {}
        for meta in cf.meta_networks:
            network_globals[meta] = 0
        edgeiter = ReducedGraph.edges(data=True)
        '''
        for (u,v,c) in edgeiter:
            edgemeta = []
            #starttags = ReducedGraph.nodes[u]['tags']
            #endtags = ReducedGraph.nodes[v]['tags']
            #tagintersect = [val for val in starttags if val in endtags] #intersection of tags for proper printing in D3
            #c['edgetags'] = tagintersect
            for action_key in cf.interaction_keys:
                if action_key in c and len(c[action_key]) > 0 and action_key not in cf.indirect_interactions:
                    edgemeta.append(cf.meta[action_key])
                    network_globals[cf.meta[action_key]] +=1
                if action_key in c and len(c[action_key]) > 0 and action_key in cf.indirect_interactions and (ReducedGraph.nodes[u]['type'] != 'User' or ReducedGraph.nodes[v]['type'] != 'User'):
                    edgemeta.append(cf.meta[action_key])
                    network_globals[cf.meta[action_key]] +=1
            c['edgemeta'] = edgemeta
        '''
        #Update the 'sliding window'
        windowstart = windowend
        windowend = windowend + relativedelta(months=+1)
        loopcount = loopcount + 1
        

        #Create JSON files as output from the 'reduced graph'
        data = json_graph.node_link_data(ReducedGraph)
        #Add the counters of tags of users this month, combined with the tags of stories and welfare provisions created
        #Also add the counters of social interactions, donations, story interactions and welfare interactions this month
        #data['network_globals'] = network_globals
        #data['tag_globals'] = tag_globals
                
        with open('web/data/data'+str(loopcount)+'.json', 'w') as outfile:
            outfile.write(json.dumps(data))
              
    for k,v in node_data_dict.items():
        with open('web/data/users/' + str(k) + '.json', 'w') as outfile:
            outfile.write(json.dumps(v))              

actions_dict = {}
for key in cf.interaction_keys:
    actions_dict[key] = []

G_read = nx.read_gexf("../gexf/simulateddata.gexf")

ET.register_namespace("", "http://www.gexf.net/1.2draft") 
tree = ET.parse("../gexf/simulateddata.gexf")  
namespaces={'xmlns': 'http://www.gexf.net/1.2draft'}
root = tree.getroot()
startdate = root[0].attrib['start']
enddate = root[0].attrib['end']

#Pass the start and end times of the file in (which I have copied manually but there should be a way to do so automatically
calculate(G_read,datetime.strptime(startdate,"%Y/%m/%d"),datetime.strptime(enddate,"%Y/%m/%d"))