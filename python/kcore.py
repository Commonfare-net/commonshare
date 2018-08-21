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
                        #if other_id not in stats:
                        #    stats[other_id] = []
                        #print 'other_id: ',other_id
                        #stats[other_id].append((action_key,action[1]))
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
                        #if other_id not in stats:
                        #    stats[other_id] = []
                        #stats[other_id].append(("r" + action_key,action[1]))                            
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

def addStats(G,D,data_dict):
    nodeiter = G.nodes(data=True)
    #This adds the kcore value back into the GEXF
    

    for (n,c) in nodeiter:
        if n not in D or D[n] == 0:
            NewG = nx.Graph()
            G.nodes[n]['kcore'] = 0
            G.nodes[n]['stats'] = {}
            
            NewG.add_node(n,**c)        
           # print n,c
            if c['type'] == 'commoner':
                mdata = json_graph.node_link_data(NewG)
                data_dict[n].append(mdata)
        else:
            #print c
            edges = G.edges(n,data=True)
            NewG = nx.Graph()
            NewG.add_node(n,**c)
            NewG.nodes[n]['kcore'] = D[n]
            NewG.nodes[n]['cumu_totals'] = {k:(v*D[n]) for k,v in c['cumu_totals'].items()}
            NewG.nodes[n]['avg_totals'] = {k:(v*D[n]) for k,v in c['avg_totals'].items()}
            NewG.nodes[n]['stats'] = getNodeStats(G,n)
            NewG.add_edges_from(edges)
            for node in G.neighbors(n):
                G.nodes[node]['kcore'] = D[node]
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
    
    return (G,data_dict)

#Comment edges from commoner to commoner that are necessary for k-core calculation but clutter up the graph
commoner_comment_edges = []

def filteredges(G,start,end):
    global commoner_comment_edges
    edgeiter = G.edges(data=True)
    
    for (u,v,c) in edgeiter:
        edgemeta = []
        for action_key in cf.interaction_keys:
            if action_key in c and len(c[action_key]) > 0 and action_key not in cf.indirect_interactions:
                for action in c[action_key]:
                    if (start <= datetime.strptime(action[1],"%Y/%m/%d") < end):                
                        edgemeta.append(cf.meta[action_key])
            if action_key in c and len(c[action_key]) > 0 and action_key in cf.indirect_interactions and (G.nodes[u]['type'] != 'commoner' or G.nodes[v]['type'] != 'commoner'):
                for action in c[action_key]:
                    if (start <= datetime.strptime(action[1],"%Y/%m/%d") < end):                
                        edgemeta.append(cf.meta[action_key])
        c['edgemeta'] = edgemeta
        if G.nodes[u]['type'] == 'commoner' and G.nodes[v]['type'] == 'commoner' and ('transaction' not in edgemeta) and ('social' not in edgemeta):
            commoner_comment_edges.append((u,v,c))
    return G
    
            
