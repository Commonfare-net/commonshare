import networkx as nx
import dynetworkxmulti as dx
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
from dateutil.relativedelta import *
'''
This module does the necessary k-core calculations and appends the results to each node in the Graph.
Plotly functions now exist in 'kcoreplotly.py' as this generates data to be used in a D3 visualisation instead
'''

#def getNodeStats(G,node_id,starttime,endtime):
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
                    if str(action[0][0]) == str(node_id):
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

def add_user(SimpleGraph,G,u):
    SimpleGraph.add_node(u)
    dict = copy.deepcopy(actions_dict)
    dict['type'] = 'user'
    dict['commoner_name'] = G.nodes[u]['commoner_name']
    nx.set_node_attributes(SimpleGraph,{u: dict})
    SimpleGraph = nx.convert_node_labels_to_integers(SimpleGraph)
    
#def calculate(G,startdate,enddate,granularity):  
def calculate(G): 
    user_id = 0
    
    if not os.path.exists("../json"):
        os.makedirs("../json")
        
 #   windowstart = startdate
  #  windowend = windowstart+ relativedelta(months=+1)

 #   alpha = 0.4
 #  loopcount = 0
    

    
    node_data_dict = {}
    nodeiter = G.nodes(data=True)      
    for (n,c) in nodeiter:
        node_data_dict[n] = []
    
  #  while(windowend < enddate):
        #Find edges which have a spell that started or ended within the bounds of a given hour/day
        #For those edges that didn't, remove them, then calculate the k-core
    ebunch = []
    indirectedges = []
        
        #GCopy = G.copy()
        #Apparently the above doesn't deep copy node attributes that are lists. The documentation on this is confusing
        #as, supposedly, it's meant to be a deep copy of the graph by default. Instead, the below works just fine
        #GCopy = copy.deepcopy(G)
        #iter = GCopy.edges(data=True)


    
    #In this bit I'd like to find parallel edges
    SimpleGraph = nx.Graph()
    iter = G.edges(data=True)
    for (u,v,c) in iter:
        edgetype = c['label']
        if edgetype.startswith('transaction'):
            edgetype = cf.transaction
        elif edgetype.startswith('conversation'):
            edgetype = cf.friendship
        else:
            edgetype = cf.comment_story
        if SimpleGraph.has_node(u) == False:
            add_user(SimpleGraph,G,u)
        if SimpleGraph.has_node(v) == False:
            add_user(SimpleGraph,G,v)
        if SimpleGraph.has_edge(u,v) == False:
            SimpleGraph.add_edge(u, v)
            for key in cf.interaction_keys:
                SimpleGraph[u][v][key] = []
        SimpleGraph[u][v][edgetype].append(([u,v],s_today,s_fortnight))
        SimpleGraph.nodes[u][edgetype].append(([u,v],s_today,s_fortnight))    
        SimpleGraph.nodes[v][edgetype].append(([u,v],s_today,s_fortnight))       
    '''
        edgeexists = False
        for intervals in c['spells']:
            #Cumulative                 
            #if windowend > intervals[0]:
            #Non-cumulative
            if (windowstart < datetime.strptime(intervals[0],"%d/%m/%y") < windowend):
                edgeexists = True
                break
        if edgeexists == False:
            ebunch.append((u,v,c))
    GCopy.remove_edges_from(ebunch)
    
    #Here a similar operation is done to remove nodes that do not exist at this point in time
    nbunch = []
    nodeiter = GCopy.nodes(data=True)
    for (n,c) in nodeiter:
        c['date'] = datetime.strftime(windowstart,"%d/%m/%y")
        for intervals in c['spells']:
            if datetime.strptime(intervals[0],"%d/%m/%y") < windowend:
                break
            else:
                nbunch.append(n)
    GCopy.remove_nodes_from(nbunch)
        

    #Go through them again, remove unnecessary actions and add 'meta-data' to nodes based on their remaining actions
    '''
    nodeiter = SimpleGraph.nodes(data=True)      
    for (n,c) in nodeiter:
        nodemeta = []
        for action_key in cf.interaction_keys:
            #Here instead, we need to iterate over the actions 'read', 'commented' and 'shared' and see who did them.
            if action_key in c:
                actions_to_keep = []
                for action in c[action_key]:
                    #if (windowstart < datetime.strptime(action[1],"%d/%m/%y") < windowend):
                    actions_to_keep.append(action)
                c[action_key] = actions_to_keep
                if len(actions_to_keep) == 0:
                    continue
                if action_key not in cf.indirect_interactions:
                    nodemeta.append(cf.meta[action_key])
                #If the user has left a comment and they are the commenter (user to resource) rather than the receiver (user to user)...
                #...then this node is active in the story/discussion network too
                
                if action_key in cf.indirect_interactions: #and n in list(map(lambda x: str(x[0][0]), c[action_key])): 
                    nodemeta.append(cf.meta[action_key])
        #if c['type'] == 'story':
        #    nodemeta.append('story')
        #elif c['type'] == 'ForumPost':
        #    nodemeta.append('discussion')
        c['nodemeta'] = nodemeta
            
            
    #This uses a modified core_number algorithm that takes the weights of each node's edges into account
    #Trying it for both standard undirected graphs and my 'directed' equivalent
