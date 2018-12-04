import math
import config as cf
from datetime import datetime
import networkx as nx
#import matplotlib.pyplot as plt
from scipy import stats

FREQUENCY_THRESHOLD = 5
#REPUTATION_THRESHOLD = 5
PERCENTAGE_THRESHOLD = 33
#Basic collusion checking algorithm
def check_collusion(G,n1,n2,n2_weight,starttime,endtime):
    if G.has_edge(n1,n2) == False:
        return False
    edge = G[n1][n2]
    edgeweight = 0
    frequency = 0
    print 'checking between ',n1,' and ',n2
    for action_key in cf.interaction_keys:
        if action_key in edge:
            for action in edge[action_key]:
                if (starttime <= datetime.strptime(action[1],"%Y/%m/%d") < endtime):
                    edgeweight = edgeweight + cf.weights[action_key]
                    frequency = frequency + 1
    #if frequency > FREQUENCY_THRESHOLD and ((edgeweight/n2_weight)*100) > PERCENTAGE_THRESHOLD:
    print 'edgeweight is ',edgeweight,' and overall weight is ',n2_weight
    if ((edgeweight/n2_weight)*100) > PERCENTAGE_THRESHOLD:
        return True
    return False

'''
This method finds the weight corresponding to the interactions at the particular point in time
'''
def nodeweight_directed(G,node_id,starttime,endtime,is_cumulative,nodeweights):
    network_globals = {}
    for meta in cf.meta_networks:
        network_globals[meta] = 0
    edges = G.edges(node_id,data=True)
    edgeweights = []
    
    
    #Find the total number of weeks this node has been active since the beginning of commonfare.net
    if is_cumulative: 
        active_weeks = [0] * ((endtime - starttime).days / 7) # A list of 0s representing every week from this edge to the end
        for spell in G.nodes[node_id]['spells']:
            #print spell        
            nodespell = datetime.strptime(spell[1],"%Y/%m/%d")
            index = ((nodespell-starttime).days / 7)-1
            active_weeks[index] = 1
        total_weeks_active = float(sum(active_weeks))

    maxweight = 0
    influence = 0
    flagged = False    
    for (u,v,c) in edges:
        depreciating_constant = 0.75 
        overallweight = 0.0
        
        if is_cumulative:
          
          #Estimate the 'influence' of this node. Look at every other node it connects to, and determine how many weeks since the connection
          #that this node has been active for. 
            spelldate = datetime.strptime(c['spells'][0][0],"%Y/%m/%d")
            active_weeks = [0] * ((endtime - spelldate).days / 7) # A list of 0s representing every week from this edge to the end
            for spell in G.nodes[v]['spells']:
                #print spell
                nodespell = datetime.strptime(spell[1],"%Y/%m/%d")
                if (nodespell - spelldate).days >= 7: #If this spell happened afterwards
                    index = ((nodespell-spelldate).days / 7)-1
                   # print 'index is ',index,' and length is ',len(active_weeks)
                   # print 'nodespell: ',nodespell,' and endtime: ',endtime
                    active_weeks[index] = 1
            if len(active_weeks) > 0:
                influence = float(sum(active_weeks))/len(active_weeks)
            else:
                influence = 0
        action_count = 0   
        

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
                        action_count += 1    

                        #Depreciate weight of the edge as a function of the number of days old it is. e^(-days/50) seems to work well. 
                        tdelta = endtime - datetime.strptime(action[1],"%Y/%m/%d")
                        agefraction = math.exp(-(float(tdelta.days)/50))
                        
                        #Also depreciate the value of subsequent interactions along the same edge by 25% each time
                        overallweight = overallweight + (edge_weight*agefraction*depreciating_constant)     
                        network_globals[cf.interaction_types[action_key]] += round((edge_weight*agefraction*depreciating_constant),2)                          
                        depreciating_constant = depreciating_constant*0.75
                c[action_key] = actions_to_keep #Doing it this way stops modification of the list during the loop process    
        
        if overallweight > 0:
        
            if is_cumulative:
                #Take the overall weight of this age and reduce it depending on the calculated influence of the edge, and the total weeks active of the node
                # Reduction value is (e^influence)-1 * square_root(weeks active) + 0.1, unless this value is > 1, otherwise no reduction takes place
                # The minimum reduction is when the influence is 0, and is equal to 0.1
                overallweight *= min(((math.exp(influence)-1) * math.sqrt(total_weeks_active) +0.1 ),1)
            else: #Otherwise we look at the number of actions taking place on this edge in the time period. If it's a lot, we are suspicious
                if action_count > 7:
                    flagged = True
                    print node_id,' had ',action_count,' actions! Wow!'
            edgeweights.append(overallweight)
            
            #Adds the edge's weight as an attribute
            if 'edgeweight' not in c:
                c['edgeweight'] = {}
                c['maxweight'] = overallweight
            c['edgeweight'][node_id] = round(overallweight,2)
            c['maxweight'] = round(max(c['maxweight'],overallweight),2)
            maxweight = max(c['maxweight'],maxweight)
        G.nodes[u]['maxweight'] = c['maxweight'] if 'maxweight' not in G.nodes[u] else max(G.nodes[u]['maxweight'],c['maxweight'])
        G.nodes[v]['maxweight'] = c['maxweight'] if 'maxweight' not in G.nodes[v] else max(G.nodes[v]['maxweight'],c['maxweight'])
    if len(edgeweights) == 0:
        return (G,network_globals,0)
    if flagged:
        nodeweights[node_id] = sum(edgeweights)
        print 'adding ',node_id,' to nodeweights'
    return (G,network_globals,sum(edgeweights))
    
