import math
from datetime import datetime
import copy
import networkx as nx
from scipy import stats
#import matplotlib.pyplot as plt
import config as cf

def colluding(G,n1,n2,n1_weight,n2_weight,window):
    """Check if two nodes are colluding
    
    Basic collusion checking algorithm. Determines if actions from
    one node are greater than a threshold of the recipient node's
    overall weight
    
    Algorithm adapted from the following paper:
    H.Shen, Y.Lin, K.Sapra and Z.Li, "Enhancing Collusion Resilience
    in Reputation Systems," in IEEE Transactions on Parallel and 
    Distributed Systems, vol.27, no.8, pp.2274-2287, 1 Aug. 2016.
    
    :param G: NetworkX graph of all interactions in a time window 
    :param n1: string representing Node 1 ID
    :param n2: string representing Node 2 ID
    :param n1_weight: float, sum of edge weights of Node 1
    :param n2_weight: float, sum of edge weights of Node 2
    :param window: 2-tuple of start and end dates of time window
    :returns: bool, True if strong suspicion of collusion. 
    """
    if n1 == n2:
        return False
    if G.has_edge(n1,n2) == False:
        return False
    edge = G[n1][n2]
    edgeweight = 0
    frequency = 0
    if 'edgeweight' in G[n1][n2]:
        edgeweight = G[n1][n2]['edgeweight'][n1]
    else:
        for action_key in cf.interaction_keys:
            if action_key in edge:
                for action in edge[action_key]:
                    if cf.in_date(window,action[1]):
                        edgeweight = edgeweight + cf.weights[action_key][0]
                        frequency = frequency + 1
    if n1_weight == 0:
        n_weight = n2_weight
    elif n2_weight == 0:
        n_weight = n1_weight
    else:
        n_weight = min(n1_weight,n2_weight)
    return ((edgeweight/n_weight)*100) > cf.PERCENTAGE_THRESHOLD

