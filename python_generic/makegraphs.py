import os
import json
import csv
import copy
import sys
import operator
import shutil
import xml.etree.ElementTree as ET
from datetime import datetime
from dateutil.relativedelta import *

import community
import networkx as nx
from networkx.readwrite import json_graph

import config as cf
import kcore as dx

def make_all_graphs(G,startdate,enddate,spacing,filename):     
    """Generate all JSON files from NetworkX graph
    
    This method generates a JSON file for the cumulative
    graph of interactions, JSON files for interactions within
    each time window (determined by 'spacing' parameter) and 
    JSON files for each commoner that contains their interaction 
    history.
    Files are created in the 'data/output/' directory for each 
    'spacing' as follows:
    ---------------
    graphdata/*spacing*/0.json - JSON for all interaction data
    graphdata/*spacing*/1-X.json - JSON of interaction windows,
    with size dependent on the 'spacing' parameter
    userdata/1-X.json - JSON of each commoner's interaction
    history (filename corresponds to their commoner ID)

    :param G: NetworkX graph of all interactions across time 
    :param startdate: date of first interaction
    :param enddate: date of most recent interaction  
    :param spacing: string representing size of each time window
    (either 'weekly', 'biweekly' or 'monthly'

    """
    print ('filename is ',filename)
    c_Gs = {}
    coms = []
    #Create dicts to hold the interaction data for each commoner    
    for (n,c) in G.nodes(data=True):

        if 'type' not in c or c['type'] == cf.user_type:
            c_Gs[n] = []
        c["tags"] = []   
        c["times_active"] = 0
        c["binary_active"] = ""
    #Dynamic data
    print ('spacing is ',spacing)
    
    if startdate is not None:
        if spacing == 'hourly':
            delta = relativedelta(minutes=-60)
        elif spacing == 'daily':
            delta = relativedelta(days=-1)
        elif spacing == 'weekly':
            delta = relativedelta(weeks=-1)
        elif spacing == 'biweekly':
            delta = relativedelta(weeks=-2)
        elif spacing == 'monthly':
            delta = relativedelta(months=-1)
        else:
            delta = relativedelta(years=-1)
        graph_dir = cf.GRAPHDIR
        user_dir = cf.USERDIR
        
        #Make dates for first interaction 'window'
        w_end = enddate
        w_start = w_end+delta
        
        index = 1
        if os.path.exists(graph_dir):
            shutil.rmtree(graph_dir)
        #if not os.path.exists(graph_dir):
        os.makedirs(graph_dir)
        #Makes the windowed graphs
        while(w_end > startdate):
            print ('windowend is',cf.to_str(w_end))
            (coms,c_Gs,json_G,G_new) = make_graphs(G,(w_start,w_end),index,coms,c_Gs)    
            with open(graph_dir + str(index) + '.json', 'w') as outfile:
                outfile.write(json.dumps(json_G))
            w_end = w_start
            w_start = w_end + delta
            index += 1
        
        if os.path.exists(user_dir):
            shutil.rmtree(user_dir)
        #Make individual historic files for each commoner
        os.makedirs(user_dir)
        #if spacing == 'biweekly':
        for k,v in c_Gs.items():
            if len(v) > 0:
                with open(user_dir + str(k) + '.json', 'w') as outfile:
                    outfile.write(json.dumps(v))   
        
    else:
        graph_dir = cf.GRAPHDIR
        if not os.path.exists(graph_dir):
            shutil.rmtree(graph_dir)
        #if not os.path.exists(graph_dir):
        os.makedirs(graph_dir)
        
    #Make cumulative graph
    (coms,c_Gs,json_G,G_new) = make_graphs(G,(startdate,enddate),0,coms,None)
    
    dynamic_communities = {}
    
    for i in coms:
        if len(i) > 2:
            k_high = 0
            #Give cluster a name based on its most influential node
            for nodes in i:
                if type(nodes) is list:
                    for nodeid in nodes:
                        n = G_new.nodes[nodeid]
                        k = n['kcore']
                        if k >= k_high: #and n['type'] == cf.user_type:
                            #print n
                            central_node = nodeid#n['id']#['name']
                            k_high = k
            dynamic_communities[central_node + str(coms.index(i))] = i
    
    json_G['dynamic_comms'] = dynamic_communities   
    with open(graph_dir + '0.json', 'w') as outfile:
            #outfile.write(json.dumps(json_G))
            json.dump(json_G, outfile)



