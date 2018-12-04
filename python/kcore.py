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
import os
import community

'''
This module does the necessary k-core calculations and appends the results to each node in the Graph.
Plotly functions now exist in 'kcoreplotly.py' as this generates data to be used in a D3 visualisation instead
'''

def createGraphs(G,startdate,enddate,spacing):     
    global loopcount
    global commoner_graphs
    global object_graphs
    global dyn_index
    global dc
    global stepcoms    
    loopcount = 0
    nodeiter = G.nodes(data=True)    
    #Create dictionaries to hold the interaction data for individual commoners/objects
    for (n,c) in nodeiter:
        if c['type'] == 'commoner':
            commoner_graphs[n] = []
        else:
            object_graphs[n] = []
        c["tags"] = []    
        
    if spacing == 'weekly':
        delta = relativedelta(weeks=-1)
    elif spacing == 'biweekly':
        delta = relativedelta(weeks=-2)
    else:
        delta = relativedelta(months=-1)
        
    #Create new graph representing interactions within a two-week window
    windowend = enddate
    windowstart = windowend+delta
    
    loopcount += 1
    #Makes the fortnightly graphs
    while(windowend > startdate):
        print 'windowend is',datetime.strftime(windowend,"%Y/%m/%d")
        calculate(G,windowstart,windowend,spacing)
        windowend = windowstart
        windowstart = windowend + delta
        loopcount += 1

    #Make individual historic files for each commoner and each object (i.e., story, listing)
    directory = '../web/data/userdata/'
    if not os.path.exists(directory):
        os.makedirs(directory)
    for k,v in commoner_graphs.items():
        if len(v) > 0:
            with open('../web/data/userdata/' + str(k) + '.json', 'w') as outfile:
                outfile.write(json.dumps(v))   
    
    #Make cumulative graphs
    loopcount = 0
    G_new = calculate(G,startdate,enddate,spacing)
    
    #Reset dynamic communities
    dyn_index = 0
    dc = {}   
    stepcoms = {} 
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
                    
                    #Interactions also indexed by the date on which they occurred. This initialises necessary data structures 
                    if action[1] not in stats: #action[1] is the date of the interaction
                        stats[action[1]] = {}
                    if interaction_type not in stats[action[1]]:
                        stats[action[1]][interaction_type] = {}                            
                    if action_key not in stats[action[1]][interaction_type]:
                        stats[action[1]][interaction_type][action_key] = [1,cf.no_weights[action_key]]
                    else:
                        stats[action[1]][interaction_type][action_key][0] += 1 #Number of actions
                        stats[action[1]][interaction_type][action_key][1] += cf.no_weights[action_key] #Weight of actions    
                    stats[interaction_type][action_key].append(action)
    return stats

