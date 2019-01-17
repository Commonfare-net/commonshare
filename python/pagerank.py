#!/usr/bin/env python
import random
import sys
import operator
import ast
import math
import os
from datetime import datetime

import networkx as nx
import xml.etree.ElementTree as ET

import config as cf

#Make this a web service
from flask import Flask,jsonify,request,Blueprint
#app = Flask(__name__)
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
    
    :param core_graph: NetworkX graph of platform interactions with
    additional data on neglected nodes and edge weights
    :param story: string ID of story a user is reading 
    :param user: string ID of platform user (or 0 if not logged in)
    :returns: dictionary of story IDs mapped to their PageRank value

    """
    now = datetime.now()
    
    #Get the nodes surrounding both the story and the user, to use as
    #the personalisation vector in the page-rank calculation 
    surrounding_nodes = {k:10 for k in core_graph.neighbors(story)}
    if user != '0':
        user_nodes = {k:10 for k in core_graph.neighbors(user)}
        surrounding_nodes.update(user_nodes)

    core_graph.remove_nodes_from([story]) #don't recommend story itself
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
    
    for k in rank_values.keys():
       #Only want to keep PageRank values of other stories 
       if core_graph.nodes[k]["type"] != "story":
           del rank_values[k]
    return rank_values
  
@pagerank_api.route('/recommend/<storyid>/<userid>')
def run(storyid,userid):
    #Will hardcode filename here because it ought not to change
    filename = os.environ['PAGERANK_FILE']
    #storyid = os.environ['STORY_ID']
    #userid = os.environ['USER_ID']
    """Print three recommended stories for user reading a story
    
    This uses the personalised pagerank algorithm to print the IDs
    of three stories that a user should be recommended on reading a
    particular story. The print output is captured by pagerank.php
    and returned to the calling Javascript code

    :param filename: string path to recommenderdata.gexf file 
    :param storyid: string ID of story user is reading
    :param userid: string ID of user (or 0 if no user logged in)

    """
    
    G_read = nx.read_gexf(filename)
    pr_vals = personalisedPageRank(G_read,storyid,userid)

    #Sort the recommended nodes by their PageRank value
    ranked = sorted(pr_vals.items(),key=operator.itemgetter(1),reverse=True)
    
    G_untainted = nx.read_gexf(filename)
    recommended_list = []
    
    #User's kcore determines how influential they are
    if userid == '0': #When no user is logged in 
        influence = 0
    else:
        influence = G_untainted.nodes[userid]['kcore']
    
    ET.register_namespace("", "http://www.gexf.net/1.2draft") 
    tree = ET.parse(filename)  
    root = tree.getroot()
    #'neglected nodes'= new stories/listings with few interactions
    neglected_nodes = root[0].attrib['neglected_nodes'].split(" ")
    
    #If node is influential, connect them to unknown stories to increase 
    #density of the graph 
    for i in range(min(influence,len(neglected_nodes))):
        recommended_list.append(neglected_nodes[i])
    for j in range(10-influence):
        recommended_list.append(ranked[j][0])
    
    #Print three at random
    #print " ".join(recommended_list[v] 
    returned_list = []
    for v in random.sample(range(0, len(recommended_list)),3):
        returned_list.append(recommended_list[v])
    return jsonify(returned_list)

#if __name__ == "__main__":    
#    app.run(debug=True,host=os.environ.get('HTTP_HOST', '127.0.0.1'),
#        port=int(os.environ.get('HTTP_PORT', '5001')))
