import config as cf
import datetime
import networkx as nx
import dynetworkx as dx
import time
import math
import random
import kcore
import os
import sys
import copy

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
      if cf.SHOULD_COLLUDE and random_no > 19:
        return random.sample(cf.colluding_nodes,2)
      else:
          users = random.sample(G.nodes(),2)
          if type[users[0]] == 'user' and type[users[1]] == 'user' and users[0] not in cf.colluding_nodes and users[1] not in cf.colluding_nodes:
            if cf.SHOULD_CLIQUE == True: #Nodes should only talk if they have similar tags
                user1tags = tags[users[0]].split(',')
                user2tags = tags[users[1]].split(',')
                if len([val for val in user1tags if val in user2tags]) > 0:
                    break
            else:
                break
    else:
      users = random.sample(G.nodes(),1)
      if type[users[0]] == 'user':
        break     
  #This just randomly updates the tags of our selected user (maybe they're interested in different things this month or whatever
  G.nodes[users[0]]['tags'] = User().__get_tags__()
  return users    



#Will be effectively the same as the 'create story' function

def create_object(user,objtype):
  global G
  e = Edge()
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
  G.add_edge(user,obj_node)
  for x in actions_dict:
    G[user][obj_node][x] = []
  
  #G.nodes[user]['create_'+objtype].append(([user,obj_node],s_today,s_today))    
  G[user][obj_node]['spells'] = [(s_today,s_fortnight)]
  if cf.SHOULD_CLIQUE:
    tags = G.nodes[user]['tags'].split(',')
    numtags = len(tags)
    G.nodes[obj_node]['tags'] = tags[random.randrange(0,numtags)] #Gives story a random tag from this user
  else:
    G.nodes[obj_node]['tags'] = object.__get_tags__()
  update(user,obj_node,'create_'+objtype)
  
#What kind of interactions might users have? Conversation? 
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
      with open('out.txt', 'a') as f:
        print >> f, 'create_',objtype,' is in G[',target,'][',object,']'
        print >> f, 'because it is ',G[target][object]
      #print 'create_'+objtype + ' is in G[',target,'][',object,']'
     # if cf.SHOULD_CLIQUE == True: #If we're 'cliquing', only want users to interact with stories with which they share a tag
     #   usertags = tags[source].split(',')
     #   objtags = tags[object].split(',')
     #   if len([val for val in usertags if val in objtags]) == 0: #If there are no shared tags between user and story,  carry on
     #       continue
    #  print source,'read story',story,'of user',target
      #Is this the first time source user has interacted with this story?
      if G.has_edge(source,object) == False:
        G.add_edge(source,object)
        for x in actions_dict:
            G[source][object][x] = []
        G[source][object]['spells'] = []
      #Is this the first time source user has interacted with the target user?
      if G.has_edge(source,target) == False:
        G.add_edge(source,target)
        for x in actions_dict:
            G[source][target][x] = []
        G[source][target]['spells'] = []
    #add the spells
        
      G[source][target]['spells'].append((s_today,s_fortnight))
      G[source][object]['spells'].append((s_today,s_fortnight))
      
      update(source,object,interaction)
      update(source,target,interaction)
      return
    
def update(source,target,interaction):
    G[source][target][interaction].append(([source,target],s_today,s_fortnight))
    G.nodes[source][interaction].append(([source,target],s_today,s_fortnight))    
    G.nodes[target][interaction].append(([source,target],s_today,s_fortnight))    

def add_user():
    global G
    user = User()
    G.add_node(user)
    dict = copy.deepcopy(actions_dict)
    dict['type'] = 'user'
    dict['name'] = str(user)
    nx.set_node_attributes(G,{user: dict})
    G.nodes[user]['spells'] = [(s_today,None)]
    G.nodes[user]['tags'] = user.__get_tags__()
    G = nx.convert_node_labels_to_integers(G)

#TODO: Figure out how user's 'accepting' another user's forum post answer might work
def do_random_thing():
  num = random.randint(1,11)
  if num == 1:
    create_object(get_users(False)[0],'Story')
  elif num == 2:
    create_object(get_users(False)[0],'ForumPost')
  elif num == 3:
    object_interact('Story','comment')
  elif num == 4 or num == 11:
    object_interact('ForumPost','comment')
  elif num == 5 or num == 9:
    object_interact('Story','like')
  elif num == 6 or num == 10:
    object_interact('ForumPost','like')
  elif num == 7:
    user_interact('friendship')
  elif num == 8:
    user_interact('transaction')

cur_date = datetime.datetime(2018,6,1)
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
  s_today = cur_date.strftime("%d/%m/%y")
  s_fortnight = (cur_date+cf.two_weeks).strftime("%d/%m/%y")
  counter = counter + 1
  G = nx.convert_node_labels_to_integers(G)
  while len(G.nodes()) < cf.INITIAL_USERS:
    add_user()
    
    if len(G.nodes()) == cf.INITIAL_USERS-1:
        cf.colluding_nodes = random.sample(G.nodes(),cf.NUM_COLLUDERS)
        #So they have something to interact with
        for i in range(cf.NUM_COLLUDERS):
            print 'colluder is ',cf.colluding_nodes[i]
            create_object(cf.colluding_nodes[i],'Story')
            
  for i in range(cf.ACTIONS_PER_DAY):
    do_random_thing()
  #if counter % 3 == 0:
  #  add_user()
  G = nx.convert_node_labels_to_integers(G)

  if counter % 30 == 0:
    edge_labels = {}
    filename = "../gexf/data"+str(counter)+".gexf"
    print 'filename is ',filename
    nx.write_gexf(G, filename)

#Test reading is working properly
G_read = nx.read_gexf("../gexf/data360.gexf")
#Pass the start and end times of the file in, as well as the granularity at which you want the data (default 1 month)
kcore.calculate(G_read,start_date,cur_date,"month")
