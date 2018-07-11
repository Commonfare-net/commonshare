import datetime

DAYS = 365
TAGS = 50
INITIAL_USERS = 500
ACTIONS_PER_DAY = 30

#Collusion things

SHOULD_CLIQUE = False
SHOULD_COLLUDE = True
NUM_COLLUDERS = 3
FREQUENCY_THRESHOLD = 5
REPUTATION_THRESHOLD = 30
PERCENTAGE_THRESHOLD = 36
defaultexpiry = 3600*24*365
oneyear = 365*24*3600
two_weeks = datetime.timedelta(days=14)
tenyears = oneyear*10
one_day = datetime.timedelta(days=1)
one_month = datetime.timedelta(days=30)
one_year = datetime.timedelta(days=365)
epoch = datetime.datetime.utcfromtimestamp(0)

DEPRECIATION = 2.5
comment_story="comment_story"
comment_listing="comment_listing"
create_story="create_story"
create_listing="create_listing"
conversation="conversation"
transaction="transaction"
tag_story="tag_story"
tag_listing="tag_listing"
tag_commoner="tag_commoner"
#accept_post="accept_post"
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
        tag_commoner:'social'
        }

'''
comment_key = "comment"
share_key = "share"
create_key = "create"
talk_key = "talk"
give_key = "give"
create_listing_key = "create_list"
comment_listing_key = "comment_list"
create_provision_key = "create_prov"
comment_provision_key = "comment_prov"
share_provision_key = "share_prov"
interaction_keys = [read_key,comment_key,share_key,create_key,talk_key,give_key]
direct_interaction_keys = [talk_key,give_key]
#,create_listing_key,comment_listing_key,create_provision_key,comment_provision_key,share_provision_key]
'''

#Weighted, directed

#Story-based interactions
weights = {
           tag_commoner:(0,2),
           comment_story:(2,2),
           create_story:(2,2),
           tag_story:(0,2),
#Friendship-based interactions
           conversation:(10,10),
#Transaction-based interactions
           transaction:(5,5),
#Forum-based interactions
           create_listing:(2,2),
           comment_listing:(2,2),
           tag_listing:(0,2)
           }
'''           
#Unweighted
weights = {like_story:(1,1),
           comment_story:(1,1),
           create_story:(1,1),
#Friendship-based interactions
           friendship:(1,1),
#Transaction-based interactions
           transaction:(1,1),
#Forum-based interactions
           create_post:(1,1),
           like_post:(1,1),
           comment_post:(1,1),
           accept_post:(1,1)}

#Weighted, undirected

weights = {like_story:(1,1),
           comment_story:(2,2),
           create_story:(2,2),
#Friendship-based interactions
           friendship:(10,10),
#Transaction-based interactions
           transaction:(5,5),
#Forum-based interactions
           create_post:(2,2),
           like_post:(1,1),
           comment_post:(2,2),
           accept_post:(6,6)}           

'''
def utmillis(dt):
    return (dt - epoch).total_seconds()