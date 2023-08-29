from flask import Flask, render_template, request, redirect, url_for, make_response,flash,session,jsonify
from config import client
from models import *
import secrets
import datetime
from bson import ObjectId
from random import randint
import os
from mongoengine import Document, StringField, BooleanField, DateTimeField
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from functools import wraps
from flask_login import LoginManager, UserMixin, login_user, login_required, current_user
import re
app = Flask(__name__)

login_manager = LoginManager()
login_manager.login_view = 'login_user'
login_manager.init_app(app)

app.secret_key='my_key'

class User(UserMixin):
    def __init__(self, id):
        self.id = id

@login_manager.user_loader
def load_user(user_id):
    return User(user_id)

UPLOAD_FOLDER = 'static/images/profiles'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif','mp4'}

def send_verification_email(verification_token, email):
    try:
        get_user_details = StudentRegistration.objects.get(verification_token=verification_token)
        if get_user_details:
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login('saralkumar238@gmail.com','xxbcoqhhanliheyo')

            subject = 'Account Verification'
            html_content = f'''
                <html>
                    <body>
                        <p>Hi {get_user_details.username},</p>
                        <p>Click this link to verify your email: <a href="{url_for("login_user", verification_token=get_user_details.verification_token, _external=True)}">Verify Email</a></p>
                    </body>
                </html>
            '''
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = 'saralkumar238@gmail.com'
            msg['To'] = get_user_details.email
            
            msg.attach(MIMEText(html_content, 'html'))
            server.sendmail('saralkumar238@gmail.com', [get_user_details.email], msg.as_string())
            server.quit()
        else:
            return "Something went wrong"
    except Exception as e:
        print(e)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            return redirect(url_for('login_user'))
        return f(*args, **kwargs)
    return decorated_function

def login_required_admin(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            return redirect(url_for('login_user'))
        user = StudentRegistration.objects(username=session['username']).first()
        if not user or not user.is_admin:
            flash("Access denied. Admin permission required.")
            return redirect(url_for('crud_page'))
        return f(*args, **kwargs)
    return decorated_function

def is_valid_email(email):
    email_pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(email_pattern, email)

def is_existing_email(email):
    existing_student = StudentRegistration.objects.filter(email=email).first()
    return existing_student is not None

def is_valid_phone(phone):
    phone_pattern = r'^\d{10}$'
    return re.match(phone_pattern, phone)

def is_valid_password(password):
    password_pattern = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$'
    return re.match(password_pattern, password)

@app.route('/images/profiles/<filename>')
def send_uploaded_profile_pic(filename=''):
    from flask import send_from_directory
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)

#admin login
@login_required_admin
@app.route("/", methods=["GET", "POST"])
def adminIndex():
    
    if request.method == "POST":
        admin_email = request.form.get("admin_email")
        admin_password = request.form.get("admin_password")
        admin = adminDetails.objects(admin=admin_email, password=admin_password).first()
        if admin and admin.is_admin:
            session['admin'] = admin_email
            # return redirect(url_for('viewAllProfiles'))
            return render_template("india.html",admin=admin_email,isAdmin=admin.is_admin)
        flash("Invalid admin credentials.")
    
    return render_template("admin_login.html")