#    (ReducedGraph,D) = dx.core_number_weighted(GCopy,windowstart,windowend,True,False)

    #Have to remove the self-loops that have cropped up
    SimpleGraph.remove_edges_from(SimpleGraph.selfloop_edges())
    (ReducedGraph,D) = dx.core_number_weighted(SimpleGraph,True,False)
    d1 = Counter(D.values())

        
    tag_globals = {}
    loners = []
    nodeiter = SimpleGraph.nodes(data=True)
    #This adds the kcore value back into the GEXF
    for (n,c) in nodeiter:
        
        if D[n] == 0:
            loners.append(n);
            c['kcore'] = 0
            c['stats'] = {}
            node_data_dict[n].append(c)                
        else:
            c['kcore'] = D[n]
            c['cumu_totals'] = {k:(v*D[n]) for k,v in c['cumu_totals'].items()}
            c['avg_totals'] = {k:(v*D[n]) for k,v in c['avg_totals'].items()}
            #c['stats'] = getNodeStats(SimpleGraph,n,windowstart,windowend)
            c['stats'] = getNodeStats(SimpleGraph,n)
            #c['tags'] = c['tags'].split(",") #Turns it into an array for nice JSON reading
            #Now accumulate tag number
            #for tag in c['tags']:
            #    if tag not in tag_globals:
            #        tag_globals[tag] = 1
            #    else:
            #        tag_globals[tag] = tag_globals[tag] + 1
            node_data_dict[n].append(c)
    #ReducedGraph.remove_nodes_from(loners)
    
    
    network_globals = {}
    for meta in cf.meta_networks:
        network_globals[meta] = 0
    edgeiter = SimpleGraph.edges(data=True)
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

    #Update the 'sliding window'
    #windowstart = windowend
    #windowend = windowend + relativedelta(months=+1)
    #loopcount = loopcount + 1
    

    #Create JSON files as output from the 'reduced graph'
    data = json_graph.node_link_data(SimpleGraph)
    #Add the counters of tags of users this month, combined with the tags of stories and welfare provisions created
    #Also add the counters of social interactions, donations, story interactions and welfare interactions this month
    #data['network_globals'] = network_globals
    #data['tag_globals'] = tag_globals
            
    with open('../json/datapietro.json', 'w') as outfile:
        outfile.write(json.dumps(data))
              
    for k,v in node_data_dict.items():
        with open('../json/users/' + str(k) + '.json', 'w') as outfile:
            outfile.write(json.dumps(v))              
    
    #Now print out the whole history of each user
    #nodeiter = G.nodes(data=True)
    #for (n,c) in nodeiter:
    #    UserG=nx.Graph()
   #     UserG.add_node(n)
   #     UserG.nodes[n].update(c)
   #     UserG.add_edges_from(G.edges(n,data=True))
   #     data = json_graph.node_link_data(UserG)
   #     with open('../json/users/' + str(n) + '.json', 'w') as outfile:
   #         outfile.write(json.dumps(data))
#cur_date = datetime(2018,6,1)
cur_date = datetime.now()
s_today = cur_date.strftime("%d/%m/%y")
s_fortnight = (cur_date+cf.two_weeks).strftime("%d/%m/%y")
actions_dict = {}
for key in cf.interaction_keys:
    actions_dict[key] = []
#start_date = cur_date
#cur_date = cur_date + cf.one_year            
#Test reading is working properly
G_read = nx.read_gexf("pietro.gexf")
#Pass the start and end times of the file in, as well as the granularity at which you want the data (default 1 month)
calculate(G_read)