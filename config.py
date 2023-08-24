from mongoengine import connect
# import pymongo
# from pymongo import MongoClient

# client = connect('studentprofiles',host='localhost',port=27017)

connection_string = "mongodb+srv://saralkumar001:PoUhiEHIBBP970Xf@cluster0.pv0sybl.mongodb.net/studentprofiles?ssl=true"
client=connect(host=connection_string)

# from retrying import retry
# from mongoengine import connect
# import pymongo.errors

# @retry(wait_fixed=2000, stop_max_attempt_number=5)
# def connect_to_mongodb():
#     try:
#         connection_string = "mongodb+srv://saralkumar001:PoUhiEHIBBP970Xf@cluster0.pv0sybl.mongodb.net/studentprofiles?ssl=true"
#         client = connect(host=connection_string)
#         return client
#     except pymongo.errors.ServerSelectionTimeoutError as e:
#         print("Connection failed. Retrying...")
#         raise e

# db_client = connect_to_mongodb()