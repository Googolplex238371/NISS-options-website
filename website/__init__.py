from flask import Flask, redirect, url_for
from flask_sqlalchemy import SQLAlchemy,inspect
from os import path
from flask_login import LOGIN_MESSAGE, LoginManager
from werkzeug.security import generate_password_hash
import string
import random
import dotenv
import os
from datetime import datetime
def dict_object(obj): # This function converts an object to a dictionary
    return {c.key: getattr(obj, c.key) for c in inspect(obj).mapper.column_attrs} # This converts the object to a dictionary
dotenv.load_dotenv() # This loads the environment variables from the .env file
db = SQLAlchemy() # Initializes the database object
DB_NAME = "database.db" # Databse filename
def create_app(): # This function creates the app
    app = Flask(__name__) # Initializes the app
    app.config['SECRET_KEY'] = os.getenv("SECRET_KEY") #Secret key to encode data
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}' # Database URI
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True # This is to track modifications
    db.init_app(app) # Initializes the database
    create_database(app) # Creates the database
    @app.errorhandler(404) # This is the error handler for 404 errors
    def page_not_found(error): # This is the function that will be called when a 404 error occurs
        return redirect(url_for("views.nopage")) # This redirects the user to the 404 page

    from .views import views # This imports the views from the views.py file
    from .auth import auth # This imports the auth from the auth.py file
    from .models import User # This imports the User from the models.py file
    app.register_blueprint(views, url_prefix='/') # This registers the views blueprint
    app.register_blueprint(auth, url_prefix='/') # This registers the auth blueprint
    login_manager = LoginManager() #This helps users login and logout
    login_manager.login_view = 'auth.login' #Gives the location of the function for the login page
    login_manager.init_app(app) # Initializes the login manager
    @login_manager.user_loader #This will load users to log them in
    def load_user(id): # This is the function that will be called when a user is loaded
        return User.query.get(int(id)) # This returns the user with the given id
    return app # This returns the app


def create_database(app): # This function creates the database
    with app.app_context(): # This is to create the database in the app context
        from .models import User,Subjects,Block # This imports the User,Subjects and Block from the models.py file
        import json # This imports the json module
        if not path.exists('website/' + DB_NAME): #Checks if a database exists yet
            print("Creating database") # If not, it will create one
            db.drop_all() # Drops the database if it exists
            db.session.commit()
            db.create_all(app=app) # Creates the database
            with open("backup.json") as f: # This opens the backup.json file 
                data = json.load(f) # This loads the data from the backup.json file
                for s in data: # This iterates through the data
                    db.session.add(User(**s)) # This adds the data to the database
            with open("subjects.json") as f: # This opens the subjects.json file
                data = json.load(f) # This loads the data from the subjects.json file
                for s in data: # This iterates through the data
                    db.session.add(Subjects(**s)) # This adds the data to the database
            with open("blocks.json") as f: # This opens the blocks.json file
                data = json.load(f) # This loads the data from the blocks.json file
                for s in data: # This iterates through the data
                    db.session.add(Block(**s)) # This adds the data to the database
            db.session.commit() # This commits the changes to the database
        else: # If a database exists, it will load the data from the backup.json file
            print("Database already exists")
            '''db.drop_all()
            db.session.commit()
            db.create_all(app=app)
            with open("backup.json") as f:
                data = json.load(f)
                for s in data:
                  db.session.add(User(**s))
            with open("subjects.json") as f:
                data = json.load(f)
                for s in data:
                    db.session.add(Subjects(**s))
            with open("blocks.json") as f:
                data = json.load(f)
                for s in data:
                    db.session.add(Block(**s))
            db.session.commit()'''
            students = [dict_object(student) for student in User.query.all()] # This converts the students to a dictionary
            with open("backup.json", "w") as f: # This opens the backup.json file
                json.dump(students, f) # This dumps the data to the backup.json file
            subjects = [dict_object(subject) for subject in Subjects.query.all()] # This converts the subjects to a dictionary
            with open("subjects.json", "w") as f: # This opens the subjects.json file
                json.dump(subjects, f) # This dumps the data to the subjects.json file
            blocks = [dict_object(block) for block in Block.query.all()] # This converts the blocks to a dictionary
            with open("blocks.json", "w") as f: # This opens the blocks.json file
                json.dump(blocks, f) #  This dumps the data to the blocks.json file