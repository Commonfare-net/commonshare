import datetime

DAYS = 365
TAGS = 70
INITIAL_USERS = 50
ACTIONS_PER_DAY = 10

#Collusion things

SHOULD_CLIQUE = False
SHOULD_COLLUDE = True
NUM_COLLUDERS = 3
SPAMMERID = 22
FREQUENCY_THRESHOLD = 5
REPUTATION_THRESHOLD = 30
PERCENTAGE_THRESHOLD = 35
oneyear = 365*24*3600
two_weeks = datetime.timedelta(days=14)
one_day = datetime.timedelta(days=1)
one_year = datetime.timedelta(days=365)
epoch = datetime.datetime.utcfromtimestamp(0)

comment_story="comment_story"
comment_listing="comment_listing"
create_story="create_story"
create_listing="create_listing"
conversation="conversation"
transaction="transaction"
tag_story="tag_story"
tag_listing="tag_listing"
tag_commoner="tag_commoner"
mutual_interactions = [conversation,transaction]
interaction_keys =[comment_story,comment_listing,create_story,create_listing,conversation,transaction,tag_commoner,tag_story,tag_listing]
indirect_interactions = [comment_story,comment_listing]
meta_networks = ['story','listing','social','transaction']
#Meta-data to add to nodes and edges based on actions

meta = {
        comment_story:'story',
        create_story:'story',
        tag_story:'story',
        comment_listing:'listing',
        create_listing:'listing',
        tag_listing:'listing',
        conversation:'social',
        transaction:'transaction',
        tag_commoner:''
        }

#Story-based interactions
weights = {
           tag_commoner:(0,2),
           comment_story:(2,2),
           create_story:(2,2),
           tag_story:(0,2),
#Friendship-based interactions
           conversation:(4,4),
#Transaction-based interactions
           transaction:(4,4),
#Forum-based interactions
           create_listing:(2,2),
           comment_listing:(2,2),
           tag_listing:(0,2)
           }
