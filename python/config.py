import datetime

DAYS = 365
TAGS = 10
INITIAL_USERS = 40
ACTIONS_PER_DAY = 8

#Collusion things
FREQUENCY_THRESHOLD = 5
PERCENTAGE_THRESHOLD = 33

SHOULD_CLIQUE = True
SHOULD_COLLUDE = True
NUM_COLLUDERS = 2
SPAMMERID = 22
MAX_WEIGHT = 0
colluding_nodes = []
oneyear = 365*24*3600
two_weeks = datetime.timedelta(days=14)
one_day = datetime.timedelta(days=1)
one_year = datetime.timedelta(days=365)
epoch = datetime.datetime.utcfromtimestamp(0)

comment_story="comment_story"
rcomment_story="rcomment_story"
comment_listing="comment_listing"
rcomment_listing="rcomment_listing"
create_story="create_story"
rcreate_story="rcreate_story"
create_listing="create_listing"
rcreate_listing="rcreate_listing"
conversation="conversation"
rconversation="rconversation"
transaction="transaction"
rtransaction="rtransaction"
tag_story="tag_story"
tag_listing="tag_listing"
tag_commoner="tag_commoner"
mutual_interactions = [conversation,transaction]

interaction_keys =[comment_story,rcomment_story,
comment_listing,rcomment_listing,
create_story,rcreate_story,
create_listing,rcreate_listing,
conversation,rconversation,
transaction,rtransaction,
tag_commoner,tag_story,tag_listing]
indirect_interactions = [comment_story,comment_listing]
meta_networks = ['story','listing','social','transaction']

#Meta-data to add to nodes and edges based on actions
interaction_types = {
        comment_story:'story',
        rcomment_story:'story',
        create_story:'story',
        rcreate_story:'story',
        tag_story:'story',
        comment_listing:'listing',
        rcomment_listing:'listing',
        create_listing:'listing',
        rcreate_listing:'listing',
        tag_listing:'listing',
        conversation:'social',
        rconversation:'social',
        transaction:'transaction',
        rtransaction:'transaction',
        tag_commoner:''
        }

#Story-based interactions
weights = {
           tag_commoner:0,
           comment_story:2,
           rcomment_story:2,
           create_story:3,
           rcreate_story:1,
           tag_story:0,
#Friendship-based interactions
           conversation:5,
           rconversation:5,
#Transaction-based interactions
           transaction:4,
           rtransaction:4,
#Forum-based interactions
           create_listing:2,
           rcreate_listing:1,
           comment_listing:1,
           rcomment_listing:2,
           tag_listing:0
           }
          
#Story-based interactions
no_weights = {
           tag_commoner:0,
           comment_story:1,
           rcomment_story:1,
           create_story:1,
           rcreate_story:1,
           tag_story:0,
#Friendship-based interactions
           conversation:1,
           rconversation:1,
#Transaction-based interactions
           transaction:1,
           rtransaction:1,
#Forum-based interactions
           create_listing:1,
           rcreate_listing:1,
           comment_listing:1,
           rcomment_listing:1,
           tag_listing:0
           }
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