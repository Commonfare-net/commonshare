import networkx as nx
import dynetworkx as dx
import time
import math
import random
import plotly
import plotly.plotly as py
import plotly.graph_objs as go
from datetime import datetime
import config as cf
from plotly import tools
import json
from networkx.readwrite import json_graph
from collections import Counter
from networkx.algorithms.approximation import clique

'''
This module does the necessary k-core calculations and appends the results to each node in the Graph.
It also has separate methods for plotting charts with Plotly
'''

#My Plotly account credentials
plotly.tools.set_credentials_file(username='DJR53', api_key='2WZTNjaJOyOoxGeTcIq4')

end_of_time = datetime.now() + cf.one_year
cliquelist = []
cliqueids = []

def getNodeStats(G,node_id,starttime,endtime):
    edges = G.edges(node_id,data=True)
    stories_created = 0
    stories_read = 0
    stories_commented = 0
    stories_shared = 0
    read_by_others = 0
    commented_by_others = 0
    shared_by_others = 0
    talks_started = 0
    talks_received = 0
    givings = 0
    receivings = 0
    
    #There are more elegant ways of doing this but it works for now
    for (u,v,c) in edges:
        if 'create' in c:
            for createactions in c['create']:
                if (starttime < datetime.strptime(createactions[1],"%d/%m/%y") < endtime):
                    if str(createactions[0]) == str(node_id):
                        stories_created = stories_created + 1 
        if 'read' in c:
            for readactions in c['read']:
                if (starttime < datetime.strptime(readactions[1],"%d/%m/%y") < endtime):
                    if str(readactions[0]) == str(node_id):
                        stories_read = stories_read + 1
                    else:
                        read_by_others = read_by_others + 1
        if 'comment' in c:
            for commentactions in c['comment']:
                if (starttime < datetime.strptime(commentactions[1],"%d/%m/%y") < endtime):
                    if str(commentactions[0]) == str(node_id):
                        stories_commented = stories_commented + 1
                    else:
                        commented_by_others = commented_by_others + 1
        if 'share' in c:                
            for shareactions in c['share']:
                if (starttime < datetime.strptime(shareactions[1],"%d/%m/%y") < endtime):
                    if str(shareactions[0]) == str(node_id):
                        stories_shared = stories_shared + 1
                    else:
                        shared_by_others = shared_by_others + 1
        if 'talk' in c:
            for talkactions in c['talk']:
                if (starttime < datetime.strptime(talkactions[1],"%d/%m/%y") < endtime):
                    if str(talkactions[0]) == str(node_id):
                        talks_started = talks_started + 1
                    else:
                        talks_received = talks_received + 1
        if 'give' in c:
            for giveactions in c['give']:
                if (starttime < datetime.strptime(giveactions[1],"%d/%m/%y") < endtime):
                    if str(giveactions[0]) == str(node_id):
                        givings = givings + 1
                    else:
                        receivings = receivings + 1                      
    stats = {"sc":stories_created,
             "r":stories_read,"c":stories_commented,"s":stories_shared,
             "or":read_by_others,"oc":commented_by_others,"os":shared_by_others,
             "ts":talks_started,"tr":talks_received,
             "giv":givings,"rec":receivings}
    return stats
    
usertimes = []
storiescreated = {}
selfactions = {}
othersactions = {}
starttalks = {}
replytalks = {}
givings = {}
receivings = {}
cliquestats = {}
d_labels = []
d_cliquevals = {}
d_cliquesmoothed = {}
d_avgs = []
max_y_axis = 0