def build_commoner_data(G,commoner_graphs,nodes_to_remove):
    """Extract commoners' interaction histories. 

    This extracts the individual interactions of each commoner
    from the NetworkX graph, converts it to JSON and appends it 
    to their personal interaction history, represented in the 
    'commoner_graphs' dictionary 
    
    :param G: NetworkX graph of all interactions in a time window 
    :param commoner_graphs: dictionary mapping each commoner ID to
    their personal interaction history in JSON format

    """
    #Nee to add 0 values in too
    for (n,c) in nodes_to_remove:
        c_graph = nx.Graph()
        c_graph.add_node(n,date=c['date'],kcore=0)
        commoner_json = json_graph.node_link_data(c_graph)
        if 'platform_id' in c:
            commoner_json['commoner_id'] = c['platform_id']
        commoner_graphs[n].append(commoner_json)
        
    nodeiter = copy.deepcopy(G.nodes(data=True))
    for (n,c) in nodeiter:
        if 'type' in c and c['type'] != cf.user_type:
            continue
        #Ignore commoners who have done nothing
        if 'kcore' not in G.nodes[n] or G.nodes[n]['kcore'] == 0:
            continue
            
        edges = G.edges(n,data=True)
        surrounding_nodes = G.neighbors(n)    
        
        #c_graph is the ego-centric graph of this commoner
        c_graph = nx.Graph()
        c_graph.add_node(n,**c)
        vals_to_delete = []
        for val in c_graph.nodes[n]:
            if val != 'kcore' and val != 'id' and val != 'date' and val != 'times_active' and val != 'binary_active':
                vals_to_delete.append(val)
        for val in vals_to_delete:
            del c_graph.nodes[n][val]
                #print 'val is ',val
        if 'name' in c_graph.nodes[n]:
            c_graph.nodes[n]['t'] = c_graph.nodes[n]['name']
        #Delete unnecessary info 
            del c_graph.nodes[n]['name']
        #del c_graph.nodes[n]['spells']
        if 'tags' in c_graph.nodes[n]:
            del c_graph.nodes[n]['tags']
        if 'platform_id' in c_graph.nodes[n]:
            del c_graph.nodes[n]['platform_id']
        if 'label' in c_graph.nodes[n]:
            del c_graph.nodes[n]['label']
        if 'maxweight'  in c_graph.nodes[n]:
            del c_graph.nodes[n]['maxweight']
        #Add edges coming from this commoner
        #But remove specific interaction dates for efficiency
        #c_graph.add_edges_from(edges)
        for action_key in cf.interaction_keys:
            if action_key in c_graph.nodes[n]:
                #print c_graph.nodes[n][action_key]
                c_graph.nodes[n][action_key] = [
                i[0] for i in c_graph.nodes[n][action_key]
                ] 
        commoner_json = json_graph.node_link_data(c_graph)
        if 'platform_id' in c:
            commoner_json['commoner_id'] = c['platform_id']
        commoner_graphs[n].append(commoner_json)
    
