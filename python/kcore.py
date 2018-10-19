import networkx as nx
import dynetworkx as dx
from datetime import datetime
import config as cf
import json
from networkx.readwrite import json_graph
import copy
import sys
import operator
import xml.etree.ElementTree as ET
from dateutil.relativedelta import *

'''
This module does the necessary k-core calculations and appends the results to each node in the Graph.
Plotly functions now exist in 'kcoreplotly.py' as this generates data to be used in a D3 visualisation instead
'''




def createGraphs(G,startdate,enddate):     
    global loopcount
    global commoner_graphs
    global object_graphs

    nodeiter = G.nodes(data=True)    
    #Create dictionaries to hold the interaction data for individual commoners/objects
    for (n,c) in nodeiter:
        if c['type'] == 'commoner':
            commoner_graphs[n] = []
        else:
            object_graphs[n] = []
        c["tags"] = []    
        
    #Create new graph representing interactions within a two-week window
    windowend = enddate
    windowstart = windowend+relativedelta(weeks=-2)
    
    #Makes the cumulative graph
    G_new = calculate(G,startdate,enddate)

    loopcount += 1
    #Makes the fortnightly graphs
    while(windowstart > startdate):
        print 'windowend is',datetime.strftime(windowend,"%Y/%m/%d")
        calculate(G,windowstart,windowend)
        windowend = windowstart
        windowstart = windowend + relativedelta(weeks=-2)
        loopcount += 1
        
    #Make individual historic files for each commoner and each object (i.e., story, listing)
    for k,v in commoner_graphs.items():
        if len(v) > 0:
            with open('../web/data/userdata/' + str(k) + '.json', 'w') as outfile:
                outfile.write(json.dumps(v))              
    for k,v in object_graphs.items():
        if len(v) > 0:
            with open('../web/data/objectdata/' + str(k) + '.json', 'w') as outfile:
                outfile.write(json.dumps(v[0]))  
    return G 
'''
For each node, store the interactions it has been involved with by their type, and by their date
'''
def getNodeStats(core_graph,node_id):
    edges = core_graph.edges(node_id,data=True)
    
    stats = {}
    for (u,v,c) in edges:
        #Loop through all interactions that the node could've done 
        for action_key in cf.interaction_keys:
            if action_key in c:
                
                interaction_type = cf.interaction_types[action_key] #What kind of interaction is this? (i.e. story, transaction, social)
                
                #This initialises the data structures to store the interaction data if they're not already created 
                if interaction_type not in stats:
                    stats[interaction_type] = {}
                if action_key not in stats[interaction_type]:
                    stats[interaction_type][action_key] = []
                    stats[interaction_type]["r"+action_key] = [] #This is the inverse (i.e. comment received, like received)
                
                
                for action in c[action_key]:
                    if action_key in cf.indirect_interactions: #'Indirect' interactions are initiated by someone else, but receiving node gets klout (e.g. a story comment)                          
                        action_key = "r" + action_key
                        
                    elif action[0] != str(node_id) and action_key not in cf.mutual_interactions:    
                        stats[interaction_type][action_key].append(action)                    
                        continue
                    
                    #stats[interaction_type][action_key].append(action)    
                    #Interactions also indexed by the date on which they occurred. This initialises necessary data structures 
                    if action[1] not in stats: #action[1] is the date of the interaction
                        stats[action[1]] = {}
                    if interaction_type not in stats[action[1]]:
                        stats[action[1]][interaction_type] = {}                            
                    if action_key not in stats[action[1]][interaction_type]:
                        stats[action[1]][interaction_type][action_key] = [1,cf.weights[action_key]]
                    else:
                        stats[action[1]][interaction_type][action_key][0] += 1 #Number of actions
                        stats[action[1]][interaction_type][action_key][1] += cf.weights[action_key] #Weight of actions    
                    stats[interaction_type][action_key].append(action)
    return stats
#https://stackoverflow.com/questions/22742754/finding-the-n-degree-neighborhood-of-a-node
'''
Finds all nodes exactly two steps away from a given node - does not include those one step away 
'''
def neighbourPaths(G, node):
    path_lengths = nx.shortest_path_length(G, node)
    all_paths = {}
    for neighbour, length in path_lengths.iteritems():
        if length ==2:
            all_paths[neighbour] = [p[1] for p in nx.all_shortest_paths(G,node,neighbour)]
        elif length == 1:
            all_paths[neighbour] = []
    return all_paths

