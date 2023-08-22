from flask import Flask, render_template, request, redirect, url_for, make_response,flash,session
from config import client
from models import *
import secrets
import datetime
from bson import ObjectId
# from datetime import datetime
from random import randint
import os
from flask import jsonify
from mongoengine import Document, StringField, BooleanField, DateTimeField
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from functools import wraps
from flask_login import LoginManager, UserMixin, login_user, login_required, current_user

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


@app.route('/images/profiles/<filename>')
def send_uploaded_profile_pic(filename=''):
    from flask import send_from_directory
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)


@app.route("/", methods=["GET", "POST"])
def adminIndex():
    try:
        if request.method == "POST":
            uname = request.form["uname"]
            pwd = request.form["pwd"]
            user = adminDetails.objects(admin=uname, password=pwd).first()
            if user:
                if user.is_admin:
                    session['admin'] = uname  # Set the admin session variable
                    return redirect(url_for("all_profiles"))
                else:
                    flash("Access denied. Admin permission required.")  # Display proper message
            else:
                flash("Invalid username or password", "error")
    except Exception as e:
        print(e)
    return render_template("dashboard.html")


@app.route('/register', methods=['GET', 'POST'])
def register_user():
    if request.method == 'POST':
        # Collect user data from the registration form
        username = request.form['username']
        email = request.form['email']
        phone = request.form['phone']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        viewOptionStatus=1
        # Check if passwords match
        if password != confirm_password:
            flash('Passwords do not match.')
            return redirect(url_for('register_user'))
        verification_token = secrets.token_urlsafe(32)
        new_student = StudentRegistration(
            username=username, 
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


@app.route('/verify/<verification_token>')
def verify_email(verification_token):
    student = StudentRegistration.objects(verification_token=verification_token).first()
    if student:
        return redirect(url_for('login_user'))
    return 'Invalid verification token.'


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

@app.route('/crudpage')
@login_required 
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

@login_required
@app.route("/getStateDetails/<state>")
def get_state_details(state):
    try:
        state_students = StudentProfile.objects(addressList__state=state)
        student_list = []
        if state_students:
            for student in state_students:
                student_info = {
                    "profilePic": student.profilePic,
                    "name": student.userName,
                    "state": student.addressList.get("state", ""),
                    "district": student.addressList.get("district", ""),
                    "studentId": student.studentId
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
                    "name": district_data.userName,
                    "profilePic": district_data.profilePic,
                    "studentId": district_data.studentId
                }
                district_list.append(district_info)
        return district_list
    except Exception as e:
        print(f"Error fetching {state} district data:", str(e))
        return []


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
            company_name = request.form.get('companyName' + str(epd))
            role = request.form.get('role' + str(epd))
            from_year = request.form.get('fromYear' + str(epd))
            to_year = request.form.get('toYear' + str(epd))
            project_desc = request.form.get('projectDesc' + str(epd))
            
            if all(value is None or value == '' for value in [company_name, role, from_year, to_year, project_desc]):
                continue
            
            experience_dict = {
                'companyName': company_name,
                'role': role,
                'from_year': from_year,
                'to_year': to_year,
                'projectDesc': project_desc
            }
            experience_list.append(experience_dict)

        if not experience_list:
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
                studentId=studentId
                )
            add_profile.save()
            if add_profile:
                update_option = get_student_data.update(optionStatus=2,viewOptionStatus=2)
            flash("Data Submitted successfully !")
            return redirect(url_for('crud_page'))
        else:
            flash("Something went wrong! Please check your details once!!")
    return render_template('student/add_profile.html',username=username)


