import datetime

#Output directories
GRAPHDIR = '../data/output/graphdata/'
USERDIR = '../data/output/userdata/'
RECOMMEND_FILE = '../data/output/recommenderdata.gexf'

#Constants for simulation
DAYS = 365
TAGS = 10
INITIAL_USERS = 40
ACTIONS_PER_DAY = 8
SHOULD_COLLUDE = True
NUM_COLLUDERS = 2
colluding_nodes = []

#Holds maximum edge weight for a given time step - do not adjust
MAX_WEIGHT = 0

#Collusion things
FREQUENCY_THRESHOLD = 5
PERCENTAGE_THRESHOLD = 33

SPACING = 'biweekly' #or use 'weekly' or 'monthly'

COMMUNITY_SIM = 0.25 #Jaccard similarity coefficient needed for two communities to be considered the same

#Keys are interaction types, values are a list containing:
#meta network, sender weight, receiver weight
INTERACTIONS = {"comment_story":['story',2,2],
"create_story": ['story',3,1],
"tag_story": ['story',0,0],
"comment_listing": ['listing',1,1],
"create_listing": ['listing',2,1],
"tag_listing": ['listing',0,0],
"conversation": ['social',5,5],
"transaction": ['transaction',4,4],
"tag_commoner": ['',0,0]
}

TYPES = ['story','listing','social','transaction']

def to_str(date):
    """Convert datetime date to string

    :param date: a datetime date
    :returns: String representation in form Year/month/day
    """
    return datetime.datetime.strftime(date,"%Y/%m/%d")

def to_date(str):
    """Convert date-formatted string to datetime date 

    :param str: string in form Year/month/day 
    :returns: a datetime date

    """
    return datetime.datetime.strptime(str,"%Y/%m/%d")
    
def in_date(window,date_str):
    """Check if date is within a given time window

    :param window: 2-tuple of start and end dates 
    :param date_str: date-formatted string
    :returns: bool (True if date is within window)
    """
    return window[0] <= to_date(date_str) < window[1]