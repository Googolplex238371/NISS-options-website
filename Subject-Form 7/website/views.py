from flask import Blueprint, render_template, request, flash, redirect, url_for,jsonify
from flask_login import login_required,current_user
from . import db,dict_object #The main database and the function to convert an object to a dictionary
from .models import Subjects,User,Block #This is how we will access the table
import json
import os
from dotenv import load_dotenv
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import random
import string
import smtplib
from datetime import datetime,timezone,timedelta
last_date = datetime.now()>datetime.strptime("05 12 2025 07:00:00","%d %m %Y %H:%M:%S")
igcse_plans = ["I intend to take IGCSEs at Nexus","I am looking at studying at another school in Singapore","I am likely to leave Singapore and go to a new school in another country","I am not sure of my plans for IGCSE"] # This is the list of options for the IGCSE plans
ib_plans = ["I intend to study IBDP/IB Courses at Nexus next year","I am exploring options at other schools in Singapore for next year","I am likely to leave Singapore and go to a new school in another country next year","I am not sure of my plans for IB"] # This is the list of options for the IB plans
load_dotenv() # This loads the environment variables from the .env file
EMAIL_ADDRESS = os.getenv('EMAIL_ADDRESS') # This gets the email address from the .env file
EMAIL_PASSWORD = os.getenv('PASSWORD') # This gets the email address and password from the .env file
views = Blueprint('views', __name__) # This is the blueprint for the views pages
@views.route("/") # home page
@login_required #Only allows logged in users to access
def home(): # This is the function that will be called when the user tries to access the home page
  o = None # This is to tell the frontend we do not have any submissions yet
  if current_user.role == "Student": # Checks if the user is a student
    igcse_drafts = Subjects.query.filter_by(user_id=current_user.id,course="IGCSE").all() # Gets all the subject selections made by the user
    ib_drafts = Subjects.query.filter_by(user_id=current_user.id,course="IB").all()
    o = Subjects.query.filter_by(user_id=current_user.id).all() # Gets the subject selections made by the user
    if o == []: #If the user has not made any selections yet, it will return an empty list, so we set o to None
      o = None # This is to tell the frontend we do not have any submissions yet
    else: #If the user has made selections, it will return a list of all their selections
      o = o[-1] # We set o to the most recent selection
  if current_user.role == "Admin": # Checks if the user is an admin
    students = User.query.filter_by(role="Student",verified=True).all() # Gets all students
    subjects = [Subjects.query.filter_by(user_id=student.id).all() for student in students] # Gets all subject selections made by the students
    for idx in range(len(subjects)): # Iterates through all the subject selections
      if subjects[idx] == []: # If the student has not made any selections yet, it will return an empty list, so we set subjects[idx] to None
        subjects[idx] = None # We set subjects[idx] to None
      else: # If the student has made selections, it will return a list of all their selections
        subjects[idx] = Subjects.query.filter_by(user_id=students[idx].id,course="IGCSE",selected=True).first() # We set subjects[idx] to the most recent selection
    block1 = Block.query.filter_by(id=1).first() # Gets the subjects in block 1
    block2 = Block.query.filter_by(id=2).first() # Gets the subjects in block 2
    block3 = Block.query.filter_by(id=3).first() # Gets the subjects in block 3
    return render_template("admin_home.html",user=current_user,igcse_subjects=subjects,students=students,block1=block1.subjects.split(","),block2=block2.subjects.split(","),block3=block3.subjects.split(",")) # Renders the admin home page
  return render_template("student_home.html",user=current_user,options=o,igcse_drafts=igcse_drafts,ib_drafts=ib_drafts,deadline=last_date) # Renders the student home page
@views.route("/ib") # IB page
@login_required #Only allows logged in users to access
def ib(): # This is the function that will be called when the user tries to access the home page
  if current_user.role == "Student": # Checks if the user is a student
    return redirect(url_for("views.nopage")) # Redirects to 404 page
  if current_user.role == "Admin": # Checks if the user is an admin
    students = User.query.filter_by(role="Student",verified=True).all() # Gets all students
    subjects = [Subjects.query.filter_by(user_id=student.id).all() for student in students] # Gets all subject selections made by the students
    for idx in range(len(subjects)): # Iterates through all the subject selections
      if subjects[idx] == []: # If the student has not made any selections yet, it will return an empty list, so we set subjects[idx] to None
        subjects[idx] = None # We set subjects[idx] to None
      else: # If the student has made selections, it will return a list of all their selections
        subjects[idx] = Subjects.query.filter_by(user_id=students[idx].id,course="IB",selected=True).first() # We set subjects[idx] to the most recent selection
    return render_template("ib_students.html",user=current_user,ib_subjects=subjects,students=students) # Renders the admin home page
@views.route("/options") # Options page, does not need requests so we do not add any methods
@login_required # Only allows logged in users to access
def select_course(): # This is the function that will be called when the user tries to access the options page
  if last_date: # Checks if the deadline has passed
    return redirect(url_for("views.deadlinepassed")) # Redirects to deadline passed page
  o = None # This is to tell the frontend we do not have any submissions yet
  if current_user.role == "Admin": # Checks if the user is an admin
    return redirect(url_for("views.nopage")) # Redirects to 404 page
  o = Subjects.query.filter_by(user_id=current_user.id).all() # Gets the subject selections made by the user
  if o == []: # If the user has not made any selections yet, it will return an empty list, so we set o to None
    o = None # This is to tell the frontend we do not have any submissions yet
  else: # If the user has made selections, it will return a list of all their selections
    o = o[-1] # Gets the most recent submission
  return render_template("options.html",user=current_user,options=o,deadline=last_date) # Renders options page
@views.route("/edit") # Edit page, does not need requests so we do not add any methods
@login_required # Only allows logged in users to access
def select_edit(): # This is the function that will be called when the user tries to access the edit page
  if last_date: # Checks if the deadline has passed
    return redirect(url_for("views.deadlinepassed")) # Redirects to deadline passed page
  o = None # This is to tell the frontend we do not have any submissions yet
  if current_user.role == "Admin": # Checks if the user is an admin
    return redirect(url_for("views.nopage")) # Redirects to 404 page
  o = Subjects.query.filter_by(user_id=current_user.id).all() # Gets the subject selections made by the user
  if o == []: # If the user has not made any selections yet, it will return an empty list, so we set o to None
    o = None # This is to tell the frontend we do not have any submissions yet
  else: # If the user has made selections, it will return a list of all their selections
    o = o[-1] # Gets the most recent submission
  return render_template("edit-options.html",user=current_user,options=o,deadline=last_date) # Renders edit options page
