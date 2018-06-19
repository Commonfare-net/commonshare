import config as cf
import datetime
import networkx as nx
import dynetworkx as dx
import time
import math
import random
import kcore
import os
from graphclasses import *

#Run this script to generate simulated GEXF data files to be used in the modified k-core algorithm

def get_users(need_two_users):
  type=nx.get_node_attributes(G,'type')
  tags=nx.get_node_attributes(G,'tags')
  all_users = False
  #Randomly determine whether colluding nodes get detected
  random_no = random.randint(1,10)
  while True:
    if need_two_users:
      if cf.SHOULD_COLLUDE and random_no > 7:
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
  G.nodes[users[0]]['tags'] = user.__get_tags__()
  return users    



#Will be effectively the same as the 'create story' function

def create_welfare(user):
  global G
  e = Edge()
  welfare = Welfare()
  G.add_node(welfare)
  G = nx.convert_node_labels_to_integers(G)
  welfare_node = nx.number_of_nodes(G) -1

  nx.set_node_attributes(G,{welfare_node: {'type': 'welfare','title':unicode(str(welfare)),'read':[],'comment':[],'share':[],'talk':[],'give':[]}})
  G.nodes[welfare_node]['spells'] = [(cur_date.strftime("%d/%m/%y"),(cur_date+cf.two_weeks).strftime("%d/%m/%y"))]
  
  G.add_edge(user,welfare_node,read=[],comment=[],share=[],create=[],talk=[],give=[])
  
  G.nodes[user]['create'].append(([user,welfare_node],cur_date.strftime("%d/%m/%y"),cur_date.strftime("%d/%m/%y")))    
  G[user][welfare_node]['spells'] = [(cur_date.strftime("%d/%m/%y"),(cur_date+cf.two_weeks).strftime("%d/%m/%y"))]
  G[user][welfare_node]['create'].append(([user,welfare_node],cur_date.strftime("%d/%m/%y"),cur_date.strftime("%d/%m/%y") ))
  if cf.SHOULD_CLIQUE:
    tags = G.nodes[user]['tags'].split(',')
    numtags = len(tags)
    G.nodes[welfare_node]['tags'] = tags[random.randrange(0,numtags)] #Gives story a random tag from this user
  else:
    G.nodes[welfare_node]['tags'] = welfare.__get_tags__()
    
def create_story(user):
  global G
  e = Edge()
  story = Story()
  G.add_node(story)
  G = nx.convert_node_labels_to_integers(G)
  story_node = nx.number_of_nodes(G) -1
  nx.set_node_attributes(G,{story_node: {'type': 'story','title':unicode(str(story)),'read':[],'comment':[],'share':[],'talk':[],'give':[]}})
  G.nodes[story_node]['spells'] = [(cur_date.strftime("%d/%m/%y"),(cur_date+cf.two_weeks).strftime("%d/%m/%y"))]
  
  G.add_edge(user,story_node,read=[],comment=[],share=[],create=[],talk=[],give=[])
  
  G.nodes[user]['create'].append(([user,story_node],cur_date.strftime("%d/%m/%y"),cur_date.strftime("%d/%m/%y")))    
  G[user][story_node]['spells'] = [(cur_date.strftime("%d/%m/%y"),(cur_date+cf.two_weeks).strftime("%d/%m/%y"))]
  G[user][story_node]['create'].append(([user,story_node],cur_date.strftime("%d/%m/%y"),cur_date.strftime("%d/%m/%y") ))
  if cf.SHOULD_CLIQUE:
    tags = G.nodes[user]['tags'].split(',')
    numtags = len(tags)
    G.nodes[story_node]['tags'] = tags[random.randrange(0,numtags)] #Gives story a random tag from this user
  else:
    G.nodes[story_node]['tags'] = story.__get_tags__()
    
#What kind of interactions might users have? Conversation? 
def user_interact(interaction):
  pair = get_users(True)
  source = pair[0]
  target = pair[1]
 # print source,'started talking to',target
  if G.has_edge(source,target) == False:
    G.add_edge(source,target,read=[],comment=[],share=[],create=[],talk=[],give=[])
    G[source][target]['spells'] = []
  #Add the spells
  G[source][target]['spells'].append((cur_date.strftime("%d/%m/%y"),(cur_date+cf.two_weeks).strftime("%d/%m/%y")))
  update_links(source,target,interaction)
  update_nodes(source,target,interaction)


