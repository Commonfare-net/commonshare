import math
import config as cf
from datetime import datetime
import networkx as nx
import ast
def check_collusion(G,n1,n2,n2_weight,starttime,endtime):
    if G.has_edge(n1,n2) == False:
        return False
    edge = G[n1][n2]
    edgeweight = 0
    frequency = 0
    for action_key in cf.interaction_keys:
        if action_key in edge:
            for action in edge[action_key]:
                if (starttime < datetime.strptime(action[1],"%d/%m/%y") < endtime):
                    #print 'node_id is',node_id,'and createactions[0] is',createactions[0]
                    if str(ast.literal_eval(action[0])[0]) == str(n1):
                        edgeweight = edgeweight + cf.weights[action_key][0]
                        frequency = frequency + 1
    #print 'freq',n1,'-',n2,'=',frequency,'and % is',((edgeweight/n2_weight)*100)
    if frequency > cf.FREQUENCY_THRESHOLD and ((edgeweight/n2_weight)*100) > cf.PERCENTAGE_THRESHOLD:
        return True
    return False
 
#DJR modified this again to return the graph with the unnecessary bits removed        
def nodeweight_directed(G,node_id,starttime,endtime):
    #Here finds the weight corresponding to the interactions at the particular point in time
    edges = G.edges(node_id,data=True)
    #print "START TIIIIIME: ",starttime
    edgeweights = []
    for (u,v,c) in edges:
        overallweight = 0
        for action_key in cf.interaction_keys:
            #Here instead, we need to iterate over the actions 'read', 'commented' and 'shared' and see who did them.
            if action_key in c:
                actions_to_keep = []
                for action in c[action_key]:
                    if (starttime < datetime.strptime(action[1],"%d/%m/%y") < endtime):
                        #print 'node_id is',node_id,'and createactions[0] is',createactions[0]
                        if str(ast.literal_eval(action[0])[0]) == str(node_id):
                            #print 'yes node',node_id,'created this'
                            overallweight = overallweight + cf.weights[action_key][0]     
                        else:
                            overallweight = overallweight + cf.weights[action_key][1]
                        actions_to_keep.append(action)

                c[action_key] = actions_to_keep #Doing it this way stops modification of the list during the loop process    
                
        if overallweight > 0:
            edgeweights.append(int(overallweight))
            #Adds it as a nice attribute
            if 'edgeweight' not in c:
                c['edgeweight'] = {}
            c['edgeweight'][node_id] = int(overallweight)
            
    #Also remove unnecessary attributes from the nodes
    
    if len(edgeweights) == 0:
        return (G,1)
    mean = sum(edgeweights)/len(edgeweights)
  #  if node_id == cf.colluding_nodes[0] or node_id == cf.colluding_nodes[1]:
  #      print 'weights are ',edgeweights
    #normalize weights to mean
    norm = [(float(i)/mean)/(float(min(edgeweights))/mean) for i in edgeweights]
    #print 'sum of norm ',sum(norm)
    return (G,sum(norm))

#DJR Modified this method to return the modified graph for spitting out JSON
def core_number_weighted(G,starttime,endtime,directed,ignore_indirect):

    if G.is_multigraph():
        raise nx.NetworkXError(
                'MultiGraph and MultiDiGraph types not supported.')

    if G.number_of_selfloops()>0:
        raise nx.NetworkXError(
                'Input graph has self loops; the core number is not defined.',
                'Consider using G.remove_edges_from(G.selfloop_edges()).')

    if G.is_directed():
        import itertools
        def neighbors(v):
            return itertools.chain.from_iterable([G.predecessors_iter(v),
                                                  G.successors_iter(v)])
    else:
        neighbors=G.neighbors
    


    degrees=G.degree()
    
    nodeweights = {}
    degrees = dict(G.degree())
    if directed:
        if ignore_indirect:
            for k,v in degrees.items():
                degrees[k] = int(math.sqrt(math.ceil(int(v) * nodeweight_directed_ignore_indirect_links(G,k,starttime,endtime))))  
              
        else:
            for k,v in degrees.items():
                (G,directed_weight) = nodeweight_directed(G,k,starttime,endtime)
                degrees[k] = int(math.sqrt(math.ceil(int(v) * directed_weight)))
               # print 'directed weight of',k,'is',directed_weight
                if directed_weight > cf.REPUTATION_THRESHOLD:
                    nodeweights[k] = directed_weight
    else:
        for k,v in degrees.items():
            degrees[k] = int(math.sqrt(math.ceil(int(v) * nodeweight_undirected(G,k,starttime,endtime))))  

    activenodes = list(nodeweights.keys())
    for i in activenodes:
        for j in activenodes:
            if (i != j) and check_collusion(G,i,j,nodeweights[j],starttime,endtime) and check_collusion(G,j,i,nodeweights[i],starttime,endtime):
                print i,'and',j,'might be colluding'
                
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
    return (G,core)
 