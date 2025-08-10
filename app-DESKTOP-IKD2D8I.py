# Main app that brings all the pieces together in perfect harmony
from flask import Flask, render_template, request, redirect, url_for, session, flash, Blueprint, send_from_directory, jsonify, current_app
from utils.user import User
import os
from datetime import datetime
from utils.message import Message
from utils.file_handler import *
from werkzeug.utils import secure_filename
from utils.validator import validate_id, validate_password, is_valid_file

def get_assignment(course_id, assignment_id):
    assignments = load_json(os.path.join('data', 'assignments.json')) or []
    # assignments may be a list or dict, handle both
    if isinstance(assignments, dict):
        assignments = list(assignments.values())
    for a in assignments:
        if a.get('course_id') == course_id and a.get('id') == assignment_id:
            return a
    return None

app = Flask(__name__) # Create Flask app instance
app.secret_key = 'dignifiedloverboy123!' # Initialize secret key (better to randomize)

@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST']) # Map URL path to python functions
def register():
    if request.method == 'POST':
        user_id = request.form['user_id'] # Retrieve form data
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        role = request.form['role']
        # Validate ID
        valid_id = validate_id(user_id)
        if valid_id is not True:
            flash(str(valid_id), 'error')
            return redirect(url_for('register'))

        # Enforce role-based ID rules
        if role == 'faculty' and not (user_id.isdigit() and len(user_id) == 8 and user_id.endswith('0000')):
            flash('Faculty ID must be 8 digits and end with 0000.', 'error')
            return redirect(url_for('register'))
        if role == 'student':
            try:
                year = int(user_id[-4:])
                if not (user_id.isdigit() and len(user_id) == 8 and 2022 <= year <= 2028):
                    flash('Student ID must be 8 digits and end with a valid year (2022-2028).', 'error')
                    return redirect(url_for('register'))
            except ValueError:
                flash('Invalid student ID format.', 'error')
                return redirect(url_for('register'))

        # Validate Password
        if not validate_password(password):
            flash('Password must include upper, lower, digit, special char, and be at least 8 characters.', 'error')
            return redirect(url_for('register'))

        try:
            theme = request.form.get('theme', 'dark')
            user = user = User.register(user_id, name, email, password, role, theme) # Create a user object from form data
            flash('Registration successful. Please log in.', 'success')
            return redirect(url_for('login'))
        except ValueError as e:
            flash(str(e) + '; Invalid credentials', 'error')
            return redirect(url_for('register'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user_id = request.form['user_id']
        email = request.form['email']
        password = request.form['password']
        role = request.form['role']
        valid_id = validate_id(user_id)
        if valid_id is not True:
            flash(str(valid_id), 'error')
            return redirect(url_for('login'))

        try:
            user = User.login(user_id, password)
            session['user_id'] = user.user_id
            session['role'] = user.role
            session['theme'] = user.theme
            flash(f'Welcome, {user.name}!', 'success') # Send feedback message to user in a given category
            return redirect(url_for(f'{user.role}_dashboard'))
        except ValueError as e:
            flash(f'Error: {str(e)}', 'error')
            return redirect(url_for('login'))
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

@app.route('/student')
def student_dashboard():
    if 'user_id' not in session or session.get('role') != 'student':
        return redirect(url_for('login'))
    
    user_id = session.get('user_id')
    users   = load_json(os.path.join('data', 'users.json')) or {}
    user    = users.get(user_id, {})
    enrolled_codes = user.get('enrolled_courses', [])
    raw_courses = load_json(os.path.join('data', 'courses.json')) or {}
    enrolled_courses = [
        { **info, 'code': course_id }       
        for course_id, info in raw_courses.items()
        if course_id in enrolled_codes
    ]
    return render_template('std_dashboard.html', courses=enrolled_courses, user=user)


@app.route('/student/enrollment', methods=['GET', 'POST'])
def student_enrollment():
    user_id = session.get('user_id')
    users = load_json(os.path.join('data', 'users.json')) or {}
    user = users.get(user_id, {})

    raw_courses = load_json(os.path.join('data', 'courses.json')) or {}

    course_list = [
        { **info, 'code': info['id'] }
        for info in raw_courses.values()
    ]

    current_codes = user.get('enrolled_courses', [])

    if request.method == 'POST':
        course_code = request.form.get('course_code')
        if course_code and course_code not in current_codes:
            current_codes.append(course_code)
            user['enrolled_courses'] = current_codes
            users[user_id] = user
            save_json(os.path.join('data', 'users.json'), users)
            flash('Enrolled successfully!', 'success')
        else:
            flash('Already enrolled or invalid course.', 'error')
        return redirect(url_for('student_enrollment'))

    return render_template(
        'std_crse_enrll.html',
        courses=course_list,
        current_codes=current_codes,
        user=user
    )

@app.route('/student/course/<course_id>')
def student_course(course_id):
    user_id = session.get('user_id')
    users   = load_json(os.path.join('data', 'users.json')) or {}
    user    = users.get(user_id, {})

    raw_courses = load_json(os.path.join('data', 'courses.json')) or {}
    course = raw_courses.get(course_id)
    if not course:
        flash("Course not found.", "error")
        return redirect(url_for('student_dashboard'))
    course['code'] = course_id
    modules = course.get('modules', [])
    all_assignments = load_json(os.path.join('data', 'assignments.json')) or {}
    assignments = [
        a for a in all_assignments
        if a.get('course_id') == course_id
    ]
    all_submissions = load_json(os.path.join('data', 'submissions.json')) or {}
    grades = []
    for sub in all_submissions.values():
        if sub.get('student_id') == user_id and sub.get('course_id') == course_id:
            grades.append({
                "assignment_id": sub['assignment_id'],
                "assignment_title": all_assignments[sub['assignment_id']]['title'],
                "score": sub.get('score')
            })
    announcements = []
    anns = load_json(os.path.join('data', 'announcements.json')) or {}
    if course_id in anns:
        announcements = anns[course_id]
    return render_template(
        'std_crse.html',
        course=course,
        modules=modules,
        assignments=assignments,
        grades=grades,
        announcements = announcements, 
        user=user
    )

@app.route('/student/inbox', methods=['GET', 'POST'])
def student_inbox():
    user_id = session.get('user_id')
    users   = load_json(os.path.join('data', 'users.json')) or {}
    user    = users.get(user_id, {})
    messages = load_json('data/messages.json')
    inbox = [msg for msg in messages if msg['recipient_id'] == user_id or msg['sender_id'] == user_id]
    
    if not user_id:
        return redirect(url_for('login'))

    if request.method == 'POST':
        recipient_id = request.form['lecturer_id']
        text         = request.form['message_text'].strip()
        if not recipient_id or not text:
            flash('Please choose a lecturer and type a message.', 'error')
        else:
            msg = Message(
                sender_id    = user_id,
                recipient_id = recipient_id,
                content      = text,
                sender_role  = user.get("role"),
                recipient_role = next((u.get("role") for u in users.values() if u.get("user_id") == recipient_id), None)
            )
            msg.send()
            flash('Message sent to faculty!', 'success')
        return redirect(url_for('student_inbox'))

    replies = Message.for_recipient(user_id)
    users = load_json("data/users.json") or {}
    faculty_list = [u for u in users.values() if u.get("role") == "faculty"]

    return render_template(
        'inbox_stud.html',
        replies = replies,
        faculty_list = faculty_list, 
        user=user
    )


@app.route('/faculty')
def faculty_dashboard():
    if session.get('role') != 'faculty':
        return redirect(url_for('login'))
    user_id = session.get('user_id')
    users = load_json(os.path.join('data', 'users.json')) or {}
    user = users.get(user_id, {})
    file_path = os.path.join('data', 'courses.json')
    courses = load_json(file_path) if os.path.exists(file_path) else {}
    return render_template('faculty_dashboard.html', user=user, courses=courses)

@app.route('/faculty/add-course', methods=['POST'])
def add_course():
    if session.get('role') != 'faculty':
        return redirect(url_for('login'))

    name = request.form.get('courseName')
    description = request.form.get('courseDescription')
    if not name:
        flash('Course name is required.', 'error')
        return redirect(url_for('faculty_dashboard'))

    new_course = {
        'id': str(int(datetime.datetime.now().timestamp())),  # unique ID
        'name': name,
        'description': description
    }
    
    file_path = os.path.join('data', 'courses.json')
    courses = load_json(file_path) if os.path.exists(file_path) else {}
    for course in courses.values():
        if course['name'].lower() == name.lower():
            flash('Course name already exists.', 'error')
            return redirect(url_for('faculty_dashboard'))
    courses[new_course['id']] = new_course
    save_json(file_path, courses)

    flash('Course created successfully!', 'success')
    return redirect(url_for('faculty_dashboard'))

@app.route('/faculty/edit-course/<course_id>', methods=['GET', 'POST'])
def edit_course(course_id):
    if session.get('role') != 'faculty':
        return redirect(url_for('login'))

    file_path = os.path.join('data', 'courses.json')
    courses = load_json(file_path)
    course = courses.get(course_id)

    if not course:
        flash('Course not found.', 'error')
        return redirect(url_for('faculty_dashboard'))

    if request.method == 'POST':
        course['name'] = request.form.get('courseName')
        course['description'] = request.form.get('courseDescription')
        save_json(file_path, courses)
        flash('Course updated successfully!', 'success')
        return redirect(url_for('faculty_dashboard'))
    users = load_json('data/users.json') or {}
    enrolled_students = []
    for uid, u in users.items():
        if 'enrolled_courses' in u and course_id in u['enrolled_courses']:
            enrolled_students.append({
                'id':   uid,
                'name': u.get('name')
            })

    return render_template('faculty_crse.html', course=course, course_id=course_id, students=enrolled_students)

@app.route('/faculty/course/<course_id>', methods=['GET', 'POST'], endpoint='course_page')
def course_page(course_id):
    if session.get('role') != 'faculty':
        return redirect(url_for('login'))

    file_path = os.path.join('data', 'courses.json')
    courses = load_json(file_path)
    course = courses.get(course_id)

    if not course:
        flash('Course not found.', 'error')
        return redirect(url_for('faculty_dashboard'))

    if request.method == 'POST':
        course['name'] = request.form.get('courseName')
        course['description'] = request.form.get('courseDescription')
        save_json(file_path, courses)
        flash('Course updated successfully!', 'success')
        return redirect(url_for('course_page', course_id=course_id))
    
    users = load_json('data/users.json') or {}
    enrolled_students = []
    for uid, u in users.items():
        if 'enrolled_courses' in u and course_id in u['enrolled_courses']:
            enrolled_students.append({
                'id':   uid,
                'name': u.get('name')
            })


    return render_template('faculty_crse.html', course=course, course_id=course_id, students=enrolled_students)

@app.route('/faculty/delete-course/<course_id>', methods=['POST'])
def delete_course(course_id):
    if session.get('role') != 'faculty':
        return redirect(url_for('login'))

    file_path = os.path.join('data', 'courses.json')
    courses = load_json(file_path)

    if course_id in courses:
        del courses[course_id]
        save_json(file_path, courses)
        flash('Course deleted successfully.', 'success')
    else:
        flash('Course not found.', 'error')

    return redirect(url_for('faculty_dashboard'))

modules_bp = Blueprint('modules', __name__, url_prefix='/faculty')
@modules_bp.route('/course/<course_id>/modules', methods=['GET', 'POST'])
def modules_page(course_id):
    if session.get('role') != 'faculty':
        return redirect(url_for('login'))

    file_path = os.path.join('data', 'courses.json')
    courses = load_json(file_path) or {}
    course = courses.get(course_id)

    if not course:
        flash("Course not found.", "error")
        return redirect(url_for("faculty_dashboard"))
    if request.method == 'POST':
        title = request.form['moduleTitle']
        desc  = request.form['moduleDesc']
        files = request.files.getlist('moduleFiles')
        
        if files and not all(is_valid_file(f.filename) for f in files):
            flash("Only .txt and .py files are accepted.", "error")
            return redirect(request.url)

        # Prepare module entry
        module = {'title': title, 'description': desc, 'files': []}
        module_folder = f'static/files/modules/{course_id}'
        os.makedirs(module_folder, exist_ok=True)

        for f in files:
            if not is_valid_file(f.filename):
                flash("Only .txt and .py files are accepted.", "error")
                return redirect(request.url)
            ext = f.filename.rsplit('.', 1)[1].lower()
            safe_name = secure_filename(f.filename)
            unique_name = f"{course_id}_{int(datetime.datetime.now().timestamp())}_{safe_name}"
            f.save(os.path.join(module_folder, unique_name))
            module['files'].append(f'{course_id}/{unique_name}')

        course.setdefault('modules', []).append(module)
        save_json(f'data/courses.json', courses)
        flash("Module added!", "success")
        return redirect(request.url)


    modules = course.get('modules', [])
    return render_template(
        'faculty_modules.html',
        course_id=course_id,
        modules=modules,
    )

@modules_bp.route('/course/<course_id>/modules/<int:idx>/delete', methods=['POST'])
def delete_module(course_id, idx):
    if session.get('role') != 'faculty':
        return redirect(url_for('login'))

    courses  = load_json(f'data/courses.json') or {}
    modules  = courses.get(course_id, {}).get('modules', [])
    if 0 <= idx < len(modules):
        modules.pop(idx)
        save_json(f'data/courses.json', courses)
        flash("Module deleted.", "info")
    return redirect(url_for('modules.course_modules_page', course_id=course_id))


@app.route('/faculty-inbox')
def faculty_inbox():
    user_id = session.get('user_id')
    messages = load_json(os.path.join('data', 'messages.json'))
    inbox = [msg for msg in messages if msg['recipient_id'] == user_id]
    return render_template('faculty_inbox.html', inbox=inbox)

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory('data/uploads', filename)

@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form['email']
        new_password = request.form['new_password']
        users = load_json(os.path.join('data', 'users.json')) or {}
        for uid, user in users.items():
            if user['email'] == email:
                if not validate_password(new_password):
                    flash('Password must include upper, lower, digit, special char, and be at least 8 characters.', 'error')
                    return redirect(url_for('forgot_password'))
                user['password'] = User.hash_password(new_password)
                users[uid] = user
                save_json(os.path.join('data', 'users.json'), users)
                flash('Password reset successful. Please log in.', 'success')
                return redirect(url_for('login'))
        flash('Email not found.', 'error')
        return redirect(url_for('forgot_password'))
    return render_template('forgot_password.html')

@app.route('/faculty/course/<course_id>/assignments', methods=['GET', 'POST'])
def manage_assignments(course_id):
    if session.get('role') != 'faculty':
        return redirect(url_for('login'))

    store_path = os.path.join('data', 'assignments.json')
    uploads_dir = os.path.join('data', 'uploads')
    os.makedirs(uploads_dir, exist_ok=True)

    assignments = load_json(store_path) or []
    submissions = load_json('data/submissions.json') or {}
    grades = load_json('data/grades.json') or {}

    if request.method == 'POST':
        title       = request.form['title']
        description = request.form.get('description', '')
        due_date    = request.form['due_date']
        file        = request.files.get('attachment')
        
        if file and not is_valid_file(file.filename):
            flash("Only .txt and .py files are accepted.", "error")
            return redirect(request.url)

        new_asg = {
            'id':        str(len(assignments) + 1),
            'course_id': course_id,
            'title':     title,
            'description': description,
            'due_date':  due_date,
            'filename':  None
        }

        if file and file.filename:
            ext = file.filename.rsplit('.', 1)[1].lower()
            fn = f"{course_id}_asg{len(assignments)+1}.{ext}"
            file.save(os.path.join(uploads_dir, fn))
            new_asg['filename'] = fn

        assignments.append(new_asg)
        save_json(store_path, assignments)
        flash('Assignment created successfully!', 'success')
        return redirect(url_for('manage_assignments', course_id=course_id))

    # filter for this course only
    course_asgs = [a for a in assignments if a['course_id'] == course_id]
    return render_template(
        'faculty_assignments.html',
        course_id=course_id,
        assignments=course_asgs
    )

@app.route('/faculty/course/<course_id>/grading', methods=['GET', 'POST'])
def faculty_grading(course_id):
    if session.get('role') != 'faculty':
        return redirect(url_for('login'))

    users      = load_json('data/users.json') or {}
    all_asgs   = load_json('data/assignments.json') or []
    all_grades = load_json('data/grades.json') or {}
    
    if isinstance(all_asgs, list):
        assignments = [a for a in all_asgs if a.get('course_id') == course_id]
    else:
        assignments = [a for a in all_asgs.values() if a.get('course_id') == course_id]

    seen = set()
    students = []
    for uid, u in users.items():
        if course_id in u.get('enrolled_courses', []):
            if uid not in seen:
                students.append({'id': uid, 'name': u.get('name')})
                seen.add(uid)
    
    if request.method == 'POST':
        try:
            payload = request.get_json() 
            all_grades[course_id] = {  
                    entry['id']: entry['grades']
                    for entry in payload
                }
            save_json('data/grades.json', all_grades)
            return jsonify({'success': True}), 200
        except Exception as e:
            app.logger.error(f"Grading error: {e}")
            return jsonify(success=False, error=str(e)), 500

    existing = all_grades.get(course_id, {})
    return render_template(
        'faculty_grades.html',
        course_id=course_id,
        students=students,
        assignments = assignments,
        existing    = existing

    )
    
@app.route('/student/course/<course_id>/assign/<assignment_id>', methods=['GET','POST'])
def submit_assignment(course_id, assignment_id):
    if session.get('role') != 'student':
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    if request.method == 'POST':
        file = request.files.get('submission')
        if not file or not is_valid_file(file.filename):
            flash("Submit a .txt or .py file only.", "error")
            return redirect(request.url)

        ext        = file.filename.rsplit('.',1)[1].lower()
        timestamp  = datetime.utcnow().strftime('%Y%m%d%H%M%S')
        filename   = f"{user_id}_{assignment_id}_{timestamp}.{ext}"
        sub_folder = f'static/files/submissions/{course_id}/{user_id}'
        os.makedirs(sub_folder, exist_ok=True)
        file.save(os.path.join(sub_folder, filename))

        # record in submissions.json
        subs = load_json('data/submissions.json') or {}
        subs.setdefault(course_id, {})\
            .setdefault(assignment_id, {})\
            [user_id] = {
                'filename': filename,
                'timestamp': timestamp
            }
        save_json('data/submissions.json', subs)
        notif_dir = os.path.join('notifications', user_id)
        os.makedirs(notif_dir, exist_ok=True)
        with open(os.path.join(notif_dir, f'{assignment_id}_submitted.txt'), 'w') as f:
            f.write(f'Submission received for assignment {assignment_id} at {timestamp}')

        flash("Submitted successfully!", "success")
        # return redirect(url_for('student_dashboard'))

    users = load_json(os.path.join('data', 'users.json')) or {}
    user = users.get(user_id, {})
    subs = load_json('data/submissions.json') or {}
    return render_template(
      'std_submit_assignment.html',
      course_id=course_id,
      assignment=get_assignment(course_id, assignment_id),
      existing=subs.get(course_id, {}).get(assignment_id, {}).get(user_id),
      user=user
    )
    
@app.route('/faculty/course/<course_id>/submissions')
def view_submissions(course_id):
    if session.get('role') != 'faculty':
        return redirect(url_for('login'))

    assigns   = load_json('data/assignments.json') or []
    subs_all  = load_json('data/submissions.json') or {}
    grades    = load_json('data/grades.json') or {}

    course_asgs = [a for a in assigns if a['course_id']==course_id]
    course_subs = subs_all.get(course_id, {})
    course_grd  = grades.get(course_id, {})

    return render_template(
      'faculty_submissions.html',
      course_id=course_id,
      assignments=course_asgs,
      submissions=course_subs,    
      grades=course_grd            
    )

@app.route('/faculty/course/<course_id>/submissions/grade/<student_id>', methods=['POST'])
def grade_and_email(course_id, student_id):
    data_dir = current_app.root_path+'/data'
    grades   = load_json(f'{data_dir}/grades.json') or {}
    body     = request.get_json() or {}

    # Save grades + feedback per-student
    grades.setdefault(course_id, {}).setdefault(student_id, {}).update(body)
    save_json(f'{data_dir}/grades.json', grades)
    
    notif_dir = os.path.join('notifications', student_id)
    os.makedirs(notif_dir, exist_ok=True)
    with open(os.path.join(notif_dir, f'{course_id}_grades.txt'), 'w') as f:
        f.write(content)

    # Simulate email by logging (or use Flask-Mail)
    subject = f"Grades for Course {course_id}"
    content = "\n".join([f"{aid}: {body[aid]['score']} — {body[aid]['feedback']}" for aid in body])
    current_app.logger.info(f"Email to {student_id}: {subject}\n{content}")

    return jsonify(success=True)

@app.route('/faculty/course/<course_id>/grades-data')
def grades_data(course_id):
    grades = load_json('data/grades.json') or {}
    assignments = load_json('data/assignments.json') or []
    course_grades = grades.get(course_id, {})
    assignment_titles = {a['id']: a['title'] for a in assignments if a['course_id'] == course_id}
    avg_grades = {}
    for aid in assignment_titles:
        scores = [
            v for student_grades in course_grades.values()
            if isinstance(student_grades, dict)
            for k, v in student_grades.items()
            if k == aid and isinstance(v, (int, float))
        ]
        if scores:
            avg_grades[assignment_titles[aid]] = sum(scores) / len(scores)
    return jsonify(avg_grades)

@app.route('/faculty/course/<course_id>/announcement', methods=['POST'])
def post_announcement(course_id):
    if session.get('role') != 'faculty':
        return redirect(url_for('login'))
    text = request.form['announcement']
    ann_path = os.path.join('data', 'announcements.json')
    anns = load_json(ann_path) or {}
    anns.setdefault(course_id, []).append({
        'text': text,
        'timestamp': datetime.datetime.now().isoformat()
    })
    save_json(ann_path, anns)
    flash('Announcement posted!', 'success')
    return redirect(url_for('course_page', course_id=course_id))

app.register_blueprint(modules_bp)
if __name__ == '__main__':
    app.run(debug=True)
