import networkx as nx
import dynetworkx as dx
from datetime import datetime
import config as cf
import json
from networkx.readwrite import json_graph
import copy
import sys
import xml.etree.ElementTree as ET
from dateutil.relativedelta import *

'''
This module does the necessary k-core calculations and appends the results to each node in the Graph.
Plotly functions now exist in 'kcoreplotly.py' as this generates data to be used in a D3 visualisation instead
'''

loopcount = 0
m_data_dict = {}
c_data_dict = {}
object_data_dict = {}
if len(sys.argv) < 2:
    print 'Missing filename'
    sys.exit()
filename = sys.argv[1]

G_read = nx.read_gexf(filename)
ET.register_namespace("", "http://www.gexf.net/1.2draft") 
tree = ET.parse(filename)  
root = tree.getroot()
startdate = root[0].attrib['start']
enddate = root[0].attrib['end']

#Pass the start and end times of the file in
calculate(G_read,datetime.strptime(startdate,"%Y/%m/%d"),datetime.strptime(enddate,"%Y/%m/%d"))

def getNodeStats(G,node_id):
    edges = G.edges(node_id,data=True)
    
    stats = {}
    #other_id = ""
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
                    if action[0] == str(node_id)or action_key in cf.mutual_interactions:
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
#https://stackoverflow.com/questions/22742754/finding-the-n-degree-neighborhood-of-a-node
def neighbourPaths(G, node):
    path_lengths = nx.shortest_path_length(G, node)
    all_paths = {}
    #return [(neighbour,distance) for neighbour,distance in path_lengths.iteritems() if distance <= n]
    for neighbour, length in path_lengths.iteritems():
        if length ==2:
            all_paths[neighbour] = [p[1] for p in nx.all_shortest_paths(G,node,neighbour)]
        elif length == 1:
            all_paths[neighbour] = []
    return all_paths

def addStats(G,D,PR,data_dict):
    global loopcount
    global m_data_dict
    global c_data_dict
    global object_data_dict
    nodeiter = G.nodes(data=True)
    #This adds the kcore value back into the GEXF
    

    for (n,c) in nodeiter:    
        if n not in D or D[n] == 0:
            NewG = nx.Graph()
            G.nodes[n]['kcore'] = 0
            G.nodes[n]['pagerank'] = 0
            G.nodes[n]['stats'] = {}
            NewG.add_node(n,**c)        
            #Here we append a blank fortnight for this commoner 
            if c['type'] == 'commoner':
                mdata = json_graph.node_link_data(NewG)
                data_dict[n].append(mdata)
        else:
        
            #If this is the all-time cumulative graph, for each user include all the nodes and surrounding edges
            if loopcount == 0 and data_dict != m_data_dict:
                #TWO DEGREES OF SEPARATION
                neighbours_and_inbetweens = neighbourPaths(G,n)

                surrounding_nodes = neighbours_and_inbetweens.keys()
                edges = G.edges(surrounding_nodes,data=True)
            else:
                edges = G.edges(n,data=True)
                surrounding_nodes = G.neighbors(n)
              
            NewG = nx.Graph()
            NewG.add_node(n,**c)
            NewG.nodes[n]['kcore'] = D[n]
            NewG.nodes[n]['pagerank'] = PR[n]
            NewG.nodes[n]['cumu_totals'] = {k:(v*D[n]) for k,v in c['cumu_totals'].items()}
            NewG.nodes[n]['avg_totals'] = {k:(v*D[n]) for k,v in c['avg_totals'].items()}
            NewG.nodes[n]['stats'] = getNodeStats(G,n)
            NewG.add_edges_from(edges)
            if loopcount == 0 and data_dict != m_data_dict:
                for node,inbetweens in neighbours_and_inbetweens.iteritems():
                    G.nodes[node]['kcore'] = D[node]
                    G.nodes[n]['pagerank'] = PR[n]
                    #Don't bother with the stats as it'll just start clogging things up
                    #G.nodes[node]['stats'] = getNodeStats(G,node)
                    G.nodes[node]['inbetweens'] = inbetweens
                    closeness = 0
                    for inbetweener in inbetweens:
                        if G.nodes[inbetweener]['type'] == 'commoner':
                            closeness = closeness + 3
                        elif G.nodes[inbetweener]['type'] == 'story':
                            closeness = closeness + 2
                        else:
                            closeness = closeness + 2
                    G.nodes[node]['closeness'] = closeness
                    NewG.add_node(node,**G.nodes[node])
            else:
                for node in surrounding_nodes:
                    G.nodes[node]['kcore'] = D[node]
                    G.nodes[node]['pagerank'] = PR[node]
                    G.nodes[node]['stats'] = getNodeStats(G,node)
                    NewG.add_node(node,**G.nodes[node])
            all_edges = G.edges(NewG.nodes,data=True)
            for (u,v,x) in all_edges:
                if u in NewG.nodes and v in NewG.nodes:
                    NewG.add_edge(u,v,**x)
            #NewG.add_node(n,**c)  
            if c['type'] == 'commoner':
                mdata = json_graph.node_link_data(NewG)
                data_dict[n].append(mdata)
            elif loopcount == 0 and data_dict != m_data_dict:
                mdata = json_graph.node_link_data(NewG)
                object_data_dict[n].append(mdata)
    
    return (G,data_dict)

