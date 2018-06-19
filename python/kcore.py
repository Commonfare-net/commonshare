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
                    if str(ast.literal_eval(createactions[0])[0]) == str(node_id):
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
                    if str(ast.literal_eval(commentactions[0])[0]) == str(node_id):
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
                    if str(ast.literal_eval(talkactions[0])[0]) == str(node_id):
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
                    if str(ast.literal_eval(giveactions[0])[0]) == str(node_id):
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
            nodemeta = []
            for action_key in cf.interaction_keys:
                #Here instead, we need to iterate over the actions 'read', 'commented' and 'shared' and see who did them.
                if action_key in c:
                    actions_to_keep = []
                    for action in c[action_key]:
                        if (windowstart < datetime.strptime(action[1],"%d/%m/%y") < windowend):
                            actions_to_keep.append(action)
                    c[action_key] = actions_to_keep
                    if action_key == 'talk' and len(actions_to_keep) > 0:
                        nodemeta.append('social')
                    elif action_key == 'give' and len(actions_to_keep) > 0:
                        nodemeta.append('finance')

                    elif action_key == 'create':
                        for creations in c['create']:
                            nodepair = ast.literal_eval(creations[0])
                            if GCopy.node[str(nodepair[1])]['type'] == 'story': 
                                nodemeta.append('story')
                            elif GCopy.node[str(nodepair[1])]['type'] == 'welfare': 
                                nodemeta.append('welfare')    
                    #Here's where it gets tricky
                    #If the user has left a comment and they are the commenter (user to resource) rather than the receiver (user to user)...
                    #...then this node is active in the resource network too
                    elif action_key == 'comment' and len(actions_to_keep) > 0 and n in list(map(lambda x: str(ast.literal_eval(x[0])[0]), c['comment'])):
                        for comments in c['comment']:
                            nodepair = ast.literal_eval(comments[0])                        
                            if GCopy.node[str(nodepair[1])]['type'] == 'story': 
                                nodemeta.append('story')
                            elif GCopy.node[str(nodepair[1])]['type'] == 'welfare': 
                                nodemeta.append('welfare')
            #Any story or welfare node that still exists in the reduced graph 
            if c['type'] == 'story':
                nodemeta.append('story')
            elif c['type'] == 'welfare':
                nodemeta.append('welfare')
            c['nodemeta'] = nodemeta
                
        #This uses a modified core_number algorithm that takes the weights of each node's edges into account
        #Trying it for both standard undirected graphs and my 'directed' equivalent
        
        (ReducedGraph,D) = dx.core_number_weighted(GCopy,windowstart,windowend,True,False)
        d1 = Counter(D.values())


        
        tag_globals = {}
        loners = []
        nodeiter = ReducedGraph.nodes(data=True)
        #This adds the kcore value back into the GEXF
        for (n,c) in nodeiter:
            if D[n] == 0:
                loners.append(n);
            else:
                c['kcore'] = D[n]
                c['stats'] = getNodeStats(ReducedGraph,n,windowstart,windowend)
                c['tags'] = c['tags'].split(",") #Turns it into an array for nice JSON reading
                #Now accumulate tag number
                for tag in c['tags']:
                    if tag not in tag_globals:
                        tag_globals[tag] = 1
                    else:
                        tag_globals[tag] = tag_globals[tag] + 1
        ReducedGraph.remove_nodes_from(loners)
        
        network_globals = {}
        num_social = 0;
        num_story = 0;
        num_welfare = 0;
        num_donation = 0;        
        #Hopefully this will label edges appropriately both with the tags, and the type of communications that happen along them
        edgeiter = ReducedGraph.edges(data=True)
        for (u,v,c) in edgeiter:
            edgemeta = []
            starttags = ReducedGraph.nodes[u]['tags']
            endtags = ReducedGraph.nodes[v]['tags']
            tagintersect = [val for val in starttags if val in endtags] #intersection of tags for proper printing in D3
            c['edgetags'] = tagintersect
            if 'talk' in c:
                edgemeta.append('social')
                num_social = num_social + len(c['talk'])
            if 'give' in c:
                edgemeta.append('finance')
                num_donation = num_donation + len(c['give'])                
            #It's not part of the 'resource' network if it's a user-user comment interaction
            if ('comment' in c or 'create' in c) and (ReducedGraph.nodes[u]['type'] == 'story' or ReducedGraph.nodes[v]['type'] == 'story'):
                edgemeta.append('story')
                if 'comment' in c:
                    num_story = num_story + len(c['comment'])
                if 'create' in c:
                    num_story = num_story + len(c['create'])            
            if ('comment' in c or 'create' in c) and (ReducedGraph.nodes[u]['type'] == 'welfare' or ReducedGraph.nodes[v]['type'] == 'welfare'):
                edgemeta.append('welfare')  
                if 'comment' in c:
                    num_welfare = num_welfare + len(c['comment'])
                if 'create' in c:
                    num_welfare = num_welfare + len(c['create'])
            c['edgemeta'] = edgemeta
        network_globals['social'] = num_social
        network_globals['story'] = num_story
        network_globals['welfare'] = num_welfare
        network_globals['donation'] = num_donation

        #Update the 'sliding window'
        windowstart = windowend
        windowend = windowend + relativedelta(months=+1)
        loopcount = loopcount + 1


        #Create JSON files as output from the 'reduced graph'
        data = json_graph.node_link_data(ReducedGraph)
        #Add the counters of tags of users this month, combined with the tags of stories and welfare provisions created
        #Also add the counters of social interactions, donations, story interactions and welfare interactions this month
        data['network_globals'] = network_globals
        data['tag_globals'] = tag_globals
                
        with open('../json/data'+str(loopcount)+'.json', 'w') as outfile:
            outfile.write(json.dumps(data))
#cur_date = datetime(2018,6,1)
#start_date = cur_date
#cur_date = cur_date + cf.one_year            
#Test reading is working properly
#G_read = nx.read_gexf("../gexf/data360.gexf")
#Pass the start and end times of the file in, as well as the granularity at which you want the data (default 1 month)
#calculate(G_read,start_date,cur_date,"month")
#kcore.plotgraph()