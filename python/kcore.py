import networkx as nx
import dynetworkx as dx
import time
import math
import random
from datetime import datetime
from datetime import date
import config as cf
import json
from networkx.readwrite import json_graph
from collections import Counter
import os
import copy
import ast
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
    for (u,v,c) in edges:
       # if node_id == '37':
        #    print c
        for action_key in cf.interaction_keys:
            if action_key in c:
                meta = cf.meta[action_key]
                if meta not in stats:
                    stats[meta] = {}
                if action_key not in stats[meta]:
                    stats[meta][action_key] = []
                    stats[meta]["r"+action_key] = [] #This is the inverse (i.e. comment received, like received)
                for action in c[action_key]:
                        
                    if str(ast.literal_eval(action[0])[0]) == str(node_id)or action_key in cf.mutual_interactions:
                        #print str(node_id), " is " + str(ast.literal_eval(action[0])[0])
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
        if n not in D:
            c['kcore'] = 0
            c['stats'] = {}
            data_dict[n].append(c)
        elif D[n] == 0:
            c['kcore'] = 0
            c['stats'] = {}
            data_dict[n].append(c)                
        else:
            c['kcore'] = D[n]
            c['cumu_totals'] = {k:(v*D[n]) for k,v in c['cumu_totals'].items()}
            c['avg_totals'] = {k:(v*D[n]) for k,v in c['avg_totals'].items()}
            c['stats'] = getNodeStats(G,n)
            data_dict[n].append(c)
    return (G,data_dict)
 
def filteredges(G,start,end):
    network_globals = {}
    for meta in cf.meta_networks:
        network_globals[meta] = 0
    edgeiter = G.edges(data=True)
    
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
            if action_key in c and len(c[action_key]) > 0 and action_key in cf.indirect_interactions and (G.nodes[u]['type'] != 'User' or G.nodes[v]['type'] != 'User'):
                edgemeta.append(cf.meta[action_key])
                network_globals[cf.meta[action_key]] +=1
        c['edgemeta'] = edgemeta
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
                if action_key not in cf.indirect_interactions:
                    nodemeta.append(cf.meta[action_key])                  
                if action_key in cf.indirect_interactions and n in list(map(lambda x: str(ast.literal_eval(x[0])[0]), c[action_key])): 
                    nodemeta.append(cf.meta[action_key])
        if c['type'] == 'story':
            nodemeta.append('story')
        elif c['type'] == 'listing':
            nodemeta.append('listing')
        c['nodemeta'] = nodemeta
    return G
    
