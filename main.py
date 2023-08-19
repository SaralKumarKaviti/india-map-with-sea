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


# from datetime import datetime
from keys import sg_api_key, from_email, subject
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
        # Retrieve user details based on verification token
        get_user_details = StudentRegistration.objects.get(verification_token=verification_token)
        
        if get_user_details:
            # Set up SMTP server
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login('saralkumar238@gmail.com','xxbcoqhhanliheyo')

            subject = 'Account Verification'
            
            # HTML content with clickable verification link
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


@app.route('/images/profiles/<filename>')
def send_uploaded_profile_pic(filename=''):
    from flask import send_from_directory
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)


@app.route("/")
def index():
    return render_template('india.html')

@app.route('/register', methods=['GET', 'POST'])
def register_user():
    if request.method == 'POST':
        # Collect user data from the registration form
        username = request.form['username']
        email = request.form['email']
        phone = request.form['phone']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        # Check if passwords match
        if password != confirm_password:
            flash('Passwords do not match.')
            return redirect(url_for('register_user'))

        # Save user data to the database
        verification_token = secrets.token_urlsafe(32)  # Generate verification token
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
            optionStatus = 1
            )
        new_student.save()

        # Send verification email
        send_verification_email(verification_token,email)
        
        flash('Registration successful. Please check your email to verify your account.')
        return redirect(url_for('register_user'))

    return render_template('student/student_register.html')


@app.route('/verify/<verification_token>')
def verify_email(verification_token):
    student = StudentRegistration.objects(verification_token=verification_token).first()
    if student:
        # StudentRegistration.update(verified=True)
        print('Email verified')
        return redirect(url_for('login_user'))
    return 'Invalid verification token.'


@app.route('/login', methods=['GET', 'POST'])
def login_user():
    if request.method == 'POST':
        # Collect user data from the login form
        username = request.form['username']
        password = request.form['password']

        # Check if user with given username and password exists
        user = StudentRegistration.objects(username=username, password=password).first()

        if user:
            if user.verified:
                session['username'] = username
                # Redirect to t(or any other appropriate page)
                return redirect(url_for('activate_account'))
            else:
                # Show a message for non-verified users and render the login template
                flash('Your account is not verified. Please check your email for the verification link.')
                return render_template('student/login.html', verified=False, show_resend=True)

        # Invalid login credentials, show message and render the login template
        flash('Invalid login credentials.')
        return render_template('student/login.html', verified=False, show_resend=False)

    return render_template('student/login.html', verified=True, show_resend=False)



@app.route('/activate', methods=['GET', 'POST'])
def activate_account():
    if request.method == 'POST':
        username = session.get('username')  
        print('in session')# Retrieve username from session
        
        user = StudentRegistration.objects(username=username).first()
        print(username)

        if user and not user.user_activation:  # Check if user exists and is not activated
            user.update(user_activation=True)  # Set user_activation to True
            print('user activation')
            flash('Account activated successfully. You can now log in.')
            return redirect(url_for('crud_page'))  # Redirect to CRUD page

    # If activation is successful or for GET requests, redirect to CRUD page if user is activated
    username = session.get('username')  # Retrieve username from session
    user = StudentRegistration.objects(username=username).first()
    
    if user and user.user_activation:  # Check if user is activated
        return redirect(url_for('crud_page'))
    
    # Render the activation page for both GET and POST requests
    return render_template('student/activation.html')

@app.route('/crudpage')
@login_required 
def crud_page():
    username = session.get('username')
    get_student_data = StudentRegistration.objects(username=username).first()
    if get_student_data:
        optionStatus = get_student_data.optionStatus
        print(optionStatus)
    return render_template('student/crudpage.html',username=username,option=optionStatus)


@app.route("/getStateDetails/<state>")
def get_state_details(state):
    try:
        # Fetch student details for the specified state
        state_students = StudentProfile.objects(addressList__state=state)
        student_list = [{"profilePic": student.profilePic, "ref":student.ref,"state": student.addressList["state"]} for student in state_students]

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
        # Fetch district data for the specified state from your MongoDB collection
        state_districts = StudentProfile.objects.filter(addressList__state=state)

        # Prepare the data to match the format you need
        district_list = []
        if state_districts:
            for district_data in state_districts:
                district_info = {
                    "district": district_data.addressList.get("district", ""),
                    "name": "Saral",
                    "profilePic":district_data.profilePic,
                    "profileUrl": 'http://127.0.0.1:5000'+url_for('student_profile', ref=district_data.ref)
                }
                print(district_info['profileUrl'])
                district_list.append(district_info)
        else:
            district_list.append({"district": "No data available", "value": ""})

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
    if get_student_data:
        email = get_student_data.email
        phone_number = get_student_data.phone
    if current_user.is_authenticated:
        # Retrieve the user's information using current_user
        username = current_user.username
        

        # email = current_user.email
        # phone_number = current_user.phone_number

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
        # user_email = current_user.email
        # user_phone = current_user.phone_number

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
                
                )
            add_profile.save()
            if add_profile:
                update_option = get_student_data.update(optionStatus=2)
            
            flash("Data Submitted successfully !")
            return redirect(url_for('addStudentProfile'))
        else:
            flash("Something went wrong! Please check your details once!!")

    
    return render_template('student/add_profile.html',username=username)

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
                "email":"ss",
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

@app.route('/logout', methods=['POST','GET'])
def logout():
    session.pop('username', None)
    return redirect(url_for('login_user'))


if __name__ == '__main__':
    app.run(debug=True)

