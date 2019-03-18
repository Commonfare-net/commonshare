import math
from datetime import datetime

import networkx as nx
from scipy import stats

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
    print 'checking between ',n1,' and ',n2
    for action_key in cf.interaction_keys:
        if action_key in edge:
            for action in edge[action_key]:
                if cf.in_date(window,action[1]):
                    edgeweight = edgeweight + cf.weights[action_key]
                    frequency = frequency + 1
    n_weight = min(n1_weight,n2_weight)
    return ((edgeweight/n_weight)*100) > cf.PERCENTAGE_THRESHOLD

def nodeweight(G,node_id,window,suspect_nodes):
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
    
    #This holds the contribution of each type of action to
    #the node's overall weight 
    action_weights = {}
    for meta in cf.meta_networks:
        action_weights[meta] = 0
    edges = G.edges(node_id,data=True)
    edgeweights = []
    
    #'if len(active_weeks) > 52' is used throughout to check 
    #if this is the cumulative graph
    
    #Find no. weeks this node is active from start of commonfare.net
    active_weeks = [0] * ((window[1]-window[0]).days / 7) 
    if len(active_weeks) > 52: #If this is the cumulative graph...
        for spell in G.nodes[node_id]['spells']:
            nodespell = cf.to_date(spell[1])
            index = ((nodespell-window[0]).days / 7) -1
            active_weeks[index] = 1
        total_weeks_active = float(sum(active_weeks))

    maxweight = 0
    influence = 0
    flagged = False    
    for (u,v,c) in edges:
    
        #Constant used to decrease the 'value' of multiple interactions
        #between the same two nodes
        depreciating_constant = 0.75 
        
        overallweight = 0.0
        
        if len(active_weeks) > 52:
          
          #Estimate the 'influence' of this node. 
          #For each neighbour node, determine its activity
          #since connecting with this node
            spelldate = cf.to_date(c['spells'][0][0])
            after_weeks = [0]*((window[1] - spelldate).days / 7)
            for spell in G.nodes[v]['spells']:
                nodespell = cf.to_date(spell[1])
                #If this spell happened afterwards...
                if (nodespell - spelldate).days >= 7: 
                    index = ((nodespell-spelldate).days / 7)-1
                    after_weeks[index] = 1
            if len(after_weeks) > 0:
                influence = float(sum(after_weeks))/len(after_weeks)
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
                    edge_weight = cf.weights[action_key]
                else: #This node was the recipient of the action
                    edge_weight = cf.weights["r"+action_key]
                actions_to_keep.append(action)
                action_count += 1    
                '''
                Depreciate weight of the edge as a function of 
                the number of days old it is. 
                e^(-days/100) seems to work well. 
                '''
                tdelta = window[1] - cf.to_date(action[1])
                agefraction = math.exp(-(float(tdelta.days)/100))
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
            continue 
        if len(active_weeks) > 52:
            '''
            Reduce edgeweight based on its influence and
            weeks active of the node. Reduction value = 
            (e^influence)-1 * square_root(weeks active) + 0.1
            Minimum reduction = 0.1 when influence is 0
            '''

            overallweight *= min(((pow(1.3,influence)-1)
            * math.sqrt(total_weeks_active) +0.1),1)
          
        else: #'flag' a node if it has been particularly active 
            if action_count > 7: 
                flagged = True
                
        edgeweights.append(overallweight)
        
        #Adds the edge's weight as an attribute
        if 'edgeweight' not in c:
            c['edgeweight'] = {}
            c['maxweight'] = overallweight
        c['edgeweight'][node_id] = round(overallweight,2)
        c['maxweight'] = round(max(c['maxweight'],overallweight),2)
        if overallweight > cf.MAX_WEIGHT:
            cf.MAX_WEIGHT = overallweight
        maxweight = max(c['maxweight'],maxweight)
        
        if 'maxweight' not in G.nodes[u]:
            G.nodes[u]['maxweight'] = c['maxweight']
        G.nodes[u]['maxweight'] = max(G.nodes[u]['maxweight'],c['maxweight'])

        if 'maxweight' not in G.nodes[v]:
            G.nodes[v]['maxweight'] = c['maxweight']
        G.nodes[v]['maxweight'] = max(G.nodes[v]['maxweight'],c['maxweight'])

    if len(edgeweights) == 0:
        return (G,action_weights,0)
        
    if flagged: #High activity node, add it to dictionary 
        suspect_nodes[node_id] = sum(edgeweights)
    #if len(active_weeks) > 52:
    #    print 'edgeweight for node ',node_id,' is ',sum(edgeweights)
    return (G,action_weights,sum(edgeweights))
    

def weighted_core(G,window):
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
    cf.MAX_WEIGHT = 0
    
    for k,v in degrees.items():
        #Compute the new node weight here
        #Also return 'action_weights' that holds node weight relevant
        #to each different action type 
        (G,action_weights,weight) = nodeweight(G,k,window,suspect_nodes)
        G.nodes[k]['edgetotals'] = action_weights
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
        degrees[k] = int(math.sqrt(int(v)) * weight)

    #Do a collusion check
    activenodes = list(suspect_nodes.keys())
    for i in activenodes:
        for j in activenodes:
            if colluding(G,i,j,suspect_nodes[i],suspect_nodes[j],window): 
                print i,'and',j,'might be colluding'
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
        
    #Finally, normalise log-transform values on a scale of 1-10
    if len(log_core.values()) > 0:
        k_min = min(log_core.values())
        k_max = max(log_core.values())
        if k_max == k_min:
            k_max = k_max+1
        for k,v in log_core.iteritems():
            if sumofedges[k] == 0:
                log_core[k] = 0
                continue
            log_core[k] = int(math.ceil((float(v-k_min)/(k_max-k_min))*9))+1

    nodeiter = G.nodes(data=True)
    
    #Add k-core value to each node in the graph
    #Also update the average and cumulative action weights
    #by multiplying them by the node's k-core value
    for (n,c) in nodeiter:
        G.nodes[n]['kcore'] = log_core[n]
        G.nodes[n]['cumu'] = {
        k:(v*c['kcore']) for k,v in c['cumu'].items()
        }    
        G.nodes[n]['avg'] = {
        k:(v*c['kcore']) for k,v in c['avg'].items()
        }
    return (G,colluders)
 