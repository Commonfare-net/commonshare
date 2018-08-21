#Generates random usernames
import names
#Generates random listing names
import listinggenerator
#Generates random story names
import phrases
		
class user(object):

    def __init__(self):
        self.__name = names.get_full_name()

    def __str__(self):
        return self.__name

    def __repr__(self):
        return str(self)	

		
class story(object):

    def __init__(self):
        self.__name = phrases.random_phrase()	
        
    def __str__(self):
        return self.__name

    def __repr__(self):
        return str(self)		


class listing(object):

    def __init__(self):
        self.__name = listinggenerator.random_listing()
        
    def __str__(self):
        return self.__name

    def __repr__(self):
        return str(self)		


class tag(object):

    def __init__(self):
        self.__name = phrases.random_tag()	
        
    def __str__(self):
        return self.__name

    def __repr__(self):
        return str(self)	
        
class Group(object):

    def __init__(self):
       print ''      