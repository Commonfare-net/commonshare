import config as cf
import datetime
import networkx as nx
import dynetworkx as dx
import time
import math
import random
#import kcore
import os
import sys
import copy
import xml.etree.ElementTree as ET

from graphclasses import *

def str_to_class(classname):
    return reduce(getattr, classname.split("."), sys.modules[__name__])    
#Run this script to generate simulated GEXF data files to be used in the modified k-core algorithm

def get_users(need_two_users):
  type=nx.get_node_attributes(G,'type')
  tags=nx.get_node_attributes(G,'tags')
  all_users = False
  #Randomly determine whether colluding nodes get detected
  random_no = random.randint(1,20)
  while True:
    if need_two_users:
      if cf.SHOULD_COLLUDE and random_no > 17:
        return random.sample(cf.colluding_nodes,2)
      else:
          users = random.sample(G.nodes(),2)
          if type[users[0]] == 'commoner' and type[users[1]] == 'commoner' and users[0] not in cf.colluding_nodes and users[1] not in cf.colluding_nodes and users[0] != cf.SPAMMERID:
            #if cf.SHOULD_CLIQUE == True: #Nodes should only talk if they have similar tags
            #    user1tags = tags[users[0]].split(',')
            #    user2tags = tags[users[1]].split(',')
            #    if len([val for val in user1tags if val in user2tags]) > 0:
            #        break
            #else:
            break
    else:
      users = random.sample(G.nodes(),1)
      if type[users[0]] == 'commoner':
        break     
  #This just randomly updates the tags of our selected user (maybe they're interested in different things this month or whatever
  return users    



#Will be effectively the same as the 'create story' function

def create_object(user,objtype):
  global G
  object = str_to_class(objtype)()
  G.add_node(object)
  G = nx.convert_node_labels_to_integers(G)
  obj_node = nx.number_of_nodes(G) -1
  dict = copy.deepcopy(actions_dict)
  dict['type'] = objtype
  dict['title'] = unicode(str(object))
  nx.set_node_attributes(G,{obj_node: dict})
  #Spells can be used to determine how long an action contributes to a user's commonfare for
  G.nodes[obj_node]['spells'] = [(s_today,s_fortnight)]
  G.nodes[user]['spells'].append((s_today,s_fortnight))
  G.add_edge(user,obj_node)
  G[user][obj_node]['spells'] = [(s_today,s_fortnight)]
  #while True:
  #  tag = random.sample(G.nodes(),1)
  #  if G.nodes[tag[0]]['type'] == 'tag':
  #      break
  #tag_assign(obj_node,tag[0])
  for x in actions_dict:
    G[user][obj_node][x] = []
  #print G.nodes[user]
  update(user,obj_node,'create_'+objtype)

#Make an edge between a tag node and a commoner, story, or listing 
def tag_assign(thing,tag):
    if G.has_edge(thing,tag) == False:
        G.add_edge(thing,tag)
        for x in actions_dict:
            G[thing][tag][x] = []
        G[thing][tag]['spells'] = []
    #Add the spells
    G[thing][tag]['spells'].append((s_today,s_fortnight))
    update(thing,tag,'tag_' + G.nodes[thing]['type'])  
    

def user_interact(interaction):
  pair = get_users(True)
  source = pair[0]
  target = pair[1]
 # print source,'started talking to',target
  if G.has_edge(source,target) == False:
    G.add_edge(source,target)
    for x in actions_dict:
        G[source][target][x] = []
    G[source][target]['spells'] = []
  #Add the spells
  G[source][target]['spells'].append((s_today,s_fortnight))
  update(source,target,interaction)

def object_interact(objtype,interaction):
  interaction = interaction+'_'+objtype
  pair = get_users(True)
  source = pair[0]
  target = pair[1]
  #tags=nx.get_node_attributes(G,'tags')
  type=nx.get_node_attributes(G,'type')
  for object in G.neighbors(target):
    #Pick a random story of the target user
    if type[object] == objtype and len(G[target][object]['create_'+objtype]) > 0:
      #Is this the first time source user has interacted with this story?
      if G.has_edge(source,object) == False:
        G.add_edge(source,object)
        for x in actions_dict:
            G[source][object][x] = []
        G[source][object]['spells'] = []
      #Is this the first time source user has interacted with the target user?
      if G.has_edge(object,target) == False:
        G.add_edge(object,target)
        for x in actions_dict:
            G[object][target][x] = []
        G[object][target]['spells'] = []
    #add the spells
        
      G[object][target]['spells'].append((s_today,s_fortnight))
      G[source][object]['spells'].append((s_today,s_fortnight))
      
      update(source,object,interaction)
      update(object,target,interaction)
      return
    
