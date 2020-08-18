from flask import Flask
from flask import jsonify
from flask import request
from flask_pymongo import PyMongo
from pymongo import MongoClient
from bson.objectid import ObjectId
import datetime
import json
from flask_cors import CORS
import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
import random
import string

#from sendgrid.helpers.mail import *
#from sendgrid.helpers.mail import Mail

#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

from mongoengine_jsonencoder import JSONEncoder
app = Flask(__name__)
CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'
app.config["MONGO_URI"] = 'mongodb+srv://aakarshs:Back2thefuture%21@cluster0-mvg6j.mongodb.net/dlDatabase?retryWrites=true&w=majority'
app.config['MONGO_DBNAME'] = 'dlDatabase'
#app.config['SECRET_KEY'] = 'ad208930-cdb6-444a-a846-89834f2ef3ac'

# Connect to MongoDB using Flask's PyMongo wrapper

'''
471529468558-dknd1m2819atvrn7h5lojpu3kai3aqrl.apps.googleusercontent.com
'''

mongo = PyMongo(app)
db = mongo.db
col = mongo.db["admin"]

@app.route('/')
def index():
  return "<h1>Welcome to CodingX</h1>"

def get_random_alphanumeric_password(letters_count, digits_count):
    sample_str = ''.join((random.choice(string.ascii_letters) for i in range(letters_count)))
    sample_str += ''.join((random.choice(string.digits) for i in range(digits_count)))

    # Convert string to list and shuffle it to mix letters and digits
    sample_list = list(sample_str)
    random.shuffle(sample_list)
    final_string = ''.join(sample_list)
    return final_string


def calculate_grade_from_exercise(exercise_id):
    studentExercises = db.studentExercises.find_one({'_id': exercise_id}) 
    total_grade = 0
    number_of_exercises = 0
    for i in studentExercises['details']:
        total_grade = total_grade + int(i['grade'])
        number_of_exercises += 1
    return str(total_grade/number_of_exercises)

@app.route('/get_total_grade_from_lesson_id/<student_id>/<lesson_id>', methods=['GET'])
def get_total_grade_from_lesson_id(student_id,lesson_id):
    student = db.student.find_one({'_id': ObjectId(str(student_id))}) 
    student_lesson_id = student['course_details'][0]['lesson_reference']
    
    studentLessons = db.studentLessons.find_one({'_id': student_lesson_id}) 
    for i in studentLessons['lesson_details']:
        print(str(i['original_lesson_reference']) == str(lesson_id))
        if str(i['original_lesson_reference']) == str(lesson_id):
            return calculate_grade_from_exercise(i['student_exercises_reference'])
    return "0"

@app.route('/create_student_profile/', methods=['POST'])
def create_student_profile():

    try:
        newObjectId = ObjectId()
        new_student_object = {}
        new_student_object['teachers_id'] = request.json['teachers_id']
        new_student_object['is_loggedin'] = False
        new_student_object['fullname'] = request.json['fullname']
        new_student_object['email'] = request.json['email']
        new_student_object['username'] = request.json['fullname'][0] #can be removed in the future, I don't think it is being used anywhere.
        new_student_object['password'] = get_random_alphanumeric_password(5,5)
        new_student_object['course_details'] = [{'course_id':'none',"lesson_reference":newObjectId}]

        db.studentLessons.insert_one({"_id":newObjectId,"lesson_details":[]})
        db.student.insert_one(new_student_object)
        
        teacher = db.teacher.find_one({'_id': ObjectId(str(new_student_object['teachers_id']))}) 
        teachers_students = teacher['students']
        teachers_students.append(newObjectId)
        db.teacher.update_one({'_id': ObjectId(str(new_student_object['teachers_id']))}, {'$set': {'students': teachers_students}}) #Updating teacher's student list.
        
        message = Mail(
        from_email = 'aakarsh@example.com',
        to_emails = new_student_object['email'],
        subject = 'Your Digital Leaders login and password.',
        html_content = ''' <div> Your login credentials are: </div>
                        <div> Email - <strong>  ''' + new_student_object['email'] + ''' </strong> </div>
                        <div> Password - <strong>  ''' + new_student_object['password'] + ''' </strong> </div>
        ''')

        sg = SendGridAPIClient('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')
        response = sg.send(message)
        return "1"

    except Exception as e:
        print(e)
        return "0"

