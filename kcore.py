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

plotly.tools.set_credentials_file(username='DJR53', api_key='2WZTNjaJOyOoxGeTcIq4')
from collections import Counter
from networkx.algorithms.approximation import clique

#Possibly useful times in epoch milliseconds
hourinms = 3600000
threehoursinms = 10800000
twohoursinms = 7200000
day_in_s = 3600*24
week_in_s = 3600*24*7
month_in_s = 30*3600*24
year_in_s = week_in_s*52
end_of_time = datetime.now() + cf.one_year
cliquelist = []
cliqueids = []

def calculate(G):
    global cliquelist
    windowstart = datetime.now()
    windowend = windowstart + cf.one_month
    C=nx.core_number(G)
    #D= dx.core_number_weighted(G,windowstart,windowend,False)
    #E= dx.core_number_weighted(G,windowstart,windowend,True)
    c1 = Counter(C.values())
 #   myclique = clique.max_clique(G)
 #   cliquelist = list(myclique)
    cliquelist = random.sample(G.nodes, 100)
    
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
    
    for (u,v,c) in edges:
        for createactions in c['create']:
            if (starttime < datetime.strptime(createactions[1],"%d/%m/%y") < endtime) or (starttime < datetime.strptime(createactions[2],"%d/%m/%y") < endtime):
                if str(createactions[0]) == str(node_id):
                    stories_created = stories_created + 1     
        for readactions in c['read']:
            if (starttime < datetime.strptime(readactions[1],"%d/%m/%y") < endtime) or (starttime < datetime.strptime(readactions[2],"%d/%m/%y") < endtime):
                if str(readactions[0]) == str(node_id):
                    stories_read = stories_read + 1
                else:
                    read_by_others = read_by_others + 1
        for commentactions in c['comment']:
            if (starttime < datetime.strptime(commentactions[1],"%d/%m/%y") < endtime) or (starttime < datetime.strptime(commentactions[2],"%d/%m/%y") < endtime):
                if str(commentactions[0]) == str(node_id):
                    stories_commented = stories_commented + 1
                else:
                    commented_by_others = commented_by_others + 1
        for shareactions in c['share']:
            if (starttime < datetime.strptime(shareactions[1],"%d/%m/%y") < endtime) or (starttime < datetime.strptime(shareactions[2],"%d/%m/%y") < endtime):
                if str(shareactions[0]) == str(node_id):
                    stories_shared = stories_shared + 1
                else:
                    shared_by_others = shared_by_others + 1
        for talkactions in c['talk']:
            if (starttime < datetime.strptime(talkactions[1],"%d/%m/%y") < endtime) or (starttime < datetime.strptime(talkactions[2],"%d/%m/%y") < endtime):
                if str(talkactions[0]) == str(node_id):
                    talks_started = talks_started + 1
                else:
                    talks_received = talks_received + 1
        for giveactions in c['give']:
            if (starttime < datetime.strptime(giveactions[1],"%d/%m/%y") < endtime) or (starttime < datetime.strptime(giveactions[2],"%d/%m/%y") < endtime):
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

