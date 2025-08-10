'''
    This file defines the Submission class is the blueprint for the instance
    of any user submitting an assignment. It takes into account the student id, 
    assignment id, the file path of the submitted file, a timestamp on the submission,
    as well as placeholders for grade and feedback (to be replaced later by faculty). 
'''
import json, datetime

class Submission:
    def __init__(self, student_id, assignment_id, file_path):
        self.student_id = student_id
        self.assignment_id = assignment_id
        self.file_path = file_path
        self.timestamp = datetime.datetime.now().isoformat()
        self.grade = None
        self.feedback = None

    # Function to save submission info to submission.json
    def save(self):
        # Open the submissions.json file to read and/or write and close it after
        with open("data/submissions.json", "r+") as file:
            submissions = json.load(file) #Load submissions.json file's contents as a py dictionary
            key = f"{self.student_id}_{self.assignment_id}"
            submissions[key] = self.__dict__ # self.__dict__ converts an instance of the object into a dictionary (simplifies manual assignemnt of each element of the dict)
            file.seek(0)
            json.dump(submissions, file, indent=4) # Overwrite the json file with the updated dictionary
            
            
'''
    The timestamp variable in the __int__ first gets the exact current date and time down to microsecs
    using (datetime.datetime.now()) in the form, for example; 2025-07-19 13:42:58.123456
    .isoformat() converts this time to a standardized string (eg. 2025-07-19T13:42:58.123456). This standard form
    allows for easy reading across multiple systems, sorting submissions by time or even to track submissions.
    
    Also, similarly to __init__() and __str__(), which are built-in methods of classes or objects, class instances 
    also have special built-in attributes and these include the __dict__ attribute. It is basically a dictioanry of the 
    objects internal attributes, just as they have entered in the __int__() method and stored in memory.
    It can even be accesed outside the class definition, eg.
    >>> s = Submission("12342024", "hw1", "file.py")
    >>> print(s.__dict__)

'''