"""
def send_email():
    message = Mail(
    from_email='aakarshs@outlook.com',
    to_emails='asinha16@earlham.edu',
    subject='Sending with Twilio SendGrid is Fun',
    html_content='<strong>and easy to do anywhere, even with Python</strong>')
    try:
        sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
        response = sg.send(message)
        print(response.status_code)
        print(response.body)
        print(response.headers)
    except Exception as e:
        print(e.message)
"""

@app.route('/get_course_title/<course_id>', methods=['GET'])
def get_course_title(course_id):
    x = db.admin.find_one({'_id': ObjectId(str(course_id))})
    return JSONEncoder().encode(x["course_title"])


@app.route('/get_student_fullname/<student_id>', methods=['GET'])
def get_student_fullname(student_id):
    x = db.student.find_one({'_id': ObjectId(str(student_id))})
    return JSONEncoder().encode(x["fullname"])


def get_lesson_ids_by_course_id(course_id):
    x = db.admin.find_one({'_id': ObjectId(str(course_id))})
    lesson_ids = []
    for i in x['lessons']:
        lesson_ids.append(i['lesson_id'])
    return (lesson_ids)

@app.route('/get_student_lesson_details_by_course_id/<course_id>/<student_id>', methods=['GET'])
def get_student_lesson_details_if_complete(course_id,student_id):
    lessons_in_course = get_lesson_ids_by_course_id(course_id)
    print(lessons_in_course)
    lessons_in_course_array = []
    student = db.student.find_one({'_id': ObjectId(str(student_id))})
    lesson_reference = student['course_details'][0]['lesson_reference']
    lesson_details = db.studentLessons.find_one({'_id': ObjectId(str(lesson_reference))})
    lesson_details = lesson_details['lesson_details']
    for i in lesson_details:
        if str(i['original_lesson_reference']) in str(lessons_in_course):
            lessons_in_course_array.append(i)
    return JSONEncoder().encode(lessons_in_course_array)

def get_student_details_from_array(array):
    student_detail_array = []
    new_obj = {}
    for i in array:
        get_student_name = db.student.find_one({'_id': i})
        get_student_obj = db.student.find_one({'_id': i})
        print("00000000")
        print("00000000")
        print("00000000")
        print(i)
        print("00000000")
        print("00000000")
        print("00000000")
        new_obj["student_id"] = i
        new_obj["fullname"] = get_student_name["fullname"]
        
        new_obj["course_details"] = get_student_obj["course_details"]
        student_detail_array.append(new_obj)
        new_obj = {}
    
    print("==-=-===-=")
    print(student_detail_array)
    print("==-=-===-=")
    return JSONEncoder().encode(student_detail_array)


@app.route('/get_student_details_all/<student_id>', methods=['GET'])
def get_student_details(student_id):
    x = db.student.find_one({'_id': ObjectId(str(student_id))})
    return JSONEncoder().encode(x["course_details"])


@app.route('/get_student_from_teacher/<teacher_id>', methods=['GET'])
def get_student_from_teacher(teacher_id):
    x = db.teacher.find_one({'_id': ObjectId(str(teacher_id))})
    return get_student_details_from_array(x["students"])


@app.route('/get_teacher_courses/<teacher_id>', methods=['GET'])
def get_teacher_courses(teacher_id):
    x = db.teacher.find_one({'_id': ObjectId(str(teacher_id))})

    array = []
    for i in x["courses_enrolled_in"]:
        newObj = {}
        newObj['course_id'] = i
        newObj['course_name'] = get_course_title(str(i))
        array.append(newObj)
   
    return JSONEncoder().encode(array)