@views.route('/select-options/<course>',methods=["GET","POST"]) # options page, allows both get and post methods
@login_required #Only allows logged in users to access
def options(course):
  if last_date: # Checks if the deadline has passed
    return redirect(url_for("views.deadlinepassed")) # Redirects to deadline passed page
  o = None # This is to tell the frontend we do not have any submissions yet
  if current_user.role == "Admin": # Checks if the user is an admin
    return redirect(url_for("views.nopage")) # Redirects to 404 page
  o = Subjects.query.filter_by(user_id=current_user.id).all() # Gets the subject selections made by the user
  block1 = Block.query.filter_by(id=1).first() # Gets the subjects in block 1
  block2 = Block.query.filter_by(id=2).first() # Gets the subjects in block 2
  block3 = Block.query.filter_by(id=3).first() # Gets the subjects in block 3
  if o == []: # If the user has not made any selections yet, it will return an empty list, so we set o to None
    o = None # This is to tell the frontend we do not have any submissions yet
  else: # If the user has made selections, it will return a list of all their selections
    o = o[-1] # Gets the most recent submission
  if last_date: # Checks if the request is past the deadline
    return redirect(url_for("views.deadlinepassed")) # Redirects to deadline passed page
  if course.upper() == "IGCSE":
    if request.method == "POST" and current_user.role == "Student": # Checks if the user is a student and if the request method is POST
        current_user.studying_igcse = request.form.get("igcse") # Gets the IGCSE plans from the form
        lote = request.form.get('lote') # Gets the LOTE from the form in options.html
        if lote == "Chinese": # Checks if the user has selected Chinese as their LOTE
          lote_level = request.form.get('chinese') # If it's chinese it uses chinese_form in options.html
        else: # If it's not chinese there is no need for the lote level as the user cannot select that
          lote_level = "" # If it's not chinese there is no need for the lote level as the user cannot select that
        elective1 = request.form.get('elective1') # Gets the elective 1 from the form in options.html
        if elective1 not in block1.subjects.split(","): # Checks if the elective is in block 1
          elective1 = "N/A" # If it's not in block 1, it sets it to N/A
        elective2 = request.form.get('elective2') # Gets the elective 2 from the form in options.html
        if elective2 not in block2.subjects.split(","): # Checks if the elective is in block 2
          elective2 = "N/A" # If it's not in block 2, it sets it to N/A
        elective3 = request.form.get('elective3') # Gets the elective 3 from the form in options.html
        if elective3 not in block3.subjects.split(","): # Checks if the elective is in block 3
          elective3 = "N/A" # If it's not in block 3, it sets it to N/A
        reserve = request.form.get('reserve') # Gets the reserve choice from the form in options.html
        #request.form.get() gets the data from the input with the name of the string in the brackets. This allows us to fetch the data from the form in options.html
        bool = False # If the user has made any selections yet, it will set the selected column to False
        if not Subjects.query.filter_by(user_id=current_user.id,course="IGCSE",selected=True).first(): # If the user has not made any selections yet, it will set the selected column to False
          bool = True # If the user has not made any selections yet, it will set the selected column to True
        x = len(Subjects.query.filter_by(user_id=current_user.id).all())+1 # Gets the number of drafts the user has made
        while Subjects.query.filter_by(name="Draft "+str(x),user_id=current_user.id).first():
          x+=1 # Checks if the draft name already exists, if it does, it increments x by 1
        id = ''.join(random.choices(string.ascii_letters + string.digits, k=16)) # Generates a random id for the draft
        while Subjects.query.filter_by(id=id).first(): # Checks if the id already exists, if it does, it generates a new one
          id = ''.join(random.choices(string.ascii_letters + string.digits, k=16)) # Generates a random id for the draft
        new_subject = Subjects(lote=lote,lote_level=lote_level,elective1=elective1,elective2=elective2,elective3=elective3,user_id=current_user.id,name="Draft "+str(x),selected=bool,course="IGCSE",id=id,reserve_choice=reserve,datetime=datetime.now(timezone(timedelta(hours=8))).strftime("%d/%m/%Y %H:%M:%S")) #Register new entry to database
        flash("Options selected successfully!",category="success")
        db.session.add(new_subject) #Adds new entry, but needs to be committed
        db.session.commit() #Commits changes
        if request.form.get('email'): # Checks if the user wants to send an email
          if lote == "Chinese": # Checks if the user has selected Chinese as their LOTE
            lote = lote_level # If the user has selected Chinese as their LOTE, it sets the lote to the lote level
          msg = MIMEMultipart("alternative") # This allows us to send HTML emails
          msg["Subject"] = "IGCSE Options - Nexus Options" # This is the subject of the email
          msg["From"] = EMAIL_ADDRESS # This is the email address that the email will be sent from
          msg["To"] = current_user.email # This is the email that the user entered in the form
          html = f"""
          <!DOCTYPE html><html><body style="color:black">
          <div style="padding:20px; margin:auto;" align="center">
            <h1>Your IGCSE Options:</h1>
            <h2>{lote}</h2>
            <h2>{elective1}</h2>
            <h2>{elective2}</h2>
            <h2>{elective3}</h2>
            <h2>Reserve choice: {reserve}</h2>
          </div></body></html>
          """ # This is the HTML of the email
          msg.attach(MIMEText(html, "html")) # This attaches the HTML to the email
          with smtplib.SMTP_SSL("smtp.elasticemail.com", 465) as smtp: # This is the SMTP server for Elastic Email
            try: # This is if the email could be sent
              smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD) # This logs into the email account
              smtp.send_message(msg) # This sends the email
              db.session.commit() # This commits the changes to the database
              flash("An email has been sent to your email address",category="success") # This flashes a success message
              return redirect(url_for("views.home")) # Redirects to home page
            except Exception as e: # This is if the email could not be sent
              flash("An error occured, please try again",category="error") # This flashes an error message
              print(e)
              return redirect(url_for("views.home")) # Redirects to home page
        return redirect(url_for('views.home')) #Redirects to home page
    return render_template("igcse-options.html",user=current_user,options=o,block1=block1.subjects.split(","),block2=block2.subjects.split(","),block3=block3.subjects.split(","),igcse_plans=igcse_plans) # Renders options page
  elif course.upper() == "IB": # Checks if the user has selected IB
    if request.method == "POST" and current_user.role == "Student": # Checks if the user is a student and if the request method is POST
        current_user.studying_ib = request.form.get("ib") # Gets the IB plans from the form
        group1 = request.form.get('group1') # Gets the group 1 from the form in home.html
        if "self" in group1.lower(): # Checks if the user has selected self taught
          group1 += " "+request.form.get("ssst-input") # If the user has selected self taught, it adds the self taught subject to the group
        if group1 != "IB Courses": # Checks if the user has selected IB Courses
          group1 += " "+request.form.get(request.form.get('group1')+"-select") # If the user has not selected IB Courses, it adds the subject to the group
        group2 = request.form.get('group2') # Gets the group 2 from the form in home.html
        if group2 != "IB Courses": # Checks if the user has selected IB Courses
          group2 += " "+request.form.get(group2+"-select") # If the user has not selected IB Courses, it adds the subject to the group
        group3 = request.form.get('group3') # Gets the group 3 from the form in home.html
        if group3 != "IB Courses": # Checks if the user has selected IB Courses
          group3 += " "+request.form.get(group3+"-select")
        group4 = request.form.get('group4') # Gets the group 4 from the form in home.html
        if group4 != "IB Courses": # Checks if the user has selected IB Courses
          group4 += " "+request.form.get(group4+"-select") # If the user has not selected IB Courses, it adds the subject to the group
        group5 = request.form.get('group5') # Gets the group 5 from the form in home.html
        if group5 != "IB Courses": # Checks if the user has selected IB Courses
          group5 += " "+request.form.get(group5+"-select") # If the user has not selected IB Courses, it adds the subject to the group
        group6 = request.form.get('group6') # Gets the group 6 from the form in home.html
        group6 += " " + request.form.get(group6+"-select-group6") # Gets the group 6 from the form in home.html
        bool = False # If the user has made any selections yet, it will set the selected column to False
        if not Subjects.query.filter_by(user_id=current_user.id,course="IB",selected=True).first(): # If the user has not made any selections yet, it will set the selected column to False
          bool = True # If the user has not made any selections yet, it will set the selected column to True
        x = len(Subjects.query.filter_by(user_id=current_user.id).all())+1 # Gets the number of drafts the user has made
        while Subjects.query.filter_by(name="Draft "+str(x),user_id=current_user.id).first():
          x+=1 # Checks if the draft name already exists, if it does, it increments x by 1
        id = ''.join(random.choices(string.ascii_letters + string.digits, k=16)) # Generates a random id for the draft
        while Subjects.query.filter_by(id=id).first(): # Checks if the id already exists, if it does, it generates a new one
          id = ''.join(random.choices(string.ascii_letters + string.digits, k=16)) # Generates a random id for the draft
        new_subject = Subjects(group1=group1,group2=group2,group3=group3,group4=group4,group5=group5,group6=group6,user_id=current_user.id,name="Draft "+str(x),selected=bool,course="IB",id=id,datetime=datetime.now(timezone(timedelta(hours=8))).strftime("%d/%m/%Y %H:%M:%S")) # Register new entry to database
        flash("Options selected successfully!",category="success") # Flashes a success message
        db.session.add(new_subject) # Adds new entry, but needs to be committed
        db.session.commit() # Commits changes
        if request.form.get('email'): # Checks if the user wants to send an email
          msg = MIMEMultipart("alternative") # This allows us to send HTML emails
          msg["Subject"] = "IB Options - Nexus Options" # This is the subject of the email
          msg["From"] = EMAIL_ADDRESS # This is the email address that the email will be sent from
          msg["To"] = current_user.email # This is the email that the user entered in the form
          new_group5 = group5 # Gets the group 5 from the form in home.html
          if new_group5 != "IB Courses": # Checks if the group 5 is not IB Courses
            new_group5 = "Mathematics "+group5 # If it's not IB Courses, it sets it to Mathematics + group 5
          html = f"""
          <!DOCTYPE html><html><body style="color:black">
          <div style="padding:20px; margin:auto;" align="center">
            <h1>Your IB Options:</h1>
            <h2>{group1}</h2>
            <h2>{group2}</h2>
            <h2>{group3}</h2>
            <h2>{group4}</h2>
            <h2>{new_group5}</h2>
            <h2>{group6}</h2>
          </div></body></html>
          """ # This is the HTML of the email
          msg.attach(MIMEText(html, "html")) # This attaches the HTML to the email
          with smtplib.SMTP_SSL("smtp.elasticemail.com", 465) as smtp: # This is the SMTP server for Elastic Email
            try: # This is if the email could be sent
              smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD) # This logs into the email account
              smtp.send_message(msg) # This sends the email
              db.session.commit() # This commits the changes to the database
              flash("An email has been sent to your email address",category="success") # This flashes a success message
            except Exception as e:
              flash("An error occured, please try again",category="error") # This flashes an error message
              print(e)
              return redirect(url_for("views.home")) # Redirects to home page
        return redirect(url_for('views.home')) # Redirects to home page
    return render_template("ib-options.html",user=current_user,options=o,ib_plans=ib_plans) # Renders options page
  else: # If the user has not selected IGCSE, it will redirect to the 404 page
    return redirect(url_for("views.nopage")) # Redirects to 404 page
