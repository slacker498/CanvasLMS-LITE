from flask import request, flash, redirect, url_for, session, render_template
import json, datetime
from utils.file_handler import *

class Course:
    def __init__(self, course_id, course_name, description):
        self.crse_id = course_id
        self.crse_name = course_name
        self.description = description

    def save(self):
        with open("data/courses.json", "r+") as file:
            # Load data and also handle exception if file is empty
            try:
                courses = load_json("data/courses.json")
            except:
                courses = {}
                
            # Prevent overwriting an existing course
            if self.crse_id in courses:
                raise ValueError("Course already exists.")
            
            courses[self.course_id] = self.__dict__
            save_json("data/courses.json", courses)
            
    def get_enrolled_courses(user_id):
        try:
            with open("data/enrollments.json", "r") as file:
                enrollments = json.load(file)
            user_courses = enrollments.get(user_id, [])
            return user_courses
        except (FileNotFoundError, json.JSONDecodeError):
            return []