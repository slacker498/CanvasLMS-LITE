CanvasLMS-Lite is a lightweight, scalable Learning Management System (LMS) built using Python. It is designed to replicate core features of Canvas, supporting role-based access for faculty and students. Key functionalities include assignment creation, submission, grading, simulated notifications, and messaging. This project emphasizes usability, security, and extensibility while leveraging standard Python libraries and simple file-based (JSON and text) data management. The system may also incorporate innovative features to enhance the learning experience, such as gamification and analytics dashboards.

Key Features:
Our LMS consists of fourteen pages with specific features aligned to both student and faculty users. These pages include the register page, login page for both faculty and students, student's course enrollment, students single course page, student dashboard, student assignments submission page, student inbox page, faculty modules page, faculty inbox page, faculty grades, faculty courses, faculty dashboard, and the forgot password page.

To facilitate creation of our canvas we incorporated html, python, CSS and JavaScript. The HTML and CSS (Cascading style sheets) was used for frontend that is making the static webpages and styling them. We used JavaScript to make the pages dynamic especially with regard to the students section, for example, changing color theme. We used python for our backend to create classes, and also to use Flask, the web framework linking the frontend and backend together.

Faculty Section:
Our faculty page utilizes a dark theme which we implemented for consistency and to reduce eye strain.
The faculty navigation bar has Dashboard, Account and Sign Out. 
The Account Tab displays the account information of the user. 
The Dashboard has a manage courses section. This allows the faculty to add a course, a description and edit course details. 
Clicking a courses allows the faculty to access the course details, enrolled students, modules and grading. 

The Course section also allows the faculty to post announcements.
The Assignment Tab, allows the faculty to upload a file as an assignment, create and upload a new assignment and add a due date for the assignment. 
The faculty can access the assignments submitted by the students. Once accessed, they can grade and add feedback. 
The Modules tab allows the faculty to upload files(.doc, .pdf, .txt or even videos) or delete existing modules.
The grading tab allows the faculty to access the students grade, edit the grad as well as perform grad analysis. 

Student Section:
The student section consists of an inbox where students can view assignment notifications and grading feedback.
We allowed a section where students can choose between light or dark theme from their profile settings.
There is a submission section for submitting assignments in the form of .txt files or .py files.
Both sections have an inbox section for messaging between students and faculty
The Student Navigation Bar consists of Dashboard, Enrollment, inbox, Account and Sign Out Tabs. 

Student Dashboard shows the courses the student is enrolled in. 
The Enrollment Tab displays the courses the student is currently enrolled in. 
The inbox is the portion of the student section where they can interact with their faculty through messaging. The students have options to interact with specific faculty. 
Enrolling into a course sends you into the course dashboard where the student can access the modules, assignments, grades and announcements for the course.
Login and Registration Section:

Our login page consists of a section where the user enters their unique 8-digit ID that ends in 0000 for faculty and a year between 2022 and 2028 for students.
We made sure for password, there were certain requirements for a valid password. The password must have one uppercase letter, one lowercase letter, one digit and on especial character.
The password was encrypted and encoded for security and privacy reasons.
During the first login or registration, users enter their ID, full name, email address, password and role (i.e Student or faculty).

GUI Features:
We created our Graphical User Interface and Dashboards with the assistance of Flask.
There is a faculty dashboard displaying assignment creation forms, lists of students who have submitted, and grading interfaces.
Student Dashboard shows the courses the student is enrolled in 
Flask aided in creation of the dashboard. It also aided in input validation.
We also had to route each of the pages to unique URLs.
Our GUI allows Students to enable Theme Customization. Users can toggle between Light and Dark themes.
JSON files allow us to store information such as course data, student data etc.