@app.route('/get_students_by_course/<course_id>', methods=['GET'])
def get_students_by_course(course_id):
    cursor_array = []
    x = (db.student.find({'courses_enrolled_in': {
         '$all': [ObjectId(str(course_id))]}}))
    for i in x:
        cursor_array.append(i)
    return JSONEncoder().encode(cursor_array)


@app.route('/get_student_details_by_course/<student_id>/<course_id>', methods=['GET'])
def get_student_details_by_course(student_id, course_id):
    x = db.student.find_one({'$and': [{'_id': ObjectId(str(student_id))}, {
                            'course_details.course_id': ObjectId(str(course_id))}]})
    if (x):
        for i in x['course_details']:
            if (i['course_id'] == ObjectId(str(course_id))):
                return JSONEncoder().encode(get_lesson_detail_by_id(i['lesson_reference']))
    else:
        return "0"


def get_lesson_detail_by_id(lesson_id):
    x = db.studentLessons.find_one({'lesson_id': lesson_id})
    return x


@app.route('/get_student_exercises_by_exercise_reference/<exercise_reference>', methods=['GET'])
def get_student_exercises_by_lesson_id(exercise_reference):
    x = db.studentExercises.find_one(
        {'_id': ObjectId(str(exercise_reference))})
    return (JSONEncoder().encode(x))


#if it cannot find one it creates one.
@app.route('/get_student_lesson_by_reference/<student_id>/<original_lesson_reference>', methods=['GET'])
def get_student_lesson_by_reference(student_id, original_lesson_reference):
    x = db.student.find_one({'_id': ObjectId(str(student_id))})
    array_to_send = []
    lesson_reference = ""

    lesson_reference = (x['course_details'][0]['lesson_reference'])
    array_to_send.append(lesson_reference)
    lesson = db.studentLessons.find_one({'_id': ObjectId(str(lesson_reference))})
    
    new_obj = {}
    found = 0 
    lesson_details = lesson['lesson_details']
    for i in lesson_details:
        if str(i['original_lesson_reference']) == str(original_lesson_reference):
            array_to_send.append(i['student_exercises_reference'])
            found = 1
  
    if found == 0:
        new_exercise_id = ObjectId()
        new_question_id = ObjectId()
        new_obj['status'] = "in-progress"
        new_obj['original_lesson_reference'] = ObjectId(str(original_lesson_reference))
        new_obj['student_exercises_reference'] = ObjectId(str(new_exercise_id))
        lesson_details.append(new_obj)
        db.studentLessons.update_one({'_id': ObjectId(str(lesson_reference))}, {'$set': {'lesson_details': lesson_details}})
        db.studentExercises.insert_one({'_id':ObjectId(str(new_exercise_id)), 'details':[] })
        post_answer_template(new_exercise_id,new_question_id)
        return "0"

    
    if(len(array_to_send) != 0):
        return JSONEncoder().encode(array_to_send)
    else:
        return ("0")

def Merge(dict1, dict2): 
    res = {**dict1, **dict2} 
    return res 


def get_key(val,my_dict): 
    for key, value in my_dict.items(): 
         if val == value: 
             return key 
  
    return "key doesn't exist"


def checkIfGraded(lesson_id):
    l

@app.route('/show_dash_board/<teacher_id>', methods=['GET'])
def show_dash_board(teacher_id):
    teacher = db.teacher.find_one({'_id': ObjectId(str(teacher_id))})
    teacher_courses = teacher['courses_enrolled_in']    
    recent_submissions = teacher['recent_submissions']
    dash = {}
    for i in teacher_courses:
        dash[str(i)] = []

    array_to_send = []
    for i in recent_submissions:
        if i['course_id'] in dash.keys():
            dash[i['course_id']].append(i)
    
    new_dict = {}
    for i in dash.values():
        new_dict[get_course_title(get_key(i,dash))] = i
    
    return JSONEncoder().encode([new_dict])