@views.route('/blocks',methods=["GET","POST"]) # Blocks page, allows both get and post methods
@login_required # Only allows logged in users to access
def blocks(): # This is the function that will be called when the user tries to access the blocks page
  if current_user.role == "Student": # Checks if the user is a student
    return redirect(url_for("views.nopage")) # Redirects to 404 page
  block1 = Block.query.filter_by(id=1).first() # Gets the subjects in block 1
  block2 = Block.query.filter_by(id=2).first() # Gets the subjects in block 2
  block3 = Block.query.filter_by(id=3).first() # Gets the subjects in block 1,2 and 3
  return render_template("blocks.html",user=current_user,block1=block1,block2=block2,block3=block3,blocks=[block.subjects.split(",") for block in [block1,block2,block3]]) # Renders blocks page
@views.route('/edit-options/<course>',methods=["GET","POST"]) # options page, allows both get and post methods
@login_required #Only allows logged in users to access
def edit_options(course): # This is the function that will be called when the user tries to edit their options
  if last_date: # Checks if the request is past the deadline
    return redirect(url_for("views.deadlinepassed")) # Redirects to deadline passed page
  if course.upper() != "IGCSE" and course.upper() != "IB": # Checks if the user has selected IGCSE
    return redirect(url_for("views.nopage")) # Redirects to 404 page
  if current_user.role == "Admin": # Checks if the user is an admin
    return redirect(url_for("views.nopage")) # Redirects to 404 page
  o = Subjects.query.filter_by(user_id=current_user.id,course=course.upper()).all() # Gets the subject selections made by the user
  block1 = Block.query.filter_by(id=1).first() # Gets the subjects in block 1
  block2 = Block.query.filter_by(id=2).first() # Gets the subjects in block 2
  block3 = Block.query.filter_by(id=3).first() # Gets the subjects in block 3
  if o == []: #If the user has not made any selections yet, it will return an empty list, so we set o to None
    o = None # This is to tell the frontend we do not have any submissions yet
  else: #If the user has made selections, it will return a list of all their selections
    try:
      o = o[-1]  # Gets the most recent submission
    except: # If the user has not made any selections yet, it will return an empty list, so we set o to Noner
      flash("Please select your options first",category="warning") # Flashes a warning message
      return redirect(url_for("views.options",course=course.upper()))
  if o == None: # Checks if the user has not made any selections yet
    flash("Please select your options first",category="warning") # Flashes a warning message
    return redirect(url_for("views.options",course=course.upper())) # Redirects to options page
  return render_template(f"select-{course.lower()}-draft.html",user=current_user,options=o,drafts=Subjects.query.filter_by(user_id=current_user.id,course=course.upper()).all(),igcse_plans=igcse_plans,ib_plans=ib_plans) # Renders edit options page
