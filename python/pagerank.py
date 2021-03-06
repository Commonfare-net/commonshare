#!/usr/bin/env python
import random
import sys
import operator
import ast
import math
import os
import json
from datetime import datetime

import networkx as nx
import xml.etree.ElementTree as ET

import config as cf

#Make this a Flask web service
from flask import Flask,jsonify,request,Blueprint
app = Flask(__name__)
#The 'Blueprint' allows app methods to be distributed across modules
pagerank_api = Blueprint('pagerank_api',__name__)

def personalisedPageRank(core_graph,story,user):
    """Compute personalised PageRank of stories for given user
    
    This uses NetworkX's built in Personalised PageRank algorithm
    to compute PageRank value of other stories on the platform 
    for a given user reading a given story 

    More info on the algorithm and its personalisation in:
    
    Page, L., Brin, S., Motwani, R., & Winograd, T. (1999). 
    The PageRank citation ranking: Bringing order to the web. 
    Stanford InfoLab.
    
    :param core_graph: NetworkX graph of platform interactions with additional data on neglected nodes and edge weights
    :param story: string ID of story a user is reading 
    :param user: string ID of platform user (or 0 if not logged in)
    :returns: dictionary of story IDs mapped to their PageRank value

    """
    story_id = 0
    user_id = 0
    influence = 0
    now = datetime.now()
    #Becuase the GEXF ID and commonfare.net ID are different, this finds
    #the right story/user nodes 
    for (n,c) in core_graph.nodes(data=True):
        if c['platform_id']==str(story) and c['type']=='story':
            story_id = n
            break
    for (n,c) in core_graph.nodes(data=True):
        if c['platform_id']==str(user) and c['type']=='commoner':
            user_id = n
            influence = c['kcore']
            break
    if story_id == 0:
        return ({},0)
        
    #Get the nodes surrounding both the story and the user, to use as
    #the personalisation vector in the page-rank calculation 
    surrounding_nodes = {k:10 for k in core_graph.neighbors(story_id)}
    if user_id != 0:
        user_nodes = {k:10 for k in core_graph.neighbors(user_id)}
        surrounding_nodes.update(user_nodes)

    core_graph.remove_nodes_from([story_id]) #don't recommend story itself
    core_graph = core_graph.to_directed()
    iter = core_graph.edges(data=True)
    
    for (u,v,c) in iter:
        #Find last time each edge was 'active' in the network 
        last_time_activated = cf.to_date(c['last_date'])
        delta = (now - last_time_activated).days / 7.0
        
        #Edge weight depreciates by 5% every week        
        depreciation = math.pow(0.95,delta) 
        if 'edgeweight' in c:
            c['edgeweight'] = (ast.literal_eval(c['edgeweight'])[v] 
            * depreciation)
        else:
            c['edgeweight'] = depreciation
    
    rank_values = nx.pagerank(core_graph,personalization=surrounding_nodes,
                              alpha=0.85,weight='edgeweight')
    
    for k in list(rank_values.keys()):
       #Only want to keep PageRank values of other stories 
       if core_graph.nodes[k]["type"] != "story":
           del rank_values[k]
    return (rank_values,influence)
  
@pagerank_api.route('/recommend/<storyid>/<userid>')
def run(storyid,userid):
    """Return three recommended stories for user reading a story
    
    This uses the personalised pagerank algorithm to return the IDs
    of three stories that a user should be recommended on reading a
    particular story. The method is routed using the Flask API to 
    the '/recommend' URL, which also contains the parameters

    :param storyid: string ID of story user is reading
    :param userid: string ID of user

    """
    #This is initialised as a Docker environment variable
    filename = os.environ['PAGERANK_FILE']
    G_read = nx.read_gexf(filename)
    (pr_vals,influence) = personalisedPageRank(G_read,storyid,userid)

    if len(pr_vals) == 0:
        return jsonify([0,0,0])
        
    #Sort the recommended nodes by their PageRank value
    ranked = sorted(pr_vals.items(),key=operator.itemgetter(1),reverse=True)
    
    G_untainted = nx.read_gexf(filename)
    recommended_list = []
    
    
    ET.register_namespace("", "http://www.gexf.net/1.2draft") 
    tree = ET.parse(filename)  
    root = tree.getroot()
    #'neglected nodes'= new stories/listings with few interactions
    if len(root[0].attrib['neglected_nodes']) == 0:
        neglected_nodes = []
    else:
        neglected_nodes = root[0].attrib['neglected_nodes'].split(" ")
        
    #If node is influential, connect them to unknown stories to increase 
    #density of the graph 
    for i in range(min(influence,len(neglected_nodes))):
        platform_id = G_untainted.nodes[neglected_nodes[i]]['platform_id']
        recommended_list.append(platform_id)
    for j in range(10-min(influence,len(neglected_nodes))):
        platform_id = G_untainted.nodes[ranked[j][0]]['platform_id']
        recommended_list.append(platform_id)
    
    #Return three at random
    returned_list = []
    for v in random.sample(range(0, len(recommended_list)),3):
        returned_list.append(recommended_list[v])
    return jsonify(returned_list)

    #Run as a Flask app
if __name__ == "__main__":    
    app.run(debug=True,host=os.environ.get('HTTP_HOST', '127.0.0.1'),
        port=int(os.environ.get('HTTP_PORT', '5001')))  