'''
This method creates the individual commoner/object graphs
'''
def createEntityGraphs(core_graph,core_values):
    global loopcount
    global commoner_graphs
    global object_graphs

    #Here 'entity_graph' refers to the graph of surrounding nodes of a particular commoner or object 
    nodeiter = copy.deepcopy(core_graph.nodes(data=True))
    for (n,c) in nodeiter:    
        if 'kcore' not in core_graph.nodes[n] or core_graph.nodes[n]['kcore'] == 0:
            continue
        else:
            edges = core_graph.edges(n,data=True)
            surrounding_nodes = core_graph.neighbors(n)    
            
            entity_graph = nx.Graph()
            entity_graph.add_node(n,**c)
            if 'title' in entity_graph.nodes[n]:
                entity_graph.nodes[n]['t'] = entity_graph.nodes[n]['title']
                del entity_graph.nodes[n]['title']
            else:
                entity_graph.nodes[n]['t'] = entity_graph.nodes[n]['name']
                del entity_graph.nodes[n]['name']
            del entity_graph.nodes[n]['spells']
            #del entity_graph.nodes[n]['date']
            del entity_graph.nodes[n]['tags']
            del entity_graph.nodes[n]['platform_id']
            del entity_graph.nodes[n]['maxweight']
            del entity_graph.nodes[n]['label']
            entity_graph.nodes[n]['kcore'] = core_values[n]
            entity_graph.nodes[n]['cumu_totals'] = {k:(v*core_values[n]) for k,v in c['cumu_totals'].items()}
            entity_graph.nodes[n]['avg_totals'] = {k:(v*core_values[n]) for k,v in c['avg_totals'].items()}
            #entity_graph.nodes[n]['stats'] = getNodeStats(core_graph,n)
            entity_graph.add_edges_from(edges)
            for action_key in cf.interaction_keys:
                if action_key in entity_graph.nodes[n]:
                   for i in range(len(entity_graph.nodes[n][action_key])):
                            entity_graph.nodes[n][action_key][i] = entity_graph.nodes[n][action_key][i][0] 
                        
            for node in surrounding_nodes:
                #core_graph.nodes[node]['stats'] = getNodeStats(core_graph,node)
                if 'name' in core_graph.nodes[node]:
                    entity_graph.add_node(node,type=core_graph.nodes[node]['type'],t=core_graph.nodes[node]['name'])
                else:
                    entity_graph.add_node(node,type=core_graph.nodes[node]['type'],t=core_graph.nodes[node]['title'])
            #Now that all relevant nodes have been added, need to make sure that appropriate edges are drawn between them 
            all_edges = copy.deepcopy(core_graph.edges(entity_graph.nodes,data=True))
            for (u,v,x) in all_edges:
                if u in entity_graph.nodes and v in entity_graph.nodes:
                    entity_graph.add_edge(u,v,**x)
                    for action_key in cf.interaction_keys:
                        if action_key in entity_graph.edges[u,v]:
                          for i in range(len(entity_graph.edges[u,v][action_key])):
                            entity_graph.edges[u,v][action_key][i] = entity_graph.edges[u,v][action_key][i][0] 
                    del entity_graph.edges[u,v]['spells']
                    del entity_graph.edges[u,v]['weight']
                    del entity_graph.edges[u,v]['label']
                    if 'maxweight' in entity_graph.edges[u,v]:
                        del entity_graph.edges[u,v]['maxweight']
                    
            if c['type'] == 'commoner' and loopcount > 0:
                commoner_json = json_graph.node_link_data(entity_graph)
                commoner_json['commoner_id'] = c['platform_id']
                commoner_graphs[n].append(commoner_json)
    
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
    