def personalisedPageRank(core_graph,node):
 #Do the pagerank calculations 
    multi_di_graph = nx.MultiDiGraph()
    multi_di_graph.add_nodes_from(core_graph.nodes())
    for (u,v,c) in core_graph.edges(data=True):
        multi_di_graph.add_edge(u,v,**c)
        multi_di_graph.add_edge(v,u,**c)
    iter = multi_di_graph.edges(data=True)
    for (u,v,c) in iter:
        if 'edgeweight' in c:
            c['edgeweight'] = c['edgeweight'][u]
        else:
            c['edgeweight'] = 1
    return nx.pagerank_numpy(multi_di_graph,personalization={node:1},alpha=0.85,weight='edgeweight')
'''
This method creates the individual commoner/object graphs
'''
def createEntityGraphs(core_graph,core_values):
    global loopcount
    global commoner_graphs
    global object_graphs

    #Here 'entity_graph' refers to the graph of surrounding nodes of a particular commoner or object 
    nodeiter = core_graph.nodes(data=True)
    for (n,c) in nodeiter:    
        if 'kcore' not in core_graph.nodes[n] or core_graph.nodes[n]['kcore'] == 0:
            entity_graph = nx.Graph()
            entity_graph.add_node(n,kcore=0,pagerank=0,stats={})        
            #Here we append a blank fortnight for this commoner 
            if c['type'] == 'commoner':
                commoner_data = json_graph.node_link_data(entity_graph)
                commoner_graphs[n].append(commoner_data)
        else:
            #If this is the all-time cumulative graph, for each user include all the nodes and surrounding edges
            '''
            if loopcount == 0:
                neighbours_and_inbetweens = neighbourPaths(core_graph,n)
                surrounding_nodes = neighbours_and_inbetweens.keys()
                edges = core_graph.edges(surrounding_nodes,data=True)
            else:
                edges = core_graph.edges(n,data=True)
                surrounding_nodes = core_graph.neighbors(n)
            '''
            edges = core_graph.edges(n,data=True)
            surrounding_nodes = core_graph.neighbors(n)    
            
            entity_graph = nx.Graph()
            entity_graph.add_node(n,**c)
            entity_graph.nodes[n]['kcore'] = core_values[n]
            entity_graph.nodes[n]['cumu_totals'] = {k:(v*core_values[n]) for k,v in c['cumu_totals'].items()}
            entity_graph.nodes[n]['avg_totals'] = {k:(v*core_values[n]) for k,v in c['avg_totals'].items()}
            entity_graph.nodes[n]['stats'] = getNodeStats(core_graph,n)
            entity_graph.add_edges_from(edges)
            '''
            if loopcount == 0:
                #Do a 'closeness' calculation of each surrounding node base 
                #page_rank_values = personalisedPageRank(core_graph,n)
                for node,inbetweens in neighbours_and_inbetweens.iteritems():
                    closeness = 0
                    for inbetweener in inbetweens:
                        if core_graph.nodes[inbetweener]['type'] == 'commoner':
                            closeness = closeness + 3
                        elif core_graph.nodes[inbetweener]['type'] == 'story':
                            closeness = closeness + 2
                        else:
                            closeness = closeness + 2
                    entity_graph.add_node(node,**core_graph.nodes[node])
                    entity_graph.nodes[node]['closeness'] = closeness
                    entity_graph.nodes[node]['inbetweens'] = inbetweens                
                    
            else:
            
            #if loopcount == 0:
            #    page_rank_values = personalisedPageRank(core_graph,n) 
            #    sorted_rank = sorted(page_rank_values.items(), key=operator.itemgetter(1),reverse=True)
            #    print 'best matches for ',n,' are ',sorted_rank[0],sorted_rank[1],sorted_rank[2]
                for node in surrounding_nodes:
                    core_graph.nodes[node]['stats'] = getNodeStats(core_graph,node)
                    entity_graph.add_node(node,**core_graph.nodes[node])
           #    if loopcount == 0:
           #         entity_graph.nodes[node]['pagerank'] = page_rank_values[node]
            '''
            
            for node in surrounding_nodes:
                core_graph.nodes[node]['stats'] = getNodeStats(core_graph,node)
                entity_graph.add_node(node,**core_graph.nodes[node])
                    
            #Now that all relevant nodes have been added, need to make sure that appropriate edges are drawn between them 
            all_edges = core_graph.edges(entity_graph.nodes,data=True)
            for (u,v,x) in all_edges:
                if u in entity_graph.nodes and v in entity_graph.nodes:
                    entity_graph.add_edge(u,v,**x)
            if c['type'] == 'commoner':
                commoner_json = json_graph.node_link_data(entity_graph)
                commoner_graphs[n].append(commoner_json)
            #elif loopcount == 0:
            #    object_json = json_graph.node_link_data(entity_graph)
            #    object_graphs[n].append(object_json)
    
    return core_graph

    
