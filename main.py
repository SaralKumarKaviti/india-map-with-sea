from flask import Flask, render_template, request, redirect, url_for, make_response,flash
from config import client
from models import *
import secrets
import datetime
from bson import ObjectId
# from datetime import datetime
from random import randint
import os
from flask import jsonify

app = Flask(__name__)

app.secret_key='my_key'

UPLOAD_FOLDER = 'static/images/profiles'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif','mp4'}



@app.route('/images/profiles/<filename>')
def send_uploaded_profile_pic(filename=''):
    from flask import send_from_directory
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)

from flask import render_template


@app.route("/")
def index():
    return render_template('india.html')


@app.route("/getStateDetails/<state>")
def get_state_details(state):
    try:
        # Fetch student details for the specified state
        state_students = StudentProfile.objects(addressList__state=state)
        student_list = [{"name": "ss", "state": student.addressList["state"]} for student in state_students]

       
        if state == "Telangana":
            telangana_districts = get_telangana_districts()
            response = {
                "state_students": student_list,
                "state_districts": telangana_districts
            }

        elif state == "Andhra Pradesh":
            andhra_districts = get_andhra_districts()
            response = {
                "state_students": student_list,
                "state_districts": andhra_districts
            }

        else:
            response = {
                "state_students": student_list,
                "state_districts": []
            }
        
        
        return jsonify(response)
    except Exception as e:
        return jsonify({"error": str(e)})


def get_telangana_districts():
    try:
        # Fetch district data for Telangana from your MongoDB collection
        telangana_districts = StudentProfile.objects.filter(addressList__state="Telangana")

        # Prepare the data to match the format you need
        district_list = []
        for district_data in telangana_districts:
            district_info = {
                "name": district_data.addressList.get("district", ""),
                "value": "ee"
            }
            district_list.append(district_info)

        return district_list
    except Exception as e:
        print("Error fetching Telangana district data:", str(e))
        return []

def get_andhra_districts():
    try:
        # Fetch district data for Andhra Pradesh from your MongoDB collection
        andhra_districts = StudentProfile.objects.filter(addressList__state="Andhra Pradesh")

        # Prepare the data to match the format you need
        district_list = []
        for district_data in andhra_districts:
            district_info = {
                "name": district_data.addressList.get("district", ""),
                "value": "ee"
            }
            district_list.append(district_info)

        return district_list
    except Exception as e:
        print("Error fetching Andhra Pradesh district data:", str(e))
        return []

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
    experience_details={}
    media_details={}

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

        # total_experience_entries = int(request.form.get('totalExperienceEntries'))

        total_experience_entries = int(request.form.get('totalExperienceEntries'))
        experience_list = []  # Initialize an empty list to hold experience details

        for epd in range(1, total_experience_entries + 1):
            company_name = request.form.get('companyName' + str(epd))
            role = request.form.get('role' + str(epd))
            from_year = request.form.get('fromYear' + str(epd))
            to_year = request.form.get('toYear' + str(epd))
            project_desc = request.form.get('projectDesc' + str(epd))
            
            # Check if all key-value pairs are empty or None
            if all(value is None or value == '' for value in [company_name, role, from_year, to_year, project_desc]):
                # If all values are empty, skip this experienceDetails object
                continue
            
            experience_dict = {
                'companyName': company_name,
                'role': role,
                'from_year': from_year,
                'to_year': to_year,
                'projectDesc': project_desc
            }
            experience_list.append(experience_dict)

        # Check if the entire experienceDetails array is empty
        if not experience_list:
            # Handle the case when all objects in experienceDetails are empty
            # For example, you can set a default value or skip creating the experienceList object
            default_experience = {
                'companyName': '',
                'role': '',
                'from_year': '',
                'to_year': '',
                'projectDesc': ''
            }
            experience_list.append(default_experience)
            
        else:
            experience_details = {
                "experienceDetails": experience_list
            }


        total_skill_entries = int(request.form.get('totalskills'))
        skill_list = []  # Initialize an empty list to hold skill details
        
        for sk in range(1, total_skill_entries + 1):
            tech_name = request.form.get('technologyName' + str(sk))
            skill_level = request.form.get('skillLevel' + str(sk))
            
            # Check if all key-value pairs are empty or None
            if all(value is None or value == '' for value in [tech_name, skill_level]):
                # If all values are empty, skip this experienceDetails object
                continue
                

            
            skill_dict = {
                'techName': tech_name,
                'skillLevel': skill_level,
            }
            skill_list.append(skill_dict)

        # Check if the entire experienceDetails array is empty
        if not skill_list:
            # Handle the case when all objects in experienceDetails are empty
            # For example, you can set a default value or skip creating the experienceList object
            default_skill= {
                'techName': '',
                'skillLevel': ''
            }
            skill_list.append(default_skill)
            
        else:
            skill_details = {
                "skillDetails": skill_list
            }

        

        total_media = int(request.form.get('totalMedia'))
        for sm in range(1,total_media + 1):
            media_name = request.form.get('socialMedia' + str(sm))
            url = request.form.get('socialMediaURL' + str(sm))
            if all(value is None or value == '' for value in [media_name, url]):
                # If all values are empty, skip this experienceDetails object
                continue
            if media_name and url and request.method == 'POST':
                media_dict ={
                    "socialMedia": media_name,
                    "socialMediaURL": url
                }

                media_list.append(media_dict)
        if not media_list:
            default_media = {
                "socialMedia" : "",
                "socialMediaURL":""
            }
            media_list.append(default_media)
        else:

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

