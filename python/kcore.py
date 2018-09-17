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

def addStats(G,D,data_dict):
    nodeiter = G.nodes(data=True)
    #This adds the kcore value back into the GEXF
    

    for (n,c) in nodeiter:
        if n not in D or D[n] == 0:
            NewG = nx.Graph()
            G.nodes[n]['kcore'] = 0
            G.nodes[n]['stats'] = {}
            
            NewG.add_node(n,**c)        
            #Here we append a blank fortnight for this commoner 
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
                if tagname not in mtagcounts:
                    mtagcounts[tagname] = 0
                mtagcounts[tagname] +=1
   
            if cumuedgeexists == False:
                cbunch.append((u,v,c))
            elif G.nodes[u]["type"] == "tag" or G.nodes[v]["type"] == "tag":
                ctagedges.append((u,v,c))
                tagname = G.nodes[u]["name"] if G.nodes[u]["type"] == "tag" else G.nodes[v]["name"]
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

  
        #Add the tags back in
        MGraph.add_edges_from(mtagedges)
        CGraph.add_edges_from(ctagedges)

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