@app.route("/editStudentProfile", methods=['POST', 'GET'])
@login_required
def editStudentProfile():
    username = session.get('username')
    get_student_data = StudentProfile.objects(userName=username).first()
    if current_user.is_authenticated:
        # Retrieve the user's information using current_user
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

        edited_website = request.form.get('website')
        edited_career = request.form.get('careerObjective')
        student_id = request.form.get('_id')
        edited_experience = []
        total_experience_entries = int(request.form.get('totalExperienceEntries'))
        
        for epd in range(1, total_experience_entries + 1):
            company_name = request.form.get('editedCompanyName' + str(epd))
            role = request.form.get('editedRole' + str(epd))
            from_year = request.form.get('editedFromYear' + str(epd))
            to_year = request.form.get('editedToYear' + str(epd))
            project_desc = request.form.get('editedProjectDesc' + str(epd))
            if any(value.strip() for value in [company_name, role, from_year, to_year, project_desc]):
                experience_dict = {
                    'companyName': company_name,
                    'role': role,
                    'from_year': from_year,
                    'to_year': to_year,
                    'projectDesc': project_desc
                }
                edited_experience.append(experience_dict)

        edited_skills = []
        total_skill_entries = int(request.form.get('totalskills'))
        for sk in range(1, total_skill_entries + 1):
            tech_name = request.form.get('editedTechnologyName' + str(sk))
            skill_level = request.form.get('editedSkillLevel' + str(sk))
            if all(value is None or value == '' for value in [tech_name, skill_level]):
                continue
            if tech_name and skill_level:
                skill_dict = {
                    'techName': tech_name,
                    'skillLevel': skill_level
                }
                edited_skills.append(skill_dict)
        edited_address = {
            "pincode": request.form.get('editedPincode'),
            "state": request.form.get('editedState'),
            "district": request.form.get('editedDistrict'),
            "mandal": request.form.get('editedMandal'),
            "village": request.form.get('editedVillage'),
            "country": request.form.get('editedCountry')
        }
        edited_hobbies = request.form.get('editedHobbies')
        edited_media = []
        total_media_entries = int(request.form.get('editedTotalMedia', 0))
        for sm in range(1, total_media_entries + 1):
            media_name = request.form.get('editedSocialMedia' + str(sm))
            media_url = request.form.get('editedSocialMediaURL' + str(sm))
            if all(value is None or value == '' for value in [media_name, media_url]):
                continue
            if media_name and media_url:
                media_dict = {
                    'socialMedia': media_name,
                    'socialMediaURL': media_url
                }
                edited_media.append(media_dict)
        get_student_data.update(
            website=edited_website,
            careerObjective=edited_career,
            experienceList=edited_experience,
            skillsList=edited_skills,
            addressList=edited_address,
            hobbies=edited_hobbies,
            socialMedia=edited_media,
            profilePic=file_name
        )
        flash("Profile updated successfully!")
        return redirect(url_for('editStudentProfile'))

    existing_website = get_student_data.website
    existing_career = get_student_data.careerObjective
    experience_list_object = get_student_data.experienceList
    if experience_list_object and 'experienceDetails' in experience_list_object:
        existing_experience = experience_list_object['experienceDetails']
    else:
        existing_experience = []
    skills_list_object = get_student_data.skillsList
    if skills_list_object and 'skillDetails' in skills_list_object:
        existing_skills = skills_list_object['skillDetails']
    else:
        existing_skills = []
    social_media_object = get_student_data.socialMedia
    if social_media_object and 'socialMediaDetails' in social_media_object:
        existing_media = social_media_object['socialMediaDetails']
    else:
        existing_media = []
    existing_address = get_student_data.addressList
    existing_hobbies = get_student_data.hobbies
    return render_template('student/edit_profile.html', username=username, existing_website=existing_website, existing_career=existing_career, existing_experience=existing_experience, existing_skills=existing_skills, existing_address=existing_address, existing_hobbies=existing_hobbies, existing_media=existing_media)

@app.route("/deleteStudentProfile/<student_id>", methods=['POST','GET'])
@login_required
def deleteStudentProfile(student_id):
    username = session.get('username')
    try:
        student_id_obj = ObjectId(student_id)
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


@app.route("/profile/<student_id>",methods=['POST','GET'])
@login_required
def studentProfile(student_id):
    username = session.get('username')
    try:
        student_liat=[]
        student_dict={}
        experience_info=[]
        media_detail={}
        student_id_obj = ObjectId(student_id)
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
        return render_template('student/profile.html', 
            student_data=student_dict, 
            experience_info=experience_info, 
            social_media_list=social_media_list,
            skillsinfo=skills_info
            )

    except StudentProfile.DoesNotExist:
        return "Student not found"

@login_required_admin
@app.route("/admin/allStudentProfiles", methods=['GET'])
def all_profiles():
    admin = session.get('admin')
    if not admin:
        flash("Session not authorized.")
        return redirect(url_for('adminIndex'))
    get_admin = adminDetails.objects(admin=admin).first()
    if get_admin and get_admin.is_admin:
        return render_template('india.html')
    else:
        flash("Access denied. Admin permission required.")
        return redirect(url_for('adminIndex'))


@app.route('/logout', methods=['POST','GET'])
def logout():
    session.pop('username', None)
    return redirect(url_for('login_user'))

@app.route('/adminlogout', methods=['POST', 'GET'])
def alogout():
    session.pop('admin', None)
    return redirect(url_for('adminIndex'))


if __name__ == '__main__':
    app.run(debug=True)

