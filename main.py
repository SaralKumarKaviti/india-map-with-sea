from flask import Flask, render_template, request, redirect, url_for, make_response,flash
from config import client
from models import *
import secrets
import datetime
from bson import ObjectId
# from datetime import datetime
from random import randint
import os

app = Flask(__name__)

app.secret_key='my_key'

UPLOAD_FOLDER = 'static/images/profiles'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif','mp4'}


@app.route("/")
def index():
    return render_template('india.html')

@app.route("/addStudentProfile",methods=['POST','GET'])
def addStudentProfile():
    createdOn = datetime.datetime.now()
    experience_list = []
    experience_dict = {}
    skill_list = []
    skill_dict = {}
    media_list = []
    media_dict = {}
    skill_details ={}

    if request.method == 'POST':
        profilePic = request.files['profilePic']
        if not profilePic.filename:
            flash("Profile picture file should be uploaded.", "error")
            return redirect(url_for('addStudentProfile'))
        

        if profilePic.filename.rsplit('.',1)[1].lower() in ALLOWED_EXTENSIONS:
            ext = profilePic.filename.rsplit('.',1)[1].lower()
            # file_name = str(hs_reg_id)+"."+ext
            file_name = "samplefile"+"."+ext
            if not os.path.exists(app.config['UPLOAD_FOLDER']):
                os.mkdir(app.config['UPLOAD_FOLDER'])
            profile = app.config['UPLOAD_FOLDER']
            profilePic.save(os.path.join(profile,file_name))

        website = request.form.get('website')
        if website:
            processed_website = website
        else:
            processed_website = ""

        careerObjective = request.form.get('careerObjective')
        if careerObjective:
            processed_carrer = careerObjective
        else:
            processed_carrer = ""

        total_experience_entries = int(request.form.get('totalExperienceEntries'))
        
        for epd in range(1, total_experience_entries + 1):
            company_name = request.form.get('companyName' + str(epd))
            role = request.form.get('role' + str(epd))
            from_year = request.form.get('fromYear' + str(epd))
            to_year = request.form.get('toYear' + str(epd))
            project_desc = request.form.get('projectDesc' + str(epd))

            if company_name and role and from_year and to_year and project_desc and request.method == 'POST':
                experience_dict = {
                    'companyName' + str(epd): company_name,
                    'role' + str(epd): role,
                    'from_year' + str(epd): from_year,
                    'to_year' + str(epd): to_year,
                    'projectDesc' + str(epd): project_desc
                }
                experience_list.append(experience_dict)
            else:
                experience_list.append({})
        experience_details = {
            "experienceDetails": experience_list
            }
        total_skill_entries = int(request.form.get('totalskills'))
        skill_perc = 0
        for sk in range(1,total_skill_entries + 1):
            tech_name = request.form.get('technologyName' + str(sk))
            skill_level = request.form.get('skillLevel' + str(sk))

            if tech_name and skill_level and request.method == 'POST':
                if skill_level == 'Beginner':
                    skill_perc = 40
                elif skill_level == 'Intermediate':
                    skill_perc = 50
                elif skill_level == 'Advanced':
                    skill_perc = 60
                elif skill_level == 'Professional':
                    skill_perc = 80
                elif skill_level == 'Master':
                    skill_perc = 100
                else:
                    error = "Something went wrong!"
                skill_dict ={
                    "technologyName" + str(sk) : tech_name,
                    "skillLevel" + str(sk) : skill_perc
                }

                skill_list.append(skill_dict)
            else:
                skill_list.append({})

        skill_details = {
            "skillsDetails" : skill_list
        }

        total_media = int(request.form.get('totalMedia'))
        for sm in range(1,total_media + 1):
            media_name = request.form.get('socialMedia' + str(sm))
            url = request.form.get('socialMediaURL' + str(sm))

            if media_name and url and request.method == 'POST':
                media_dict ={
                    "socialMedia" + str(sm) : media_name,
                    "socialMediaURL" + str(sm) : url
                }

                media_list.append(media_dict)
            else:
                media_list.append({})

        media_details = {
            "socialMediaDetails" : media_list
        }

        # print(experience_details)
        pincode = request.form.get('pincode')
        if not pincode:
            flash("Please enter pincode")
        else:
            address_details={
                "pincode":pincode,
                "state":request.form.get('state'),
                "district":request.form.get('district'),
                "mandal":request.form.get('mandal'),
                "village":request.form.get('village'),
                "country":request.form.get('country')
            }

        hobbies = request.form.get('hobbies')
        

        if profilePic and pincode and request.method == 'POST':
            add_profile=StudentProfile(
                profilePic=file_name,
                website = processed_website,
                careerObjective = processed_carrer,
                experienceList = experience_details,
                skillsList = skill_details,
                socialMedia = media_details,
                addressList = address_details,
                hobbies=hobbies,
                createdOn = createdOn,
                status = 1
                )
            add_profile.save()
            
            flash("Data Submitted successfully !")
            return redirect(url_for('addStudentProfile'))
        else:
            flash("Something went wrong! Please check your details once!!")

    
    return render_template('student/add_profile.html')

@app.route("/profile",methods=['POST','GET'])
def studentProfile():

    return render_template('student/profile.html')

# def address(pincode):
#     import requests
#     import json
#     end_point = "https://api.postalpincode.in/pincode/"
#     response = requests.get(end_point + pincode)
#     data = json.loads(response.text)
#     if data[0]['Status'] == 'Success':
#         details = data[0]['PostOffice'][0]
#         state = details['State']
#         district = details['District']
#         mandal = details['Block']
#         village = details['Name']
#         return f"State: {state}, District: {district}, Mandal: {mandal}, Village: {village}"
#     else:
#         return "Pincode not found."

# # Example usage
# pincode = "500001"  # Replace with the desired pincode
# result = address(pincode)
# print(result)  # This will print the extracted details


if __name__ == '__main__':
    app.run(debug=True)

