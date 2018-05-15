from pymongo import MongoClient
import pprint

key = {"bread": {"brand1": 10, "brand2" : 23},
       "thanh": "1147",
       "faraz": "7141",
       "admin": "pass"}


client = MongoClient("localhost", 27017)
db = client.test_keys
db.test_keys.remove({})
db.test_keys.insert(key)

posts = db.test_keys
post_id = posts.insert_one(posts).inserted_id
doc = posts.find_one()

for k in doc:
    print (k)