def object_interact(objtype,interaction):
  pair = get_users(True)
  source = pair[0]
  target = pair[1]
  tags=nx.get_node_attributes(G,'tags')
  for object in G.neighbors(target):
    type=nx.get_node_attributes(G,'type')
    #Pick a random story of the target user
    if type[object] == objtype and 'create' in G[target][object]:
      if cf.SHOULD_CLIQUE == True: #If we're 'cliquing', only want users to interact with stories with which they share a tag
        usertags = tags[source].split(',')
        objtags = tags[object].split(',')
        if len([val for val in usertags if val in objtags]) == 0: #If there are no shared tags between user and story,  carry on
            continue
    #  print source,'read story',story,'of user',target
      #Is this the first time source user has interacted with this story?
      if G.has_edge(source,object) == False:
        G.add_edge(source,object,read=[],comment=[],share=[],create=[],talk=[],give=[])
        G[source][object]['spells'] = []
      #Is this the first time source user has interacted with the target user?
      if G.has_edge(source,target) == False:
        G.add_edge(source,target,read=[],comment=[],share=[],create=[],talk=[],give=[])
        G[source][target]['spells'] = []
    #add the spells
        
      G[source][target]['spells'].append((cur_date.strftime("%d/%m/%y"),(cur_date+cf.two_weeks).strftime("%d/%m/%y")))
      G[source][object]['spells'].append((cur_date.strftime("%d/%m/%y"),(cur_date+cf.two_weeks).strftime("%d/%m/%y")))
      
      update_links(source,object,interaction)
      update_links(source,target,interaction)
      update_nodes(source,target,interaction)
      update_nodes(source,object,interaction)
      return
    
def update_links(source,target,interaction):
    w = cf.weights.get(interaction)
    source_weight = w[0]
    target_weight = w[1]
    G[source][target][interaction].append(([source,target],cur_date.strftime("%d/%m/%y"),(cur_date+cf.two_weeks).strftime("%d/%m/%y")))

def update_nodes(source,target,interaction):
    w = cf.weights.get(interaction)
    source_weight = w[0]
    target_weight = w[1]
    G.nodes[source][interaction].append(([source,target],cur_date.strftime("%d/%m/%y"),(cur_date+cf.two_weeks).strftime("%d/%m/%y")))    
    G.nodes[target][interaction].append(([source,target],cur_date.strftime("%d/%m/%y"),(cur_date+cf.two_weeks).strftime("%d/%m/%y")))    

  
def do_random_thing():
  num = random.randint(1,11)
  if num == 1:
    create_story(get_users(False)[0])
  elif num == 3:
    create_welfare(get_users(False)[0])
 # elif num == 3 or num == 4:
 #   story_interact('read')
  elif num == 5 or num == 6 or num == 2:
    object_interact('story','comment')
  elif num == 7:
    user_interact('talk')
  elif num == 8:
    user_interact('give')
  elif num == 9  or num == 4 or num == 10:
    object_interact('welfare','comment')
  #else:
  #  story_interact('share')

cur_date = datetime.datetime(2018,6,1)
start_date = cur_date
G=nx.Graph()
counter = 0

if not os.path.exists("../gexf"):
    os.makedirs("../gexf")

while counter < cf.DAYS:
  cur_date = cur_date + cf.one_day
  counter = counter + 1
  G = nx.convert_node_labels_to_integers(G)
  while len(G.nodes()) < cf.USERS:
    user = User()
    G.add_node(user)
    nx.set_node_attributes(G,{user: {'type': 'user','name': str(user),'read':[],'comment':[],'share':[],'create':[],'talk':[],'give':[]}})
    G.nodes[user]['spells'] = [(cur_date.strftime("%d/%m/%y"),None)]
    G.nodes[user]['viz'] = {}
    G.nodes[user]['viz']['color'] = {'r' : 0, 'g' : 0, 'b' : 254, 'a':1.0}
    G.nodes[user]['tags'] = user.__get_tags__()
    G = nx.convert_node_labels_to_integers(G)
    
    if len(G.nodes()) == cf.USERS-1:
        cf.colluding_nodes = random.sample(G.nodes(),cf.NUM_COLLUDERS)
        #So they have something to interact with
        for i in range(cf.NUM_COLLUDERS):
            print 'colluder is ',cf.colluding_nodes[i]
            create_story(cf.colluding_nodes[i])
            
  for i in range(cf.ACTIONS_PER_DAY):
    do_random_thing()
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
#kcore.plotgraph()