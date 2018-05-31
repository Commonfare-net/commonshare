
''' Not  using these ones right now
    
def nodeweight_directed_depreciating(G,node_id,starttime,endtime):
    #Here finds the weight corresponding to the interactions at the particular point in time
    edges = G.edges(node_id,data=True)
    edgeweights = []
    for (u,v,c) in edges:
        overallweight = 0
        for action_key in cf.interaction_keys:
            #Here instead, we need to iterate over the actions 'read', 'commented' and 'shared' and see who did them. Impact will have to be for vis purposes in Gephi only
            times_occurred = 0
            for action in c[action_key]:
                if (starttime < action[1] < endtime) or (starttime < action[2] < endtime):
                    #print 'node_id is',node_id,'and createactions[0] is',createactions[0]
                    if str(action[0]) == str(node_id):
                        #print 'yes node',node_id,'created this'
                        overallweight = overallweight + (cf.weights[action_key][0]/math.pow(cf.DEPRECIATION,times_occurred))     
                    else:
                        overallweight = overallweight + (cf.weights[action_key][1]/math.pow(cf.DEPRECIATION,times_occurred))
                    times_occurred = times_occurred + 1
        if overallweight > 0:
            edgeweights.append(int(overallweight))
    if len(edgeweights) == 0:
        return 1
    mean = sum(edgeweights)/len(edgeweights)
    #print 'weights are ',weights
    #normalize weights to mean
    norm = [(float(i)/mean)/(float(min(edgeweights))/mean) for i in edgeweights]
    #print 'sum of norm ',sum(norm)
    return sum(norm)

#A bit wordy but should work
def nodeweight_directed_ignore_indirect_links(G,node_id,starttime,endtime):
    #Here finds the weight corresponding to the interactions at the particular point in time
    edges = G.edges(node_id,data=True)
    edgeweights = []
    for (u,v,c) in edges:
        overallweight = 0
        #Check if this is a user--user edge
        if G.nodes[u]['type'] == 'user' and G.nodes[v]['type'] == 'user':
            #Then only take direct actions into account
            for action_key in cf.direct_interaction_keys:
                for action in c[action_key]:
                    if (starttime < action[1] < endtime) or (starttime < action[2] < endtime):
                        #print 'node_id is',node_id,'and createactions[0] is',createactions[0]
                        if str(action[0]) == str(node_id):
                            #print 'yes node',node_id,'created this'
                            overallweight = overallweight + (cf.weights[action_key][0])     
                        else:
                            overallweight = overallweight + (cf.weights[action_key][1])
        else:
            for action_key in cf.interaction_keys:
                #Here instead, we need to iterate over the actions 'read', 'commented' and 'shared' and see who did them. Impact will have to be for vis purposes in Gephi only
                for action in c[action_key]:
                    if (starttime < action[1] < endtime) or (starttime < action[2] < endtime):
                        #print 'node_id is',node_id,'and createactions[0] is',createactions[0]
                        if str(action[0]) == str(node_id):
                            #print 'yes node',node_id,'created this'
                            overallweight = overallweight + (cf.weights[action_key][0])     
                        else:
                            overallweight = overallweight + (cf.weights[action_key][1])
        if overallweight > 0:
            edgeweights.append(int(overallweight))
    if len(edgeweights) == 0:
        return 1
    mean = sum(edgeweights)/len(edgeweights)
    #print 'weights are ',weights
    #normalize weights to mean
    norm = [(float(i)/mean)/(float(min(edgeweights))/mean) for i in edgeweights]
    #print 'sum of norm ',sum(norm)
    return sum(norm)

'''   
'''
def nodeweight_undirected(G,node_id,starttime,endtime):
    #Here finds the weight corresponding to the interactions at the particular point in time
    edges = G.edges(node_id,data=True)
    edgeweights = []
    for (u,v,c) in edges:
        overallweight = 0
        for action_key in cf.interaction_keys:
            for action in c[action_key]:
                if (starttime < action[1] < endtime) or (starttime < action[2] < endtime):
                        overallweight = overallweight + cf.weights[action_key][0]      
            if overallweight > 0:
                edgeweights.append(int(overallweight))
    if len(edgeweights) == 0:
        return 1
    mean = sum(edgeweights)/len(edgeweights)
    #print 'weights are ',weights
    #normalize weights to mean
    norm = [(float(i)/mean)/(float(min(edgeweights))/mean) for i in edgeweights]
    #print 'sum of norm ',sum(norm)
    return sum(norm)    
'''    