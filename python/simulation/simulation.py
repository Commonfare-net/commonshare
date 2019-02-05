import datetime
import time
import math
import random
import os
import copy
import sys
sys.path.append("../")

import networkx as nx
import xml.etree.ElementTree as ET

import config as cf
import kcore as dx
from graphclasses import *

def str_to_class(classname):
    """Convert a string to a class

    :param classname: string name of class to access
    :returns: class corresponding to name
    
    """
    return reduce(getattr, classname.split("."), sys.modules[__name__])   

def get_users(need_two_users):
    """Return two random user nodes from graph 

    :param need_two_users: bool, True if 2 users are needed
    :returns: list containing one or two user IDs
    """
    type=nx.get_node_attributes(G,'type')
    name=nx.get_node_attributes(G,'name')

    #Randomly determine whether colluding nodes get detected
    r = random.randint(1,20)
    while True:
        if need_two_users:
            if cf.SHOULD_COLLUDE and r > 10:
                users = random.sample(cf.colluding_nodes,2)
            else:
                users = random.sample(G.nodes(),2)
                if ((r < 15 and users[0] in cf.colluding_nodes) or 
                   (r > 5 and users[1] in cf.colluding_nodes)):
                    continue 
            if (type[users[0]] == type[users[1]] == 'commoner' and 
                name[users[0]] != name[users[1]]):
                break
        else:  
            users = random.sample(G.nodes(),1)
            if (type[users[0]] == 'commoner' and 
            (r > 16 or users[0] not in cf.colluding_nodes)):
                break     
    return users    



def create_object(user,objtype):
    """Create object and edge between it and its creating user

    :param user: string ID of user who created object 
    :param objtype: string type of object

    """
    
    global G    
    object = str_to_class(objtype)()
    G.add_node(object)
    G = nx.convert_node_labels_to_integers(G)
    obj_node = nx.number_of_nodes(G) -1
    dict = {'type':objtype,'title':unicode(str(object))}
    nx.set_node_attributes(G,{obj_node: dict})
    
    #Spells can be used to determine how long an action 
    #contributes to a user's commonfare for
    G.nodes[obj_node]['spells'] = [(s_today,s_today)]
    G.nodes[user]['spells'].append((s_today,s_today))
    G.add_edge(user,obj_node)
    G[user][obj_node]['spells'] = [(s_today,s_today)]
    while True:
      tag = random.sample(G.nodes(),1)
      if G.nodes[tag[0]]['type'] == 'tag':
          break
    tag_assign(obj_node,tag[0])
    update(user,obj_node,'create_'+objtype)

def tag_assign(thing,tag):
    """Create edge between a tag node and a user/story/listing node

    :param thing: string ID of a user, story or listing node
    :param tag: string ID of a tag node

    """
    if G.has_edge(thing,tag) == False:
        G.add_edge(thing,tag)
        G[thing][tag]['spells'] = []
    #Add the spells
    G[thing][tag]['spells'].append((s_today,s_today))
    update(thing,tag,'tag_' + G.nodes[thing]['type'])  
    

def user_interact(interaction):
    """Create edge between two user nodes

    :param interaction: string type of interaction taking place 

    """
    pair = get_users(True)
    source = pair[0]
    target = pair[1]
    if G.has_edge(source,target) == False:
        G.add_edge(source,target)
    G[source][target]['spells'] = []
    #Add the spells
    G[source][target]['spells'].append((s_today,s_today))
    update(source,target,interaction)

def object_interact(objtype,interaction):
    """Create edge between user node and story/listing node

    :param objtype: string type of object 
    :param interaction: string type of interaction

    """
    interaction = interaction+'_'+objtype
    pair = get_users(True)
    source = pair[0]
    target = pair[1]
    type=nx.get_node_attributes(G,'type')
    for object in G.neighbors(target):
        #Pick a random story of the target user
        if type[object] == objtype and ('create_'+objtype) in G[target][object]:
            
            #Is this the first time source user has interacted with this story?
            if G.has_edge(source,object) == False:
                G.add_edge(source,object)
                G[source][object]['spells'] = []
                
            #Is this the first time source user has interacted with the target user?
            if G.has_edge(object,target) == False:
                G.add_edge(object,target)
                G[object][target]['spells'] = []
            #add the spells
            
            G[object][target]['spells'].append((s_today,s_today))
            G[source][object]['spells'].append((s_today,s_today))
          
            update(source,object,interaction)
            update(object,target,interaction)
            return
    
