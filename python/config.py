import datetime

DAYS = 365
USERS = 50
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
like_story="like_Story"
comment_story="comment_Story"
create_story="create_Story"
friendship="friendship"
transaction="transaction"
create_post="create_ForumPost"
like_post="like_ForumPost"
comment_post="comment_ForumPost"
#accept_post="accept_post"
interaction_keys =[like_story,comment_story,create_story,friendship,transaction,create_post,like_post,comment_post]
indirect_interactions = [like_story,comment_story,like_post,comment_post]
meta_networks = ['story','discussion','social','transaction']
#Meta-data to add to nodes and edges based on actions
meta = {like_story:'story',
        comment_story:'story',
        create_story:'story',
        like_post:'discussion',
        comment_post:'discussion',
        create_post:'discussion',
        friendship:'social',
        transaction:'transaction'
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
weights = {like_story:(0,1),
           comment_story:(2,2),
           create_story:(2,0),
#Friendship-based interactions
           friendship:(10,10),
#Transaction-based interactions
           transaction:(5,5),
#Forum-based interactions
           create_post:(2,0),
           like_post:(0,1),
           comment_post:(2,2)}
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