dyn_index = 0
dc = {}   
stepcoms = {} 
def calculate(G,windowstart,windowend,spacing):
    global unparsed_startdate
    global unparsed_enddate
    global dyn_index
    global dc
    global stepcoms
    edges_to_remove = []    
    tag_edges = []
    tag_nodes = {}
    tag_counts = {} #Holds counts of each of the tags      
    
    create_count = 0
    comment_count = 0
    convo_count = 0
    trans_count = 0
    graph_copy = copy.deepcopy(G) #Need to deep copy to avoid screwing future iterations

    nodeiter = G.nodes(data=True)
    iter = G.edges(data=True)   

    for (u,v,c) in iter:
        edge_exists = False
        
        for intervals in c['spells']:

            if (windowstart <= datetime.strptime(intervals[0],"%Y/%m/%d") < windowend):
                edge_exists = True
                if G.nodes[u]["type"] == "story" and cf.create_story in G.nodes[u]:                        
                        G.nodes[v]['nodemeta'] = ['story']
                elif G.nodes[v]["type"] == "story" and cf.create_story in G.nodes[v]:
                        #Node 'u' has created this story, add it to their nodemeta
                        G.nodes[u]['nodemeta'] = ['story']
        if edge_exists == False:
            edges_to_remove.append((u,v,c))
        else:
            if cf.create_story in c:
                if windowstart <= datetime.strptime(c[cf.create_story][0][1],"%Y/%m/%d") < windowend:
                    create_count +=1
            if cf.comment_story in c:
                for comment in c[cf.comment_story]:
                    if windowstart <= datetime.strptime(comment[1],"%Y/%m/%d") < windowend:
                        comment_count += 1
            if cf.conversation in c:
                for convo in c[cf.conversation]:
                    if windowstart <= datetime.strptime(convo[1],"%Y/%m/%d") < windowend:
                        convo_count += 1
            if cf.transaction in c:
                for trans in c[cf.transaction]:
                    if windowstart <= datetime.strptime(trans[1],"%Y/%m/%d") < windowend:
                        trans_count += 1
            if G.nodes[u]["type"] == "tag" or G.nodes[v]["type"] == "tag":
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
    is_cumulative = True if loopcount == 0 else False
    (core_graph,core_values,colluders) = dx.core_number_weighted(graph_copy,windowstart,windowend,is_cumulative)

    #Add the tags back in
    core_graph.add_edges_from(tag_edges)
    
    nodeiter = core_graph.nodes(data=True)
    neglected_nodes = []
    #Can add the k-core and page-rank stats here
    for (n,c) in nodeiter:
        core_graph.nodes[n]['kcore'] = core_values[n]
        if c['type'] == 'tag':
            tag_nodes[n] = c
    #if loopcount > 0:
    core_graph = createEntityGraphs(core_graph,core_values)
    if loopcount == 0:
        nodeiter = core_graph.nodes(data=True)
        core_graph.remove_edges_from(tag_edges)        #Get rid of tag edges so that they don't influence the story node degrees
        for (n,c) in nodeiter:
            if 'nodemeta' in c:
                c['nodemeta'] = ','.join(c['nodemeta'])
            if 'tags' in c:
                c['tags'] = ','.join(c['tags'])
            #We're calling 'neglected nodes' all stories that are less than a month old with little to no interactions
            if core_graph.degree[n] < 2 and c['type'] == 'story' and 'create_story' in c and (datetime.now() - datetime.strptime(c['create_story'][0][1],"%Y/%m/%d")).days < 50:
                neglected_nodes.append(n)
        edgeiter = core_graph.edges(data=True)
        core_graph.add_edges_from(tag_edges)
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
        root[0].set('neglected_nodes',' '.join(neglected_nodes))
        root[0].set('start',unparsed_startdate)
        root[0].set('end',unparsed_enddate)
        root[0].set('timeformat', 'date') 
        tree.write("newdata.gexf")      

    #Remove any isolated nodes that exist from removing Basic Income interactions 
    core_graph.remove_nodes_from(list(nx.isolates(core_graph)))

    iter = core_graph.edges(data=True)
    for (u,v,c) in iter:
        if 'edgeweight' in c:
            c['edgeweight'] = c['edgeweight'][u]
        else:
            c['edgeweight'] = 1
    stepcoms = {}
    #core_graph.remove_nodes_from(tag_nodes.keys())    

    #core_graph.remove_edges_from(tag_edges)        #Get rid of tag edges so that they don't influence the story node degrees
    #print 'AND NOW'
    #tag_based_isolates = list(nx.isolates(core_graph))
    #core_graph.remove_nodes_from(list(nx.isolates(core_graph))) #Actually now THIS will remove any nodes that are only there because they've tagged themselves    

    partition = community.best_partition(core_graph,weight='edgeweight')
    
            
    for k,v in partition.iteritems():
        if v not in stepcoms:
            stepcoms[v] = []
        stepcoms[v].append(k)

    print 'stepcomcounts be ',len(stepcoms)
    #Now compare fronts to previous step communities
    cdate = loopcount
    if loopcount > 0:
        if len(dc) == 0: #Bootstrapping
            for i in range(len(stepcoms)):
                dc[str(dyn_index)] = [cdate,stepcoms.values()[dyn_index]]
                dyn_index += 1
            fronts = {k:v[len(v)-1] for k,v in dc.iteritems()} 
        else:
            #Get most recent step community of each dynamic community
            fronts = {k:v[len(v)-1] for k,v in dc.iteritems()} 
            print 'front length be ',len(fronts)
            #Keep a record of how many new things have been appended onto a dynamic community
            #If it's more than one we need to split the community
            appendings = {k:0 for k in dc.keys()}
            
            #(stepcoms are the communities detected at this particular time step)
            for c_val in stepcoms.values():
                matching_coms = []
                for key,f_val in fronts.iteritems():
                    similarity = jaccard(f_val,c_val)
                    if similarity < 0.3:
                        continue
                    else:
                        matching_coms.append(key)
                if len(matching_coms) == 0: #Didn't find a matching dynamic community, best make a new one    
                    dc[str(dyn_index)] = [cdate,c_val]
                    dyn_index += 1
                else: #Two dynamic communities match this step community, do a merge?
                    for key in matching_coms:
                        dc[key].append(cdate)
                        dc[key].append(c_val)
                        appendings[key] += 1
      
    '''
    for u,v,c in tag_edges:
        if u in tag_based_isolates or v in tag_based_isolates:
            continue
        else:
            core_graph.add_edge(u,v,**c)
    #core_graph.add_edges_from(tag_edges)
    for k,v in tag_nodes.iteritems():
        if k in core_graph.nodes():
            core_graph.add_node(k,**v)   
    '''
    c_count = 0
    s_count = 0
    t_count = 0
    l_count = 0
    nodeiter = core_graph.nodes(data=True)
    for n,c in nodeiter:
        #if c['type'] != 'tag':
        c['cluster'] = partition[n]
        if c['type'] == 'commoner':
            c_count += 1
        elif c['type'] == 'story':
            s_count += 1
        elif c['type'] == 'tag':
            t_count += 1
            
        elif c['type'] == 'listing':
            l_count += 1
            
    #core_graph.remove_edges_from(tag_edges)        #Get rid of tag edges so that they don't influence the story node degrees  
    #core_graph.remove_nodes_from(tag_nodes.keys())
    num_nodes = nx.number_of_nodes(core_graph)
    num_edges = nx.number_of_edges(core_graph)

    #density = nx.density(core_graph)
    #for k,v in tag_nodes.iteritems():
    #    core_graph.add_node(k,**v)
    #core_graph.add_edges_from(tag_edges) 
    
    core_graph_json = json_graph.node_link_data(core_graph)
    core_graph_json['node_num'] = num_nodes
    core_graph_json['commoners'] = c_count
    core_graph_json['stories'] = s_count
    core_graph_json['listings'] = l_count
    core_graph_json['tags'] = t_count
    core_graph_json['create'] = create_count
    core_graph_json['comment'] = comment_count
    core_graph_json['convo'] = convo_count
    core_graph_json['trans'] = trans_count
    core_graph_json['edge_num'] = num_edges
    #core_graph_json['density'] = density          
    core_graph_json['date'] = datetime.strftime(windowend,"%Y/%m/%d")
    tag_list = sorted(tag_counts.iteritems(),reverse=True, key=lambda (k,v): (v,k))
    core_graph_json['tagcount'] = tag_list
    if loopcount == 0:
        dynamic_communities = {}
        for k,v in dc.iteritems():
            if len(v) > 2:
                highcore = 0;
                #Give this cluster a name based on the most high-profile node in it
                for nodes in v:
                    if type(nodes) is list:
                        for nodeid in nodes:
                            n = core_graph.nodes[nodeid]
                            nodecore = n['kcore']
                            if nodecore >= highcore:
                                central_node = n['title'].split()[0] if 'title' in n else n['name']
                                highcore = nodecore
                dynamic_communities[central_node + k] = v
        core_graph_json['dynamic_comms'] = dynamic_communities
    core_graph_json['colluders'] = colluders
    directory = '../web/data/graphdata/'+spacing+'/'
    if not os.path.exists(directory):
        os.makedirs(directory)
    with open('../web/data/graphdata/'+spacing+'/'+ str(loopcount) +'.json', 'w') as outfile:
        outfile.write(json.dumps(core_graph_json))
    return core_graph
           
loopcount = 0
commoner_graphs = {}
object_graphs = {}
filename = ""   

def jaccard(front,stepcommunity):
    intersection = list(set(stepcommunity) & set(front))
    union = list(set(stepcommunity) | set(front))
    similarity = float(len(intersection)) / float(len(union))
    return similarity

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
    #createGraphs(G_read,datetime.strptime(unparsed_startdate,"%Y/%m/%d"),datetime.strptime(unparsed_enddate,"%Y/%m/%d"),'weekly')  
    createGraphs(G_read,datetime.strptime(unparsed_startdate,"%Y/%m/%d"),datetime.strptime(unparsed_enddate,"%Y/%m/%d"),'biweekly')  
    #createGraphs(G_read,datetime.strptime(unparsed_startdate,"%Y/%m/%d"),datetime.strptime(unparsed_enddate,"%Y/%m/%d"),'monthly')  
   
if __name__ == "__main__":
    global filename
    if len(sys.argv) < 2:
        print 'Missing filename'
        sys.exit()
    filename = sys.argv[1]
    init(filename)