@app.route('/get_student_answers_from_teacher/<student_exercise_id>/<question_id>/<index>', methods=['GET'])
def get_student_answers_from_teacher(student_exercise_id, question_id, index):
    answer_details = get_student_answers(student_exercise_id)
    if answer_details != "0" and len(answer_details)!=0 and answer_details!= None and len(answer_details)>int(index):
        return (JSONEncoder().encode(answer_details[int(index)]))
    else:
        new_question_id = ObjectId()
    return "0"

@app.route('/save_grade/<exercise_id>/<index>', methods=['GET', 'POST'])
def save_grade(exercise_id,index):
    try:
        x = db.studentExercises.find_one({'_id': ObjectId(str(exercise_id) )})
        details = x['details']
        grade = request.json['grade']
        new_obj = {}
        details[int(index)]["grade"] = grade
        db.studentExercises.update_one({'_id': ObjectId(str(exercise_id))}, {'$set': {'details': details}})
        return "1"
    except:
        return "0"

@app.route('/update_access_rights/<course_id>/<lesson_id>/<teacher_id>', methods=['POST'])
def update_access_rights(course_id,lesson_id,teacher_id):
    x = db.admin.find_one({'_id': ObjectId(str(course_id))})
    lessons = x['lessons']
    for i in lessons:
        if str(i['lesson_id']) == str(lesson_id):    
            if(teacher_id) not in i['access_rights']:
                i['access_rights'].append(teacher_id)
            else:
                i['access_rights'].remove(teacher_id)
            db.admin.update_one({'_id': ObjectId(str(course_id))}, {'$set': {'lessons': lessons}})
            return "1"
    return "0"

#===========Student APIs===============#

@app.route('/submitForGrading/<course_id>/<student_id>/<original_lesson_reference>/<student_exercises_reference>', methods=['POST'])
def submitForGrading(course_id,student_id,original_lesson_reference,student_exercises_reference):
    student = db.student.find_one({'_id': ObjectId(str(student_id))})
    teacher_id = student['teachers_id']
    teacher = db.teacher.find_one({'_id': ObjectId(str(teacher_id))})
    
    lesson_reference = student['course_details'][0]['lesson_reference']
    recent_submissions = teacher['recent_submissions']
    student_name = get_student_fullname(student_id)

    #where i left off - 
    #original_lesson_reference is not correct in everythign
    #resovled.... I think.

    #change student status to submitted.
    lessons = db.studentLessons.find_one({'_id': ObjectId(str(lesson_reference))})
    lesson_details = lessons['lesson_details']
    for i in lessons['lesson_details']:
        if str(i['original_lesson_reference']) == str(original_lesson_reference):
            i['status'] = 'submitted'
            #update student.
            db.studentLessons.update_one({'_id': ObjectId(str(lesson_reference))}, {'$set': {'lesson_details':lesson_details }})

    #This is to prevent duplicates.
    for i in recent_submissions:
        if i['student_id'] == student_id and i['original_lesson_reference'] == original_lesson_reference:
            return "2" #2 stands for action already done.
    
    #appending to existing list and update teacher.
    recent_submissions.append({'course_id':course_id, 'student_id':student_id, 'original_lesson_reference':original_lesson_reference, 
    'student_exercises_reference':student_exercises_reference, 'student_name':student_name,'status':'grade-pending'})
    db.teacher.update_one({'_id': ObjectId(str(teacher_id))}, {'$set': {'recent_submissions': recent_submissions}})
    
    return "0"

