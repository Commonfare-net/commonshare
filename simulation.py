import config as cf
import datetime
import networkx as nx
import dynetworkx as dx
import time
import math
import random
import kcore
from graphclasses import *

#Some constants
starttime = time.time()
cur_date = datetime.datetime.now()
G=nx.Graph()
counter = 0
def get_users(need_two_users):
  type=nx.get_node_attributes(G,'type')
  all_users = False
  #Randomly determine whether colluding nodes get detected
  random_no = random.randint(1,10)
  while True:
    if need_two_users:
      if cf.SHOULD_COLLUDE and random_no > 7:
        #Which order?
        return random.sample(cf.colluding_nodes,2)
        #if random_no > 9:
        #    return cf.colluding_nodes
        #else:
        #    return [cf.colluding_nodes[1],cf.colluding_nodes[0]]
      else:
          users = random.sample(G.nodes(),2)
          if type[users[0]] == 'user' and type[users[1]] == 'user' and users[0] not in cf.colluding_nodes and users[1] not in cf.colluding_nodes:
            break
    else:
      users = random.sample(G.nodes(),1)
      if type[users[0]] == 'user':
        break      
  return users    


def create_story(user):
  #user = get_users(False)[0]
  e = Edge()
  story = Story()
  G.add_node(story)
  nx.set_node_attributes(G,{story: {'type': 'story','title':unicode(str(story)),'read':[],'comment':[],'share':[],'talk':[],'give':[]}})
  G.nodes[story]['spells'] = [(cur_date.strftime("%d/%m/%y"),(cur_date+cf.one_month).strftime("%d/%m/%y"))]
  #G.nodes[story]['size'] = [(5,cur_date,(cur_date+cf.oneyear))]
  G.add_edge(user,story,read=[],comment=[],share=[],create=[],talk=[],give=[])
  
  #last_creator = G.nodes[user]['size'][-1]
  #last_size = last_creator[0]
  #updated_last_creator = (last_size,last_creator[1],cur_date)
  #G.nodes[user]['size'][-1] = updated_last_creator
  #G.nodes[user]['size'].append((last_size+10,cur_date,(cur_date+cf.oneyear)))
  G.nodes[user]['create'].append((str(user),cur_date.strftime("%d/%m/%y"),cur_date.strftime("%d/%m/%y")))    
    
  #G[user][story]['created'] = []
  #G[user][story]['edited'] = []
  #G[user][story]['impact'] = []
  G[user][story]['spells'] = [(cur_date.strftime("%d/%m/%y"),(cur_date+cf.one_month).strftime("%d/%m/%y"))]
  G[user][story]['create'].append((str(user),cur_date.strftime("%d/%m/%y"),cur_date.strftime("%d/%m/%y") ))
  G.nodes[story]['viz'] = {}
  G.nodes[story]['viz']['color'] = {'r' : 254, 'g' : 0, 'b' : 0, 'a':1.0}
# print user,'created story',story

'''
#Method to edit a story
def edit_story():
  user = get_users(False)[0]
  for story in G.neighbors(user):
      type=nx.get_node_attributes(G,'type')
      if type[story] == 'story' and 'created' in G[user][story]:
        print user, 'edited story', story
        if len(G[user][story]['edited']) > 0:
          last_edit = G[user][story]['edited'][-1]
          updated_last_edit = (last_edit[0],last_edit[1],cur_date )
          G[user][story]['edited'][-1] = updated_last_edit
        G[user][story]['edited'].append(('10',cur_date ,(cur_date+oneyear) ))
        returnp
 # print 'User',user,'has no story to edit'	  
  
def delete_story():
  user = get_users(False)[0]
  for story in G.neighbors(user):
    type=nx.get_node_attributes(G,'type')
    if type[story] == 'story' and 'created' in G[user][story]:
      print user, 'deleted story', story
      #Set spell end of edge and noode to now
      edgespelltuple = G[user][story]['spells'][-1]
      nodespelltuple = G.nodes[story]['spells'][-1]
      updated_edge_spell = (edgespelltuple[0],cur_date)
      updated_node_spell = (nodespelltuple[0],cur_date)
      G[user][story]['spells'][-1] = updated_edge_spell
      G.nodes[story]['spells'][-1] = updated_node_spell
      return
 # print 'User',user,'has no story to delete'	
'''

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
  G[source][target]['spells'].append((cur_date.strftime("%d/%m/%y"),(cur_date+cf.one_month).strftime("%d/%m/%y")))
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
   #Update the strength of the links between source user, target user, and story
    #last_impact = G[source][target]['impact'][-1:]
    #if len(last_impact) > 0:
    #    #last_impact = last_impact[0]
    ##    last = last_impact[0]
     #   last_impact = last[0]
     #   updated_last_impact = (last_impact,last[1],cur_date)
        #G[source][target]['impact'][-1] = updated_last_impact
        #G[source][target]['impact'].append((last_impact+source_weight,cur_date,(cur_date+cf.one_month)))
    #else:
    #    G[source][target]['impact'].append((source_weight,cur_date,(cur_date+cf.one_month)))
    G[source][target][interaction].append((str(source),cur_date.strftime("%d/%m/%y"),cur_date.strftime("%d/%m/%y")))

def update_nodes(source,target,interaction):
    w = cf.weights.get(interaction)
    source_weight = w[0]
    target_weight = w[1]
#    last_source = G.nodes[source]['size'][-1]
#    last_size = last_source[0]
#    updated_last_source = (last_size,last_source[1],cur_date)
    #G.nodes[source]['size'][-1] = updated_last_source
    #G.nodes[source]['size'].append((last_size+source_weight,cur_date,(cur_date+cf.one_month)))
    G.nodes[source][interaction].append((str(source),cur_date.strftime("%d/%m/%y"),cur_date.strftime("%d/%m/%y")))    
    
    #last_target = G.nodes[target]['size'][-1]
 #   last_size = last_target[0]
 #   updated_last_target = (last_size,last_target[1],cur_date)
    #G.nodes[target]['size'][-1] = updated_last_target
    #G.nodes[target]['size'].append((last_size+target_weight,cur_date,(cur_date+cf.one_month)))  
    G.nodes[target][interaction].append((str(source),cur_date.strftime("%d/%m/%y"),cur_date.strftime("%d/%m/%y")))    

  
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

while counter < cf.DAYS:
  cur_date = cur_date + cf.one_day
  counter = counter + 1
  #print "tick"
 # time.sleep(0.2 - ((time.time() - starttime) % 0.2))
  G = nx.convert_node_labels_to_integers(G)
  while len(G.nodes()) < cf.USERS:
    user = User()
    G.add_node(user)
    nx.set_node_attributes(G,{user: {'type': 'user','name': str(user),'read':[],'comment':[],'share':[],'create':[],'talk':[],'give':[]}})
    G.nodes[user]['spells'] = [(cur_date.strftime("%d/%m/%y"),None)]
   # G.nodes[user]['size'] = [(5,cur_date,(cur_date+cf.oneyear))]
    G.nodes[user]['viz'] = {}
    G.nodes[user]['viz']['color'] = {'r' : 0, 'g' : 0, 'b' : 254, 'a':1.0}
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

  #print 'curdate is ',cur_date  
  if counter % 60 == 0:
    pos = nx.spring_layout(G)
    edge_labels = {}
    filename = "test"+str(counter)+".gexf"
    print 'filename is ',filename
    nx.write_gexf(G, filename)

print 'let us get the k core'
kcore.calculate(G)
print 'now let us plot the graph'
kcore.plotgraph(G)