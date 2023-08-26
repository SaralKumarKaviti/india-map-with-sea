from mongoengine import connect
# import pymongo
# from pymongo import MongoClient

# client = connect('studentprofiles',host='localhost',port=27017)

connection_string = "mongodb+srv://saralkumar001:PoUhiEHIBBP970Xf@cluster0.pv0sybl.mongodb.net/studentprofiles?ssl=true&ssl_cert_reqs=CERT_NONE"
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

from pymongo import MongoClient
import ssl

# Replace this with your actual connection string
connection_string = "mongodb+srv://saralkumar001:PoUhiEHIBBP970Xf@cluster0.pv0sybl.mongodb.net/studentprofiles"

# Create a MongoClient instance using the connection string
client = MongoClient(connection_string, ssl=True, ssl_cert_reqs=ssl.CERT_NONE)

# Access the "studentprofiles" database
db = client.studentprofiles

# Now you can work with the database collections
# # For example:
# collection = db.students
# result = collection.find_one({"name": "John Doe"})
# print(result)

# Remember to close the connection when you're done
client.close()