@app.route('/check_lesson_status/<student_id>/<original_lesson_id>/', methods=['GET'])
def check_lesson_status(student_id,original_lesson_id):
    x = db.student.find_one({'_id': ObjectId(str(student_id))})
    lesson_reference = x['course_details'][0]['lesson_reference']
    lessons = db.studentLessons.find_one({'_id': ObjectId(str(lesson_reference))})
    if lessons!= None:
        for i in lessons['lesson_details']:
            if str(i['original_lesson_reference'])==str(original_lesson_id):
                return i['status']
    return '0'

@app.route('/get_lesson_by_reference/<student_id>', methods=['GET'])
def get_lesson_by_reference(student_id):
    student = db.student.find_one({'_id': ObjectId(str(student_id))})
    teacher = db.teacher.find_one({'_id': ObjectId(str(student['teachers_id']))})
    data_to_send = []
    for i in teacher['courses_enrolled_in']:
        lesson_data = get_original_lesson_by_reference(ObjectId(str(i)))
        if lesson_data != None:
            for j in lesson_data:
                j['status'] = check_lesson_status(student_id,j['lesson_id'])
                j['grade'] = get_total_grade_from_lesson_id(student_id,j['lesson_id'])
            data_to_send.append({"course_id": i,"course_name": get_course_title(str(i)),"teacher_id":ObjectId(str(student['teachers_id'])), "lesson_data": lesson_data})
        else:
            data_to_send.append({"course_id": str(i),"teacher_id":ObjectId(str(student['teachers_id'])), "lesson_data": [""]})
    return (JSONEncoder().encode(data_to_send))


@app.route('/get_exercise_by_reference/<exercise_reference>', methods=['GET'])
def get_exercise_by_reference(exercise_reference):
    x = db.studentExercises.find_one(
        {'exercise_id': ObjectId(str(exercise_reference))})
    return (JSONEncoder().encode(x['exercise_details']))


def get_original_lesson_by_reference(course_id):
    x = db.admin.find_one({'_id': ObjectId(str(course_id))})
    return ((x['lessons']))


@app.route('/get_lesson_from_course_for_prepare/<course_id>', methods=['GET'])
def get_lesson_from_course_for_prepare(course_id):
    return JSONEncoder().encode(get_original_lesson_by_reference(course_id))


@app.route('/get_lesson_from_course/<course_id>/<lesson_id>', methods=['GET'])
def get_lesson_from_course(course_id, lesson_id):
    lessons = get_original_lesson_by_reference(course_id)
    for i in lessons:
        if str(i['lesson_id']) == str(lesson_id):
            return (JSONEncoder().encode(i['exercises']))
    return "0"


def get_student_answers(student_exercise_id):
    x = db.studentExercises.find_one(
        {'_id': ObjectId(str(student_exercise_id))})
    if x != None:
        return ((x['details']))
    return "0"

@app.route('/get_student_answers/<student_exercise_id>/<question_id>/<index>', methods=['GET'])
#add data from questions here.
# This gets called when the student first loads the exercise screen or when the student clicks on next question.
# need to create another one for the teacher.
def get_student_answer_details(student_exercise_id, question_id, index):
    answer_details = get_student_answers(student_exercise_id)

    if answer_details != "0" and len(answer_details)!=0 and answer_details!= None and len(answer_details)>int(index):
        return (JSONEncoder().encode(answer_details[int(index)]))
    else:
        new_question_id = ObjectId()
        post_answer_template(student_exercise_id,new_question_id) #This needs to be changed to post_template.
        return "1"
    return "0"

@app.route('/authenticate_teacher/', methods=['GET', 'POST'])
def authenticate_teacher():
    email = request.json['Email']
    password = request.json['Password']
    x = db.teacher.find_one({'email': email})
    if x != None:
        if x['password'] == password:
            return JSONEncoder().encode((x['_id']))
    return "0"

@app.route('/authenticate_student/', methods=['GET', 'POST'])
def authenticate_student():
    email = request.json['Email']
    password = request.json['Password']
    x = db.student.find_one({'email': email})
    if x != None:
        if x['password'] == password:
            return JSONEncoder().encode((x['_id']))
    return "0"


