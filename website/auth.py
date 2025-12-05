from flask import Blueprint, render_template, request, flash, redirect, url_for,jsonify
from sqlalchemy.sql import table
from .models import User
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from flask_login import login_user, login_required, logout_user, current_user
import random
import string
import json
import smtplib
from email.message import EmailMessage
import os
from dotenv import load_dotenv
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
link = "https://niss-options.replit.app/" # This is the link to the website
load_dotenv() # This loads the environment variables from the .env file
EMAIL_ADDRESS = os.getenv('EMAIL_ADDRESS') # This gets the email address from the .env file
EMAIL_PASSWORD = os.getenv('PASSWORD') # This gets the email password from the .env file

auth = Blueprint('auth', __name__) # This is the blueprint for the authentication pages
@auth.route('/login', methods=['GET', 'POST']) # This is the route for the login page
def login(): # This is the function that will be called when the user tries to login
    if request.method == 'POST': # This checks if the request method is POST
        email = request.form.get('email') # This gets the email from the form in login.html
        password = request.form.get('password') # This gets the password from the form in login.html
        user = User.query.filter_by(email=email).first() # This gets the user from the database
        if user: # This checks if the user exists
          if user.verified: # This checks if the user is verified
            if check_password_hash(user.password, password): # This checks if the password is correct
                flash('Logged in successfully!', category='success') # This flashes a success message
                login_user(user, remember=True) # This logs the user in
                return redirect(url_for('views.home')) # This redirects the user to the home page
            else: # This is if the password is incorrect
                flash('Incorrect password, try again.', category='error') # This flashes an error message
          else: # This is if the user is not verified
            flash("Account not verified, the OTP has been sent to your email. ",category='error') # This flashes an error message
        else: # This is if the user does not exist
            flash('Email does not exist.', category='error') # This flashes an error message
    return render_template("login.html", user=current_user) # This renders the login page
@auth.route('/logout') # This is the route for the logout page
@login_required # This checks if the user is logged in
def logout(): # This is the function that will be called when the user tries to logout
    logout_user() # This logs the user out
    return redirect(url_for('auth.login')) # This redirects the user to the login page
@auth.route('/confirm',methods=["GET","POST"]) # This is the route for the confirm page
def confirm(): # This is the function that will be called when the user tries to confirm their account
  if request.method == "POST": # This checks if the request method is POST
    user = User.query.filter_by(otp=request.form["otp"]).first() # This gets the user from the database
    if user and user.verified: # This checks if the user exists and if the user is verified
      flash("Account already verified, please log in") # This flashes an error message
    elif user: # This checks if the user is not verified
      user.verified = True # This sets the user to verified
      user.otp = "" # This sets the user's OTP to empty
      flash("Account verified successfully!",category="success") # This flashes a success message
      login_user(user) # This logs the user in
      db.session.commit() # This commits the changes to the database
      return redirect(url_for("views.home")) # This redirects the user to the home page
    else: # This is if the user does not exist
      flash("Invalid OTP", category = "error") # This flashes an error message
  return render_template("confirm.html",user=current_user) # This renders the confirm page