@views.route('/edit-draft/<subject_id>',methods=["GET","POST"]) # options page, allows both get and post methods
@login_required #Only allows logged in users to access
def edit_draft(subject_id): # This is the function that will be called when the user tries to edit their options
  if last_date: # Checks if the deadline has passed
    return redirect(url_for("views.deadlinepassed")) # Redirects to deadline passed page
  if current_user.role == "Admin": # Checks if the user is an admin
    return redirect(url_for("views.nopage")) # Redirects to 404 page
  o = Subjects.query.filter_by(user_id=current_user.id).all() # Gets the subject selections made by the user
  block1 = Block.query.filter_by(id=1).first() # Gets the subjects in block 1
  block2 = Block.query.filter_by(id=2).first() # Gets the subjects in block 2
  block3 = Block.query.filter_by(id=3).first() # Gets the subjects in block 3
  if o == []: #If the user has not made any selections yet, it will return an empty list, so we set o to None
    o = None # This is to tell the frontend we do not have any submissions yet
  else: #If the user has made selections, it will return a list of all their selections
    try: # Tries to get the most recent submission
      o = Subjects.query.filter_by(id=subject_id).first() # Gets the most recent submission
      if o.user_id != current_user.id: # Checks if the user is trying to edit someone else's submission
        return redirect(url_for("views.nopage")) # Redirects to 404 page
    except: 
      return redirect(url_for("views.nopage")) # Redirects to 404 page
  if o == None: # Checks if the user has not made any selections yet
    flash("Please select your options first",category="warning") # Flashes a warning message
    return redirect(url_for("views.options")) # Redirects to options page
  if request.method == "POST" and current_user.role == "Student": # Checks if the user is a student and if the request method is POST
      if o.course.upper() == "IGCSE":
        draft = Subjects.query.filter_by(id=subject_id).first() # Gets the most recent submission
        if not draft: # Checks if the draft does not exist
          flash("Draft not found",category="error") # Flashes an error message
          return redirect(url_for("views.home")) # Redirects to home page
        draft.lote = request.form.get('lote') # Gets the LOTE from the form in home.html
        if request.form.get('lote') == "Chinese": # Checks if the user has selected Chinese as their LOTE
          draft.lote_level = request.form.get('chinese') #If it's chinese it uses chinese_form in home.html
        else: # If it's not Chinese, it uses the other_form in home.html
          draft.lote_level = "" #If it's not chinese it uses other_form in home.html
        if request.form.get('elective1') not in block1.subjects.split(","): # Checks if the elective is in block 1
          draft.elective1 = "N/A" # If it's not in block 1, it sets it to N/A
        else: # If it's in block 1, it sets it to the elective
          draft.elective1 = request.form.get('elective1') # This is the same as the options page, but it will update the existing entry instead of creating a new one
        if request.form.get('elective2') not in block2.subjects.split(","): # Checks if the elective is in block 2
          draft.elective2 = "N/A" # If it's not in block 2, it sets it to N/A
        else: # If it's in block 2, it sets it to the elective
          draft.elective2 = request.form.get('elective2') # This is the same as the options page, but it will update the existing entry instead of creating a new one
        if request.form.get('elective3') not in block3.subjects.split(","): # Checks if the elective is in block 3
          draft.elective3 = "N/A" # If it's not in block 3, it sets it to N/A
        else: # If it's in block 3, it sets it to the elective
          draft.elective3 = request.form.get('elective3') # This is the same as the options page, but it will update the existing entry instead of creating a new one
        draft.reserve_choice = request.form.get('reserve')
        #request.form.get() gets the data from the input with the name of the string in the brackets. This allows us to fetch the data from the form in home.html
      elif o.course.upper() == "IB":
        draft = Subjects.query.filter_by(id=subject_id).first() # Gets the most recent submission
        if not draft: # Checks if the draft does not exist
          flash("Draft not found",category="error") # Flashes an error message
          return redirect(url_for("views.home")) # Redirects to home page
        group1 = request.form.get('group1') # Gets the group 1 from the form in home.html
        draft.group1 = group1 # Gets the group 1 from the form in home.html
        if "self" in draft.group1.lower(): # Checks if the user has selected self taught
          draft.group1 += " "+request.form.get("ssst-input") # If the user has selected self taught, it adds the self taught subject to the group
        if draft.group1 != "IB Courses": # Checks if the group 1 is not IB Courses
          draft.group1 += " "+request.form.get(request.form.get('group1')+"-select") # Gets the group 1 from the form in home.html
        group2 = request.form.get('group2') # Gets the group 2 from the form in home.html
        draft.group2 = group2 # Gets the group 2 from the form in home.html
        if group2 != "IB Courses": # Checks if the group 2 is not IB Courses
          draft.group2 += " "+request.form.get(group2+"-select") # Gets the group 2 from the form in home.html
        group3 = request.form.get('group3') # Gets the group 3 from the form in home.html
        draft.group3 = group3 # Gets the group 3 from the form in home.html
        if group3 != "IB Courses": # Checks if the group 3 is not IB Courses
          draft.group3 += " "+request.form.get(group3+"-select") # Gets the group 3 from the form in home.html
        group4 = request.form.get('group4') # Gets the group 4 from the form in home.html
        draft.group4 = group4 # Gets the group 4 from the form in home.html
        if group4 != "IB Courses": # Checks if the group 4 is not IB Courses
          draft.group4 += " "+request.form.get(group4+"-select") # Gets the group 4 from the form in home.html
        group5 = request.form.get('group5') # Gets the group 5 from the form in home.html
        draft.group5 = group5 # Gets the group 5 from the form in home.html
        if group5 != "IB Courses": # Checks if the group 5 is not IB Courses
          draft.group5 += " "+request.form.get(group5+"-select") # Gets the group 5 from the form in home.html
        group6 = request.form.get('group6') # Gets the group 6 from the form in home.html
        draft.group6 = group6 + " " + request.form.get(group6+"-select-group6") # Gets the group 6 from the form in home.html
      if o.course.lower() == "igcse": # The user is editing IGCSE options
        current_user.studying_igcse = request.form.get("igcse") # Gets the IGCSE plans from the form
      else: # The user is editing IB options
        current_user.studying_ib = request.form.get("ib") # Gets the IB plans from the form
      draft.datetime = datetime.now(timezone(timedelta(hours=8))).strftime("%d/%m/%Y %H:%M:%S") # Gets the current date and time
      db.session.commit() #Commits changes
      if request.form.get('email'): # Checks if the user wants to send an email
        if draft.course == "IB": # Checks if the user has selected IB
          msg = MIMEMultipart("alternative") # This allows us to send HTML emails
          msg["Subject"] = "IB Options - Nexus Options" # This is the subject of the email
          msg["From"] = EMAIL_ADDRESS # This is the email address that the email will be sent from
          msg["To"] = current_user.email # This is the email that the user entered in the form
          group5 = draft.group5 # Gets the group 5 from the form in home.html
          if group5 != "IB Courses": # Checks if the group 5 is not IB Courses
            group5 = "Mathematics "+draft.group5 # If it's not IB Courses, it sets it to Mathematics + group 5
          html = f"""
          <!DOCTYPE html><html><body style="color:black">
          <div style="padding:20px; margin:auto;" align="center">
            <h1>Your IB Options:</h1>
            <h2>{draft.group1}</h2>
            <h2>{draft.group2}</h2>
            <h2>{draft.group3}</h2>
            <h2>{draft.group4}</h2>
            <h2>{group5}</h2>
            <h2>{draft.group6}</h2>
          </div></body></html>
          """ # This is the HTML of the email
          msg.attach(MIMEText(html, "html")) # This attaches the HTML to the email
          with smtplib.SMTP_SSL("smtp.elasticemail.com", 465) as smtp: # This is the SMTP server for Elastic Email
            try: # This is if the email could be sent
              smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD) # This logs into the email account
              smtp.send_message(msg) # This sends the email
              flash("An email has been sent to your email address",category="success") # This flashes a success message
            except Exception as e:
              flash("An error occured, please try again",category="error") # This flashes an error message
              print(e)
              return redirect(url_for("views.home"))
        elif draft.course == "IGCSE":
          lote = draft.lote
          if draft.lote == "Chinese":
            lote = draft.lote_level
          msg = MIMEMultipart("alternative") # This allows us to send HTML emails
          msg["Subject"] = "IGCSE Options - Nexus Options" # This is the subject of the email
          msg["From"] = EMAIL_ADDRESS # This is the email address that the email will be sent from
          msg["To"] = current_user.email # This is the email that the user entered in the form
          html = f"""
          <!DOCTYPE html><html><body style="color:black">
          <div style="padding:20px; margin:auto;" align="center">
            <h1>Your IGCSE Options:</h1>
            <h2>{lote}</h2>
            <h2>{draft.elective1}</h2>
            <h2>{draft.elective2}</h2>
            <h2>{draft.elective3}</h2>
            <h2>Reserve choice: {draft.reserve_choice}</h2>
          </div></body></html>
          """ # This is the HTML of the email
          msg.attach(MIMEText(html, "html")) # This attaches the HTML to the email
          with smtplib.SMTP_SSL("smtp.elasticemail.com", 465) as smtp: # This is the SMTP server for Elastic Email
            try: # This is if the email could be sent
              smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD) # This logs into the email account
              smtp.send_message(msg) # This sends the email
              db.session.commit() # This commits the changes to the database
              flash("An email has been sent to your email address",category="success") # This flashes a success message
              return redirect(url_for("views.home"))
            except Exception as e:
              flash("An error occured, please try again",category="error") # This flashes an error message
              print(e)
              return redirect(url_for("views.home"))
      flash("Updated options successfully!",category="success") # Flashes a success message
      return redirect(url_for('views.home')) #Redirects to home page
  if o.course == "IGCSE": # Checks if the user has selected IGCSE
    return render_template("edit-igcse-options.html",user=current_user,options=o,block1=block1.subjects.split(","),block2=block2.subjects.split(","),block3=block3.subjects.split(","),deadline=last_date,igcse_plans=igcse_plans) # Renders edit options page
  elif o.course.upper() == "IB": # Checks if the user has selected IB
    return render_template("edit-ib-options.html",user=current_user,options=o,deadline=last_date,ib_plans=ib_plans) # Renders edit options page
  else: # If the user has not selected IGCSE, it will redirect to the 404 page
    return redirect(url_for("views.nopage")) # Redirects to 404 page