def calculate(G):   
    global cliqueids
    global cliquelist
    global usertimes
    global storiescreated
    global selfactions
    global othersactions
    global starttalks
    global replytalks
    global givings
    global receivings
    global max_y_axis
    user_id = 0
    
    while len(cliqueids) < 10:
        for id in cliquelist:
            if len(cliqueids) < 10 and G.nodes[id]['type'] == 'user':
                cliqueids.append(id)
        cliquelist = random.sample(G.nodes, 100)
        
        
    windowstart = datetime.now()
    windowend = windowstart + cf.one_month

    d_keys = []
    d_values = []

    
    
    for id in cliqueids:
        d_cliquevals[id] = []
        d_cliquesmoothed[id] = []
        storiescreated[id] = []
        selfactions[id] = []
        othersactions[id] = []
        starttalks[id] = []
        replytalks[id] = []
        cliquestats[id] = []
        givings[id] = []
        receivings[id] = []
    alpha = 0.4
    loopcount = 0

    
    
    while(windowend < end_of_time):
        #Find edges which have a spell that started or ended within the bounds of a given hour/day
        #For those edges that didn't, remove them, then calculate the k-core

        ebunch = []
        indirectedges = []
        GCopy = G.copy()
        iter = GCopy.edges(data=True)

        for (u,v,c) in iter:
            edgeexists = False
            for intervals in c['spells']:
                #Cumulative                 
                #if windowend > intervals[0]:
                #Non-cumulative
                if (windowstart < datetime.strptime(intervals[0],"%d/%m/%y") < windowend):
                    edgeexists = True
                    break
            if edgeexists == False:
                ebunch.append((u,v,c))
        GCopy.remove_edges_from(ebunch)
        
        #Here a similar operation is done to remove nodes that do not exist at this point in time
        nbunch = []
        nodeiter = GCopy.nodes(data=True)
        for (n,c) in nodeiter:
            for intervals in c['spells']:
                if datetime.strptime(intervals[0],"%d/%m/%y") < windowend:
                    break
                else:
                    nbunch.append(n)
        GCopy.remove_nodes_from(nbunch)


        #This uses a modified core_number algorithm that takes the weights of each node's edges into account
        #Trying it for both standard undirected graphs and my 'directed' equivalent
        
        (ReducedGraph,D) = dx.core_number_weighted(GCopy,windowstart,windowend,True,False)
        d1 = Counter(D.values())

        nodeiter = ReducedGraph.nodes(data=True)
        #This adds the kcore value back into the GEXF
        for (n,c) in nodeiter:
            c['kcore'] = D[n]
        usertimes.append(windowend)
            
   
        for id in cliqueids:
            d_cliquevals[id].append(D[id])
            if D[id] > max_y_axis:
                max_y_axis = D[id]
            if loopcount > 0:
                d_smoothed = (alpha * D[id]) + (1-alpha)*d_cliquesmoothed[id][-1]
            else:
                d_smoothed = D[id]

            #Add the stats for each user at each point in time
            d_cliquesmoothed[id].append(d_smoothed)
            stats = getNodeStats(GCopy,id,windowstart,windowend)
            cliquestats[id].append(str(stats))
            storiescreated[id].append(stats['sc'])
            selfactions[id].append(stats['r'] + stats['c'] + stats['s'])
            othersactions[id].append(stats['or'] + stats['oc'] + stats['os'])
            starttalks[id].append(stats['ts'])
            replytalks[id].append(stats['tr'])
            givings[id].append(stats['giv'])
            receivings[id].append(stats['rec'])

        d_keysum = 0
        d_numvalues = 0
        for k, v in d1.items():
            if k == 0: 
                continue
            d_keysum = d_keysum + (k * v)
            d_numvalues = d_numvalues + v
            d_keys.append(k)
            d_values.append(v)
        d_avg = d_keysum / d_numvalues
        d_avgs.append(d_avg)
  
        #Update the 'sliding window'
        windowstart = windowend
        windowend = windowend + cf.one_month
        loopcount = loopcount + 1
        
        #Create JSON files as output from the 'reduced graph'
        data = json_graph.node_link_data(ReducedGraph)
        with open('data'+str(loopcount)+'.json', 'w') as outfile:
            outfile.write(json.dumps(data))

