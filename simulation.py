import config as cf
import datetime
import networkx as nx
import dynetworkx as dx
import time
import math
import random
import kcore
from graphclasses import *

#Run this script to generate simulated GEXF data files to be used in the modified k-core algorithm

def get_users(need_two_users):
  type=nx.get_node_attributes(G,'type')
  all_users = False
  #Randomly determine whether colluding nodes get detected
  random_no = random.randint(1,10)
  while True:
    if need_two_users:
      if cf.SHOULD_COLLUDE and random_no > 7:
        return random.sample(cf.colluding_nodes,2)
      else:
          users = random.sample(G.nodes(),2)
          if type[users[0]] == 'user' and type[users[1]] == 'user': #and users[0] not in cf.colluding_nodes and users[1] not in cf.colluding_nodes:
            break
    else:
      users = random.sample(G.nodes(),1)
      if type[users[0]] == 'user':
        break      
  return users    


def create_story(user):
  e = Edge()
  story = Story()
  G.add_node(story)
  nx.set_node_attributes(G,{story: {'type': 'story','title':unicode(str(story)),'read':[],'comment':[],'share':[],'talk':[],'give':[]}})
  G.nodes[story]['spells'] = [(cur_date.strftime("%d/%m/%y"),(cur_date+cf.two_weeks).strftime("%d/%m/%y"))]
  G.add_edge(user,story,read=[],comment=[],share=[],create=[],talk=[],give=[])
  
  G.nodes[user]['create'].append((str(user),cur_date.strftime("%d/%m/%y"),cur_date.strftime("%d/%m/%y")))    
  G[user][story]['spells'] = [(cur_date.strftime("%d/%m/%y"),(cur_date+cf.two_weeks).strftime("%d/%m/%y"))]
  G[user][story]['create'].append((str(user),cur_date.strftime("%d/%m/%y"),cur_date.strftime("%d/%m/%y") ))
  G.nodes[story]['viz'] = {}
  G.nodes[story]['viz']['color'] = {'r' : 254, 'g' : 0, 'b' : 0, 'a':1.0}

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
  
#These are two-way interactions. Different 'impact' depending on the direction. 
#For example, having your story read is worth more than reading a story?
def story_interact(interaction):
  pair = get_users(True)
  source = pair[0]
  target = pair[1]
  for story in G.neighbors(target):
    type=nx.get_node_attributes(G,'type')
    #Pick a random story of the target user
    if type[story] == 'story' and 'create' in G[target][story]:
    #  print source,'read story',story,'of user',target
      #Is this the first time source user has interacted with this story?
      if G.has_edge(source,story) == False:
        G.add_edge(source,story,read=[],comment=[],share=[],create=[],talk=[],give=[])
        G[source][story]['spells'] = []
      #Is this the first time source user has interacted with the target user?
      if G.has_edge(source,target) == False:
        G.add_edge(source,target,read=[],comment=[],share=[],create=[],talk=[],give=[])
        G[source][target]['spells'] = []
    #add the spells
        
      G[source][target]['spells'].append((cur_date.strftime("%d/%m/%y"),(cur_date+cf.two_weeks).strftime("%d/%m/%y")))
      G[source][story]['spells'].append((cur_date.strftime("%d/%m/%y"),(cur_date+cf.two_weeks).strftime("%d/%m/%y")))
      
      update_links(source,story,interaction)
      update_links(source,target,interaction)
      update_nodes(source,target,interaction)
      update_nodes(source,story,interaction)
      return
    
def update_links(source,target,interaction):
    w = cf.weights.get(interaction)
    source_weight = w[0]
    target_weight = w[1]
    G[source][target][interaction].append((str(source),cur_date.strftime("%d/%m/%y"),(cur_date+cf.two_weeks).strftime("%d/%m/%y")))

def update_nodes(source,target,interaction):
    w = cf.weights.get(interaction)
    source_weight = w[0]
    target_weight = w[1]
    G.nodes[source][interaction].append((str(source),cur_date.strftime("%d/%m/%y"),(cur_date+cf.two_weeks).strftime("%d/%m/%y")))    
    G.nodes[target][interaction].append((str(source),cur_date.strftime("%d/%m/%y"),(cur_date+cf.two_weeks).strftime("%d/%m/%y")))    

  
def do_random_thing():
  num = random.randint(1,9)
  if num == 1 or num == 2:
    create_story(get_users(False)[0])
  elif num == 3 or num == 4:
    story_interact('read')
  elif num == 5 or num == 6:
    story_interact('comment')
  elif num == 7:
    user_interact('talk')
  elif num == 8:
    user_interact('give')
  else:
    story_interact('share')

cur_date = datetime.datetime.now()
G=nx.Graph()
counter = 0

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
    G = nx.convert_node_labels_to_integers(G)
    '''
    if len(G.nodes()) == cf.USERS-1:
        cf.colluding_nodes = random.sample(G.nodes(),cf.NUM_COLLUDERS)
        #So they have something to interact with
        for i in range(cf.NUM_COLLUDERS):
            print 'colluder is ',cf.colluding_nodes[i]
            create_story(cf.colluding_nodes[i])
    '''        
  for i in range(cf.ACTIONS_PER_DAY):
    do_random_thing()
  G = nx.convert_node_labels_to_integers(G)

  if counter % 30 == 0:
    pos = nx.spring_layout(G)
    edge_labels = {}
    filename = "test"+str(counter)+".gexf"
    print 'filename is ',filename
    nx.write_gexf(G, filename)

kcore.calculate(G)
kcore.plotgraph(G)