#DJR Modified this method to return the modified graph for spitting out JSON
def core_number_weighted(G,starttime,endtime,is_cumulative):

    neighbors=G.neighbors
    degrees=G.degree()
    
    nodeweights = {}
    sumofedges = {}
    colluders = []
    degrees = dict(G.degree())
    for k,v in degrees.items():
        (G,network_globals,directed_weight) = nodeweight_directed(G,k,starttime,endtime,is_cumulative,nodeweights)

        G.nodes[k]['edgetotals'] = network_globals
        sum_edges = float(sum(network_globals.values()))
        sumofedges[k] = sum_edges                
        avg_edges = sum_edges / len(network_globals.keys())
        G.nodes[k]['cumu_totals'] = {e:(round((v/sum_edges),2) if sum_edges > 0 else 0) for e,v in G.nodes[k]['edgetotals'].items()}
        G.nodes[k]['avg_totals'] = {e:(round((v/avg_edges),2) if avg_edges > 0 else 0) for e,v in G.nodes[k]['edgetotals'].items()}

        #Different weighting algorithm used now - square root of node degree, multiplied by calculated weighting. 
        #This gives higher precedence to the calculated weight than the node degree itself, unlike previous calculation that gave equal precedence to both
        degrees[k] = int(math.sqrt(int(v)) * directed_weight)
        #print 'degrees of ',k, ' are ',degrees[k]
        #if directed_weight > REPUTATION_THRESHOLD: 
            #nodeweights[k] = directed_weight


    #Do the collusion check
    activenodes = list(nodeweights.keys())
    print 'nodweight keys are ',activenodes
    for i in activenodes:
        for j in activenodes:
            if (i != j) and check_collusion(G,i,j,nodeweights[j],starttime,endtime) and check_collusion(G,j,i,nodeweights[i],starttime,endtime):
                print i,'and',j,'might be colluding'
                colluders.append([i,j])
    
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
                

    #Output of k-core algorithm is a logarithmic distribution. Use SciPy's 'boxcox' function to do a log transformation with lambda=0
    #First 0 values need to be removed
    log_core = {k: v for k, v in core.iteritems() if v >0}
    data = stats.boxcox(log_core.values(), 0)

    #Then we add 0 values back in
    loopcount = 0
    for k,v in log_core.iteritems():
        log_core[k] = data[loopcount]
        loopcount += 1
    
    for k,v in core.iteritems():
        if v == 0:
            log_core[k] = 0
    
    #These are just for plotting evidence histograms
    outliers_removed_core = {k: v for k, v in log_core.iteritems() if v >0}
    before_core = {k: v for k, v in core.iteritems() if v >0}

    
    #Normalize from a scale of 0-10 because otherwise people who have done perfectly fine don't look like they've done much
    #if is_cumulative:
    ##    fig, axs = plt.subplots(1, 2, sharey=False, tight_layout=True)
    #    axs[0].hist(outliers_removed_core.values(), 20)
    #    axs[1].hist(before_core.values(), 20)
    #    plt.show()
        
    #Finally, normalise the output log-transform values on a scale of 1-10
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
    return (G,log_core,colluders)
 