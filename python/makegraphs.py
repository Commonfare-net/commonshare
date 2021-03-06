import os
import json
import copy
import sys
import operator
import xml.etree.ElementTree as ET
from datetime import datetime
from dateutil.relativedelta import *
import community
import pagerank
import networkx as nx
from networkx.readwrite import json_graph

import config as cf
import kcore as dx
import gc

def make_all_graphs(G,startdate,enddate,spacing):     
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

    Note that the output directory is within this directory 
    (i.e., its path is python/data/output and not 
    commonshare/data/output). This is so that the Docker container
    can access the output files properly.
    
    :param G: NetworkX graph of all interactions across time 
    :param startdate: date of first interaction
    :param enddate: date of most recent interaction  
    :param spacing: string representing size of each time window
    (either 'weekly', 'biweekly' or 'monthly'

    """
    c_Gs = {}
    coms = []
    #Create dicts to hold the interaction data for each commoner    
    for (n,c) in G.nodes(data=True):
        if c['type'] == 'commoner':
            c_Gs[n] = []
        c["tags"] = []    
        
    if spacing == 'weekly':
        delta = relativedelta(weeks=-1)
    elif spacing == 'biweekly':
        delta = relativedelta(weeks=-2)
    else:
        delta = relativedelta(months=-1)
    graph_dir = cf.GRAPHDIR
    user_dir = cf.USERDIR
    
    #Make dates for first interaction 'window'
    w_end = enddate
    w_start = w_end+delta
    
    index = 1
    #Makes the windowed graphs
    while(w_end > startdate):
        (coms,c_Gs,json_G) = make_graphs(G,(w_start,w_end),index,coms,c_Gs)
        if not os.path.exists(graph_dir):
            os.makedirs(graph_dir)
        json_G['absolute_max'] = cf.MAX_WEIGHT
        with open(graph_dir + str(index) + '.json', 'w') as outfile:
            outfile.write(json.dumps(json_G))
        outfile.close()
        del json_G
        w_end = w_start
        w_start = w_end + delta
        index += 1

    #Make individual historic files for each commoner
    if not os.path.exists(user_dir):
        os.makedirs(user_dir)
    if spacing == 'biweekly':
        for k,v in c_Gs.items():
            if len(v) > 0:
                with open(user_dir + str(k) + '.json', 'w') as outfile:
                    outfile.write(json.dumps(v))  
                    outfile.close()                    
    
    #Make cumulative graph
    (coms,c_Gs,json_G) = make_graphs(G,(startdate,enddate),0,coms,None)
    dynamic_communities = {}
    
    
    for i in coms:
        if len(i) > 2:
            k_high = 0
            #Give cluster a name based on its most influential node
            for nodes in i:
                if type(nodes) is list:
                    for nodeid in nodes:
                        n = G.nodes[nodeid]
                        k = n['kcore']
                        if k >= k_high:# and n['type'] == 'commoner':
                            central_node = nodeid
                            k_high = k
            dynamic_communities[central_node + '_' + str(coms.index(i))] = i
    json_G['dynamic_comms'] = dynamic_communities 
    json_G['absolute_max'] = cf.MAX_WEIGHT    
    
    with open(graph_dir + '0.json', 'w') as outfile:
        outfile.write(json.dumps(json_G))
        outfile.close()


def build_commoner_data(G,commoner_graphs,nodes_to_remove):
    """Extract commoners' interaction histories. 

    This extracts the individual interactions of each commoner
    from the NetworkX graph, converts it to JSON and appends it 
    to their personal interaction history, represented in the 
    'commoner_graphs' dictionary 
    
    :param G: NetworkX graph of all interactions in a time window 
    :param commoner_graphs: dictionary mapping each commoner ID to
    their personal interaction history in JSON format
    :param nodes_to_remove: list of nodes not present in this time
    window (so that 0 values can be added to their JSON)

    """
    #Need to add 0 values in too
    for (n,c) in nodes_to_remove:
        c_graph = nx.Graph()
        if 'platform_id' in c:
            pid = c['platform_id']
        else:
            pid = str(n)
        c_graph.add_node(n,date=c['date'],kcore=0,platform_id=pid)
        commoner_json = json_graph.node_link_data(c_graph)
        #if 'platform_id' in c:
        commoner_json['commoner_id'] = pid
        commoner_graphs[n].append(commoner_json)
        
    nodeiter = copy.deepcopy(G.nodes(data=True))
    for (n,c) in nodeiter:
        if c['type'] != 'commoner':
            continue
        #Ignore commoners who have done nothing
        if 'kcore' not in G.nodes[n] or G.nodes[n]['kcore'] == 0:
            continue
            
        edges = G.edges(n,data=True)
        surrounding_nodes = G.neighbors(n)    
        
        #c_graph is the ego-centric graph of this commoner
        c_graph = nx.Graph()
        c_graph.add_node(n,**c)
        c_graph.nodes[n]['t'] = c_graph.nodes[n]['name']
        #Delete unnecessary info 
        del c_graph.nodes[n]['name']
        del c_graph.nodes[n]['spells']
        del c_graph.nodes[n]['tags']
        del c_graph.nodes[n]['label']
        if 'maxweight'  in c_graph.nodes[n]:
            del c_graph.nodes[n]['maxweight']
        #Add edges coming from this commoner
        #But remove specific interaction dates for efficiency
        c_graph.add_edges_from(edges)
        for k,v in iter(cf.INTERACTIONS.items()):
        #for action_key in cf.interaction_keys:
            if k in c_graph.nodes[n]:
                #print c_graph.nodes[n][action_key]
                c_graph.nodes[n][k] = [
                i[0] for i in c_graph.nodes[n][k]
                ] 

        #Add nodes these edges connect to with minimal info
        for node in surrounding_nodes:
            name = 'name' if 'name' in G.nodes[node] else 'title'
            nodetype = G.nodes[node]['type']
            c_graph.add_node(node,type=nodetype,t=G.nodes[node][name])

        #Other edges are drawn between added nodes
        #Again with minimal information
        all_edges = copy.deepcopy(G.edges(c_graph.nodes,data=True))
        for (u,v,x) in all_edges:
            if u in c_graph.nodes and v in c_graph.nodes:
                c_graph.add_edge(u,v,**x)
                for k,val in iter(cf.INTERACTIONS.items()):
                #for action_key in cf.interaction_keys:
                    if k in c_graph.edges[u,v]:
                        c_graph.edges[u,v][k] = [
                        i[0] for i in c_graph.edges[u,v][k]
                        ]
                del c_graph.edges[u,v]['spells']
                if 'weight'  in c_graph.edges[u,v]:
                    del c_graph.edges[u,v]['weight']
                if 'label' in c_graph.edges[u,v]:
                    del c_graph.edges[u,v]['label']
                if 'maxweight' in c_graph.edges[u,v]:
                    del c_graph.edges[u,v]['maxweight']
        commoner_json = json_graph.node_link_data(c_graph)
        if 'platform_id' in c:
            pid = c['platform_id']
        else:
            pid = str(n)
        #if 'platform_id' in c:
        commoner_json['commoner_id'] = pid
        commoner_graphs[n].append(commoner_json)
    
def filter_spells(G,window):
    """Remove all attributes outside time window from nodes/edges
    
    This removes all the spells and actions from the nodes and edges
    where they fall outside of the window slot. This makes
    JSON files much less bulky and easier to read

    :param G: NetworkX graph  
    :param window: 2-tuple containing start date and end date
    """
    #First, filter node spells/actions
    nodeiter = G.nodes(data=True)      
    for (n,c) in nodeiter:
        nodemeta = []
        spells_to_keep = []
        for spell in c['spells']:
            if cf.in_date(window,spell[0]):
                spells_to_keep.append(spell)
        c['spells'] = spells_to_keep
        
        for k,v in iter(cf.INTERACTIONS.items()):
        #for action_key in cf.interaction_keys:
            if k in c:
                actions_to_keep = []
                for action in c[k]:
                    if cf.in_date(window,action[1]):
                        actions_to_keep.append(action)
                c[k] = actions_to_keep
                if len(actions_to_keep) == 0:
                    continue
                #Add existing action to node's 'nodemeta'
                #nodemeta.append(cf.interaction_types[action_key])
                nodemeta.append(v[0])
        #If node is a story, its nodemeta always contains 'story'
        if c['type'] == 'story':
            nodemeta.append('story')
        c['nodemeta'] = c['nodemeta'] + nodemeta
    
    #Do the same for edges
    #TODO: Do edge spells need to be filtered too? 
    edgeiter = G.edges(data=True)
    for (u,v,c) in edgeiter:
        edgemeta = []
        for k,val in iter(cf.INTERACTIONS.items()):
        #for action_key in cf.interaction_keys:
            if k in c and len(c[k]) > 0:
                for action in c[k]:
                    if cf.in_date(window,action[1]):
                        #edgemeta.append(cf.interaction_types[action_key])
                        edgemeta.append(val[0])
        c['edgemeta'] = edgemeta
    
def make_recommender_data(G,window,tag_edges):
    """Make the GEXF used for recommending stories

    This takes the GEXF file containing every interaction over
    time and generates the 'recommenderdata.gexf' file, which
    is used by 'pagerank.py' to determine stories that should be
    recommended to users 
    
    It also makes the 'neglected_nodes' list, consisting of nodes
    with a degree < 2 and age < 50 days 
    
    :param G: NetworkX graph of all interactions across time 
    :param window: A 2-tuple containing the start and end dates
                   of the graph actions
    :param tag_edges: List of NetworkX edges to tag nodes
    
    """
    print ('making recommender data')
    nodeiter = G.nodes(data=True)
    neglected_nodes = []
    
    #Find new stories that have not received any attention yet
    G.remove_edges_from(tag_edges)        
    
    for (n,c) in nodeiter:   
        del c['nodemeta']
        del c['tags']
        #'neglected_nodes' = new stories with little interaction
        if G.degree[n] < 2 and c['type'] == 'story' and 'create_story' in c:
            created = cf.to_date(c['create_story'][0][1])
            if (datetime.now() - created).days < 50:
                neglected_nodes.append(n)
            
    edgeiter = G.edges(data=True)
    G.add_edges_from(tag_edges)
    
    for (u,v,c) in edgeiter:
        if 'edgemeta' in c:
            del c['edgemeta']
        #Find most recent activation of this edge (used for PageRank)
        updated = cf.to_date(c['spells'][0][1])
        for spell in c['spells']:
            if cf.to_date(spell[1]) > updated:
                updated = cf.to_date(spell[1])
        c['last_date'] = cf.to_str(updated)                 

    #create the 'recommenderdata.gexf' file for use by pagerank.py
    nx.write_gexf(G,"newdata.gexf")
    tree = ET.parse("newdata.gexf")  
    root = tree.getroot()
    root[0].set('neglected_nodes',' '.join(neglected_nodes))
    root[0].set('start',cf.to_str(window[0]))
    root[0].set('end',cf.to_str(window[1]))
    root[0].set('timeformat', 'date') 
    tree.write(cf.RECOMMEND_FILE)      
    os.remove("newdata.gexf")

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
    partition = community.best_partition(core_G,weight='edgeweight')      
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
                if similarity >= cf.COMMUNITY_SIM: 
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
    """
    edges_to_remove = []    
    tag_edges = []
    tag_nodes = {}
    tag_counts = {} #Holds counts of each of the tags      
    cumulative = (index == 0)
    create_count = 0
    comment_count = 0
    convo_count = 0
    trans_count = 0
    
    if index > 0:
        graph_copy = copy.deepcopy(G) #To avoid screwing future iterations        
    else:
        graph_copy = G
    nodeiter = G.nodes(data=True)
    edgeiter = G.edges(data=True)   

    #Filter edges outside time window and add count stats 
    for (u,v,c) in edgeiter:
        edge_exists = False
        
        for intervals in c['spells']:
            if (window[0] <= cf.to_date(intervals[0]) < window[1]):
                edge_exists = True
                        
        if edge_exists == False:
            edges_to_remove.append((u,v,c))
        else:
            #Find node that wrote story, add it to their 'nodemeta'        
            if G.nodes[u]["type"] == "story":
                if "create_story" in G.nodes[u]:                        
                    G.nodes[v]['nodemeta'] = ['story']
            elif G.nodes[v]["type"] == "story":
                if "create_story" in G.nodes[v]:
                    G.nodes[u]['nodemeta'] = ['story']     
                    
            #Count how many different edge types there are 
            if "create_story" in c:
                if cf.in_date(window,c["create_story"][0][1]):
                    create_count +=1
            if "comment_story" in c:
                for comment in c["comment_story"]:
                    if cf.in_date(window,comment[1]):
                        comment_count += 1
            if "conversation" in c:
                for convo in c["conversation"]:
                    if cf.in_date(window,convo[1]):
                        convo_count += 1
            if "transaction" in c:
                for trans in c["transaction"]:
                    if cf.in_date(window,trans[1]):
                        trans_count += 1

            #Special actions if the edge connects a node to a tag
            if G.nodes[u]["type"] == "tag" or G.nodes[v]["type"] == "tag":
                tag_edges.append((u,v,c))
                if G.nodes[u]["type"] == "tag":
                    tagname = G.nodes[u]["name"]
                else:
                    tagname = G.nodes[v]["name"]
                graph_copy.nodes[u]["tags"].append(tagname)
                graph_copy.nodes[v]["tags"].append(tagname)
                if tagname not in tag_counts:
                    tag_counts[tagname] = 0
                tag_counts[tagname] +=1  
    
    #Remove non-existent edges
    graph_copy.remove_edges_from(edges_to_remove)
    
    #Also remove the tag edges so not to influence k-core calculation
    graph_copy.remove_edges_from((tag_edges))
    
    #Filter nodes outside the time window
    nodes_to_remove = []
    zero_nodes = []
    for (n,c) in nodeiter:
        graph_copy.nodes[n]['nodemeta'] = []    
            
        node_exists = False
        graph_copy.nodes[n]['date'] = cf.to_str(window[0])
        c['date'] = cf.to_str(window[0]) #TODO: Do both lines need to be here?
        if 'spells' in c:
            for intervals in c['spells']:
                if cf.in_date(window,intervals[0]):
                    node_exists = True
        if node_exists == False:
            nodes_to_remove.append(n) 
            if c['type'] == 'commoner':
                zero_nodes.append((n,c))
    graph_copy.remove_nodes_from(nodes_to_remove)

    
    #Get rid of spells and actions that fall outside the window range 
    filter_spells(graph_copy,window)
    
    #DO THE KCORE CALCULATIONS HERE
    colluders = dx.weighted_core(graph_copy,window)

    #Add the tags back in
    graph_copy.add_edges_from(tag_edges)

    nodeiter = graph_copy.nodes(data=True)
    for (n,c) in nodeiter:
        if c['type'] == 'tag':
            tag_nodes[n] = c
    
    #Recommender data is built from the cumulative graph 
    if not cumulative:
        build_commoner_data(graph_copy,commoner_graphs,zero_nodes)
    else:
        print ('making rec data HERE')
        make_recommender_data(copy.deepcopy(graph_copy),window,tag_edges)

    #Remove isolated nodes that exist after removing Basic Income
    graph_copy.remove_nodes_from(list(nx.isolates(graph_copy)))

    #Give each edge the weight of its primary direction
    #TODO: Why not take into account other direction?
    iter = graph_copy.edges(data=True)
    for (u,v,c) in iter:
        if 'edgeweight' in c:
            c['edgeweight'] = c['edgeweight'][u]
        else:
            c['edgeweight'] = 1
        
    #Now compare fronts to previous partitions
    if not cumulative:
        partition = make_dynamic_communities(graph_copy,communities,index)
    else:
        partition = community.best_partition(graph_copy,weight='edgeweight')      

    #Simple counting of different node types
    c_count = 0
    s_count = 0
    t_count = 0
    l_count = 0
    nodeiter = graph_copy.nodes(data=True)
    for n,c in nodeiter:
        if c['type'] == 'commoner':
            c_count += 1
        elif c['type'] == 'story':
            s_count += 1
        elif c['type'] == 'tag':
            t_count += 1           
        elif c['type'] == 'listing':
            l_count += 1
        c['cluster'] = partition[n] 
            
    n_count = nx.number_of_nodes(graph_copy)
    e_count = nx.number_of_edges(graph_copy)
    core_graph_json = json_graph.node_link_data(graph_copy)
   # tags = sorted(iter(tag_counts.items()),reverse=True,key=lambda kv: (kv[1], kv[0]))
    tags = [(k, tag_counts[k]) for k in sorted (tag_counts, key=tag_counts.get, reverse=True)]   
    #Additional info about the graph itself
    meta_info = {
    'commoners':c_count,'stories':s_count,'listings':l_count,'tags':t_count,
    'create':create_count,'comment':comment_count,'convo':convo_count,
    'trans':trans_count,'nodenum':n_count,'edge_num':e_count,
    'tagcount':tags,'date':cf.to_str(window[1]),'colluders':colluders
                }            
    core_graph_json.update(meta_info)
    return (communities,commoner_graphs,core_graph_json)

    
def init(filename):
    """Read GEXF file and initiate graph creation.

    This reads and parses the GEXF data file, then 
    calls the 'make_all_graphs' method with three 
    different window lengths 
    
    :param filename: Path to the GEXF graph file

    """
    
    G_read = nx.read_gexf(filename)
    ET.register_namespace("", "http://www.gexf.net/1.2draft") 
    tree = ET.parse(filename)  
    root = tree.getroot()
    unparsed_startdate = root[0].attrib['start']
    unparsed_enddate = root[0].attrib['end']

    startdate = datetime.strptime(unparsed_startdate,"%Y/%m/%d")
    enddate = datetime.strptime(unparsed_enddate,"%Y/%m/%d")
    
    make_all_graphs(G_read,startdate,enddate,cf.SPACING)  
    
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print ('Missing filename')
        sys.exit()
    filename = sys.argv[1]
    init(filename)