def filter_spells(G,window):
    """Remove all attributes outside time window from nodes/edges
    
    This removes all the spells and actions from the nodes and edges
    where they fall outside of the window slot. This makes
    JSON files much less bulky and easier to read

    :param G: NetworkX graph  
    :param window: 2-tuple containing start date and end date
    :returns: Graph with only actions and spells in the time window
    """
    #First, filter node spells/actions
    nodeiter = G.nodes(data=True)      
    for (n,c) in nodeiter:
        nodemeta = []
        if 'spells' in c:
            del c['spells']
        vals_to_delete = []
        #Get rid of some unnecessaries that can clog the JSON files
        for val in c:
            if val != 'kcore' and val != 'id' and val != 'date' and val != 'times_active' and val != 'binary_active':
                vals_to_delete.append(val)
        for val in vals_to_delete:
            del c[val]
                #print 'val is ',val
        for action_key in cf.interaction_keys:
            if action_key in c:
                actions_to_keep = []
                for action in c[action_key]:
                    if cf.in_date(window,action[1]):
                        actions_to_keep.append(action)
                c[action_key] = actions_to_keep
                if len(actions_to_keep) == 0:
                    continue
                #Add existing action to node's 'nodemeta'
                nodemeta.append(cf.interaction_types[action_key])

    #Do the same for edges
    #TODO: Do edge spells need to be filtered too? 
    edgeiter = G.edges(data=True)
    for (u,v,c) in edgeiter:
        edgemeta = []
        for action_key in cf.interaction_keys:
        #for action_key in c:
            actions_to_keep = []       
            #if action_key in c and len(c[action_key]) > 0:
            if len(c[action_key]) > 0:
                for action in c[action_key]:
                    if len(action) == 1:
                        actions_to_keep = action
                        break
                    if cf.in_date(window,action[1]):
                        #edgemeta.append(cf.interaction_types[action_key])
                        actions_to_keep.append(action)
                c[action_key] = actions_to_keep
        c['edgemeta'] = edgemeta
    return G
    
def jaccard(front,stepcommunity):
    """Compute Jaccard similarity coefficient of two node groups
    
    This uses the Jaccard index statistic to determine whether
    one node group is similar enough to a previous node group to
    be part of the same dynamic community 
    
    :param front: list of NetworkX nodes at time t-1
    :param stepcommunity: list of NetworkX nodes at time t
    :returns: Jaccard similarity coefficient
    """
    intersection = list(set(stepcommunity) & set(front))
    union = list(set(stepcommunity) | set(front))
    similarity = float(len(intersection)) / float(len(union))
    return similarity    

def make_dynamic_communities(core_G,communities,index):
    """Compute new dynamic communities at a given time step.
    
    Algorithm to find communities that exist in the network
    across multiple time steps. At each time window, 'static'
    community detection is done with the Louvain algorithm from
    https://github.com/taynaud/python-louvain
    Then, the communities at this step are compared to those from
    the previous step. If they are similar enough, they become part
    of the same 'dynamic community'. For more detail, see this paper:
    
    D. Greene, D. Doyle and P. Cunningham, "Tracking the Evolution of
    Communities in Dynamic Social Networks," 2010 International 
    Conference on Advances in Social Networks Analysis and Mining, 
    Odense, 2010, pp. 176-183.  

    :param core_G: NetworkX graph of all interactions in time window
    :param communities: list of NetworkX node 'dynamic communities' 
    :param index: integer representing time step 
    :returns: dictionary mapping each node to its Louvain community
    """
    partitions = {}
    
    #Returns a dictionary pairing of node IDs to their community
    for (n,c) in core_G.nodes(data=True):
        c['positivemax'] = max(c['maxweight'],0)
    partition = community.best_partition(core_G,weight='positivemax')      
    #Swap node ID keys and community values around 
    for k,v in iter(partition.items()):
        if v not in partitions:
            partitions[v] = []
        partitions[v].append(k)
    
    if len(communities) == 0:
        for i in range(len(partitions)):
            communities.append([index,list(partitions.values())[i]])
        fronts = [com[len(com)-1] for com in communities] 
    else:
        #Get most recent snapshot of each dynamic community
        fronts = [com[len(com)-1] for com in communities]
        #partitions are communities detected at this time step
        for part in partitions.values():
            matches = []
            #Use Jaccard similarity to check for evolving communities
            for front in fronts:
                similarity = jaccard(front,part)
                if similarity >= 0.3: #Recommended threshold
                    matches.append(fronts.index(front))
            if len(matches) == 0: #No match community? Make new one    
                communities.append([index,part])
            else: #Append evolved community nodes
                for key in matches:
                    communities[key].append(index)
                    communities[key].append(part)
    return partition
 