def filternodes(G,start,end):
    nodeiter = G.nodes(data=True)      
    for (n,c) in nodeiter:
        nodemeta = []
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
    global commoner_comment_edges
    
    windowend = enddate
    windowstart = windowend+ relativedelta(weeks=-2)

    loopcount = 0
    
    
    m_data_dict = {}
    c_data_dict = {}
    nodeiter = G.nodes(data=True)   
    commonercount = 0
    noncount = 0
    for (n,c) in nodeiter:
        if c['type'] == 'commoner':
            m_data_dict[n] = []
            c_data_dict[n] = []
            commonercount +=1
        else:
            noncount +=1
        c["tags"] = []
    print 'commoners: ',commonercount,'. Non-commoners: ',noncount    
    creation_edges = {}
          
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
        included_objects = []
      #There's getting to be a lot of repetition in here but it works 
        for (u,v,c) in iter:
            monthedgeexists = False
            cumuedgeexists = False
            
            for intervals in c['spells']:

                if (windowstart <= datetime.strptime(intervals[0],"%Y/%m/%d") < windowend):
                    monthedgeexists = True
                    if G.nodes[u]["type"] == "story":
                        included_objects.append(u)
                        if cf.create_story in G.nodes[u]:
                            story_creator = str(G.nodes[u][cf.create_story][0][0])
                            creation_edges[u] = (u,story_creator,G.edges[u,story_creator])                            
                            G.nodes[v]['nodemeta'] = ['story']
                    elif G.nodes[v]["type"] == "story":
                        included_objects.append(v)     
                        if cf.create_story in G.nodes[v]:
                            story_creator = str(G.nodes[v][cf.create_story][0][0])
                            creation_edges[v] = (story_creator,v,G.edges[story_creator,v])
                            G.nodes[u]['nodemeta'] = ['story']
                
                if datetime.strptime(intervals[0],"%Y/%m/%d") < windowend:
                    cumuedgeexists = True
                
            if monthedgeexists == False:
                mbunch.append((u,v,c))
            elif G.nodes[u]["type"] == "tag":
                mtagedges.append((u,v,c))
                tagname = G.nodes[u]["name"]
                monthCopy.nodes[v]["tags"].append(tagname)
                if tagname not in mtagcounts:
                    mtagcounts[tagname] = 0
                mtagcounts[tagname] +=1
            elif G.nodes[v]["type"] == "tag":
                mtagedges.append((u,v,c))
                tagname = G.nodes[v]["name"]
                monthCopy.nodes[u]["tags"].append(G.nodes[v]["name"])      
                if tagname not in mtagcounts:
                    mtagcounts[tagname] = 0
                mtagcounts[tagname] +=1    
   
            if cumuedgeexists == False:
                cbunch.append((u,v,c))
            elif G.nodes[u]["type"] == "tag":
                ctagedges.append((u,v,c))
                tagname = G.nodes[u]["name"]
                cumuCopy.nodes[v]["tags"].append(tagname)
                if tagname not in ctagcounts:
                    ctagcounts[tagname] = 0
                ctagcounts[tagname] +=1                 
            elif G.nodes[v]["type"] == "tag":
                ctagedges.append((u,v,c))
                tagname = G.nodes[v]["name"]
                cumuCopy.nodes[u]["tags"].append(tagname) 
                if tagname not in ctagcounts:
                    ctagcounts[tagname] = 0
                ctagcounts[tagname] +=1 
            
        monthCopy.remove_edges_from(mbunch)
        cumuCopy.remove_edges_from(cbunch)
        
        
        
        monthCopy.remove_edges_from((mtagedges))
        cumuCopy.remove_edges_from((ctagedges))
        
        
        #Here a similar operation is done to remove nodes that do not exist at this point in time
        mbunch = []
        cbunch = []
        nodeiter = G.nodes(data=True)
        for (n,c) in nodeiter:
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
         
        commoner_comment_edges = [] 
        monthCopy = filteredges(monthCopy,windowstart,windowend)
        cumuCopy = filteredges(cumuCopy,datetime(1,1,1),windowend)

        monthCopy.remove_edges_from(monthCopy.selfloop_edges())        
        cumuCopy.remove_edges_from(cumuCopy.selfloop_edges())        
      

        (MGraph,MD) = dx.core_number_weighted(monthCopy,windowstart,windowend,True,False)
        (CGraph,CD) = dx.core_number_weighted(cumuCopy,datetime(1,1,1),windowend,True,False)

        
        #Add the tags back in
        MGraph.add_edges_from(mtagedges)
        CGraph.add_edges_from(ctagedges)

        #Now add the creation edges back in
        #Because whenever a story is interacted with, we want to put the original creator back in, in order to show this
        '''
        for node in included_objects:
            if node in creation_edges:
                if MGraph.has_edge(creation_edges[node][0],creation_edges[node][1]) == False:
                    creation_edges[node][2]['manually_added'] = 'true'
                creation_edges[node][2]['edgemeta'] = ['story']
                MGraph.add_edge(creation_edges[node][0],creation_edges[node][1],**creation_edges[node][2])
        '''
        #And finally remove the commoner-commoner commenting edges
        MGraph.remove_edges_from(commoner_comment_edges)
        CGraph.remove_edges_from(commoner_comment_edges)        
        
        (MGraph,m_data_dict) = addStats(MGraph,MD,m_data_dict)
        (CGraph,c_data_dict) = addStats(CGraph,CD,c_data_dict)


        
        mdata = json_graph.node_link_data(MGraph)
        mdata['date'] = datetime.strftime(windowstart,"%Y/%m/%d")
        mtagcounts = sorted(mtagcounts.iteritems(),reverse=True, key=lambda (k,v): (v,k))
        mdata['tagcount'] = mtagcounts
        
        
        cdata = json_graph.node_link_data(CGraph)
        cdata['date'] = datetime.strftime(windowstart,"%Y/%m/%d")
        ctagcounts = sorted(ctagcounts.iteritems(),reverse=True, key=lambda (k,v): (v,k))
        cdata['tagcount'] = ctagcounts
        
        #Update the 'sliding window'
        windowend = windowstart
        windowstart = windowend + relativedelta(weeks=-2)

        loopcount = loopcount + 1

        with open('../web/data/graphdata/graphmonthly/monthdata'+str(loopcount)+'.json', 'w') as outfile:
            outfile.write(json.dumps(mdata))
        with open('../web/data/graphdata/graphcumulative/cumudata'+str(loopcount)+'.json', 'w') as outfile:
            outfile.write(json.dumps(cdata))
            
    for k,v in m_data_dict.items():
        print 'k is ',k
        if len(v) > 0:
            with open('../web/data/userdata/usersmonthly/' + str(k) + '.json', 'w') as outfile:
                outfile.write(json.dumps(v))              
    for k,v in c_data_dict.items():
        if len(v) > 0:
            with open('../web/data/userdata/userscumulative/' + str(k) + '.json', 'w') as outfile:
                outfile.write(json.dumps(v))  
actions_dict = {}
for key in cf.interaction_keys:
    actions_dict[key] = []

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

#Pass the start and end times of the file in (which I have copied manually but there should be a way to do so automatically
calculate(G_read,datetime.strptime(startdate,"%Y/%m/%d"),datetime.strptime(enddate,"%Y/%m/%d"))