def update(source,target,interaction):
    """Update stats of nodes and edge between them with an interaction

    :param source: string ID of interaction source node 
    :param target: string ID of interaction target node
    :param interaction: string interaction type

    """
    if interaction not in G[source][target]:
        G[source][target][interaction] = []
    if interaction not in G.nodes[source]:
        G.nodes[source][interaction] = []
    if interaction not in G.nodes[target]:
        G.nodes[target][interaction] = []
    G[source][target][interaction].append((source,s_today,s_today))
    G.nodes[source][interaction].append((source,s_today,s_today))    
    G.nodes[target][interaction].append((source,s_today,s_today))  
    G.nodes[source]['spells'].append((s_today,s_today))
    G.nodes[target]['spells'].append((s_today,s_today))

def add_tag():
    """Add a tag node to the graph"""
    
    global G
    mytag = tag()
    G.add_node(mytag)
    G = nx.convert_node_labels_to_integers(G)  
    tag_node = nx.number_of_nodes(G) -1    
    dict = {'type':'tag','name':str(mytag)}
    nx.set_node_attributes(G,{tag_node: dict})
    G.nodes[tag_node]['spells'] = [(s_today,s_today)]
    return G
    
def add_user():
    """Add a user node to the graph"""
    
    global G
    myuser = user()
    G.add_node(myuser)
    G = nx.convert_node_labels_to_integers(G)  
    user_node = nx.number_of_nodes(G) -1
    dict = {'type':'commoner','name':str(myuser)}
    nx.set_node_attributes(G,{user_node: dict})
    G.nodes[user_node]['spells'] = [(s_today,s_today)]
    while True:
        tag = random.sample(G.nodes(),1)
        if G.nodes[tag[0]]['type'] == 'tag':
            break
    tag_assign(user_node,tag[0])
    return G

def do_random_thing():
    """Select a random interaction to perform this turn
    
    This uses a random number generator to determine an action to perform in
    the simulation. Interactions can be made more likely simply by having 
    more result numbers correspond to them 
    """
    
    num = random.randint(1,9)
    if num == 1:
        create_object(get_users(False)[0],'story')
    elif num == 2:
        create_object(get_users(False)[0],'listing')
    elif num == 3 or num == 4:
        object_interact('story','comment')
    elif num == 5:
        object_interact('listing','comment')
    elif num == 6 or num == 7:
        user_interact('conversation')
    elif num == 8 or num == 9:
        user_interact('transaction')
    
cur_date = datetime.datetime(2016,6,1)
start_date = cur_date
G=nx.Graph()
counter = 0

if not os.path.exists("../../data/input"):
    os.makedirs("../../data/input")

#Loop for cf.DAYS days, doing cf.ACTIONS_PER_DAY actions each time
while counter < cf.DAYS:
    cur_date = cur_date + cf.one_day
    s_today = cf.to_str(cur_date)
    counter = counter + 1
    G = nx.convert_node_labels_to_integers(G)

    #Seed some tags and users to get things started
    while len(G.nodes()) < cf.TAGS:
        G = add_tag()
        
    while len(G.nodes()) < cf.INITIAL_USERS:
        G = add_user()

    G = nx.convert_node_labels_to_integers(G)
    
    if len(G.nodes()) == cf.INITIAL_USERS:
        #Pick some nodes to be the 'colluders' in the simulation 
        cf.colluding_nodes = random.sample(G.nodes(),cf.NUM_COLLUDERS)
        
        #Make each one write a story so that collusion is easier
        for i in range(cf.NUM_COLLUDERS):
            print 'colluder is ',cf.colluding_nodes[i]
            create_object(cf.colluding_nodes[i],'story')

              
    for i in range(cf.ACTIONS_PER_DAY):
        do_random_thing()
        
    G = nx.convert_node_labels_to_integers(G)

    if counter % 30 == 0:
        print 'we are at ',counter

start_date = datetime.datetime(2016,6,1)
end_date = start_date + cf.one_year
ET.register_namespace("", "http://www.gexf.net/1.2draft")
nx.write_gexf(G,"data360.gexf") 

#This seems to be the easiest way to add start/end attrs to the GEXF
tree = ET.parse("data360.gexf")  
namespaces={'xmlns': 'http://www.gexf.net/1.2draft'}
root = tree.getroot()
root[0].set('start',cf.to_str(start_date))
root[0].set('end',cf.to_str(end_date))
os.remove('data360.gexf')
tree.write('../../data/input/simulateddata.gexf')  