def make_graphs(G,window,index,communities,commoner_graphs):
    """
    Generate JSON for NetworkX graph. Update commoner graphs.
    
    This method generates all necessary information from a NetworkX
    graph representation and returns it in a JSON format. It also 
    updates the 'dynamic communities' and individual commoner graphs
    (using make_dynamic_communities and build_commoner_data methods)
    
    :param G: NetworkX graph of interactions in time window 
    :param window: 2-tuple containing start and end dates 
    :param index: integer representing time step
    :param communities: list holding NetworkX dynamic communities 
    (filled in by make_dynamic_communities method) 
    :param commoner_graphs: dictionary mapping each commoner node to
    its interaction history (filled in by build_commoner_data method)
    :returns: tuple containing:
              1. Updated dynamic communities
              2. Updated commoner_graphs
              3. JSON representation of NetworkX graph
              4. Updated NetworkX graph 
    """
    edges_to_remove = []    
    tag_edges = []
    #tag_nodes = {}
    tag_counts = {} #Holds counts of each of the tags      
    cumulative = (index == 0)
    create_count = 0
    comment_count = 0
    convo_count = 0
    trans_count = 0
    
    graph_copy = copy.deepcopy(G) #To avoid screwing future iterations        
    nodeiter = G.nodes(data=True)
    edgeiter = G.edges(data=True)   

    #Filter edges outside time window and add count stats 
    for (u,v,c) in edgeiter:
        c['activations'] = []
        if window[0] is not None:
            edge_exists = False
            for intervals in c['spells']:
                if (window[0] <= cf.to_date(intervals[0]) < window[1]):
                    edge_exists = True
                    break
        else:
            edge_exists = True #Edge always exists in static network 
                     
        if edge_exists == False:
            edges_to_remove.append((u,v,c))
        else:
            copy_edge = graph_copy.edges[u,v]
            if window[0] is not None:
                copy_edge['first_active'] = copy_edge['spells'][0][0]
                copy_edge['last_active'] = copy_edge['spells'][len(copy_edge['spells'])-1][0]
            del graph_copy.edges[u,v]['spells']

    #Remove non-existent edges

    graph_copy.remove_edges_from(edges_to_remove)
       
    #Also remove the tag edges so not to influence k-core calculation
    graph_copy.remove_edges_from((tag_edges))

 
    #Filter nodes outside the time window
    nodes_to_remove = []
    zero_nodes = []
    if window[0] is not None:
        for (n,c) in nodeiter:
            graph_copy.nodes[n]['nodemeta'] = []    
            graph_copy.nodes[n]['date'] = cf.to_str(window[0])
            c['date'] = cf.to_str(window[0]) #TODO: Do both lines need to be here?
            if nx.is_isolate(graph_copy,n):
                nodes_to_remove.append(n) 
                G.nodes[n]['binary_active'] += "0"
                graph_copy.nodes[n]['binary_active'] += "0"                
                if 'type' not in c or c['type'] == cf.user_type:
                    zero_nodes.append((n,c))
            else:
                G.nodes[n]['times_active'] += 1
                graph_copy.nodes[n]['times_active'] += 1
                G.nodes[n]['binary_active'] += "1"
                graph_copy.nodes[n]['binary_active'] += "1"
                
        graph_copy.remove_nodes_from(nodes_to_remove)

       
        #Get rid of spells and actions that fall outside the window range 
        graph_copy = filter_spells(graph_copy,window)


                
    #DO THE KCORE CALCULATIONS HERE
    (core_G,colluders) = dx.weighted_core(graph_copy.to_undirected(),window,cumulative)

    #Add the tags back in
    core_G.add_edges_from(tag_edges)

    to_remove = []
    nodeiter = core_G.nodes(data=True)
    for (n,c) in nodeiter:
        if cf.user_type != '' and 'type' not in c: #If there are meant to be types but we can't find any
            to_remove.append(n)
    core_G.remove_nodes_from(to_remove)
    
    #Recommender data is built from the cumulative graph 
    if not cumulative:
        build_commoner_data(core_G,commoner_graphs,zero_nodes)

    #Remove isolated nodes that exist after removing Basic Income 
    core_G.remove_nodes_from(list(nx.isolates(core_G)))

    #Now compare fronts to previous partitions   
    if not cumulative:
        partition = make_dynamic_communities(core_G,communities,index)
    else:
        undirectedGraph = core_G.to_undirected()
        partition = community.best_partition(undirectedGraph,weight='positivemax') 
    
        
    nodeiter = core_G.nodes(data=True)
    for n,c in nodeiter:
        c['cluster'] = partition[n]
        if cf.LABEL_KEY != "":
            c['label'] = c[cf.LABEL_KEY]
        else:
            c['label'] = str(n)
    core_graph_json = json_graph.node_link_data(core_G)

    if window[1] is not None:
        meta_info = {'date':cf.to_str(window[1]),'colluders':colluders}
        core_graph_json.update(meta_info)
    return (communities,commoner_graphs,core_graph_json,core_G)

