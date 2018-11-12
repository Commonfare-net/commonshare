import math
import config as cf
from datetime import datetime
import networkx as nx
import matplotlib.pyplot as plt
from scipy import stats

FREQUENCY_THRESHOLD = 5
REPUTATION_THRESHOLD = 10
PERCENTAGE_THRESHOLD = 25
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
def nodeweight_directed(G,node_id,starttime,endtime,is_cumulative):
    network_globals = {}
    for meta in cf.meta_networks:
        network_globals[meta] = 0
    edges = G.edges(node_id,data=True)
    edgeweights = []
    
    if is_cumulative: #Will eventually replace all these with something nicer
        active_weeks = [0] * ((endtime - starttime).days / 7) # A list of 0s representing every week from this edge to the end
        for spell in G.nodes[node_id]['spells']:
            nodespell = datetime.strptime(spell[1],"%Y/%m/%d")
            index = ((nodespell-starttime).days / 7)-1
            active_weeks[index] = 1
        total_weeks_active = float(sum(active_weeks))

    maxweight = 0
    loopcount = 1
    influence = 0
    maxdays = (endtime - starttime).days
    for (u,v,c) in edges:
        depreciating_constant = 0.95 
        overallweight = 0.0
        
        if is_cumulative:
          
            spelldate = datetime.strptime(c['spells'][0][0],"%Y/%m/%d")
            active_weeks = [0] * ((endtime - spelldate).days / 7) # A list of 0s representing every week from this edge to the end
            for spell in G.nodes[v]['spells']:
                nodespell = datetime.strptime(spell[1],"%Y/%m/%d")
                if (nodespell - spelldate).days >= 7: #If this spell happened afterwards
                    index = ((nodespell-spelldate).days / 7)-1
                    active_weeks[index] = 1
            if len(active_weeks) > 0:
                influence = float(sum(active_weeks))/len(active_weeks)
            else:
                influence = 0
        for action_key in cf.interaction_keys:
            #Here we need to iterate over the actions and see who did them.
            if action_key in c:
                actions_to_keep = []
                for action in c[action_key]:
                    if (starttime <= datetime.strptime(action[1],"%Y/%m/%d") < endtime):
                        if node_id == action[0]:
                            edge_weight = cf.weights[action_key]
                        else:
                            edge_weight = cf.weights["r"+action_key]
                        actions_to_keep.append(action)
                            
                        tdelta = endtime - datetime.strptime(action[1],"%Y/%m/%d")
                        agefraction = math.exp(-(float(tdelta.days)/50))
                        overallweight = overallweight + (edge_weight*agefraction*depreciating_constant)     
                        network_globals[cf.interaction_types[action_key]] += (edge_weight*agefraction*depreciating_constant)                          
                        depreciating_constant = depreciating_constant*0.75
                c[action_key] = actions_to_keep #Doing it this way stops modification of the list during the loop process    
        
        if overallweight > 0:
        
            if is_cumulative:
                overallweight *= min(((math.exp(influence)-1) * math.sqrt(total_weeks_active) +0.1 ),1)
            edgeweights.append(overallweight)
            
            #Adds the edge's weight as an attribute
            if 'edgeweight' not in c:
                c['edgeweight'] = {}
                c['maxweight'] = overallweight
            c['edgeweight'][node_id] = overallweight
            c['maxweight'] = max(c['maxweight'],overallweight)
            maxweight = max(c['maxweight'],maxweight)
        G.nodes[u]['maxweight'] = c['maxweight'] if 'maxweight' not in G.nodes[u] else max(G.nodes[u]['maxweight'],c['maxweight'])
        G.nodes[v]['maxweight'] = c['maxweight'] if 'maxweight' not in G.nodes[v] else max(G.nodes[v]['maxweight'],c['maxweight'])
                
    if len(edgeweights) == 0:
        return (G,network_globals,0)

    return (G,network_globals,sum(edgeweights))
    
#DJR Modified this method to return the modified graph for spitting out JSON
def core_number_weighted(G,starttime,endtime,is_cumulative):

    neighbors=G.neighbors
    degrees=G.degree()
    
    nodeweights = {}
    sumofedges = {}
    degrees = dict(G.degree())
    for k,v in degrees.items():
        (G,network_globals,directed_weight) = nodeweight_directed(G,k,starttime,endtime,is_cumulative)

        G.nodes[k]['edgetotals'] = network_globals
        sum_edges = float(sum(network_globals.values()))
        sumofedges[k] = sum_edges                
        avg_edges = sum_edges / len(network_globals.keys())
        G.nodes[k]['cumu_totals'] = {e:((v/sum_edges) if sum_edges > 0 else 0) for e,v in G.nodes[k]['edgetotals'].items()}
        G.nodes[k]['avg_totals'] = {e:((v/avg_edges) if avg_edges > 0 else 0) for e,v in G.nodes[k]['edgetotals'].items()}

        degrees[k] = int(math.sqrt(int(v)) * directed_weight)
        if directed_weight > REPUTATION_THRESHOLD: 
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
                

    log_core = {k: v for k, v in core.iteritems() if v >0}
    data = stats.boxcox(log_core.values(), 0)

    loopcount = 0
    for k,v in log_core.iteritems():
        log_core[k] = data[loopcount]
        loopcount += 1
    
    for k,v in core.iteritems():
        if v == 0:
            log_core[k] = 0
    
    outliers_removed_core = {k: v for k, v in log_core.iteritems() if v >0}
    before_core = {k: v for k, v in core.iteritems() if v >0}

    '''
    #Normalize from a scale of 0-10 because otherwise people who have done perfectly fine don't look like they've done much
    if is_cumulative:
        fig, axs = plt.subplots(1, 2, sharey=False, tight_layout=True)
        axs[0].hist(outliers_removed_core.values(), 20)
        axs[1].hist(before_core.values(), 20)
        plt.show()
    '''    
    if len(log_core.values()) > 0:
        mincore = min(log_core.values())
        maxcore = max(log_core.values())
        if maxcore == mincore:
            maxcore = maxcore+1
        for k,v in log_core.iteritems():
            if sumofedges[k] > 0:
                log_core[k] = int(math.ceil((float(v-mincore)/(maxcore-mincore))*9))+1
            else:
                log_core[k] = 0
    return (G,log_core)
 