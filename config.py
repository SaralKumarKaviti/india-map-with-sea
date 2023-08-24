from mongoengine import connect
# import pymongo
# from pymongo import MongoClient

# client = connect('studentprofiles',host='localhost',port=27017)

connection_string = "mongodb+srv://saralkumar001:PoUhiEHIBBP970Xf@cluster0.pv0sybl.mongodb.net/studentprofiles"
client=connect(host=connection_string)