def calculate(G,startdate,enddate):  
    user_id = 0
    
    windowstart = startdate
    windowend = windowstart+ relativedelta(months=+1)
    yearwindowend = windowend + relativedelta(years=+1)
    loopcount = 0
    
    
    m_data_dict = {}
    y_data_dict = {}
    c_data_dict = {}
    nodeiter = G.nodes(data=True)      
    for (n,c) in nodeiter:
        m_data_dict[n] = []
        y_data_dict[n] = []
        c_data_dict[n] = []
        c["tags"] = []
        
    while(windowstart < enddate):
        mtagcounts = {}
        ytagcounts = {}
        ctagcounts = {}
        print 'windowstart is',datetime.strftime(windowstart,"%Y/%m/%d")
        #Find edges which have a spell that started or ended within the bounds of a given hour/day
        #For those edges that didn't, remove them, then calculate the k-core
        mbunch = []
        ybunch = []
        cbunch = []
        mtagedges = []
        ytagedges = []
        ctagedges = []
        #GCopy = SimpleGraph.copy()
        #Apparently the above doesn't deep copy node attributes that are lists. The documentation on this is confusing
        #as, supposedly, it's meant to be a deep copy of the graph by default. Instead, the below works just fine
        monthCopy = copy.deepcopy(G)
        cumuCopy = copy.deepcopy(G)
        yearCopy = copy.deepcopy(G)
        iter = G.edges(data=True)
      
      #There's getting to be a lot of repetition in here but it works 
        for (u,v,c) in iter:
            monthedgeexists = False
            yearedgeexists = False
            cumuedgeexists = False
            for intervals in c['spells']:
                if (windowstart <= datetime.strptime(intervals[0],"%Y/%m/%d") < yearwindowend):
                    yearedgeexists = True
                if (windowstart <= datetime.strptime(intervals[0],"%Y/%m/%d") < windowend):
                    monthedgeexists = True
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

                
            if yearedgeexists == False:
                ybunch.append((u,v,c))
            elif G.nodes[u]["type"] == "tag":
                ytagedges.append((u,v,c))
                tagname = G.nodes[u]["name"]          
                yearCopy.nodes[v]["tags"].append(tagname)
                if tagname not in ytagcounts:
                    ytagcounts[tagname] = 0
                ytagcounts[tagname] +=1                 
            elif G.nodes[v]["type"] == "tag":
                ytagedges.append((u,v,c))
                tagname = G.nodes[v]["name"]                
                yearCopy.nodes[u]["tags"].append(tagname) 
                if tagname not in ytagcounts:
                    ytagcounts[tagname] = 0
                ytagcounts[tagname] +=1 
                
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
        yearCopy.remove_edges_from(ybunch)
        cumuCopy.remove_edges_from(cbunch)
        
        monthCopy.remove_edges_from((mtagedges))
        yearCopy.remove_edges_from((ytagedges))
        cumuCopy.remove_edges_from((ctagedges))
        
        #Here a similar operation is done to remove nodes that do not exist at this point in time
        mbunch = []
        ybunch = []
        cbunch = []
        nodeiter = G.nodes(data=True)
        for (n,c) in nodeiter:
            monthnodeexists = False
            yearnodeexists = False
            cumunodeexists = False
            monthCopy.nodes[n]['date'] = datetime.strftime(windowstart,"%Y/%m/%d")
            yearCopy.nodes[n]['date'] = datetime.strftime(windowstart,"%Y/%m/%d")
            cumuCopy.nodes[n]['date'] = datetime.strftime(windowstart,"%Y/%m/%d")
            c['date'] = datetime.strftime(windowstart,"%Y/%m/%d")
            if 'spells' in c:
                for intervals in c['spells']:
                    if (windowstart <= datetime.strptime(intervals[0],"%Y/%m/%d") < yearwindowend):
                        yearnodeexists = True
                    if (windowstart <= datetime.strptime(intervals[0],"%Y/%m/%d") < windowend):
                        monthnodeexists = True
                    if datetime.strptime(intervals[0],"%Y/%m/%d") < windowend:
                        cumunodeexists = True
            if monthnodeexists == False:
                mbunch.append(n)
            if yearnodeexists == False:
                ybunch.append(n)
            if cumunodeexists == False:
                cbunch.append(n)                
        monthCopy.remove_nodes_from(mbunch)
        yearCopy.remove_nodes_from(ybunch)
        cumuCopy.remove_nodes_from(cbunch)            
  
        #Go through them again, remove unnecessary actions and add 'meta-data' to nodes based on their remaining actions
        monthCopy = filternodes(monthCopy,windowstart,windowend)
        yearCopy = filternodes(yearCopy,windowstart,yearwindowend)
        cumuCopy = filternodes(cumuCopy,datetime(1,1,1),windowend)
        '''
        if startdate == windowstart:
            print 'yes this is at the start'
            for (n,c) in nodeiter:
                if n == '45':
                    print 'n is',n
                    print 'c is',c
        '''            
        monthCopy = filteredges(monthCopy,windowstart,windowend)
        yearCopy = filteredges(yearCopy,windowstart,yearwindowend)
        cumuCopy = filteredges(cumuCopy,datetime(1,1,1),windowend)

        monthCopy.remove_edges_from(monthCopy.selfloop_edges())        
        yearCopy.remove_edges_from(yearCopy.selfloop_edges())        
        cumuCopy.remove_edges_from(cumuCopy.selfloop_edges())        
      
        #Have to remove the self-loops that have cropped up
        #GCopy.remove_edges_from(GCopy.selfloop_edges())
        (MGraph,MD) = dx.core_number_weighted(monthCopy,windowstart,windowend,True,False)
        (YGraph,YD) = dx.core_number_weighted(yearCopy,windowstart,yearwindowend,True,False)
        (CGraph,CD) = dx.core_number_weighted(cumuCopy,datetime(1,1,1),windowend,True,False)

        
        MGraph.add_edges_from(mtagedges)
        YGraph.add_edges_from(ytagedges)
        CGraph.add_edges_from(ctagedges)
        
        (MGraph,m_data_dict) = addStats(MGraph,MD,m_data_dict)
        (YGraph,y_data_dict) = addStats(YGraph,YD,y_data_dict)
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
        windowstart = windowend
        windowend = windowend + relativedelta(months=+1)
        if windowend > yearwindowend:
            ydata = json_graph.node_link_data(YGraph)
            ydata['date'] = datetime.strftime(windowstart,"%Y/%m/%d")
            ytagcounts = sorted(ytagcounts.iteritems(),reverse=True, key=lambda (k,v): (v,k))
            ydata['tagcount'] = ytagcounts
            with open('../web/data/graphdata/graphyearly/yeardata'+str(loopcount)+'.json', 'w') as outfile:
                outfile.write(json.dumps(ydata))
            yearwindowend = yearwindowend + relativedelta(years=+1)
        loopcount = loopcount + 1

        with open('../web/data/graphdata/graphmonthly/monthdata'+str(loopcount)+'.json', 'w') as outfile:
            outfile.write(json.dumps(mdata))
        with open('../web/data/graphdata/graphcumulative/cumudata'+str(loopcount)+'.json', 'w') as outfile:
            outfile.write(json.dumps(cdata))
            
    for k,v in m_data_dict.items():
        with open('../web/data/userdata/usersmonthly/' + str(k) + '.json', 'w') as outfile:
            outfile.write(json.dumps(v))              
    for k,v in y_data_dict.items():
        with open('../web/data/userdata/usersyearly/' + str(k) + '.json', 'w') as outfile:
            outfile.write(json.dumps(v)) 
    for k,v in c_data_dict.items():
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
namespaces={'xmlns': 'http://www.gexf.net/1.2draft'}
root = tree.getroot()
startdate = root[0].attrib['start']
enddate = root[0].attrib['end']

#Pass the start and end times of the file in (which I have copied manually but there should be a way to do so automatically
calculate(G_read,datetime.strptime(startdate,"%Y/%m/%d"),datetime.strptime(enddate,"%Y/%m/%d"))