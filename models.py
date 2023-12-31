from mongoengine import *

class adminDetails(Document):
	admin = StringField()
	password = StringField()
	is_admin = BooleanField()


class StudentRegistration(Document):
    username = StringField(required=True)
    fullname = StringField(required=True)
    email = StringField(required=True)
    phone = StringField(required=True)
    password = StringField(required=True)
    verified = BooleanField(default=False)
    user_activation = BooleanField(default=False)
    created_on = DateTimeField()
    verification_token = StringField()
    status = IntField(default=0)
    optionStatus = IntField(default=0)
    viewOptionStatus = IntField(default=0)


class StudentProfile(Document):
	userName = StringField()
	email = StringField()
	phoneNumber = StringField()
	profilePic = StringField()
	website = StringField()
	addressList = DictField()
	careerObjective = StringField()
	socialMedia = DictField()
	experienceList = DictField()
	skillsList = DictField()
	hobbies = StringField()
	fullname = StringField()
	createdOn = DateTimeField()
	status = IntField()
	studentId = ObjectIdField()
	