'''
This method removes all the spells and actions from the nodes and edges where they fall outside of the window slot
'''
def filter_spells(G,start,end):
    
    #First filter nodes
    nodeiter = G.nodes(data=True)      
    for (n,c) in nodeiter:
        nodemeta = []
        spells_to_keep = []
        for spell in c['spells']:
            if (start <= datetime.strptime(spell[0],"%Y/%m/%d") < end):
                spells_to_keep.append(spell)
        c['spells'] = spells_to_keep
        for action_key in cf.interaction_keys:
            if action_key in c:
                actions_to_keep = []
                for action in c[action_key]:
                    if (start <= datetime.strptime(action[1],"%Y/%m/%d") < end):
                        actions_to_keep.append(action)
                c[action_key] = actions_to_keep
                if len(actions_to_keep) == 0:
                    continue
                nodemeta.append(cf.interaction_types[action_key])                  
        if c['type'] == 'story':
            nodemeta.append('story')
        c['nodemeta'] = c['nodemeta'] + nodemeta
    
    #Do the same for edges
    edgeiter = G.edges(data=True)
    for (u,v,c) in edgeiter:
        edgemeta = []
        for action_key in cf.interaction_keys:
            if action_key in c and len(c[action_key]) > 0:
                for action in c[action_key]:
                    if (start <= datetime.strptime(action[1],"%Y/%m/%d") < end):                
                        edgemeta.append(cf.interaction_types[action_key])
        c['edgemeta'] = edgemeta
    
    return G
    