def update(source,target,interaction):
    G[source][target][interaction].append((source,s_today,s_fortnight))
    G.nodes[source][interaction].append((source,s_today,s_fortnight))    
    G.nodes[target][interaction].append((source,s_today,s_fortnight))  
    G.nodes[source]['spells'].append((s_today,s_fortnight))
    G.nodes[target]['spells'].append((s_today,s_fortnight))

def add_tag():
    global G
    mytag = tag()
    G.add_node(mytag)
    G = nx.convert_node_labels_to_integers(G)  
    tag_node = nx.number_of_nodes(G) -1    
    dict = copy.deepcopy(actions_dict)
    dict['type'] = 'tag'
    dict['name'] = str(mytag)
    nx.set_node_attributes(G,{tag_node: dict})
    G.nodes[tag_node]['spells'] = [(s_today,None)]
    
def add_user():
    global G
    myuser = user()
    G.add_node(myuser)
    G = nx.convert_node_labels_to_integers(G)  
    user_node = nx.number_of_nodes(G) -1
    dict = copy.deepcopy(actions_dict)
    dict['type'] = 'commoner'
    dict['name'] = str(myuser)
    nx.set_node_attributes(G,{user_node: dict})
    G.nodes[user_node]['spells'] = [(s_today,None)]
    #while True:
    #    tag = random.sample(G.nodes(),1)
    #    if G.nodes[tag[0]]['type'] == 'tag':
    #        break
    #tag_assign(user_node,tag[0])

#TODO: Figure out how user's 'accepting' another user's forum post answer might work
def do_random_thing():
  num = random.randint(1,10)
  if num == 1:
    create_object(get_users(False)[0],'story')
  elif num == 2:
    create_object(get_users(False)[0],'listing')
  elif num == 3 or num == 4:
    object_interact('story','comment')
  elif num == 5 or num == 6:
    object_interact('listing','comment')
  elif num == 7 or num == 8:
    user_interact('conversation')
  elif num == 9:
    user_interact('transaction')
  else:
    num = random.randint(1,3)
    if num == 1:
        create_object(cf.SPAMMERID,'story')
    
cur_date = datetime.datetime(2016,6,1)
start_date = cur_date
G=nx.Graph()
counter = 0
#Set up the actions dictionary that applies to each node and edge
actions_dict = {}
s_today = ''
s_fortnight = ''

for key in cf.interaction_keys:
    actions_dict[key] = []
    
if not os.path.exists("../gexf"):
    os.makedirs("../gexf")

while counter < cf.DAYS:
  cur_date = cur_date + cf.one_day
  s_today = cur_date.strftime("%Y/%m/%d")
  s_fortnight = (cur_date+cf.two_weeks).strftime("%Y/%m/%d")
  counter = counter + 1
  G = nx.convert_node_labels_to_integers(G)
  

  while len(G.nodes()) < cf.INITIAL_USERS:
    add_user()

    G = nx.convert_node_labels_to_integers(G)
    
    if len(G.nodes()) == cf.INITIAL_USERS-1:
        cf.colluding_nodes = random.sample(G.nodes(),cf.NUM_COLLUDERS) 
        #So they have something to interact with
        for i in range(cf.NUM_COLLUDERS):
            print 'colluder is ',cf.colluding_nodes[i]
            create_object(cf.colluding_nodes[i],'story')

  #Seed some tags and users to get things started
  while len(G.nodes()) < cf.TAGS:
    add_tag()
              
  for i in range(cf.ACTIONS_PER_DAY):
    do_random_thing()
  G = nx.convert_node_labels_to_integers(G)

  if counter % 30 == 0:
    edge_labels = {}
    filename = "gexf/data"+str(counter)+".gexf"
    print 'filename is ',filename
    nx.write_gexf(G, filename)

start_date = datetime.datetime(2016,6,1)
end_date = start_date + cf.one_year
ET.register_namespace("", "http://www.gexf.net/1.2draft") 
tree = ET.parse("gexf/data360.gexf")  
namespaces={'xmlns': 'http://www.gexf.net/1.2draft'}
root = tree.getroot()
root[0].set('start',datetime.datetime.strftime(start_date,"%Y/%m/%d"))
root[0].set('end',datetime.datetime.strftime(end_date,"%Y/%m/%d"))
tree.write('gexf/simulateddata.gexf')  
