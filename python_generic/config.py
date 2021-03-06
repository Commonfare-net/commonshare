import datetime

#Output directories
GRAPHDIR = '../data/output/generic/graphdata/'
USERDIR = '../data/output/generic/userdata/'

#Simulation things
DAYS = 365
TAGS = 10
INITIAL_USERS = 40
ACTIONS_PER_DAY = 8
SHOULD_CLIQUE = True
SHOULD_COLLUDE = True
NUM_COLLUDERS = 2
SPAMMERID = 22
colluding_nodes = []
oneyear = 365*24*3600

#General purpose things

FREQUENCY_THRESHOLD = 5
PERCENTAGE_THRESHOLD = 45

#ADD_VIZ_STUFF = False
DIRECTED = False
user_type = ""
tag_type = ""

#These are all read in from the config.txt file now 
interaction_keys =[]
meta_networks = []

#Meta-data to add to nodes and edges based on actions
interaction_types = dict()
weights = dict()

WEIGHT_KEY = ""
LABEL_KEY = ""          
def stamp_to_str(timestamp):
    try:
        return to_str(datetime.datetime.fromtimestamp(timestamp))
    except Exception as e:
        timestamp = timestamp / 1000 #Maybe it's in milliseconds
        return to_str(datetime.datetime.fromtimestamp(timestamp))
        
def to_str(date):
    """Convert datetime date to string

    :param date: a datetime date
    :returns: String representation in form Year/month/day
    """
    try:
        return datetime.datetime.strftime(date,"%Y/%m/%d %H:%M")
    except Exception as e:
        print (date)
        
def to_date(str):
    """Convert date-formatted string to datetime date 

    :param str: string in form Year/month/day 
    :returns: a datetime date

    """
    
    try:
        return datetime.datetime.strptime(str,"%Y/%m/%d %H:%M")
    except ValueError:
        return datetime.datetime.strptime(str,"%Y/%m/%d")

def in_date(window,date_str):
    """Check if date is within a given time window

    :param window: 2-tuple of start and end dates 
    :param date_str: date-formatted string
    :returns: bool (True if date is within window)
    """
    return window[0] <= to_date(date_str) < window[1]