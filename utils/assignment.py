'''
    This file allows faculty to create assignments using 
    an Assignemnt class
'''
from flask import request, flash, redirect, url_for, session, render_template
import json, datetime
from utils.file_handler import *
'''
# code for flask, not sure
from assignment_logic import create_assignment_route  # Assuming you move the logic to assignment_logic.py

@app.route('/faculty/create-assignment', methods=['GET', 'POST'])
def create_assignment():
    return create_assignment_route()'''

# Refer to submissions.py on how this class works for initializing and saving
class Assignment:
    # Not only for this class but try implementing a class method that clears the all or selective data stored
    STORE = 'data/assignments.json'

    @classmethod
    def _load_all(cls):
        """Return dict of all assignments keyed by assignment_id."""
        return load_json(cls.STORE) or {}

    @classmethod
    def get_all(cls):
        """Return a list of all assignment dicts."""
        return list(cls._load_all().values())

    @classmethod
    def get_by_course(cls, course_id):
        """Return list of assignment dicts for this course."""
        return [a for a in cls.get_all() if a.get('course_id') == course_id]

    @classmethod
    def clear_all(cls):
        """Wipe the assignments store (useful for tests)."""
        save_json(cls.STORE, {})

    @classmethod
    def delete(cls, assignment_id):
        """Remove one assignment by ID."""
        data = cls._load_all()
        if assignment_id in data:
            data.pop(assignment_id)
            save_json(cls.STORE, data)

    @classmethod
    def next_id(cls, course_id, title):
        """Auto‐incremental ID: courseID_title_N."""
        data = cls._load_all()
        N = len(data) + 1
        safe = title.replace(' ', '_')
        return f'{course_id}_{safe}_{N}'

    # Method to automatically generate an assignment id
    @classmethod
    def generate_assignmentID(cls, course_id, title, num):
        num = len(load_json('data/assignments.json')) #Allow for real time assignment id numbering
        return f'{course_id}_{title}_{num}'
    
    def __init__(self, title, description, due_date, course_id, file_attachment_path = None):
        self.assignment_id = self.generate_assignmentID(course_id, title)
        self.title = title
        self.description = description
        self.due_date = due_date
        self.course_id = course_id
        self.file_path = file_attachment_path # This is an optional feature in the case faculty wants to attach a file to the assignment

    def save(self):
        with open("data/assignments.json", "r+") as file:
            # Load data from assignments.json or return an empty dict if the file is empty
            try:
                assignments = load_json("data/assignments.json")
            except:
                assignments = {}
            # Prevent overwriting an existing assignment
            if self.assignment_id in assignments:
                raise ValueError("Assignment already exists.")

            assignments[self.assignment_id] = self.__dict__
            save_json("data/assignments.json", assignments)
            