@views.route("/subject-info") # subject info page, does not need requests so we do not add any methods
def subject_info(): # This is the function that will be called when the user tries to access the subject info page
  o = None # This is to tell the frontend we do not have any submissions yet
  if current_user.is_authenticated: # Checks if the user is logged in
    if current_user.role == "Student": # Checks if the user is a student
      o = Subjects.query.filter_by(user_id=current_user.id).all() # Gets the subject selections made by the user
      if o == []: # If the user has not made any selections yet, it will return an empty list, so we set o to None
        o = None # This is to tell the frontend we do not have any submissions yet
      else: # If the user has made selections, it will return a list of all their selections
        o = o[-1] # Gets the most recent submission
  return render_template("subjects.html",user=current_user,options=o)
@views.route('/subjects/<course>') # subjects information page, does not need requests so we do not add any methods
def subjects(course): # This is the function that will be called when the user tries to access the subjects page
  if course.lower() not in ["ib","igcse"]: # Checks if the user has selected IGCSE
    return redirect(url_for("views.nopage")) # Redirects to 404 page
  o = None # This is to tell the frontend we do not have any submissions yet
  if current_user.is_authenticated: # Checks if the user is logged in
    if current_user.role == "Student": # Checks if the user is a student
      o = Subjects.query.filter_by(user_id=current_user.id).all() # Gets the subject selections made by the user
      if o == []: # If the user has not made any selections yet, it will return an empty list, so we set o to None
        o = None # This is to tell the frontend we do not have any submissions yet
      else: # If the user has made selections, it will return a list of all their selections
        o = o[-1] # Gets the most recent submission
  return render_template(course.lower()+"-subjects.html",user=current_user,options=o) # Renders subjects page
@views.route("/update-notes",methods=["GET","POST"]) # This is the route for the update notes page
@login_required # This checks if the user is logged in
def update_notes(): # This is the function that will be called when the user tries to update their notes
  if current_user.role == "Admin": # Checks if the user is an admin
    if request.method == "POST" and request.data: # Checks if the request method is POST and if the request has data
      data = json.loads(request.data) # Gets the data from the request
      user = User.query.filter_by(email=data["email"]).first() # Gets the user from the database
      user.notes = data["notes"] # Sets the user's notes to the new notes
      db.session.commit() # Commits the changes to the database
      return jsonify({"success":"y"}) # If the user exists, it will return a json object with the key "success" and the value "y"
    else: # If the request method is not POST or if the request does not have data, it will redirect to the 404 page
      return redirect(url_for("views.nopage")) # Redirects to 404 page
  else: # If the user is not an admin, it will redirect to the 404 page
    return redirect(url_for("views.nopage")) # Redirects to 404 page