def plotgraph():            
    data = []
    mybuttons = []
    visibility_indices = {}
    
    #For determing which traces are going to be visible on each chart
    #10 is the magic number for the number of users. 8 is the magic number for the number of traces generated for each user
    counter = 0
    for id in cliqueids:
        visibility_indices[id] = [False]*10*8
        for index in range(8):
            visibility_indices[id][(counter*8)+index] = True
        counter = counter+1
    
    #The colours from light to dark to indicate the value of the interaction that they represent
    greens = ['#186A3B', '#1D8348', '#239B56', '#28B463', '#2ECC71', '#58D68D', '#82E0AA'] 
    
    for id in range(len(cliqueids)):
        directed_data = plot(cliqueids[id],cliquestats,d_cliquevals[cliqueids[id]],d_avgs,'x','y')
        bardata = makebargraph(cliqueids[id],'x3','y3',greens)
        data = data + directed_data + bardata 
        button = {'label':'User '+str(cliqueids[id]),'method':'update','args':[{'visible':visibility_indices[cliqueids[id]]},{'title': 'User ' + str(cliqueids[id])}]}
        mybuttons.append(button)
    
    updatemenus = list([dict(active=0,buttons=mybuttons,showactive=True,)])
    
    layout = go.Layout(

    updatemenus=updatemenus,
    title = 'Undirected vs. Directed K-cores',
    xaxis=dict(
        domain=[0, 0.45]
    ),
    yaxis=dict(
        domain=[0.55,1],
        title="Directed values",
        range=[0, max_y_axis]
    ),
    xaxis2=dict(
        domain=[0.5,1],
        anchor='y2'
    ),
    yaxis2=dict(
        domain=[0.55, 1],
        anchor='x2',
        title="Ignoring indirect storylinks",
        range=[0, max_y_axis]
    ),
    xaxis3=dict(
        domain=[0, 1],
        anchor='y3'
    ),
    yaxis3=dict(
        domain=[0, 0.45],
        title="User actions",
        
    )
    )

    fig = go.Figure(data=data, layout=layout)
    py.plot(fig, filename='make-subplots-multiple-with-titles')

#Plot the bar chart for a given user
def makebargraph(userid,x_name,y_name,colours):
    global storiescreated
    global selfactions
    global othersactions
    global starttalks
    global replytalks
    global givings
    global receivings   
    bardata = []
    tracecreated = go.Bar(
        x = usertimes,
        y = storiescreated[userid],
        name='U' + str(userid) + '\'s stories',
        xaxis= x_name,
        yaxis=y_name,
        marker=dict(color=colours[2],)
    )
    traceself = go.Bar(
        x = usertimes,
        y = selfactions[userid],
        name='U' + str(userid) + '\'s actions',
        xaxis=x_name,
        yaxis=y_name,            
        marker=dict(color=colours[3],)        
    )
    traceothers = go.Bar(
        x = usertimes,
        y = othersactions[userid],
        name='U' + str(userid) + '\'s feedback',
        xaxis=x_name,
        yaxis=y_name,            
        marker=dict(color=colours[6],)        
    )
    tracetalk = go.Bar(
        x = usertimes,
        y = starttalks[userid],
        name='U' + str(userid) + '\'s chats',
        xaxis=x_name,
        yaxis=y_name,            
        marker=dict(color=colours[1],)        
    )
    tracereply = go.Bar(
        x = usertimes,
        y = replytalks[userid],
        name='U' + str(userid) + '\'s replies',
        xaxis=x_name,
        yaxis=y_name,            
        marker=dict(color=colours[5],)        
    )    
    tracegiving = go.Bar(
        x = usertimes,
        y = givings[userid],
        name='U' + str(userid) + '\'s givings',
        xaxis=x_name,
        yaxis=y_name,            
        marker=dict(color=colours[0],)        
    )  
    tracereceiving = go.Bar(
        x = usertimes,
        y = receivings[userid],
        name='U' + str(userid) + '\'s receivings',
        xaxis=x_name,
        yaxis=y_name,            
        marker=dict(color=colours[4],)        
    )      
    bardata.append(tracecreated)
    bardata.append(traceself)
    bardata.append(traceothers)
    bardata.append(tracetalk)
    bardata.append(tracereply)
    bardata.append(tracegiving)
    bardata.append(tracereceiving)
    return bardata

#Plot the line chart for a given user    
def plot(myid,labels,cliquevals,averages,myaxisx,myaxisy):
    data = []

    trace = go.Scatter(
        x = usertimes,
        y = cliquevals,
        mode = 'lines',
        name = 'U'+str(myid),
        xaxis = myaxisx,
        yaxis = myaxisy,
        line = dict(width = 2)
    )
    data.append(trace)
    return data
    
