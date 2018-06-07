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
from dateutil.relativedelta import *
'''
This module does the necessary k-core calculations and appends the results to each node in the Graph.
Plotly functions now exist in 'kcoreplotly.py' as this generates data to be used in a D3 visualisation instead
'''

def getNodeStats(G,node_id,starttime,endtime):
    edges = G.edges(node_id,data=True)
    
    #There are more elegant ways of doing this but it works for now
    stats = {}
    for (u,v,c) in edges:
        if 'create' in c:
            dates = []
            for createactions in c['create']:
                if (starttime < datetime.strptime(createactions[1],"%d/%m/%y") < endtime):
                    if str(createactions[0]) == str(node_id):
                        if createactions[1] not in stats:
                            stats[createactions[1]] = []
                        stats[createactions[1]].append(['create',cf.weights['create'][0]])
        #No data on story reads
        '''
        if 'read' in c:
            for readactions in c['read']:
                if (starttime < datetime.strptime(readactions[1],"%d/%m/%y") < endtime):
                    if str(readactions[0]) == str(node_id):
                        stories_read = stories_read + 1
                    else:
                        read_by_others = read_by_others + 1
            if stories_read >0:
                stats['Stories created'] = stories_created
            if read_by_others > 0:
                stats['Stories created'] = stories_created
        '''
        if 'comment' in c:
            commentdates = []
            receivedates = []
            for commentactions in c['comment']:
                if (starttime < datetime.strptime(commentactions[1],"%d/%m/%y") < endtime):
                    if commentactions[1] not in stats:
                        stats[commentactions[1]] = []                
                    if str(commentactions[0]) == str(node_id):
                        stats[commentactions[1]].append(["comment",cf.weights['comment'][0]])
                    else:
                        stats[commentactions[1]].append(["rcomment",cf.weights['comment'][1]])
        #No data on story shares
        '''
        if 'share' in c:                
            for shareactions in c['share']:
                if (starttime < datetime.strptime(shareactions[1],"%d/%m/%y") < endtime):
                    if str(shareactions[0]) == str(node_id):
                        stories_shared = stories_shared + 1
                    else:
                        shared_by_others = shared_by_others + 1
        '''
        if 'talk' in c:
            talkdates = []
            receivedates = []
            for talkactions in c['talk']:
                if (starttime < datetime.strptime(talkactions[1],"%d/%m/%y") < endtime):
                    if talkactions[1] not in stats:
                        stats[talkactions[1]] = []
                    if str(talkactions[0]) == str(node_id):
                        stats[talkactions[1]].append(["talk",cf.weights['talk'][0]])
                    else:
                        stats[talkactions[1]].append(["rtalk",cf.weights['talk'][1]])
                
        if 'give' in c:
            givedates = []
            receivedates = []
            for giveactions in c['give']:
                if (starttime < datetime.strptime(giveactions[1],"%d/%m/%y") < endtime):
                    if giveactions[1] not in stats:
                        stats[giveactions[1]] = []                
                    if str(giveactions[0]) == str(node_id):
                        stats[giveactions[1]].append(["give",cf.weights['give'][0]])
                    else:
                        stats[giveactions[1]].append(["rgive",cf.weights['give'][1]])
                        
    return stats

def calculate(G,startdate,enddate,granularity):   
    user_id = 0
    
    if not os.path.exists("../json"):
        os.makedirs("../json")
        
    windowstart = startdate
    windowend = windowstart+ relativedelta(months=+1)

    alpha = 0.4
    loopcount = 0
    
    
    
    while(windowend < enddate):
        #Find edges which have a spell that started or ended within the bounds of a given hour/day
        #For those edges that didn't, remove them, then calculate the k-core

        ebunch = []
        indirectedges = []
        
        #GCopy = G.copy()
        #Apparently the above doesn't deep copy node attributes that are lists. The documentation on this is confusing
        #as, supposedly, it's meant to be a deep copy of the graph by default. Instead, the below works just fine
        GCopy = copy.deepcopy(G)
        iter = GCopy.edges(data=True)

        for (u,v,c) in iter:
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

        #Go through them again and remove the unnecessary attributes
        nodeiter = GCopy.nodes(data=True)      
        for (n,c) in nodeiter:
            for action_key in cf.interaction_keys:
                #Here instead, we need to iterate over the actions 'read', 'commented' and 'shared' and see who did them.
                if action_key in c:
                    actions_to_keep = []
                    for action in c[action_key]:
                        if (windowstart < datetime.strptime(action[1],"%d/%m/%y") < windowend):
                            actions_to_keep.append(action)
                    c[action_key] = actions_to_keep
        #This uses a modified core_number algorithm that takes the weights of each node's edges into account
        #Trying it for both standard undirected graphs and my 'directed' equivalent
        
        (ReducedGraph,D) = dx.core_number_weighted(GCopy,windowstart,windowend,True,False)
        d1 = Counter(D.values())

        nodeiter = ReducedGraph.nodes(data=True)
        #This adds the kcore value back into the GEXF
        for (n,c) in nodeiter:
            c['kcore'] = D[n]
            c['stats'] = getNodeStats(ReducedGraph,n,windowstart,windowend)
            c['tags'] = c['tags'].split(",") #Turns it into an array for nice JSON reading
            
        #Hopefully this will label edges appropriately
        edgeiter = ReducedGraph.edges(data=True)
        for (u,v,c) in edgeiter:
            starttags = ReducedGraph.nodes[u]['tags']
            endtags = ReducedGraph.nodes[v]['tags']
            tagintersect = [val for val in starttags if val in endtags] #intersection of tags for proper printing in D3
            c['edgetags'] = tagintersect
            
        #Update the 'sliding window'
        windowstart = windowend
        windowend = windowend + relativedelta(months=+1)
        loopcount = loopcount + 1
        
        #Create JSON files as output from the 'reduced graph'
        data = json_graph.node_link_data(ReducedGraph)
        with open('../json/data'+str(loopcount)+'.json', 'w') as outfile:
            outfile.write(json.dumps(data))