def filteredges(G,start,end):
    edgeiter = G.edges(data=True)
    
    for (u,v,c) in edgeiter:
        edgemeta = []
        for action_key in cf.interaction_keys:
            if action_key in c and len(c[action_key]) > 0:
                for action in c[action_key]:
                    if (start <= datetime.strptime(action[1],"%Y/%m/%d") < end):                
                        edgemeta.append(cf.meta[action_key])
        c['edgemeta'] = edgemeta
    return G
    
            
def filternodes(G,start,end):
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
                nodemeta.append(cf.meta[action_key])                  

        if c['type'] == 'story':
            nodemeta.append('story')
        elif c['type'] == 'listing':
            nodemeta.append('listing')
        if 'nodemeta' not in c:
            c['nodemeta'] = nodemeta
        else:
            c['nodemeta'] = c['nodemeta'] + nodemeta
        
    return G
    

    
def calculate(G,startdate,enddate):     
    global loopcount
    global m_data_dict
    global c_data_dict
    global object_data_dict
    
    windowend = enddate
    windowstart = windowend+ relativedelta(weeks=-2)
    nodeiter = G.nodes(data=True)   
    commonercount = 0
    noncount = 0
    for (n,c) in nodeiter:
        if c['type'] == 'commoner':
            m_data_dict[n] = []
            c_data_dict[n] = []
            commonercount +=1
        else:
            object_data_dict[n] = []
            noncount +=1
        c["tags"] = []
    print 'commoners: ',commonercount,'. Non-commoners: ',noncount    
    #creation_edges = {}
          
    while(windowstart > startdate):
        mtagcounts = {}
        ctagcounts = {}
        print 'windowend is',datetime.strftime(windowend,"%Y/%m/%d")
        #Find edges which have a spell that started or ended within the bounds of a given hour/day
        #For those edges that didn't, remove them, then calculate the k-core
        mbunch = []
        cbunch = []
        mtagedges = []
        ctagedges = []
        
        #GCopy = SimpleGraph.copy()
        #Apparently the above doesn't deep copy node attributes that are lists. The documentation on this is confusing
        #as, supposedly, it's meant to be a deep copy of the graph by default. Instead, the below works just fine
        monthCopy = copy.deepcopy(G)
        cumuCopy = copy.deepcopy(G)

        iter = G.edges(data=True)
        for (u,v,c) in iter:
            monthCopy.nodes[u]['nodemeta'] = []
            monthCopy.nodes[v]['nodemeta'] = []
            cumuCopy.nodes[u]['nodemeta'] = []
            cumuCopy.nodes[v]['nodemeta'] = []
        

      #There's getting to be a lot of repetition in here but it works 
        for (u,v,c) in iter:
            monthedgeexists = False
            cumuedgeexists = False
            for intervals in c['spells']:

                if (windowstart <= datetime.strptime(intervals[0],"%Y/%m/%d") < windowend):
                    monthedgeexists = True
                    if G.nodes[u]["type"] == "story" and cf.create_story in G.nodes[u]:                        
                            #Node 'v' has created this story, add it to their nodemeta 
                            G.nodes[v]['nodemeta'] = ['story']
                    elif G.nodes[v]["type"] == "story" and cf.create_story in G.nodes[v]:
                            #Node 'u' has created this story, add it to their nodemeta
                            G.nodes[u]['nodemeta'] = ['story']
                
                if datetime.strptime(intervals[0],"%Y/%m/%d") < windowend:
                    cumuedgeexists = True
                    #DR No wait, so why don't I do the same thing here? 
                   
            if monthedgeexists == False:
                mbunch.append((u,v,c))
            elif G.nodes[u]["type"] == "tag" or G.nodes[v]["type"] == "tag":
                mtagedges.append((u,v,c))
                tagname = G.nodes[u]["name"] if G.nodes[u]["type"] == "tag" else G.nodes[v]["name"]
                monthCopy.nodes[u]["tags"].append(tagname)
                monthCopy.nodes[v]["tags"].append(tagname)
                if tagname not in mtagcounts:
                    mtagcounts[tagname] = 0
                mtagcounts[tagname] +=1
   
            if cumuedgeexists == False:
                cbunch.append((u,v,c))
            elif G.nodes[u]["type"] == "tag" or G.nodes[v]["type"] == "tag":
                ctagedges.append((u,v,c))
                tagname = G.nodes[u]["name"] if G.nodes[u]["type"] == "tag" else G.nodes[v]["name"]
                cumuCopy.nodes[u]["tags"].append(tagname)
                cumuCopy.nodes[v]["tags"].append(tagname)                
                if tagname not in ctagcounts:
                    ctagcounts[tagname] = 0
                ctagcounts[tagname] +=1                 
            
        monthCopy.remove_edges_from(mbunch)
        cumuCopy.remove_edges_from(cbunch)        
        
        #We want to remove the tag edges because they shouldn't count in the k-core calculation 
        monthCopy.remove_edges_from((mtagedges))
        cumuCopy.remove_edges_from((ctagedges))
        
        
        #Here a similar operation is done to remove nodes that do not exist at this point in time
        mbunch = []
        cbunch = []
        nodeiter = G.nodes(data=True)
        for (n,c) in nodeiter:
            if c['type'] == 'story' or c['type'] == 'listing':
                monthCopy.nodes[n]['title'] = c['title'].replace("'","")
            else:
                monthCopy.nodes[n]['name'] = c['name'].replace("'","")
            monthnodeexists = False
            cumunodeexists = False
            monthCopy.nodes[n]['date'] = datetime.strftime(windowstart,"%Y/%m/%d")
            cumuCopy.nodes[n]['date'] = datetime.strftime(windowstart,"%Y/%m/%d")
            c['date'] = datetime.strftime(windowstart,"%Y/%m/%d")
            if 'spells' in c:
                for intervals in c['spells']:
                    if (windowstart <= datetime.strptime(intervals[0],"%Y/%m/%d") < windowend):
                        monthnodeexists = True
                    if datetime.strptime(intervals[0],"%Y/%m/%d") < windowend:
                        cumunodeexists = True
            if monthnodeexists == False:
                mbunch.append(n)

            if cumunodeexists == False:
                cbunch.append(n)                
            
        monthCopy.remove_nodes_from(mbunch)
        cumuCopy.remove_nodes_from(cbunch)            
  
        #Go through them again, remove unnecessary actions and add 'meta-data' to nodes based on their remaining actions
        monthCopy = filternodes(monthCopy,windowstart,windowend)
        cumuCopy = filternodes(cumuCopy,datetime(1,1,1),windowend)
        monthCopy = filteredges(monthCopy,windowstart,windowend)
        cumuCopy = filteredges(cumuCopy,datetime(1,1,1),windowend)


        
        (MGraph,MD) = dx.core_number_weighted(monthCopy,windowstart,windowend,True,False)
        (CGraph,CD) = dx.core_number_weighted(cumuCopy,datetime(1,1,1),windowend,True,False)
        
        MMGraph = nx.MultiDiGraph()
        MMGraph.add_nodes_from(MGraph.nodes())
        for (u,v,c) in MGraph.edges(data=True):
            MMGraph.add_edge(u,v,**c)
            MMGraph.add_edge(v,u,**c)
        iter = MMGraph.edges(data=True)
        for (u,v,c) in iter:
            c['edgeweight'] = c['edgeweight'][u]
        mPageRank = nx.pagerank_numpy(MMGraph, alpha=0.85,weight='edgeweight')
        #cPageRank = nx.pagerank_numpy(MMGraph, alpha=0.85)
        #Add the tags back in
        MGraph.add_edges_from(mtagedges)
        #CGraph.add_edges_from(ctagedges)

        MGraph.remove_nodes_from(list(nx.isolates(MGraph)))
        #CGraph.remove_nodes_from(list(nx.isolates(CGraph)))

        (MGraph,m_data_dict) = addStats(MGraph,MD,mPageRank,m_data_dict)
        #(CGraph,c_data_dict) = addStats(CGraph,CD,cPageRank,c_data_dict)

        mdata = json_graph.node_link_data(MGraph)
        mdata['date'] = datetime.strftime(windowstart,"%Y/%m/%d")
        mtagcounts = sorted(mtagcounts.iteritems(),reverse=True, key=lambda (k,v): (v,k))
        mdata['tagcount'] = mtagcounts
        
        
        #cdata = json_graph.node_link_data(CGraph)
        #cdata['date'] = datetime.strftime(windowstart,"%Y/%m/%d")
        #ctagcounts = sorted(ctagcounts.iteritems(),reverse=True, key=lambda (k,v): (v,k))
        #cdata['tagcount'] = ctagcounts
        
        #Update the 'sliding window'
        windowend = windowstart
        windowstart = windowend + relativedelta(weeks=-2)

        loopcount = loopcount + 1

        with open('../web/data/graphdata/graphmonthly/monthdata'+str(loopcount)+'.json', 'w') as outfile:
            outfile.write(json.dumps(mdata))
        #with open('../web/data/graphdata/graphcumulative/cumudata'+str(loopcount)+'.json', 'w') as outfile:
        #    outfile.write(json.dumps(cdata))
            
    for k,v in m_data_dict.items():
        if len(v) > 0:
            with open('../web/data/userdata/usersmonthly/' + str(k) + '.json', 'w') as outfile:
                outfile.write(json.dumps(v))              
    #for k,v in c_data_dict.items():
    #    if len(v) > 0:
    #        with open('../web/data/userdata/userscumulative/' + str(k) + '.json', 'w') as outfile:
    #            outfile.write(json.dumps(v[0]))
    for k,v in object_data_dict.items():
        if len(v) > 0:
            with open('../web/data/objectdata/' + str(k) + '.json', 'w') as outfile:
                outfile.write(json.dumps(v[0]))        

