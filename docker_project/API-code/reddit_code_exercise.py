import requests
from config import tokens  #importing the dictionary called tokens
import pymongo
import time

# 2. Prepare authentication information for requesting a temporary access token.
auth = requests.auth.HTTPBasicAuth(tokens['public'], tokens['secret'])
grant_information = {'grant_type': 'password',
        'username': tokens['username'],
        'password': tokens['password']}
headers = {'User-Agent': 'Sumac_Imbalance_S'} # !!! name der API, die ich kreiert hab
#tocken/website info in variable auth

# 3. Get the access token
res = requests.post('https://www.reddit.com/api/v1/access_token',
                auth=auth, data=grant_information , headers=headers)

#print(res.json()['access_token'])
# dict1(k1,v1) + dict2 (k2, v2) => dict3 (k1: v1, k3:v2) 2 key-value paare
# 3. Add token to the connection header.
headers = {**headers, **{'Authorization': f"bearer {res.json()['access_token']}"}}

# Send a get request to download most popular subreddits.
topic = 'DnD' # add a topic of your interest
URL = f"https://oauth.reddit.com/r/{topic}/"
res = requests.get(url=URL, headers=headers)

#print(res.json())
#print(res.json()['data'])
#print(res.json()['data']['after'])

#Crazy experiment Timestamps
# mongo_input = {}
# counter_fake = 0
# counter = 0
# for post in res.json()['data']['children']:
#         if post['data']['selftext'] == '':
#                 continue
#         else:
#                 counter_fake += 1
#                 if counter_fake >= 3:
#                         counter += 1
#                         timestamp = post['data']['created_utc']  # Extracting the timestamp
#                         posting_time = time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(timestamp))  # Convert to readable format
#                         mongo_input[str(counter)] = {
#                         'posting_time': posting_time,
#                         'selftext': post['data']['selftext']}


# 4. Prepare mongo input
mongo_input = {}
counter_fake = 0
counter = 0
for post in res.json()['data']['children']:   #only one children, followed by posts-s
        if post['data']['selftext']== '':
                continue
        else:
                counter_fake += 1
                if counter_fake >= 3:
                        counter += 1
        #text = post['data']['title'] #text not part of output-s
                        mongo_input['counter'] = counter
                        mongo_input['reddit'] = post['data']['selftext']

#dictionary erstellt und counter (i) wird index, während post value is-s

logging.critical(mongo_input)
client = pymongo.MongoClient('my_mongo', port=27017)  # my_mongo is the hostname (= service in yml file)
db = client.my_db

dbcoll = db.my_collection
#table
dbcoll.insert_one(mongo_input)
#insert downloaded stuff into mongo
