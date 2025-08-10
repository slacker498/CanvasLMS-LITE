'''
This python file concerns all things in relation to the user objects/ class
'''

import re, bcrypt, json # bcrypt will be used to secure user passwords by hashing them in the database
from utils.validator import validate_id, validate_password # Ensure id and passwords for both roles are in the right formats
from utils.file_handler import load_json, save_json # To work with json files (not sure)

# User class to handle identity validation and password hashing
class User:
    # Initializing the important attributes of the user object
    def __init__(self, user_id, name, email, password, role, theme='dark'):
        self.user_id = user_id
        self.name = name
        self.email = email
        self.password = password  # hashed
        self.role = role
        self.theme = theme

    # Method to save the data of a user instance to the user.json file
    def to_dict(self):
        return {
            "user_id": self.user_id,
            "name": self.name,
            "email": self.email,
            "password": self.password,
            "role": self.role,
            "theme": self.theme
        }

    # method to handle registering or signup of new users
    @staticmethod # static method is used here to create a user object from the class not from another existing instance
    def register(user_id, name, email, password, role, theme):
        # Ensure id and password all conform to the patterns valid of any of the roles
        if not validate_id(user_id):
            raise ValueError("Invalid ID format.")
        if not validate_password(password):
            raise ValueError("Password does not meet complexity requirements.")

        # Load all users in the json file and check for duplicates to ensure no user registers more than once
        users = load_json('data/users.json')
        if user_id in users:
            raise ValueError("User already exists.")

        # To be corrected
        # # Determine the role of the new user based on the suffix (ie. faculty must end with xxxx0000)
        # role = 'faculty' if user_id.endswith("0000") else 'student'
        
        # Hash the password with bcrypt and store it as a varable
        hashed_pw = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

        # Finally, create new user object and store the his/her data in the json file
        user = User(user_id, name, email, hashed_pw, role.lower(), theme)
        users[user_id] = user.to_dict()
        save_json('data/users.json', users)
        return user # return the user object for use (ie. to start a session in the dashboard)

    # method to handle sign-in of user existing already in database
    @staticmethod # (Similar reason for register method)
    def login(user_id, password):
        users = load_json('data/users.json') # Load user database
        user_data = users.get(user_id)
        # Check if the user is registered
        if not user_data:
            raise ValueError("User not found.")
        
        user_data.pop('enrolled_courses', None)

        # Check if the user's given password is the same as the stored hashed passowrd
        if not bcrypt.checkpw(password.encode(), user_data['password'].encode()):
            raise ValueError("Incorrect password.")

        return User(**user_data)  # return the user object for use (ie. to start a session in the dashboard)
