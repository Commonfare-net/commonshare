import names
import listinggenerator
import phrases
		
class user(object):
    """Class representing a user node"""

    def __init__(self):
        self.__name = names.get_full_name()

    def __str__(self):
        return self.__name

    def __repr__(self):
        return str(self)	

		
class story(object):
    """Class representing a story node"""

    def __init__(self):
        self.__name = phrases.random_phrase()	
        
    def __str__(self):
        return self.__name

    def __repr__(self):
        return str(self)		


class listing(object):
    """Class representing a listing node"""

    def __init__(self):
        self.__name = listinggenerator.random_listing()
        
    def __str__(self):
        return self.__name

    def __repr__(self):
        return str(self)		


class tag(object):
    """Class representing a tag node"""

    def __init__(self):
        self.__name = phrases.random_tag()	
        
    def __str__(self):
        return self.__name

    def __repr__(self):
        return str(self)	
          