@views.route("/delete-subject",methods=["GET","POST"]) # This is the route for the delete subject page
def delete_subject(): # This is the function that will be called when the user tries to delete a subject
  if current_user.role == "Admin": # Checks if the user is an admin
    if request.method == "POST" and request.data: # Checks if the request method is POST and if the request has data
      data = json.loads(request.data) # Gets the data from the request
      subject = data["subject"] # Gets the subject from the data
      idx = int(data["idx"]) # Gets the index of the block from the data
      if idx < 1 or idx > 3: # Checks if the index is valid
        return jsonify({"success":"n"}) # If the index is not valid, it will return a json object with the key "success" and the value "n"
      block = Block.query.filter_by(id=idx).first() # Gets the block from the database
      subjects = block.subjects.split(",") # Gets the subjects in the block
      if subject in subjects: # Checks if the subject is in the block
        subjects.remove(subject) # Removes the subject from the block
        block.subjects = ",".join(subjects) # Sets the subjects in the block to the new subjects
        if idx == 1: # Checks if the index is 1
          affected = Subjects.query.filter_by(elective1=subject).all() # Gets the subjects that have the subject as their elective 1
        elif idx == 2: # Checks if the index is 2
          affected = Subjects.query.filter_by(elective2=subject).all() # Gets the subjects that have the subject as their elective 2
        else: # The index is 3
          affected = Subjects.query.filter_by(elective3=subject).all() # Gets the subjects that have the subject as their elective 3
        for s in affected: # Iterates through all the subjects that have the subject as their elective
          if idx == 1: # Checks if the index is 1
            s.elective1 = "N/A" # Sets the elective 1 to N/A
          elif idx == 2: # Checks if the index is 2
            s.elective2 = "N/A" # Sets the elective 2 to N/A
          else: # The index is 3
            s.elective3 = "N/A" # Sets the elective 3 to N/A
        db.session.commit() # Commits the changes to the database
        return jsonify({"success":"y"}) # If the subject exists, it will return a json object with the key "success" and the value "y"
      else: # If the subject does not exist, it will return a json object with the key "success" and the value "n"
        return jsonify({"success":"n"}) # If the subject does not exist, it will return a json object with the key "success" and the value "n"
    else: # If the request method is not POST or if the request does not have data, it will redirect to the 404 page
      return redirect(url_for("views.nopage")) # Redirects to 404 page
  else: # If the user is not an admin, it will redirect to the 404 page
    return redirect(url_for("views.nopage")) # Redirects to 404 page
@views.route("/add-subject",methods=["GET","POST"]) # This is the route for the add subject page
def add_subject(): # This is the function that will be called when the user tries to add a subject
  if current_user.role == "Admin": # Checks if the user is an admin
    if request.method == "POST" and request.data: # Checks if the request method is POST and if the request has data
      data = json.loads(request.data) # Gets the data from the request
      subject = data["subject"] # Gets the subject from the data
      characters = list("/-_@?![]=$&:;,") # This is the list of special characters that are allowed in the draft name
      for character in characters: # Checks if the new name contains special characters
        if character in subject: # Checks if the new name contains special characters
          return jsonify({"success":"special_characters"}) # If the new name contains special characters, it will return a json object with the key "success" and the value "special_characters"
      idx = int(data["idx"]) # Gets the index of the block from the data
      if idx < 1 or idx > 3: # Checks if the index is valid
        return jsonify({"success":"n"}) # If the index is not valid, it will return a json object with the key "success" and the value "n"
      block = Block.query.filter_by(id=idx).first() # Gets the block from the database
      subjects = block.subjects.split(",") # Gets the subjects in the block
      if subject not in subjects: # Checks if the subject is not in the block
        subjects.append(subject) # Adds the new subject to the block
        block.subjects = ",".join(subjects) # Sets the subjects in the block to the new subjects
        db.session.commit() # Commits the changes to the database
        return jsonify({"success":"y"}) # If the subject does not exist, it will return a json object with the key "success" and the value "y"
      else: # If the subject already exists, it will return a json object with the key "success" and the value "n"
        return jsonify({"success":"n"}) # If the subject already exists, it will return a json object with the key "success" and the value "n"
    else: # If the request method is not POST or if the request does not have data, it will redirect to the 404 page
      return redirect(url_for("views.nopage")) # Redirects to 404 page
@views.route('/edit-subject', methods = ["GET","POST"]) # This is the route for the edit subject page
def edit_subject(): # This is the function that will be called when the user tries to edit a subject
  if last_date: # Checks if deadline has been crossed
    return redirect(url_for("views.deadlinepassed"))
  if current_user.role == "Admin": # Checks if the user is an admin
    if request.method == "POST" and request.data: # Checks if the request method is POST and if the request has data
      data = json.loads(request.data) # Gets the data from the request
      old_subject = data["old_subject"] # Gets the old name from the data
      new_subject = data["new_subject"] # Gets the new name from the data
      characters = list("/-_@?![]=$&:;,") # This is the list of special characters that are allowed in the draft name
      for character in characters: # Checks if the new name contains special characters
        if character in new_subject: # Checks if the new name contains special characters
          return jsonify({"success":"special_characters"}) # If the new name contains special characters, it will return a json object with the key "success" and the value "special_characters"
      idx = int(data["idx"]) # Gets the index of the block from the data
      if idx < 1 or idx > 3: # Checks if the index is valid
        return jsonify({"success":"n"}) # If the index is not valid, it will return a json object with the key "success" and the value "n"
      block = Block.query.filter_by(id=idx).first() # Gets the block from the database
      subjects = block.subjects.split(",") # Gets the subjects in the block
      if old_subject in subjects: # Checks if the subject is in the block
        subjects[subjects.index(old_subject)] = new_subject # Replaces the old subject with the new subject
        block.subjects = ",".join(subjects) # Sets the subjects in the block to the new subjects
        if idx == 1: # If the index is 1, it will set the elective 1 to the new subject
          affected = Subjects.query.filter_by(elective1=old_subject).all() # Gets the subjects that have the old subject as their elective
        elif idx == 2: # If the index is 2, it will set the elective 2 to the new subject
          affected = Subjects.query.filter_by(elective2=old_subject).all() # Gets the subjects that have the old subject as their elective
        else: # If the index is 3, it will set the elective 3 to the new subject
          affected = Subjects.query.filter_by(elective3=old_subject).all() # Gets the subjects that have the old subject as their elective
        for s in affected: # Iterates through all the subjects that have the old subject as their elective
          if idx == 1: # If the index is 1, it will set the elective 1 to the new subject
            s.elective1 = new_subject # If the index is 1, it will set the elective 1 to the new subject
          elif idx == 2: # If the index is 2, it will set the elective 2 to the new subject
            s.elective2 = new_subject # If the index is 2, it will set the elective 2 to the new subject
          else: # If the index is 3, it will set the elective 3 to the new subject
            s.elective3 = new_subject # Sets the new subject to the new subject
        db.session.commit() # Commits the changes to the database
        return jsonify({"success":"y"}) # If the subject exists, it will return a json object with the key "success" and the value "y"
      else: # If the subject does not exist, it will return a json object with the key "success" and the value "n"
        return jsonify({"success":"n"}) # If the subject does not exist, it will return a json object with the key "success" and the value "n"
    else: # If the request method is not POST or if the request does not have data, it will redirect to the 404 page
      return redirect(url_for("views.nopage"))