@app.route('/save_answer_upload/<exercise_id>/<index>', methods=['GET', 'POST'])
def save_answer_upload(exercise_id,index):

    x = db.studentExercises.find_one({'_id': ObjectId(str(exercise_id) )})
    details = x['details']
    notes = request.json['notes']
    filename = request.json['filename']
    
    details[int(index)]["filename"] = filename
    details[int(index)]["notes"] = notes
    db.studentExercises.update_one({'_id': ObjectId(str(exercise_id))}, {'$set': {'details': details}})
    return "1"


@app.route('/save_answer/<exercise_id>/<index>', methods=['GET', 'POST'])
def save_answer(exercise_id,index):
    try:
        x = db.studentExercises.find_one({'_id': ObjectId(str(exercise_id) )})
        details = x['details']
        notes = request.json['notes']
        option_selected = request.json['option_selected']
        details[int(index)]["option_selected"] = option_selected
        details[int(index)]["notes"] = notes
        db.studentExercises.update_one({'_id': ObjectId(str(exercise_id))}, {'$set': {'details': details}})
        return "1"
    except:
        return "0"

@app.route('/post_answer_template/<exercise_id>/<question_id>', methods=['GET', 'POST'])
def post_answer_template(exercise_id,question_id):
    print("=======================This ran==========================")
    x = db.studentExercises.find_one({'_id': ObjectId(str(exercise_id) )})
    details = x['details']
    new_obj = {}
    found = 0
    for i in details:
        if str(i["question_id"])==str(question_id):
            found = 1
            i["option_selected"] = ['a']
            break
    if found == 0:
        new_obj["question_id"] = ObjectId(str(question_id))
        new_obj["option_selected"] = []
        new_obj["notes"] = "notes will be shown here."
        new_obj["submit_time"] = "time will be shown here."
        new_obj["grade"] = "0" 
        new_obj["filename"] = ""
        details.append(new_obj)
        
    db.studentExercises.update_one({'_id': ObjectId(str(exercise_id))}, {'$set': {'details': details}})
    return "1"

@app.route('/submit_final_grades/<course_id>/<student_id>/<original_lesson_reference>/<student_exercises_reference>', methods=['POST'])
def submit_final_grades(course_id,student_id,original_lesson_reference,student_exercises_reference):
    student = db.student.find_one({'_id': ObjectId(str(student_id))})
    teacher_id = student['teachers_id']
    teacher = db.teacher.find_one({'_id': ObjectId(str(teacher_id))})
    
    lesson_reference = student['course_details'][0]['lesson_reference']
    recent_submissions = teacher['recent_submissions']
    student_name = get_student_fullname(student_id)

    #update teacher.
    for i in recent_submissions:
        if i['student_id'] == student_id and i['original_lesson_reference'] == original_lesson_reference:
            i['status'] = "graded"
    
    db.teacher.update_one({'_id': ObjectId(str(teacher_id))}, {'$set': {'recent_submissions': recent_submissions}})
    lessons = db.studentLessons.find_one({'_id': ObjectId(str(lesson_reference))})

    lesson_details = lessons['lesson_details']
    for i in lessons['lesson_details']:
        if str(i['original_lesson_reference']) == str(original_lesson_reference):
            i['status'] = 'graded'
            #update student.
            db.studentLessons.update_one({'_id': ObjectId(str(lesson_reference))}, {'$set': {'lesson_details':lesson_details }})
            return "1"
    return "0"

@app.route('/upload_file/', methods=['POST'])
def upload_file():
    file = request.files['file']
    mongo.save_file(file.filename,file)
    db.files.insert({'_id': ObjectId(),'file_name':file.filename})
    return "1"

@app.route('/retrieve_file/<filename>', methods=['GET','POST'])
def retrieve_file(filename):
    print("=======")
    print(filename)
    print("=======")
    return mongo.send_file(filename)

if __name__ == '__main__':
    app.run(debug=True)