@app.route("/profile/<ref>",methods=['POST','GET'])
def student_profile(ref):
    try:
        # Fetch the student profile using the provided ID
        student_liat=[]
        student_dict={}
        experience_info=[]
        media_detail={}
        
        student = StudentProfile.objects.get(ref=ref)
        if student:
            student_dict={
                "studentName":"Saral",
                "phone":"7207366926",
                "website":student.website,
                "careerObjective":student.careerObjective,
                "hobbies":student.hobbies,
                "profilePic":student.profilePic
            }
            get_address =student.addressList
            if not get_address:
                address={
                    "mandal":"-",
                    "district":"-"
                }    
            else:
                address = {
                    "mandal": get_address.get("mandal", ""),
                    "district": get_address.get("district", "")
                }
            student_dict["addressDetails"]=address

            experience = student.experienceList.get('experienceDetails', [])  # Get experience data or empty list
            experience_info = []
            # experience = student.experienceList['experienceDetails']
            # i=1
            for e in experience:
                experience_data={
                    "companyName":e['companyName'],
                    "role":e['role'],
                    "fromYear":e['from_year'],
                    "toYear":e['to_year'],
                    "project":e['projectDesc']
                }
                # i=i+1
                experience_info.append(experience_data)

            skills = student.skillsList.get('skillDetails', [])  # Get experience data or empty list
            skills_info = []
            # experience = student.experienceList['experienceDetails']
            # i=1
            for sk in skills:
                skills_data={
                    "techName":sk['techName'],
                    "skillLevel":sk['skillLevel']
                }
                # i=i+1
                skills_info.append(skills_data)
                print(skills_info)

            social_media_details = student.socialMedia.get('socialMediaDetails', [])
            social_media_list = []

            for sm in social_media_details:
                for key, value in sm.items():
                    if key.startswith("socialMedia"):
                        social_media_name = value
                        social_media_url_key = "socialMediaURL" + key[len("socialMedia"):]
                        social_media_url = sm.get(social_media_url_key, "")
                        if social_media_name and social_media_url:
                            social_media_list.append({"name": social_media_name, "url": social_media_url})


           
                

        return render_template('student/profile.html', 
            student_data=student_dict, 
            experience_info=experience_info, 
            social_media_list=social_media_list,
            skillsinfo=skills_info
            )

    except StudentProfile.DoesNotExist:
        return "Student not found"


if __name__ == '__main__':
    app.run(debug=True)

