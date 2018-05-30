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