def calculate(G,windowstart,windowend):
    global unparsed_startdate
    global unparsed_enddate
    edges_to_remove = []    
    tag_edges = []
    tag_counts = {} #Holds counts of each of the tags      
    
    graph_copy = copy.deepcopy(G) #Need to deep copy to avoid screwing future iterations

    nodeiter = G.nodes(data=True)
    iter = G.edges(data=True)   

    for (u,v,c) in iter:
        edge_exists = False
        for intervals in c['spells']:

            if (windowstart <= datetime.strptime(intervals[0],"%Y/%m/%d") < windowend):
                edge_exists = True
                if G.nodes[u]["type"] == "story" and cf.create_story in G.nodes[u]:                        
                        #Node 'v' has created this story, add it to their nodemeta 
                        G.nodes[v]['nodemeta'] = ['story']
                elif G.nodes[v]["type"] == "story" and cf.create_story in G.nodes[v]:
                        #Node 'u' has created this story, add it to their nodemeta
                        G.nodes[u]['nodemeta'] = ['story']

        if edge_exists == False:
            edges_to_remove.append((u,v,c))
        elif G.nodes[u]["type"] == "tag" or G.nodes[v]["type"] == "tag":
            tag_edges.append((u,v,c))
            tagname = G.nodes[u]["name"] if G.nodes[u]["type"] == "tag" else G.nodes[v]["name"]
            graph_copy.nodes[u]["tags"].append(tagname)
            graph_copy.nodes[v]["tags"].append(tagname)
            if tagname not in tag_counts:
                tag_counts[tagname] = 0
            tag_counts[tagname] +=1  

    graph_copy.remove_edges_from(edges_to_remove)
    
    #We want to remove the tag edges because they shouldn't count in the k-core calculation 
    graph_copy.remove_edges_from((tag_edges))
    
    nodes_to_remove = []
    for (n,c) in nodeiter:
        graph_copy.nodes[n]['nodemeta'] = []    
        
        #Replace all apostrophes in story/commoner names 
        if c['type'] == 'story' or c['type'] == 'listing':
            graph_copy.nodes[n]['title'] = c['title'].replace("'","")
        else:
            graph_copy.nodes[n]['name'] = c['name'].replace("'","")
            
        node_exists = False
        graph_copy.nodes[n]['date'] = datetime.strftime(windowstart,"%Y/%m/%d")
        c['date'] = datetime.strftime(windowstart,"%Y/%m/%d")
        if 'spells' in c:
            for intervals in c['spells']:
                if (windowstart <= datetime.strptime(intervals[0],"%Y/%m/%d") < windowend):
                    node_exists = True
        if node_exists == False:
            nodes_to_remove.append(n)      
    graph_copy.remove_nodes_from(nodes_to_remove)

    #Get rid of spells and actions that fall outside the window range 
    graph_copy = filter_spells(graph_copy,windowstart,windowend)
    
    #Do the kcore calculations
    (core_graph,core_values) = dx.core_number_weighted(graph_copy,windowstart,windowend,True,False)

   

    #Add the tags back in
    core_graph.add_edges_from(tag_edges)


 
 

    
    nodeiter = core_graph.nodes(data=True)

    #Can add the k-core and page-rank stats here
    for (n,c) in nodeiter:
        core_graph.nodes[n]['kcore'] = core_values[n]
        #core_graph.nodes[n]['pagerank'] = page_rank[n]  
    #if loopcount > 0:
    core_graph = createEntityGraphs(core_graph,core_values)
    if loopcount == 0:
        nodeiter = core_graph.nodes(data=True)
        for (n,c) in nodeiter:
            if 'nodemeta' in c:
                c['nodemeta'] = ','.join(c['nodemeta'])
            if 'tags' in c:
                c['tags'] = ','.join(c['tags'])
        edgeiter = core_graph.edges(data=True)
        for (u,v,c) in edgeiter:
            if 'edgemeta' in c:
                c['edgemeta'] = ','.join(c['edgemeta'])
            last_time_activated = datetime.strptime(c['spells'][0][1],"%Y/%m/%d")
            for spell in c['spells']:
                if datetime.strptime(spell[1],"%Y/%m/%d") > last_time_activated:
                    last_time_activated = datetime.strptime(spell[1],"%Y/%m/%d")
            c['last_date'] = datetime.strftime(last_time_activated,"%Y/%m/%d")                 
                
        nx.write_gexf(core_graph,"newdata.gexf")
        tree = ET.parse("newdata.gexf")  
        root = tree.getroot()
        root[0].set('start',unparsed_startdate)
        root[0].set('end',unparsed_enddate)
        root[0].set('timeformat', 'date') 
        tree.write("newdata.gexf")      

    #Remove any isolated nodes that exist from removing Basic Income interactions 
    core_graph.remove_nodes_from(list(nx.isolates(core_graph)))
    core_graph_json = json_graph.node_link_data(core_graph)
    core_graph_json['date'] = datetime.strftime(windowstart,"%Y/%m/%d")
    tag_list = sorted(tag_counts.iteritems(),reverse=True, key=lambda (k,v): (v,k))
    core_graph_json['tagcount'] = tag_list
    
    with open('../web/data/graphdata/biweekly/biweekly'+ str(loopcount) +'.json', 'w') as outfile:
        outfile.write(json.dumps(core_graph_json))
    return core_graph
    
#Initialisation code            
loopcount = 0
commoner_graphs = {}
object_graphs = {}
filename = ""   
 
def init(file):
    global filename
    global unparsed_startdate
    global unparsed_enddate
    filename = file
    G_read = nx.read_gexf(filename)
    ET.register_namespace("", "http://www.gexf.net/1.2draft") 
    tree = ET.parse(filename)  
    root = tree.getroot()
    unparsed_startdate = root[0].attrib['start']
    unparsed_enddate = root[0].attrib['end']

    #Pass the start and end times of the file in
    createGraphs(G_read,datetime.strptime(unparsed_startdate,"%Y/%m/%d"),datetime.strptime(unparsed_enddate,"%Y/%m/%d"))  
   
if __name__ == "__main__":
    global filename
    if len(sys.argv) < 2:
        print 'Missing filename'
        sys.exit()
    filename = sys.argv[1]
    init(filename)