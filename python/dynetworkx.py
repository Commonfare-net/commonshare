import math
import config as cf
from datetime import datetime
import networkx as nx

FREQUENCY_THRESHOLD = 5
REPUTATION_THRESHOLD = 10
PERCENTAGE_THRESHOLD = 35
#Basic collusion checking algorithm
def check_collusion(G,n1,n2,n2_weight,starttime,endtime):
    if G.has_edge(n1,n2) == False:
        return False
    edge = G[n1][n2]
    edgeweight = 0
    frequency = 0
    for action_key in cf.interaction_keys:
        if action_key in edge:
            for action in edge[action_key]:
                if (starttime <= datetime.strptime(action[1],"%Y/%m/%d") < endtime):
                    edgeweight = edgeweight + cf.weights[action_key]
                    frequency = frequency + 1
    if frequency > FREQUENCY_THRESHOLD and ((edgeweight/n2_weight)*100) > PERCENTAGE_THRESHOLD:
        return True
    return False

'''
This method finds the weight corresponding to the interactions at the particular point in time
'''
def nodeweight_directed(G,node_id,starttime,endtime):
    network_globals = {}
    for meta in cf.meta_networks:
        network_globals[meta] = 0
    edges = G.edges(node_id,data=True)
    edgeweights = []
    
    for (u,v,c) in edges:
        depreciating_constant = 1.0 #One for now, but it should probably be smaller
        overallweight = 0
        for action_key in cf.interaction_keys:
            #Here we need to iterate over the actions and see who did them.
            if action_key in c:
                actions_to_keep = []
                for action in c[action_key]:
                    if (starttime <= datetime.strptime(action[1],"%Y/%m/%d") < endtime):
                        overallweight = overallweight + (cf.weights[action_key]*depreciating_constant)     
                        network_globals[cf.interaction_types[action_key]] += (cf.weights[action_key]*depreciating_constant)                          
                        actions_to_keep.append(action)
                c[action_key] = actions_to_keep #Doing it this way stops modification of the list during the loop process    
        
        if overallweight > 0:
            edgeweights.append(overallweight)
            #Adds the edge's weight as an attribute
            if 'edgeweight' not in c:
                c['edgeweight'] = {}
            c['edgeweight'][node_id] = overallweight
                
    if len(edgeweights) == 0:
        return (G,network_globals,0)
    mean = sum(edgeweights)/len(edgeweights)
    #normalize weights to mean
    norm = [(float(i)/mean)/(float(min(edgeweights))/mean) for i in edgeweights]
    return (G,network_globals,sum(norm))

#DJR Modified this method to return the modified graph for spitting out JSON
def core_number_weighted(G,starttime,endtime,directed,ignore_indirect):

    neighbors=G.neighbors
    degrees=G.degree()
    
    nodeweights = {}
    sumofedges = {}
    degrees = dict(G.degree())
    for k,v in degrees.items():
        (G,network_globals,directed_weight) = nodeweight_directed(G,k,starttime,endtime)
        G.nodes[k]['edgetotals'] = network_globals
        sum_edges = float(sum(network_globals.values()))
        sumofedges[k] = sum_edges                
        avg_edges = sum_edges / len(network_globals.keys())
        G.nodes[k]['cumu_totals'] = {e:((v/sum_edges) if sum_edges > 0 else 0) for e,v in G.nodes[k]['edgetotals'].items()}
        G.nodes[k]['avg_totals'] = {e:((v/avg_edges) if avg_edges > 0 else 0) for e,v in G.nodes[k]['edgetotals'].items()}
        #Here's where the weighting gets put in
        degrees[k] = int(math.sqrt(math.ceil(int(v) * directed_weight)))
        if directed_weight > REPUTATION_THRESHOLD: #Is this node particularly reputable?
            nodeweights[k] = directed_weight

    #Do the collusion check
    activenodes = list(nodeweights.keys())
    for i in activenodes:
        for j in activenodes:
            if (i != j) and check_collusion(G,i,j,nodeweights[j],starttime,endtime) and check_collusion(G,j,i,nodeweights[i],starttime,endtime):
                print i,'and',j,'might be colluding'
    
    #This bit is the k-core algorithm directly taken from the networkx module
    nodes=sorted(degrees,key=degrees.get)
    bin_boundaries=[0]
    curr_degree=0
    for i,v in enumerate(nodes):
        if degrees[v]>curr_degree:
            bin_boundaries.extend([i]*(degrees[v]-curr_degree))
            curr_degree=degrees[v]
    node_pos = dict((v,pos) for pos,v in enumerate(nodes))
    # initial guesses for core is degree
    core=degrees
    nbrs=dict((v,set(neighbors(v))) for v in G)
    for v in nodes:
        for u in nbrs[v]:
            if core[u] > core[v]:
                nbrs[u].remove(v)
                pos=node_pos[u]
                bin_start=bin_boundaries[core[u]]
                node_pos[u]=bin_start
                node_pos[nodes[bin_start]]=pos
                nodes[bin_start],nodes[pos]=nodes[pos],nodes[bin_start]
                bin_boundaries[core[u]]+=1
                core[u]-=1
                
                
    #Normalize from a scale of 0-10 because otherwise people who have done perfectly fine don't look like they've done much
    if len(core.values()) > 0:
        mincore = min(core.values())
        maxcore = max(core.values())
        if maxcore == mincore:
            maxcore = maxcore+1
        for k,v in core.items():
            if sumofedges[k] > 0:
                core[k] = int(math.ceil((float(v-mincore)/(maxcore-mincore))*9))+1
            else:
                core[k] = 0
    print 'and now'
    return (G,core)
 