@login_required_admin
@app.route("/adminViewProfiles/<studentId>",methods=['POST','GET'])
def adminViewProfiles(studentId):
    username = session.get('admin')
    try:
        social_media_list=[]
        skills_info=[]
        student_liat=[]
        student_dict={}
        experience_info=[]
        media_detail={}
        student_id_obj = ObjectId(studentId)
        student = StudentProfile.objects(studentId=student_id_obj).first()
        if student:
            student_dict={
                "studentName":student.userName,
                "phone":student.phoneNumber,
                "email":student.email,
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

            experience = student.experienceList.get('experienceDetails', [])
            experience_info = []
            for e in experience:
                experience_data={
                    "companyName":e['companyName'],
                    "role":e['role'],
                    "fromYear":e['from_year'],
                    "toYear":e['to_year'],
                    "project":e['projectDesc']
                }
                experience_info.append(experience_data)

            skills = student.skillsList.get('skillDetails', [])
            skills_info = []
            for sk in skills:
                skills_data={
                    "techName":sk['techName'],
                    "skillLevel":sk['skillLevel']
                }
                skills_info.append(skills_data)

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
        return render_template('profile.html', 
            student_data=student_dict, 
            experience_info=experience_info, 
            social_media_list=social_media_list,
            skillsinfo=skills_info
            )

    except StudentProfile.DoesNotExist:
        return "Student not found"

#Student Register
@app.route('/register', methods=['GET', 'POST'])
def register_user():
    
    if request.method == 'POST':
        # Collect user data from the registration form
        username = request.form['username']
        fullname = request.form['fullname']
        email = request.form['email']
        phone = request.form['phone']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        viewOptionStatus=1
        # Check if passwords match

        existing_student = StudentRegistration.objects.filter(username=username).first()
        if existing_student:
            flash('Username already exists. Please choose a different username.')
            return redirect(url_for('register_user'))

        if not is_valid_email(email):
            flash('Invalid email format. Please enter a valid email address.')
            return redirect(url_for('register_user'))

        # Check if the email is already registered
        if is_existing_email(email):
            flash('Email already exists. Please use a different email address.')
            return redirect(url_for('register_user'))

        if not is_valid_phone(phone):
            flash('Phone number must be 10 digits.')
            return redirect(url_for('register_user'))

        if password != confirm_password:
            flash('Passwords do not match.')
            return redirect(url_for('register_user'))
            
        if not is_valid_password(password):
            flash('Password must contain at least one uppercase letter, one lowercase letter, one digit, and one symbol.')
            return redirect(url_for('register_user'))


        verification_token = secrets.token_urlsafe(32)
        new_student = StudentRegistration(
            username=username,
            fullname=fullname, 
            email=email, 
            phone=phone, 
            password=password, 
            verification_token=verification_token,
            verified=False,
            user_activation=False,
            created_on = datetime.datetime.now(),
            status=0,
            optionStatus = 1,
            viewOptionStatus=viewOptionStatus
            )
        new_student.save()
        send_verification_email(verification_token,email)
        flash('Registration successful. Please check your email to verify your account.')
        return redirect(url_for('register_user'))
    return render_template('student/student_register.html')

#Email Verification
@app.route('/verify/<verification_token>')
def verify_email(verification_token):
    student = StudentRegistration.objects(verification_token=verification_token).first()
    if student:
        return redirect(url_for('login_user'))
    return 'Invalid verification token.'

#Student login
@app.route('/login', methods=['GET', 'POST'])
def login_user():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = StudentRegistration.objects(username=username, password=password).first()
        if user:
            if user.verified:
                session['username'] = username
                return redirect(url_for('activate_account'))
            else:
                flash('Your account is not verified. Please check your email for the verification link.')
                return render_template('student/login.html', verified=False, show_resend=True)
        flash('Invalid login credentials.')
        return render_template('student/login.html', verified=False, show_resend=False)
    return render_template('student/login.html', verified=True, show_resend=False)

#Student activate account
@app.route('/activate', methods=['GET', 'POST'])
def activate_account():
    if request.method == 'POST':
        username = session.get('username')   
        user = StudentRegistration.objects(username=username).first()
        if user and not user.user_activation:
            user.update(user_activation=True)
            return redirect(url_for('crud_page'))
    username = session.get('username')
    user = StudentRegistration.objects(username=username).first()
    if user and user.user_activation:
        return redirect(url_for('crud_page'))
    return render_template('student/activation.html')

#Student dashboard of add,edit,delete, and view
@login_required 
@app.route('/crudpage')
def crud_page():
    optionStatus=0
    view_option=0
    username = session.get('username')
    get_student_data = StudentRegistration.objects(username=username).first()
    if get_student_data:
        optionStatus = get_student_data.optionStatus
        view_option = get_student_data.viewOptionStatus
    student_profiles = StudentProfile.objects(userName=username)
    return render_template('student/crudpage.html', username=username, option=optionStatus, view_option=view_option,student_profiles=student_profiles)

#Get states wise
@login_required
@app.route("/getStateDetails/<state>")
def get_state_details(state):
    try:
        state_students = StudentProfile.objects(addressList__state=state)
        student_list = []
        if state_students:
            for student in state_students:
                print(student.studentId)
                student_info = {
                    "profilePic": student.profilePic,
                    "username": student.userName,
                    "state": student.addressList.get("state", ""),
                    "district": student.addressList.get("district", ""),
                    "studentId":str(student.studentId),
                    "fullname":student.fullname
                }
                student_list.append(student_info)
        state_districts = get_state_districts(state)
        response = {
            "state_students": student_list,
            "state_districts": state_districts
        }
        return jsonify(response)
    except Exception as e:
        return jsonify({"error": str(e)})

def get_state_districts(state):
    try:
        state_districts = StudentProfile.objects.filter(addressList__state=state)
        district_list = []
        if state_districts:
            for district_data in state_districts:
                district_info = {
                    "district": district_data.addressList.get("district", ""),
                    "username": district_data.userName,
                    "profilePic": district_data.profilePic,
                    "studentId":str(district_data.studentId),
                    "fullname":district_data.fullname
                }
                district_list.append(district_info)
        return district_list
    except Exception as e:
        print(f"Error fetching {state} district data:", str(e))
        return []

#Student add profile
@app.route("/addStudentProfile",methods=['POST','GET'])
@login_required
def addStudentProfile():
    username = session.get('username')
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
    optionStatus = 0
    get_student_data = StudentRegistration.objects(username=username).first()
    file_name=""
    if get_student_data:
        email = get_student_data.email
        phone_number = get_student_data.phone
        studentId = ObjectId(get_student_data.id)
        fullname = get_student_data.fullname
    if current_user.is_authenticated:
        username = current_user.username

    if request.method == 'POST':
        profilePic = request.files['profilePic']
        if not profilePic.filename:
            flash("Profile picture file should be uploaded.", "error")
            return redirect(url_for('addStudentProfile'))
        
        if profilePic.filename.rsplit('.',1)[1].lower() in ALLOWED_EXTENSIONS:
            ext = profilePic.filename.rsplit('.',1)[1].lower()
            file_name = username+"."+ext
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
        experience_list = []

        for epd in range(1, total_experience_entries + 1):
            companyName = request.form.get('companyName' + str(epd))
            role = request.form.get('role' + str(epd))
            fromYear = request.form.get('fromYear' + str(epd))
            toYear = request.form.get('toYear' + str(epd))
            projectDesc = request.form.get('projectDesc' + str(epd))
            
            if all(value is None or value == '' for value in [companyName, role, fromYear, toYear, projectDesc]):
                continue
            
            experience_dict = {
                'companyName': companyName,
                'role': role,
                'fromYear': fromYear,
                'toYear': toYear,
                'projectDesc': projectDesc
            }
            experience_list.append(experience_dict)

        if not experience_list:
            default_experience = {
                'companyName': '',
                'role': '',
                'fromYear': '',
                'toYear': '',
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
            if all(value is None or value == '' for value in [tech_name, skill_level]):
                continue
            skill_dict = {
                'techName': tech_name,
                'skillLevel': skill_level,
            }
            skill_list.append(skill_dict)
        if not skill_list:
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
                status = 1,
                userName=username,
                email=email,
                phoneNumber=phone_number,
                studentId=studentId,
                fullname=fullname
                )
            add_profile.save()
            if add_profile:
                update_option = get_student_data.update(optionStatus=2,viewOptionStatus=2)
            flash("Data Submitted successfully !")
            return redirect(url_for('crud_page'))
        else:
            flash("Something went wrong! Please check your details once!!")
    return render_template('student/add_profile.html',username=username)

#student edit profile
# @app.route("/editStudentProfile", methods=['POST', 'GET'])
# @login_required
# def editStudentProfile():
#     username = session.get('username')
#     get_student_data = StudentProfile.objects(userName=username).first()
#     if current_user.is_authenticated:
#         username = current_user.username

#     experience_list=[]
#     experience_info={}

#     skill_list =[]
#     skill_info ={}
#     message = ""

#     if request.method == 'GET':
#         existing_website = get_student_data.website
#         existing_career = get_student_data.careerObjective
#         existing_hobbies = get_student_data.hobbies
#         existing_experience = get_student_data.experienceList
        

#         if existing_experience and 'experienceDetails' in existing_experience:
#             experience_details = existing_experience["experienceDetails"]
#             for experience in experience_details:
#                 experience_info = {
#                     "companyName": experience['companyName'],
#                     "role": experience['role'],
#                     "fromYear": experience['fromYear'],
#                     "toYear": experience['toYear'],
#                     "projectDesc": experience['projectDesc']
#                 }
#                 experience_list.append(experience_info)
#         else:
#             pass

#         existing_skills = get_student_data.skillsList
#         if existing_skills and 'skillDetails' in existing_skills:
#             skill_details = existing_skills["skillDetails"]

#             for skill in skill_details:
#                 skill_info ={
#                     "techName":skill['techName'],
#                     "skillLevel":skill['skillLevel']
#                 }
#                 skill_list.append(skill_info)
#         else:
#             pass


#     if request.method == 'POST':
#         edited_website = request.form.get('website')
#         edited_career = request.form.get('careerObjective')
#         edited_hobbies = request.form.get('hobbies')

#         total_experience_entries = int(request.form.get('totalExperienceEntries'))
#         existing_experience = get_student_data.experienceList.get('experienceDetails', [])

#         for epd in range(1, total_experience_entries + 1):
#             company_name = request.form.get('companyName' + str(epd))
#             role = request.form.get('role' + str(epd))
#             from_year = request.form.get('fromYear' + str(epd))
#             to_year = request.form.get('toYear' + str(epd))
#             project_desc = request.form.get('projectDesc' + str(epd))

#             if all(value is None or value == '' for value in [company_name, role, from_year, to_year, project_desc]):
#                 continue
            
#             # if any(value.strip() for value in [company_name, role, from_year, to_year, project_desc]):
#             experience_dict = {
#                 'companyName': company_name,
#                 'role': role,
#                 'fromYear': from_year,
#                 'toYear': to_year,
#                 'projectDesc': project_desc
#             }
#             experience_list.append(experience_dict)

#         if not experience_list:
#             default_experience = {
#                 'companyName': '',
#                 'role': '',
#                 'fromYear': '',
#                 'toYear': '',
#                 'projectDesc': ''
#             }
#             experience_list.append(default_experience)    
#         else:
#             experience_details = {
#                 "experienceDetails": experience_list
#             }

#         existing_experience.extend(experience_list)
#         get_student_data.update(experienceList={"experienceDetails": existing_experience})


#         total_skill_entries = int(request.form.get('totalskills'))
#         skill_list = []
#         existing_skills = get_student_data.skillsList.get('skillDetails', [])
#         for sk in range(1, total_skill_entries + 1):
#             tech_name = request.form.get('technologyName' + str(sk))
#             skill_level = request.form.get('skillLevel' + str(sk))
#             if all(value is None or value == '' for value in [tech_name, skill_level]):
#                 continue

#             skill_dict = {
#                 'techName': tech_name,
#                 'skillLevel': skill_level,
#             }
#             skill_list.append(skill_dict)

#         if not skill_list:
#             default_skill = {
#                 'techName': '',
#                 'skillLevel': '',
#             }
#             skill_list.append(default_skill)    
#         else:
#             skill_details = {
#                 "skillDetails": skill_list
#             }
#         existing_skills.extend(skill_list)
#         get_student_data.update(
#             skillsList={"skillDetails": existing_skills}
#         )





#         # edited_skills = []
#         # total_skill_entries = int(request.form.get('totalskills'))
#         # for sk in range(1, total_skill_entries + 1):
#         #     tech_name = request.form.get('editedTechnologyName' + str(sk))
#         #     skill_level = request.form.get('editedSkillLevel' + str(sk))
#         #     if all(value is None or value == '' for value in [tech_name, skill_level]):
#         #         continue
#         #     if tech_name and skill_level:
#         #         skill_dict = {
#         #             'techName': tech_name,
#         #             'skillLevel': skill_level
#         #         }
#         #         edited_skills.append(skill_dict)
#         # edited_address = {
#         #     "pincode": request.form.get('editedPincode'),
#         #     "state": request.form.get('editedState'),
#         #     "district": request.form.get('editedDistrict'),
#         #     "mandal": request.form.get('editedMandal'),
#         #     "village": request.form.get('editedVillage'),
#         #     "country": request.form.get('editedCountry')
#         # }
        
#         # edited_media = []
#         # total_media_entries = int(request.form.get('editedTotalMedia', 0))
#         # for sm in range(1, total_media_entries + 1):
#         #     media_name = request.form.get('editedSocialMedia' + str(sm))
#         #     media_url = request.form.get('editedSocialMediaURL' + str(sm))
#         #     if all(value is None or value == '' for value in [media_name, media_url]):
#         #         continue
#         #     if media_name and media_url:
#         #         media_dict = {
#         #             'socialMedia': media_name,
#         #             'socialMediaURL': media_url
#         #         }
#         #         edited_media.append(media_dict)
#         get_student_data.update(
#             website=edited_website,
#             careerObjective=edited_career,
#             # addressList=edited_address,
#             hobbies=edited_hobbies,
#             # socialMedia=edited_media,
#             # profilePic=file_name
#         )
#         flash("Profile updated successfully!")
#         return redirect(url_for('editStudentProfile'))

#     # existing_website = get_student_data.website
#     # existing_career = get_student_data.careerObjective
#     # experience_list_object = get_student_data.experienceList
#     # if experience_list_object and 'experienceDetails' in experience_list_object:
#     #     existing_experience = experience_list_object['experienceDetails']
#     # else:
#     #     existing_experience = []
#     # skills_list_object = get_student_data.skillsList
#     # if skills_list_object and 'skillDetails' in skills_list_object:
#     #     existing_skills = skills_list_object['skillDetails']
#     # else:
#     #     existing_skills = []
#     # social_media_object = get_student_data.socialMedia
#     # if social_media_object and 'socialMediaDetails' in social_media_object:
#     #     existing_media = social_media_object['socialMediaDetails']
#     # else:
#     #     existing_media = []
#     # existing_address = get_student_data.addressList
#     # existing_hobbies = get_student_data.hobbies

#     return render_template('student/edit_profile.html',
#         username=username,
#         existing_website=existing_website,
#         existing_career=existing_career,
#         experience_info=experience_list,
#         skill_info=skill_list,
#         # existing_address=existing_address,
#         existing_hobbies=existing_hobbies,
#         # existing_media=existing_media,
        
#         )

@app.route("/editStudentProfile", methods=['POST', 'GET'])
@login_required
def editStudentProfile():
    username = session.get('username')
    get_student_data = StudentProfile.objects(userName=username).first()
    if current_user.is_authenticated:
        username = current_user.username
    experience_list = []
    experience_info = {}
    skill_list = []
    skill_info = {}
    address_dict={}
    media_list = []
    media_info ={}

    if request.method == 'GET':
        existing_website = get_student_data.website
        existing_career = get_student_data.careerObjective
        existing_hobbies = get_student_data.hobbies

        existing_experience = get_student_data.experienceList
        if existing_experience and 'experienceDetails' in existing_experience:
            experience_details = existing_experience['experienceDetails']
            for experience in experience_details:
                experience_info = {
                    "companyName": experience['companyName'],
                    "role": experience['role'],
                    "fromYear": experience['fromYear'],
                    "toYear": experience['toYear'],
                    "projectDesc": experience['projectDesc']
                }
                experience_list.append(experience_info)

        existing_skills = get_student_data.skillsList
        if existing_skills and 'skillDetails' in existing_skills:
            skill_details = existing_skills["skillDetails"]

            for skill in skill_details:
                skill_info = {
                    "techName": skill['techName'],
                    "skillLevel": skill['skillLevel']
                }
                skill_list.append(skill_info)

        existing_address = get_student_data.addressList
        if existing_address:
            address_dict ={
                "pincode":existing_address.get('pincode'),
                "state":existing_address.get('state'),
                "district":existing_address.get('district'),
                "mandal":existing_address.get('mandal'),
                "village":existing_address.get('village'),
                "country":existing_address.get('country')
            }


        existing_media = get_student_data.socialMedia
        if existing_media and 'socialMediaDetails' in existing_media:
            media_details = existing_media['socialMediaDetails']
            for md in media_details:
                media_info = {
                    "socialMedia" : md['socialMedia'],
                    "socialMediaURL" : md['socialMediaURL']
                }
                media_list.append(media_info)

    if request.method == 'POST':
        edited_website = request.form.get('website')
        edited_career = request.form.get('careerObjective')
        edited_hobbies = request.form.get('hobbies')

        total_experience_entries = int(request.form.get('totalExperienceEntries'))
        existing_experience = get_student_data.experienceList.get('experienceDetails', [])

        for epd in range(1, total_experience_entries + 1):
            company_name = request.form.get('companyName' + str(epd))
            role = request.form.get('role' + str(epd))
            from_year = request.form.get('fromYear' + str(epd))
            to_year = request.form.get('toYear' + str(epd))
            project_desc = request.form.get('projectDesc' + str(epd))

            if all(value is not None and value.strip() for value in [company_name, role, from_year, to_year, project_desc]):
                experience_dict = {
                    'companyName': company_name,
                    'role': role,
                    'fromYear': from_year,
                    'toYear': to_year,
                    'projectDesc': project_desc
                }
                experience_list.append(experience_dict)

        if experience_list:
            existing_experience.extend(experience_list)
            get_student_data.update(experienceList={"experienceDetails": existing_experience})

        total_skill_entries = int(request.form.get('totalskills'))
        skill_list = []
        existing_skills = get_student_data.skillsList.get('skillDetails', [])
        for sk in range(1, total_skill_entries + 1):
            tech_name = request.form.get('technologyName' + str(sk))
            skill_level = request.form.get('skillLevel' + str(sk))
            if all(value is not None and value.strip() for value in [tech_name, skill_level]):
                skill_dict = {
                    'techName': tech_name,
                    'skillLevel': skill_level,
                }
                skill_list.append(skill_dict)

        if skill_list:
            existing_skills.extend(skill_list)
            get_student_data.update(skillsList={"skillDetails": existing_skills})

        edited_pincode = request.form.get('pincode')
        edited_state = request.form.get('state')
        edited_district = request.form.get('district')
        edited_mandal = request.form.get('mandal')
        edited_village = request.form.get('village')
        edited_country = request.form.get('country')
        addressList={
            "pincode": edited_pincode,
            "state": edited_state,
            "district": edited_district,
            "mandal": edited_mandal,
            "village": edited_village,
            "country": edited_country
        }

        total_media_entries = int(request.form.get('totalMedia'))
        media_list = []
        existing_media = get_student_data.socialMedia.get('socialMediaDetails',[])
        for sm in range(1, total_media_entries + 1):
            social_media_name = request.form.get('socialMedia' + str(sm))
            social_media_url = request.form.get('socialMediaURL' + str(sm))
            if all(value is not None and value.strip() for value in [social_media_name,social_media_url]):
                media_dict = {
                    "socialMedia":social_media_name,
                    "socialMediaURL":social_media_url
                }
                media_list.append(media_dict)
        if media_list:
            existing_media.extend(media_list)
            get_student_data.update(socialMedia={"socialMediaDetails":existing_media})



        get_student_data.update(
            website=edited_website,
            careerObjective=edited_career,
            hobbies=edited_hobbies,
            addressList=addressList
        )
        flash("Profile updated successfully!")
        return redirect(url_for('editStudentProfile'))

    return render_template('student/edit_profile.html',
        username=username,
        existing_website=existing_website,
        existing_career=existing_career,
        experience_info=experience_list,
        skill_info=skill_list,
        address_info=address_dict,
        existing_hobbies=existing_hobbies,
        media_info=media_list
    )

@app.route("/delete_experience/<string:index>", methods=['POST', 'GET'])
@login_required
def delete_experience(index):
    try:
        username = session.get('username')
        student_profile = StudentProfile.objects(userName=username).first()

        if student_profile:
            experience_list = student_profile.experienceList

            if experience_list and 'experienceDetails' in experience_list:
                experience_details = experience_list["experienceDetails"]
                index_to_delete = None
                for i, exp in enumerate(experience_details):
                    index_to_delete = i
                    break

                if index_to_delete is not None:
                    del experience_details[index_to_delete]
                    student_profile.update(
                        experienceList=experience_list
                        )

    except Exception as e:
        print("An error occurred:", e)

    return redirect(url_for('editStudentProfile'))

@app.route("/delete_skills/<string:index>",methods=['POST','GET'])
@login_required
def delete_skills(index):
    try:
        username = session.get('username')
        student_profile = StudentProfile.objects(userName=username).first()
        if student_profile:
            skill_list = student_profile.skillsList
            if skill_list and 'skillDetails' in skill_list:
                skill_details = skill_list["skillDetails"]
                index_to_delete = None

                for i, sk in enumerate(skill_details):
                    index_to_delete = i
                    break

                if index_to_delete is not None:
                    del skill_details[index_to_delete]
                    student_profile.update(
                        skillsList = skill_list
                        )
    except Exception as e:
        print("An error occurred:", e)
    return redirect(url_for('editStudentProfile'))

@app.route("/delete_social_media/<string:index>",methods=['POST','GET'])
@login_required
def delete_social_media(index):
    try:
        username = session.get('username')
        student_profile = StudentProfile.objects(userName=username).first()
        if student_profile:
            media_list = student_profile.socialMedia
            if media_list and 'socialMediaDetails' in media_list:
                media_details = media_list["socialMediaDetails"]
                index_to_delete = None

                for i, sm in enumerate(media_list):
                    index_to_delete = i
                    break

                if index_to_delete is not None:
                    del media_details[index_to_delete]
                    student_profile.update(
                        socialMedia = media_list
                        )
    except Exception as e:
        print("An error occurred:", e)
    return redirect(url_for('editStudentProfile'))




#student delete profile
@app.route("/deleteStudentProfile/<studentId>", methods=['POST','GET'])
@login_required
def deleteStudentProfile(studentId):
    username = session.get('username')
    try:
        student_id_obj = ObjectId(studentId)
        student = StudentProfile.objects(userName=username, studentId=student_id_obj).first()
        if not student:
            flash("Student profile not found.")
            return redirect(url_for('crud_page'))
        student.delete()
        user = StudentRegistration.objects(username=username).first()
        if user:
            user.update(optionStatus=1,viewOptionStatus=1)
        flash("Student profile deleted successfully!")
        return redirect(url_for('crud_page'))
    except Exception as e:
        flash("An error occurred while deleting the student profile.")
        return redirect(url_for('crud_page'))


@app.route("/studentProfile/<studentId>",methods=['POST','GET'])
@login_required
def studentProfile(studentId):
    username = session.get('username')
    try:
        student_liat=[]
        student_dict={}
        experience_info=[]
        media_detail={}
        student_id_obj = ObjectId(studentId)
        student = StudentProfile.objects(userName=username, studentId=student_id_obj).first()
        if not student:
            flash("Student profile not found.")
            return redirect(url_for('crud_page'))
        if student:
            student_dict={
                "studentName":student.userName,
                "phone":student.phoneNumber,
                "email":student.email,
                "website":student.website,
                "careerObjective":student.careerObjective,
                "hobbies":student.hobbies,
                "profilePic":student.profilePic,
                "studentId":str(student.studentId),
                "fullname":student.fullname
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

            experience = student.experienceList.get('experienceDetails', [])
            experience_info = []
            for e in experience:
                experience_data={
                    "companyName":e['companyName'],
                    "role":e['role'],
                    "fromYear":e['fromYear'],
                    "toYear":e['toYear'],
                    "projectDesc":e['projectDesc']
                }
                experience_info.append(experience_data)

            skills = student.skillsList.get('skillDetails', [])
            skills_info = []
            for sk in skills:
                skills_data={
                    "techName":sk['techName'],
                    "skillLevel":sk['skillLevel']
                }
                skills_info.append(skills_data)

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
        return render_template('student/all_profile.html', 
            student_data=student_dict, 
            experience_info=experience_info, 
            social_media_list=social_media_list,
            skillsinfo=skills_info,
            studentId = student.studentId
            )

    except StudentProfile.DoesNotExist:
        return "Student not found"


@app.route('/logout', methods=['POST','GET'])
def logout():
    session.pop('username', None)
    return redirect(url_for('login_user'))

@app.route('/adminlogout', methods=['GET'])
def alogout():
    session.pop('admin', None)
    return redirect(url_for('adminIndex'))

if __name__ == '__main__':
    app.run(debug=True)