def nodeweight(G,node_id,window,suspect_nodes,cumulative):
    """Calculate weight of a node in the interactions graph.
    
    This calculates a node's 'weight' by looking at the 
    number, type, and date of interactions with other nodes 
    in the graph. 

    :param G: NetworkX graph of all interactions in a time window 
    :param node_id: string ID of node to determine weight of 
    :param window: 2-tuple with start and end dates of time window 
    :param suspect_nodes: dictionary mapping node ID's of high
    activity to their overall weight 
    """
    
    #If there are no interaction types, check if there are built-in weights

    #This holds the contribution of each type of action to
    #the node's overall weight 
   
    action_weights = {}
    for meta in cf.meta_networks:
        action_weights[meta] = 0
    edges = G.edges(node_id,data=True)
    edgeweights = []
    active_weeks = None
    
    if window[0] is not None:
        total_weeks_active = G.nodes[node_id]['times_active']
    else:
        total_weeks_active = None
    maxweight = 0
    influence = 0
    flagged = False    
    for (u,v,c) in edges:
        initiated = 0
        #Constant used to decrease the 'value' of multiple interactions
        #between the same two nodes
        depreciating_constant = 0.75 
        if 'initiator' in c:
            for edgey in c['initiator']:
                if edgey[0] == node_id:
                    initiated += 1
        overallweight = 0.0
        #We already have the edge weight, no need to do it manually
        #HOWEVER we have to separate it from the node ID
        if cf.WEIGHT_KEY in c:
            #However it might just be a float if it's an undirected graph
            try:
                for some_weight in c[cf.WEIGHT_KEY]:
                    if not cf.in_date(window,some_weight[1]):
                        continue
                    sourceweight = c[cf.WEIGHT_KEY][0]
                    if cf.DIRECTED == False:
                        targetweight = sourceweight
                    else:
                        targetweight = None if len(c[cf.WEIGHT_KEY]) == 1 else c[cf.WEIGHT_KEY][1]
                    #If A rates B 5 and B rates A 2, it's stored as [A/5,B/2]
                    if sourceweight[0].split('/')[0] == node_id:
                        if targetweight == None:
                            overallweight += 0
                        else:
                            overallweight += float(targetweight[0].split('/')[1])
                    else:
                        overallweight += float(sourceweight[0].split('/')[1])
                    break
            except TypeError:
                overallweight = c[cf.WEIGHT_KEY]
            #So it has to be done like this. There is probably a better way
            #But I do not care right now.
            #This seems more complicated than it ought to be 
            
        #This happens when things are static
        elif total_weeks_active is None:
            overallweight = 1
            
        else:
            if cumulative:
              #Estimate the 'influence' of this node. 
              #For each neighbour node, determine its activity
              #since connecting with this node
                spelldate = cf.to_date(c['first_active'])
                after_weeks = ((window[1] - spelldate).days / 7)
                count = 0
                active_count = 0
                for x in reversed(G.nodes[v]['binary_active']):
                    if count == after_weeks:
                        break
                    else:
                        active_count += float(x)
                        count +=1
                if after_weeks > 0:
                    influence = active_count / after_weeks
                else:
                    influence = 0
            action_count = 0   
            
            #Iterate over all actions between two nodes. Increment the 
            #overall edge weight based on the type and date of the action
            for action_key in cf.interaction_keys:
                
                if action_key not in c:
                    continue 
                actions_to_keep = []
                for action in c[action_key]:
                    if not cf.in_date(window,action[1]):
                        continue 
                    if node_id == action[0].split("-")[0]: #Node initiated the action
                        edge_weight = cf.weights[action_key][0]
                    else: #This node was the recipient of the action
                        edge_weight = cf.weights[action_key][1]
                    actions_to_keep.append(action)
                    action_count += 1    
                    '''
                    Depreciate weight of the edge as a function of 
                    the number of days old it is. 
                    e^(-days/50) seems to work well. 
                    '''
                    tdelta = window[1] - cf.to_date(action[1])
                    agefraction = math.exp(-(float(tdelta.days)/50))
                    '''
                    Also depreciate the value of subsequent 
                    interactions along the same edge by 25% each time
                    '''
                    overallweight = (overallweight 
                    + (edge_weight*agefraction*depreciating_constant)) 
                  
                    '''
                    Also store the contribution to this edge's weight of
                    each different action type involved
                    '''
                    action_weights[cf.interaction_types[action_key]] \
                    += round((edge_weight*agefraction*depreciating_constant),2)                          
                    
                    depreciating_constant = depreciating_constant*0.75
                c[action_key] = actions_to_keep     
                
            if overallweight == 0:
                #Some new trickery here to give the edge a weight based on
                #the 'initiator' attvalues (if nothing else is there
                for edgey in c['initiator']:
                    if edgey[0] == node_id:
                        overallweight += 0
                    else:
                        overallweight += 3
            if cumulative:
                '''
                Reduce edgeweight based on its influence and
                weeks active of the node. Reduction value = 
                (e^influence)-1 * square_root(weeks active) + 0.1
                Minimum reduction = 0.1 when influence is 0
                '''
                overallweight *= min(((math.exp(influence)-1)
                * math.sqrt(total_weeks_active) +0.1),1)
            else: #'flag' a node if it has been particularly active 
                if action_count > 7 or ('initiator' in c and len(c['initiator']) > 7): 
                    flagged = True
                    
        edgeweights.append(overallweight)
        #Adds the edge's weight as an attribute
        if 'edgeweight' not in c:
            c['edgeweight'] = {}
            c['initiated'] = {}
            c['maxweight'] = overallweight
        c['edgeweight'][node_id] = round(overallweight,2)
        c['initiated'][node_id] = initiated
        c['maxweight'] = round(max(c['maxweight'],overallweight),2)
        maxweight = max(c['maxweight'],maxweight)
        
        if 'maxweight' not in G.nodes[u]:
            G.nodes[u]['maxweight'] = c['maxweight']
        G.nodes[u]['maxweight'] = max(G.nodes[u]['maxweight'],c['maxweight'])

        if 'maxweight' not in G.nodes[v]:
            G.nodes[v]['maxweight'] = c['maxweight']
        G.nodes[v]['maxweight'] = max(G.nodes[v]['maxweight'],c['maxweight'])

    if len(edgeweights) == 0:
        return (G,action_weights,0,False)
        
    if flagged: #High activity node, add it to dictionary 
        suspect_nodes[node_id] = sum(edgeweights)
        
    return (G,action_weights,sum(edgeweights),True)
    

