import datetime

DAYS = 30
USERS = 5
ACTIONS_PER_DAY = 2

#Collusion things

SHOULD_COLLUDE = False
NUM_COLLUDERS = 4
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
read_key = "read"
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

weights = {read_key:(2,1),
           comment_key:(4,1),
           share_key:(4,1),
           create_key:(6,0),
           talk_key:(8,4),
           give_key:(10,3),
           create_listing_key:(5,0),
           comment_listing_key:(0,0),
           create_provision_key:(0,0),
           comment_provision_key:(0,0),
           share_provision_key:(0,0),
           share_provision_key:(0,0)}

def utmillis(dt):
    return (dt - epoch).total_seconds()