@views.route("/delete-draft",methods=["GET","POST"]) # This is the route for the delete draft page
def delete_draft(): # This is the function that will be called when the user tries to delete a draft
  if last_date: # Checks if the deadline has passed
    return jsonify({"success":"deadline"}) # If the deadline has passed, it will return a json object with the key "success" and the value "deadline"
  if current_user.role == "Student": # Checks if the user is a student
    if request.method == "POST" and request.data: # Checks if the request method is POST and if the request has data
      data = json.loads(request.data) # Gets the data from the request
      name = data["name"] # Gets the name of the draft from the data
      subject = Subjects.query.filter_by(name=name).first() # Gets the draft from the database
      if subject and subject.user_id == current_user.id: # Checks if the draft exists and if the user is the owner of the draft
        db.session.delete(subject) # Deletes the draft from the database
        db.session.commit() # Commits the changes to the database
        return jsonify({"success":"y"}) # If the draft exists and if the user is the owner of the draft, it will return a json object with the key "success" and the value "y"
      else: # If the draft does not exist or if the user is not the owner of the draft, it will return a json object with the key "success" and the value "n"
        return jsonify({"success":"n"}) # If the draft does not exist or if the user is not the owner of the draft, it will return a json object with the key "success" and the value "n"
    else: # If the request method is not POST or if the request does not have data, it will redirect to the 404 page
      return redirect(url_for("views.nopage")) # This is the function that will be called when the user tries to delete a draft
  else: # If the user is not a student, it will redirect to the 404 page
    return redirect(url_for("views.nopage")) # This is the function that will be called when the user tries to delete a draft
@views.route("/edit-draft-name",methods=["GET","POST"]) # This is the route for the edit draft name page
def edit_draft_name(): # This is the function that will be called when the user tries to edit the name of a draft
  if last_date: # Checks if the deadline has passed
    return jsonify({"success":"deadline"}) # If the deadline has passed, it will return a json object with the key "success" and the value "deadline"
  if current_user.role == "Student": # Checks if the user is a student
    if request.method == "POST" and request.data: # Checks if the request method is POST and if the request has data
      data = json.loads(request.data) # Gets the data from the request
      old_name = data["old_name"] # Gets the old name from the data
      new_name = data["new_name"] # Gets the new name from the data
      characters = list("/-_@?![]=$&:;,") # This is the list of special characters that are allowed in the draft name
      for character in characters: # Checks if the new name contains special characters
        if character in new_name: # Checks if the new name contains special characters
          return jsonify({"success":"special_characters"}) # If the new name contains special characters, it will return a json object with the key "success" and the value "special_characters"
      if new_name == None: # Checks if the new name is None
        return jsonify({"success":"n"}) # If the new name is None, it will return a json object with the key "success" and the value "n"
      subject = Subjects.query.filter_by(name=old_name,user_id=current_user.id).first() # Gets the draft from the database
      duplicate = Subjects.query.filter_by(name=new_name,user_id=current_user.id).first() # Checks if the draft already exists
      if duplicate: # Checks if the draft already exists
        return jsonify({"success":"exists"}) # If the draft already exists, it will return a json object with the key "success" and the value "exists"
      if subject and subject.user_id == current_user.id: # Checks if the draft exists and if the user is the owner of the draft
        subject.name = new_name # Sets the name of the draft to the new name
        db.session.commit() # Commits the changes to the database
        return jsonify({"success":"y"}) # If the draft exists and if the user is the owner of the draft, it will return a json object with the key "success" and the value "y"
      else: # If the draft does not exist or if the user is not the owner of the draft, it will return a json object with the key "success" and the value "n"
        return jsonify({"success":"n"}) # If the draft does not exist or if the user is not the owner of the draft, it will return a json object with the key "success" and the value "n"
    else: # If the request method is not POST or if the request does not have data, it will redirect to the 404 page
      return redirect(url_for("views.nopage")) # This is the function that will be called when the user tries to edit the name of a draft
  else: # If the user is not a student, it will redirect to the 404 page
    return redirect(url_for("views.nopage")) # This is the function that will be called when the user tries to edit the name of a draft
@views.route("/select-draft",methods=["GET","POST"]) # the frontend sends a post request to select a draft as the main draft, so it allows both get and post requests
def select_draft(): # This is the function that will be called when the user tries to select a draft as the main draft
  if last_date: # Checks if the deadline has passed
    return jsonify({"success":"deadline"}) # If the deadline has passed, it will return a json object with the key "success" and the value "deadline"
  if current_user.role == "Student": # Checks if the user is a student
    if request.method == "POST" and request.data: # Checks if the request method is POST and if the request has data
      data = json.loads(request.data) # Gets the data from the request
      id = data["id"] # Gets the id of the draft from the data
      subject = Subjects.query.filter_by(id=id).first() # Gets the draft from the database
      if subject and subject.user_id == current_user.id: # Checks if the draft exists and if the user is the owner of the draft
        for s in Subjects.query.filter_by(user_id=current_user.id,course=subject.course).all(): # Iterates through all the drafts made by the user in the same course as the selected draft
          s.selected = False # Sets all the other drafts of the same course to not selected
        subject.selected = True # Sets the selected draft to selected
        db.session.commit() # Commits the changes to the database
        return jsonify({"success":"y"}) # If the draft exists and if the user is the owner of the draft, it will return a json object with the key "success" and the value "y"
      else: # If the draft does not exist or if the user is not the owner of the draft, it will return a json object with the key "success" and the value "n"
        return jsonify({"success":"n"}) # If the draft does not exist or if the user is not the owner of the draft, it will return a json object with the key "success" and the value "n"
    else: # If the request method is not POST or if the request does not have data, it will redirect to the 404 page
      return redirect(url_for("views.nopage")) # Redirects to 404 page
  else: # If the user is not a student, it will redirect to the 404 page
    return redirect(url_for("views.nopage")) # Redirects to 404 page
