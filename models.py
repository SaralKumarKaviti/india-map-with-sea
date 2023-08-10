from mongoengine import *


class StudentProfile(Document):
	#studentId = RefernceField('')
	profilePic = StringField()
	website = StringField()
	addressList = DictField()
	careerObjective = StringField()
	socialMedia = DictField()
	experienceList = DictField()
	skillsList = DictField()
	hobbies = StringField()
	createdOn = DateTimeField()
	status = IntField()