def plotgraph(G):   
    global cliqueids
    global usertimes
    global storiescreated
    global selfactions
    global othersactions
    global starttalks
    global replytalks
    global givings
    global receivings
    global cliquelist
  #  myclique = clique.max_clique(G)
   # cliquelist = list(myclique)
    user_id = 0
    while len(cliqueids) < 10:
        for id in cliquelist:
            print 'checking id:',id
            if len(cliqueids) < 10 and G.nodes[id]['type'] == 'user':
                print 'Yup',id,'is a user'
                cliqueids.append(id)
        cliquelist = random.sample(G.nodes, 100)
        
        
    windowstart = datetime.now()
    windowend = windowstart + cf.one_month

    bubbletimes = []
    d_bubbletimes = []
    e_bubbletimes = []
    
    keys = []
    d_keys = []
    e_keys = []
    
    values = []
    d_values = []
    e_values = []
    
    labels = []
    d_labels = []
    e_labels = []
    
    cliquevals = {}
    d_cliquevals = {}
    e_cliquevals = {}
    
    cliquesmoothed = {}
    d_cliquesmoothed = {}
    e_cliquesmoothed = {}
    
    cliquestats = {}
    
    for id in cliqueids:
        cliquevals[id] = []
        d_cliquevals[id] = []
        e_cliquevals[id] = []
        cliquesmoothed[id] = []
        d_cliquesmoothed[id] = []
        e_cliquesmoothed[id] = []
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
    avgs = []
    d_avgs = []
    e_avgs = []
    print 'Here we go!'
    
    max_y_axis = 0
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
                if (windowstart < datetime.strptime(intervals[0],"%d/%m/%y") < windowend) or (windowstart < datetime.strptime(intervals[1],"%d/%m/%y") < windowend):
                    edgeexists = True
                    break
            if edgeexists == False:
                ebunch.append((u,v,c))
        GCopy.remove_edges_from(ebunch)
        
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
        #detect_collusion(GCopy,windowstart,windowend)
        #C= dx.core_number_weighted(GCopy,windowstart,windowend,False,False)
        (ReducedGraph,D) = dx.core_number_weighted(GCopy,windowstart,windowend,True,False)
        #E= dx.core_number_weighted(GCopy,windowstart,windowend,True,True)
        #c1 = Counter(C.values())
        d1 = Counter(D.values())
        #e1 = Counter(E.values())
        #enddate = datetime.utcfromtimestamp(windowend)

        print 'Done the core stuff'
        usertimes.append(windowend)
        for id in cliqueids:
          #  cliquevals[id].append(C[id])
            d_cliquevals[id].append(D[id])
            if D[id] > max_y_axis:
                max_y_axis = D[id]
          #  if C[id] > max_y_axis:
          #      max_y_axis = C[id]
         #   e_cliquevals[id].append(E[id])
          #  if E[id] > max_y_axis:
           #     max_y_axis = E[id]
            #Exponential smoothing s(t) = ax(t) + (1-a)s(t-1)
            if loopcount > 0:
          #      smoothed = (alpha * C[id]) + (1-alpha)*cliquesmoothed[id][-1]
                d_smoothed = (alpha * D[id]) + (1-alpha)*d_cliquesmoothed[id][-1]
           #     e_smoothed = (alpha * E[id]) + (1-alpha)*e_cliquesmoothed[id][-1]
            else:
         #       smoothed = C[id]
                d_smoothed = D[id]
            #    e_smoothed = E[id]
                
      #      cliquesmoothed[id].append(smoothed)
            d_cliquesmoothed[id].append(d_smoothed)
            #e_cliquesmoothed[id].append(e_smoothed)
            stats = getNodeStats(GCopy,id,windowstart,windowend)
            cliquestats[id].append(str(stats))
            storiescreated[id].append(stats['sc'])
            selfactions[id].append(stats['r'] + stats['c'] + stats['s'])
            othersactions[id].append(stats['or'] + stats['oc'] + stats['os'])
            starttalks[id].append(stats['ts'])
            replytalks[id].append(stats['tr'])
            givings[id].append(stats['giv'])
            receivings[id].append(stats['rec'])
        print 'Done the stats stuff'
        '''
        keysum = 0
        numvalues = 0
        for k, v in c1.items():
            if k == 0: 
                continue
            keysum = keysum + (k * v)
            numvalues = numvalues + v
            bubbletimes.append(enddate)
            keys.append(k)
            values.append(v)
        avg = keysum / numvalues
        avgs.append(avg)
        '''
        
        d_keysum = 0
        d_numvalues = 0
        for k, v in d1.items():
            if k == 0: 
                continue
            d_keysum = d_keysum + (k * v)
            d_numvalues = d_numvalues + v
            d_bubbletimes.append(windowend)
            d_keys.append(k)
            d_values.append(v)
        d_avg = d_keysum / d_numvalues
        d_avgs.append(d_avg)
        '''
        e_keysum = 0
        e_numvalues = 0
        for k, v in e1.items():
            if k == 0: 
                continue
            e_keysum = e_keysum + (k * v)
            e_numvalues = e_numvalues + v
            e_bubbletimes.append(enddate)
            e_keys.append(k)
            e_values.append(v)
        e_avg = e_keysum / e_numvalues
        e_avgs.append(e_avg)
        '''    
        windowstart = windowend
        windowend = windowend + cf.one_month
        loopcount = loopcount + 1
        data = json_graph.node_link_data(ReducedGraph)
        with open('data'+str(loopcount)+'.json', 'w') as outfile:
            #print data 
            outfile.write(json.dumps(data))
    
    '''
    updatemenus = list([
    dict(active=-1,
         buttons=list([   
            dict(label = 'High',
                 method = 'update',
                 args = [{'visible': [True, True, False, False]},
                         {'title': 'Yahoo High',
                          'annotations': high_annotations}]),
            dict(label = 'Low',
                 method = 'update',
                 args = [{'visible': [False, False, True, True]},
                         {'title': 'Yahoo Low',
                          'annotations': low_annotations}]),
            dict(label = 'Both',
                 method = 'update',
                 args = [{'visible': [True, True, True, True]},
                         {'title': 'Yahoo',
                          'annotations': high_annotations+low_annotations}]),
            dict(label = 'Reset',
                 method = 'update',
                 args = [{'visible': [True, False, True, False]},
                         {'title': 'Yahoo',
                          'annotations': []}])
        ]),
    )
    ]) 
    '''
    data = []
    mybuttons = []
    visibility_indices = {}
    #For determing which traces are going to be visible on each chart
    #10 is the magic number for the number of users. 9 is the magic number for the number of traces generated for each user
    counter = 0
    for id in cliqueids:
        visibility_indices[id] = [False]*10*9
        for index in range(9):
            visibility_indices[id][(counter*9)+index] = True
        counter = counter+1
    #Need to find the maximum value in cliquevals,d_cliquevals,d_cliquesmoothed and e_cliquevals
    #datavals1 = plot(cliquestats,cliquevals,bubbletimes,keys,values,avgs,'k-core-undirected','K-cores undirected','x','y')
   # datavals2 = plot(cliquestats,d_cliquevals,d_bubbletimes,d_keys,d_values,d_avgs,'k-core-directed','K-cores directed','x','y')
    #datavals3 = plot(cliquestats,d_cliquesmoothed,d_bubbletimes,d_keys,d_values,d_avgs,'directed-smooth','K-cores directed, smooothed','x4','y4')
   # datavals4 = plot(cliquestats,e_cliquevals,e_bubbletimes,e_keys,e_values,e_avgs,'depreciating-smooth','K-cores directed, smooothed, depreciating','x2','y2')
    #data = datavals1 + datavals2 + datavals3 + datavals4
   # data = datavals2 + datavals4 
    greens = ['#186A3B', '#1D8348', '#239B56', '#28B463', '#2ECC71', '#58D68D', '#82E0AA'] 
    #purples = ['#512E5F', '#633974', '#76448A', '#884EA0', '#9B59B6', '#AF7AC5', '#C39BD3']
    #blues = ['#1B4F72', '#21618C', '#2874A6', '#2E86C1', '#3498DB', '#5DADE2', '#85C1E9']
    
    for id in range(len(cliqueids)):
        directed_data = plot(cliqueids[id],cliquestats,d_cliquevals[cliqueids[id]],d_avgs,'x','y')
       # directed_data_ignoring = plot(cliqueids[id],cliquestats,e_cliquevals[cliqueids[id]],e_avgs,'x2','y2')
        bardata = makebargraph(cliqueids[id],'x3','y3',greens)
        data = data + directed_data + bardata 
        '''directed_data_ignoring + '''
        button = {'label':'User '+str(cliqueids[id]),'method':'update','args':[{'visible':visibility_indices[cliqueids[id]]},{'title': 'User ' + str(cliqueids[id])}]}
        mybuttons.append(button)
    
    updatemenus = list([dict(active=0,buttons=mybuttons,showactive=True,)])
    
    layout = go.Layout(
    #autosize=False,
    #width=700,
    #height=1400,
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
    #bardata2 = makebargraph(cliqueids[1],'x6','y6',purples)
    #bardata3 = makebargraph(cliqueids[2],'x7','y7',blues)
   # data = data + bardata1 #+ bardata2 + bardata3
   #fig = tools.make_subplots(rows=1, cols=2)
    fig = go.Figure(data=data, layout=layout)
    py.plot(fig, filename='make-subplots-multiple-with-titles')

    
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

    
def plot(myid,labels,cliquevals,averages,myaxisx,myaxisy):
    '''
    trace0 = go.Scatter(
    x = bubbletimes,
        y=keys,
        mode='markers',
        marker=dict(
            size=values
        ),
        name= 'K-cores',
        xaxis = myaxisx,
        yaxis = myaxisy
    )
  
    traceavg = go.Scatter(
            x = usertimes,
            y = averages,
            mode = 'lines',
            name = 'Average',
            #text = labels[id],
            xaxis = myaxisx,
            yaxis = myaxisy,
            line = dict(
        color = ('rgb(0, 12, 24)'),
        width = 3,
        dash = 'dot')
        )
    data = [traceavg]
      '''
    data = []
    #colours = ['#27AE60','#8E44AD','#5DADE2']
    #count = 0
#    for id in cliqueids:
    trace = go.Scatter(
        x = usertimes,
        y = cliquevals,
        mode = 'lines',
        name = 'U'+str(myid),
        #text = labels[id],
        xaxis = myaxisx,
        yaxis = myaxisy,
        line = dict(
    #color = colours[0],
    width = 2)
    )
    #count = count + 1
    data.append(trace)

    
    return data
    
