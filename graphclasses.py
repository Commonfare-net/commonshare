#Generates random usernames
import names
#Generates random story names
import phrases
class Edge(object):

    def __init__(self):
	    self.weight = 0
	    self.dict = {}

    def __str__(self):
        return self.__name

    def __repr__(self):
        return str(self)			
class User(object):

    def __init__(self):
        self.__name = names.get_full_name()

    def __str__(self):
        return self.__name

    def __repr__(self):
        return str(self)	
		
class Story(object):

    def __init__(self):
	    self.__name = phrases.random_phrase()	

    def __str__(self):
        return self.__name

    def __repr__(self):
        return str(self)			
class Group(object):

    def __init__(self):
       print ''
		
#I wonder whether this is necessary, could extrapolate from the impact the interaction has?
'''
#Is this the first time this specific interaction has taken place?
if interaction not in G[source][story]:
G[source][story]['read'] = []
#Otherwise the timeframe of the last interaction of this type needs to be updated
elif len(G[source][story]['read']) > 0:
last_interaction = G[source][story][interaction][-1]
updated_last_interaction = (last_interaction[0],last_interaction[1],cur_date.strftime("%y-%m-%dT%H:%M") )
G[source][story][interaction][-1] = updated_last_interaction    
'''        