def weighted_core(G,window,cumulative):
    """Compute weighted k-core for each node in a graph
    
    This extends the standard NetworkX k-core calculation method 
    by weighting each node based on its platform interactions, 
    performing a log-transformation and normalising the final value 
    to an integer between 1 and 10

    :param G: NetworkX graph of all interactions in a time window
    :param window: 2-tuple of start and end dates of time window 
    :returns: 2-tuple containing graph updated with k-core values for
     each node, and a list of potential colluding nodes 
    """

    neighbors=G.neighbors
    suspect_nodes = {}
    sumofedges = {}
    colluders = []
    degrees = dict(G.degree())
    edgeiter = G.edges(data=True)   

    #Filter edges outside time window and add count stats 

    for k,v in degrees.items():
        #Compute the new node weight here
        #Also return 'action_weights' that holds node weight relevant
        #to each different action type 
        (G,action_weights,weight,weighted) = nodeweight(G,k,window,suspect_nodes,cumulative)
        G.nodes[k]['edgetotals'] = action_weights
        if len(action_weights) == 0:
            if v == 0:
                sumofedges[k] = 0
            else:
                sumofedges[k] = 1
        else:
            e_sum = float(sum(action_weights.values()))
            sumofedges[k] = e_sum                
            e_avg = e_sum / len(action_weights.keys())
            
            #Convert action weights to values with sum = node's weight 
            G.nodes[k]['cumu'] = {e:(round((v/e_sum),2) if e_sum > 0 else 0) 
            for e,v in G.nodes[k]['edgetotals'].items()}
            
            #Convert action weights to values with average = node's weight 
            G.nodes[k]['avg'] = {e:(round((v/e_avg),2) if e_avg > 0 else 0) 
            for e,v in G.nodes[k]['edgetotals'].items()}
        
        #Compute node's new 'degree' as function of its computed weight
        if weighted == True:
            degrees[k] = max(0,int(math.sqrt(int(v)) * weight))
        else:
            degrees[k] = int(v)

    #Do a collusion check
    activenodes = list(suspect_nodes.keys())
    for i in activenodes:
        for j in activenodes:
            if colluding(G,i,j,suspect_nodes[i],suspect_nodes[j],window): 
                colluders.append([i,j])
    
    #This is the k-core algorithm verbatim from the networkx module
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
                
    '''
    Output of k-core algorithm is logarithmic distribution. 
    Use 'boxcox' to do log transformation with lambda=0
    First, 0 values need to be removed
    '''
    if window[0] is None or cumulative:
       
        log_core = {k: v for k, v in iter(core.items()) if v >0}
        data = stats.boxcox(list(log_core.values()), 0)

        #Then we add 0 values back in
        loopcount = 0
        for k,v in iter(log_core.items()):
            log_core[k] = data[loopcount]
            loopcount += 1
        for k,v in iter(core.items()):
            if v == 0:
                log_core[k] = 0
        #These are just for plotting evidence histograms
        outliers_removed_core = {k: v for k, v in iter(log_core.items()) if v >0}
        before_core = {k: v for k, v in iter(core.items()) if v >0}
    else:
        outliers_removed_core = {k: v for k, v in iter(core.items()) if v >0}
        log_core = before_core = core
    
    #I feel that this normalisation goes from one extreme to the other
    #Like if some people have 1 and others have 2, then the ones that have 2 automatically get 10 
    if len(outliers_removed_core.values()) > 0:
        k_min = min(outliers_removed_core.values())
        k_max = max(outliers_removed_core.values())
        if k_max == k_min:
            k_max = k_max+1
        for k,v in iter(log_core.items()):
            if v == 0:
                log_core[k] = 0
                continue
            log_core[k] = int(math.ceil((float(v-k_min)/(k_max-k_min))*9))+1
    normalised_outliers_removed = {k: v for k, v in iter(log_core.items()) if v >0}
    #Normalize from a scale of 0-10 because otherwise people who have done perfectly fine don't look like they've done much
    '''
    if cumulative:
    
    #if window[0] is None or ((window[1]-window[0]).days) > 2:
        fig, axs = plt.subplots(1, 3, sharey=False, tight_layout=True)
        axs[0].hist(list(before_core.values()), 20)
        axs[1].hist(list(outliers_removed_core.values()), 20)
        axs[2].hist(list(normalised_outliers_removed.values()),20)
        axs[0].set_xlabel('Commonshare (pre-BoxCox)')
        axs[1].set_xlabel('Commonshare (post-BoxCox)')
        axs[2].set_xlabel('Commonshare (normalised)')
        axs[0].set_ylabel('number of Commoners')
        axs[1].set_ylabel('number of Commoners')
        axs[2].set_ylabel('number of Commoners')
        plt.show()   
    '''
    #Finally, normalise log-transform values on a scale of 1-10
    nodeiter = G.nodes(data=True)
    
    #Add k-core value to each node in the graph
    #Also update the average and cumulative action weights
    #by multiplying them by the node's k-core value
    lowcomm = 0
    highcomm = 0
    for (n,c) in nodeiter:
        G.nodes[n]['kcore'] = log_core[n]
        if log_core[n] >= 5:
            highcomm += 1
        else:
            lowcomm += 1
        if 'cumu' in c:
            G.nodes[n]['cumu'] = {
            k:(v*c['kcore']) for k,v in c['cumu'].items()
            }    
            G.nodes[n]['avg'] = {
            k:(v*c['kcore']) for k,v in c['avg'].items()
            }
    return (G,colluders)
 