@views.route('/select-plans',methods=["GET","POST"]) # This is the route for the select plans page
@login_required # Only allows logged in users to access
def select_plans(): # This is the function that will be called when the user tries to access the select plans page
  if last_date: # Checks if the deadline has passed
    return redirect(url_for("views.deadlinepassed")) # Redirects to deadline passed page
  if current_user.role != "Student": # Checks if the user is a student
    return redirect(url_for("views.nopage")) # Redirects to 404 page
  if last_date: # Checks if the deadline has passed
    return redirect(url_for("views.deadlinepassed"))
  o = Subjects.query.filter_by(user_id=current_user.id).all() # Gets the subject selections made by the user
  if o == []: # If the user has not made any selections yet, it will return an empty list, so we set o to None
    o = None # This is to tell the frontend we do not have any submissions yet
  else: # If the user has made selections, it will return a list of all their selections
    o = o[-1] # Gets the most recent submission
  if current_user.role == "Student": # Checks if the user is a student
    return render_template("select-plans.html",user=current_user,options=o) # Renders select plans page
@views.route('/plans/<course>',methods=["GET","POST"]) # This is the route for the plans page
@login_required # Only allows logged in users to access
def plans(course): # This is the function that will be called when the user tries to access the plans page
  if last_date: # Checks if the deadline has passed
    return redirect(url_for("views.deadlinepassed")) # Redirects to deadline passed page
  if course.upper() != "IGCSE" and course.upper() != "IB": # Checks if the user has selected IGCSE
    return redirect(url_for("views.nopage")) # Redirects to 404 page
  if current_user.role == "Admin": # Checks if the user is an admin
    return redirect(url_for("views.nopage")) # Redirects to 404 page
  if request.method == "POST": # Checks if the request method is POST
    if current_user.role == "Student": # Checks if the user is a student
      if course.upper() == "IGCSE": # Checks if the user has selected IGCSE
        current_user.studying_igcse = request.form.get("igcse") # Gets the IGCSE plans from the form in plans.html
      if course.upper() == "IB": # Checks if the user has selected IB
        current_user.studying_ib = request.form.get("ib") # Gets the IB plans from the form in plans.html
      db.session.commit() # Commits the changes to the database
      flash("Updated plans successfully!",category="success") # Flashes a success message
    else: # If the user is not a student, it will redirect to the 404 page
      return redirect(url_for("views.nopage")) # Redirects to 404 page
  if current_user.role == "Admin": # Checks if the user is an admin
    return redirect(url_for("views.nopage")) # Redirects to 404 page
  elif current_user.role == "Student": # Checks if the user is a student
    igcse_options = ["I intend to take IGCSEs at Nexus","I am looking at studying at another school in Singapore","I am likely to leave Singapore and go to a new school in another country","I am not sure of my plans for IGCSE"] # This is the list of options for the IGCSE plans
    ib_options = ["I intend to study IBDP/IB Courses at Nexus next year","I am exploring options at other schools in Singapore for next year","I am likely to leave Singapore and go to a new school in another country next year","I am not sure of my plans for IB"] # This is the list of options for the IB plans
    o = Subjects.query.filter_by(user_id=current_user.id).all() # Gets the subject selections made by the user
    if o == []: # If the user has not made any selections yet, it will return an empty list, so we set o to None
      o = None # This is to tell the frontend we do not have any submissions yet
    else: # If the user has made selections, it will return a list of all their selections
      o = o[-1] # Gets the most recent submission
    return render_template("plans.html",user=current_user,options=o,igcse_options=igcse_options,ib_options=ib_options,course=course) # Renders plans page
@views.route('/404') # 404 page
def nopage(): # This is the function that will be called when the user tries to access a page that does not exist
  o = None # This is to tell the frontend we do not have any submissions yet
  if current_user.is_authenticated: # Checks if the user is logged in
    if current_user.role == "Student": # Checks if the user is a student
      o = Subjects.query.filter_by(user_id=current_user.id).all() # Gets the subject selections made by the user
      if o == []: # If the user has not made any selections yet, it will return an empty list, so we set o to None
        o = None # This is to tell the frontend we do not have any submissions yet
      else: #If the user has made selections, it will return a list of all their selections
        o = o[-1] #Gets the most recent submission
  return render_template("404.html",user=current_user,options=o) #Renders 404 page
@views.route("/backup",methods=["GET","POST"]) # This is the route for the backup page
@login_required # Only allows logged in users to access
def backup(): # This is the function that will be called when the user tries to access the backup page
  if current_user.is_authenticated and current_user.email in ["fake.e@nexus.edu.sg"]: # Checks if the user is logged in and if the user is an admin
    if request.method == "POST": # Checks if the request method is POST
      students = [dict_object(student) for student in User.query.all()] # This converts the students to a dictionary
      with open("backup.json", "w") as f: # This opens the backup.json file
          json.dump(students, f) # This dumps the data to the backup.json file
      subjects = [dict_object(subject) for subject in Subjects.query.all()] # This converts the subjects to a dictionary
      with open("subjects.json", "w") as f: # This opens the subjects.json file
          json.dump(subjects, f) # This dumps the data to the subjects.json file
      blocks = [dict_object(block) for block in Block.query.all()] # This converts the blocks to a dictionary
      with open("blocks.json", "w") as f: # This opens the blocks.json file
          json.dump(blocks, f) #  This dumps the data to the blocks.json file
      flash("Backup created successfully!",category="success") # This flashes a success message
    last_edited = os.path.getmtime("blocks.json") # This gets the last edited time of the blocks.json file
    return render_template("backup.html",user=current_user,last_edited=last_edited,data=json.dumps([[dict_object(student) for student in User.query.all()],[dict_object(subject) for subject in Subjects.query.all()],[dict_object(block) for block in Block.query.all()]]),last_db_edit = os.path.getmtime("website/database.db")) # Renders backup page
  else:
    return redirect(url_for("views.nopage")) # Redirects to 404 page
@views.route("/deadlinepassed",methods=["GET","POST"])
def deadlinepassed(): # This is the function that will be called when the user tries to access the deadline passed page
   if not last_date: # Checks if the deadline has not passed
     return redirect(url_for("views.nopage")) # Returns the 404 page if the deadline has not passed
   o = None # This is to tell the frontend we do not have any submissions yet
   if current_user.is_authenticated: # Checks if the user is logged in
      if current_user.role == "Student": # Checks if the user is a student
         o = Subjects.query.filter_by(user_id=current_user.id).all() # Gets the subject selections made by the user
         if o == []: # If the user has not made any selections yet, it will return an empty list, so we set o to None 
            o = None # This is to tell the frontend we do not have any submissions yet
         else: # If the user has made selections, it will return a list of all their selections
            o = o[-1] # Gets the most recent submission
   return render_template("deadlinepassed.html",user=current_user,options=o) # Renders deadline passed page