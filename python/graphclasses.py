#Generates random usernames
import names
#Generates random listing names
import listinggenerator
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

    def __get_tags__(self):
        return phrases.random_tags()
		
class Story(object):

    def __init__(self):
        self.__name = phrases.random_phrase()	
        self.__tags = phrases.random_tags()
        
    def __str__(self):
        return self.__name

    def __repr__(self):
        return str(self)		

    def __get_tags__(self):
        return self.__tags

class ForumPost(object):

    def __init__(self):
        self.__name = listinggenerator.random_listing()
        self.__tags = phrases.random_tags()
        
    def __str__(self):
        return self.__name

    def __repr__(self):
        return str(self)		

    def __get_tags__(self):
        return self.__tags        
class Group(object):

    def __init__(self):
       print ''      