@auth.route('/sign-up', methods=['GET', 'POST']) # This is the route for the sign up page
def sign_up(): # This is the function that will be called when the user tries to sign up
  if request.method == 'POST': # This checks if the request method is POST
        email = request.form.get('email') # This gets the email from the form in sign_up.html
        if "@nexus.edu.sg" not in email: # This checks if the email is a Nexus email
          flash("Please use your Nexus email",category="warning") # This flashes a warning message
        name = email.split("@")[0].replace("."," ").title() # This gets the name from the email
        if len(name.split(" ")) == 3: # This checks if the name has 3 parts
            name = name.split(" ")[0] + " " + name.split(" ")[1] # This gets the name from the email
        else: # This is if the name has 2 parts
            name = name.split(" ")[1]+" "+name.split(" ")[0] # This gets the name from the email
        if email.split("@nexus.edu.sg")[0][-2:] not in [str(i) for i in range(99)]: # Student nexus emails end in their graduation year (john.doe.30@nexus.edu.sg) if they graduate in 2030 for example
          if email not in ["dummy.admin@nexus.edu.sg","fake.e@nexus.edu.sg","millington.h@nexus.edu.sg","shiel.d@nexus.edu.sg","sykes.a@nexus.edu.sg","holdcroft.v@nexus.edu.sg"]: # This checks if the email is a teacher email
            flash("Unauthorized teachers are not allowed to sign up",category="error") # This flashes an error message
            return redirect(url_for("auth.sign_up")) # This redirects the user to the sign up page
          role = "Admin" # This sets the user's role to admin
          year_group = 0 # This sets the user's year group to 0
        else: # This is if the email is a student email
          role = "Student" # This sets the user's role to student
          current_year = datetime.now().year - 2000 # This gets the current year
          current_month = datetime.now().month # This gets the current month
          if current_month < 8: # This checks if the current month is before August
            current_year -= 1 # This sets the current year to the previous year
          year_group = 14+current_year-int(email.split("@nexus.edu.sg")[0][-2:]) # This gets the user's year group
        password1 = request.form.get('password1') # This gets the password from the form in sign_up.html
        password2 = request.form.get('password2') # This gets the password confirmation from the form in sign_up.html
        user = User.query.filter_by(email=email).first() # This gets the user from the database
        if user: # This checks if the user exists
          if user.verified == True: # This checks if the user is verified
            flash('Email already exists.', category='error') # This flashes an error message
            return redirect(url_for("auth.login")) # This redirects the user to the confirm page
          else: # This is if the user is not verified
            flash("Account already exists, please verify it",category="error") # This flashes an error message
        elif password1 != password2: # This checks if the passwords match
            flash('Passwords don\'t match.', category='error') # This flashes an error message
        elif len(password1) < 8: # This checks if the password is at least 8 characters
            flash('Password must be at least 8 characters.', category='error') # This flashes an error message
        else: # This is if the user does not exist and the passwords match and the password is at least 8 characters
            otp = (''.join(random.choices(string.digits, k=6))) # This generates a random 6 digit OTP
            while User.query.filter_by(otp=otp).first(): # This checks if the OTP already exists
              otp = (''.join(random.choices(string.digits, k=6))) # This generates a new OTP
            user = User(email=email,  password=generate_password_hash(password1,  method='sha256'),verified=False,otp = otp,role=role,name=name,year_group=year_group) # This creates a new user
            db.session.add(user) # This adds the user to the database
            msg = MIMEMultipart("alternative") # This allows us to send HTML emails
            msg["Subject"] = "OTP for Nexus Options" # This is the subject of the email
            msg["From"] = EMAIL_ADDRESS # This is the email address that the email will be sent from
            msg["To"] = email # This is the email that the user entered in the form
            html = f"""
            <!DOCTYPE html><html><body style="color:black">
            <div style="padding:20px; margin:auto;" align="center">
              <p>Your OTP for Nexus Options:</p>
              <h2>{otp}</h2>
              <a href="{link+"confirm"}"
                 style="background-color:#454645; color:white; padding:15px 32px; text-decoration:none;">
                Verify Account
              </a>
            </div></body></html>
            """ # This is the HTML of the email
            msg.attach(MIMEText(html, "html")) # This attaches the HTML to the email
            with smtplib.SMTP_SSL("smtp.elasticemail.com", 465) as smtp: # This is the SMTP server for Elastic Email
              try: # This is if the email could be sent
                smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD) # This logs into the email account
                smtp.send_message(msg) # This sends the email
                db.session.commit() # This commits the changes to the database
                flash("An OTP has been sent to your email",category="success") # This flashes a success message
                return redirect(url_for("auth.confirm")) # This redirects the user to the confirm page
              except Exception as e: # This is if the email could not be sent
                print(e)
                flash("An error occured, please try again",category="error") # This flashes an error message
  return render_template("sign_up.html", user=current_user) # This renders the sign up page
@auth.route("/forgot",methods=["GET","POST"]) # This is the route for the forgot page
def forgot(): # This is the function that will be called when the user tries to forgot their password
  if request.method == "POST": # This checks if the request method is POST
    user = User.query.filter_by(email=request.form.get("email")).first() # This gets the user from the database
    if user: # This checks if the user exists
      flash("An OTP has been sent to your email.",category="success") # This flashes a success message
      return redirect(url_for("auth.restore")) # This redirects the user to the restore page
  return render_template("forgot.html",user=current_user) # This renders the forgot page
@auth.route("/verify-forgot",methods=["GET","POST"]) # This is the route for the verify forgot page
def check_forgot(): # This is the function that will be called when the user tries to verify their forgot password
  print("verify forgot") # This is the function that will be called when the user tries to verify their forgot password
  if request.data: # This checks if the request has data
    email = json.loads(request.data)["email"] # This gets the email from the form in sign_up.html
    user = User.query.filter_by(email=email).first() # This gets the user from the database
    if user and user.verified: # This checks if the user exists and if the user is verified
      otp = (''.join(random.choices(string.digits, k=6))) # This generates a random 6 digit OTP
      while User.query.filter_by(otp=otp).first(): # This checks if the OTP already exists
        otp = (''.join(random.choices(string.digits, k=6))) # This generates a new OTP
      user.otp = otp # This sets the user's OTP to the new OTP
      msg = MIMEMultipart("alternative") # This allows us to send HTML emails
      msg["Subject"] = "Password Reset - Nexus Options" # This is the subject of the email
      msg["From"] = EMAIL_ADDRESS # This is the email address that the email will be sent from
      msg["To"] = email # This is the email that the user entered in the form
      html = f"""
      <!DOCTYPE html><html><body style="color:black">
      <div style="padding:20px; margin:auto;" align="center">
        <p>Your OTP for Nexus Options:</p>
        <h2>{otp}</h2>
        <a href="{link+"restore"}"
           style="background-color:#454645; color:white; padding:15px 32px; text-decoration:none;">
          Reset Password
        </a>
      </div></body></html>
      """ # This is the HTML of the email
      msg.attach(MIMEText(html, "html")) # This attaches the HTML to the email
      with smtplib.SMTP_SSL("smtp.elasticemail.com", 465) as smtp: # This is the SMTP server for Elastic Email
        try: # This is if the email could be sent
          smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD) # This logs into the email account
          smtp.send_message(msg) # This sends the email
          db.session.commit() # This commits the changes to the database
          return jsonify({"exists":"y"}) # This is if the user exists and if the user is verified
        except Exception as e: # This is if the email could not be sent
          flash("An error occured, please try again",category="error") # This flashes an error message
          return jsonify({"exists":"n"}) # This is if the user does not exist or if the user is not verified
    else: # This is if the user does not exist or if the user is not verified
      return jsonify({"exists":"n"}) # This is if the user does not exist or if the user is not verified
  else: # This is if the request method is not POST or if the request does not have data
    return redirect(url_for("views.nopage")) # This is the route for the verify forgot page
