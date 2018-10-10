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
transaction="transaction"
tag_story="tag_story"
tag_listing="tag_listing"
tag_commoner="tag_commoner"
mutual_interactions = [conversation,transaction]

interaction_keys =[comment_story,rcomment_story,comment_listing,rcomment_listing,create_story,rcreate_story,create_listing,rcreate_listing,conversation,transaction,tag_commoner,tag_story,tag_listing]
indirect_interactions = [comment_story,comment_listing]
meta_networks = ['story','listing','social','transaction']

#Meta-data to add to nodes and edges based on actions
interaction_types = {
        comment_story:'story',
        rcomment_story:'story',
        create_story:'story',
        rcreate_story:'story',
        tag_story:'story',
        comment_listing:'transaction',
        rcomment_listing:'transaction',
        create_listing:'transaction',
        rcreate_listing:'transaction',
        tag_listing:'transaction',
        conversation:'social',
        transaction:'transaction',
        tag_commoner:''
        }

#Story-based interactions
weights = {
           tag_commoner:0,
           comment_story:1,
           rcomment_story:2,
           create_story:2,
           rcreate_story:1,
           tag_story:0,
#Friendship-based interactions
           conversation:4,
#Transaction-based interactions
           transaction:4,
#Forum-based interactions
           create_listing:2,
           rcreate_listing:1,
           comment_listing:1,
           rcomment_listing:2,
           tag_listing:0
           }