def init(filename,configfile):
    """Read GEXF file and initiate graph creation.
    
    This reads and parses the GEXF data file, then 
    calls the 'make_all_graphs' method with three 
    different window lengths 
    
    :param filename: Path to the GEXF graph file

    """
    
    with open(configfile, 'r') as csvfile:
        spamreader = csv.reader(csvfile, delimiter=',', quotechar='|')
        row = next(spamreader)
        
        if row[0].startswith('weight'):
            cf.WEIGHT_KEY = row[0].split("=")[1]
            print ('weight key is ',cf.WEIGHT_KEY)
            row = next(spamreader)
        if row[0].startswith('label'):
            cf.LABEL_KEY = row[0].split("=")[1]
            row = next(spamreader)
        if row[0].startswith('granularity'):
            granularity = row[0].split("=")[1]
        try:
            row = next(spamreader)
            if row[0].startswith('directed'):
                cf.DIRECTED = True
        except StopIteration as e:
            print ('finished')
    G_read = nx.read_gexf(filename)
    ET.register_namespace("", "http://www.gexf.net/1.2draft") 
    tree = ET.parse(filename)  
    root = tree.getroot()
    #Dynamic GEXF!
    if 'start' in root[0].attrib:
        unparsed_startdate = root[0].attrib['start']
        unparsed_enddate = root[0].attrib['end']
        try:
            startdate = datetime.strptime(unparsed_startdate,"%Y/%m/%d %H:%M")
            enddate = datetime.strptime(unparsed_enddate,"%Y/%m/%d %H:%M")
        except ValueError:
            delta = relativedelta(days=int(unparsed_enddate))
            startdate = datetime.now()
            enddate = startdate + delta
    else: #Static GEXF...
        startdate = None
        enddate = None
 
    filepath = filename.split(".")
    filename = filepath[len(filepath)-2]
    suffix = filename.split("/")
    if len(suffix) > 0:
        filename = suffix[len(suffix)-1]
    else:
        filename = suffix[0]
    make_all_graphs(G_read,startdate,enddate,granularity,filename)   
    

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print ('Missing filename')
        sys.exit()
    filename = sys.argv[1]
    if len(sys.argv) < 3:
        configfile = 'default.txt'
    else:
        configfile = sys.argv[2]
    init(filename,configfile)