@auth.route("/restore",methods=["GET","POST"]) # This is the route for the restore page
def restore(): # This is the function that will be called when the user tries to restore their password
  if request.method == "POST": # This checks if the request method is POST
    otp = request.form.get("otp") # This gets the OTP from the form in sign_up.html
    user = User.query.filter_by(otp=otp).first() # This gets the user from the database
    if user and user.verified: # This checks if the user exists and if the user is verified
      password1 = request.form.get("password1") # This gets the password from the form in sign_up.html
      password2 = request.form.get("password2") # This gets the password from the form in sign_up.html
      if len(password1)<8: # This checks if the password is at least 8 characters
        flash("Passwords have to be at least 8 characters",category="error") # This flashes an error message
      elif password1!=password2: # This checks if the passwords match
        flash("Passwords do not match",category = "error") # This checks if the passwords match
      else: # This is if the user exists and the passwords match and the password is at least 8 characters
        user.otp = "" # This sets the user's OTP to empty
        flash("Changed password successfully!",category="success") # This flashes a success message
        login_user(user=user) # This logs the user in
        user.password = generate_password_hash(password1,method='sha256') # This hashes the password
        db.session.commit() # This commits the changes to the database
        return redirect(url_for("views.home")) # This redirects the user to the home page
    else: # This is if the user does not exist
      flash("Invalid OTP",category="error") # This flashes an error message
  return render_template("restore.html",user=current_user) # This renders the restore page
@auth.route("/resend",methods=["GET","POST"])
def resend(): # This is the function that will be called when the user tries to resend their OTP
   if current_user.is_authenticated: # This checks if the user is logged in
     return redirect(url_for("views.home")) # This is if the user is logged in
   if request.method == "POST": # This checks if the request method is POST
     email = request.form.get("email") # This gets the email from the form in resend.html
     user = User.query.filter_by(email=email).first() # Gets the user from the database
     if user and not user.verified: # This checks if the user exists and if the user is not verified
        otp = (''.join(random.choices(string.digits, k=6))) # This generates a random 6 digit OTP
        while User.query.filter_by(otp=otp).first(): # This checks if the OTP already exists
          otp = (''.join(random.choices(string.digits, k=6))) # This generates a new OTP
        user.otp = otp # This sets the user's OTP to the new OTP
        msg = MIMEMultipart("alternative") # This allows us to send HTML emails
        msg["Subject"] = "OTP for Nexus Options" # This is the subject of the email
        msg["From"] = EMAIL_ADDRESS # This is the email address that the email will be sent from
        msg["To"] = email # This is the email that the user entered in the form
        html = f"""
        <!DOCTYPE html><html><body style="color:black">
        <div style="padding:20px; margin:auto;" align="center">
          <p>Your OTP for Nexus Options:</p>
          <h2>{otp}</h2>
          <a href="{link+"confirm"}"
             style="background-color:#454645; color:white; padding:15px 32px; text-decoration:none;">
            Verify Account
          </a>
        </div></body></html>
        """ # This is the HTML of the email
        msg.attach(MIMEText(html, "html")) # This attaches the HTML to the email
        with smtplib.SMTP_SSL("smtp.elasticemail.com", 465) as smtp: # This is the SMTP server for Elastic Email
           try: # This is if the email could be sent    
              smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD) # This logs into the email account
              smtp.send_message(msg) # This sends the email
              db.session.commit() # This commits the changes to the database
              flash("An OTP has been sent to your email",category="success")
              return redirect(url_for("auth.confirm")) # This is if the user exists and if the user is verified
           except Exception as e: # This is if the email could not be sent
              flash("An error occured, please try again later.",category="error") # This is if the user does not exist or if the user is not verified  
     else: # This is if the user does not exist or if the user is not verified
       if user and user.verified: # This checks if the user exists and if the user is verified
         flash("Account already verified, if this is your account log in <a href = '/login'>here</a>",category="warning") # This is if the user is verified
       elif not user: # This is if the user does not exist
         flash("Account does not exist, if you wish to sign up <a href = '/sign-up'>click here</a>",category="warning") # This is if the user does not exist   
   return render_template("resend.html",user=current_user) # This renders the resend page