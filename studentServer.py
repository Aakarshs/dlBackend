from flask import Flask
from flask import jsonify
from flask import request
from flask_pymongo import PyMongo
from pymongo import MongoClient
from bson.objectid import ObjectId
import datetime
import json
from flask_cors import CORS

from mongoengine_jsonencoder import JSONEncoder
app = Flask(__name__)
CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'
app.config["MONGO_URI"] = 'mongodb+srv://aakarshs:Back2thefuture%21@cluster0-mvg6j.mongodb.net/dlDatabase?retryWrites=true&w=majority'
app.config['MONGO_DBNAME'] = 'dlDatabase'
#app.config['SECRET_KEY'] = 'ad208930-cdb6-444a-a846-89834f2ef3ac'

# Connect to MongoDB using Flask's PyMongo wrapper
mongo = PyMongo(app)
db = mongo.db
col = mongo.db["admin"]

#===========Student APIs===============#

@app.route('/submitForGrading/<course_id>/<student_id>/<original_lesson_reference>/<student_exercises_reference>', methods=['POST'])
def submitForGrading(course_id,student_id,original_lesson_reference,student_exercises_reference):
    student = db.student.find_one({'_id': ObjectId(str(student_id))})
    teacher_id = student['teachers_id']
    teacher = db.teacher.find_one({'_id': ObjectId(str(teacher_id))})
    lesson_reference = student['course_details'][0]['lesson_reference']
    recent_submissions = teacher['recent_submissions']
    recent_submissions.append({'course_id':course_id, 'student_id':student_id, 'original_lesson_reference':original_lesson_reference, 
    'student_exercises_reference':student_exercises_reference})

    db.teacher.update_one({'_id': ObjectId(str(teacher_id))}, {'$set': {'recent_submissions': recent_submissions}})
    lessons = db.studentLessons.find_one({'_id': ObjectId(str(lesson_reference))})

    if lessons == "undefined":
        print("0-0-0--0")
        print("lesson not found")
        print("0-0-0--0")

    
    lesson_details = lessons['lesson_details']
    for i in lessons['lesson_details']:
        if str(i['original_lesson_reference']) == str(original_lesson_reference):
            i['status'] = 'submitted'
            db.studentLessons.update_one({'_id': ObjectId(str(lesson_reference))}, {'$set': {'lesson_details':lesson_details }})
            return "1"
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
            data_to_send.append({"course_id": str(i),"teacher_id":ObjectId(str(student['teachers_id'])), "lesson_data": lesson_data})
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


@app.route('/get_student_answers/<student_exercise_id>/<question_id>/<student_id>', methods=['GET'])
def save_answer(exercise_id,question_id,data):
    return "0"


@app.route('/get_student_answers/<student_exercise_id>/<question_id>/<student_id>', methods=['GET'])
def get_student_answer_details(student_exercise_id, question_id, student_id):
    return "0"


@app.route('/update_lesson_visibility/<course_id>/<lesson_id>', methods=['POST'])
def update_lesson_visibility(course_id, lesson_id):
    x = db.admin.find_one({'_id': ObjectId(str(course_id))})
    for i in x['lessons']:
        if str(i['lesson_id']) == str(lesson_id):
            i['access_rights'] = ["resrse", "rewrw"]
            db.admin.update_one({'_id': ObjectId(str(course_id))}, {'$set': {'lessons': x['lessons']}})
            return "success"
    return "0"


@app.route('/authenticate_teacher/', methods=['GET', 'POST'])
def authenticate_teacher():
    email = request.json['Email']
    password = request.json['Password']
    x = db.teacher.find_one({'email': email})
    if x != None:
        if x['password'] == password:
            return "1"
    return "0"


@app.route('/authenticate_student/', methods=['GET', 'POST'])
def authenticate_student():
    email = request.json['Email']
    password = request.json['Password']
    x = db.student.find_one({'email': email})
    if x != None:
        if x['password'] == password:
            return "1"
    return "0"


@app.route('/post_answer/<exercise_id>/<question_id>', methods=['GET', 'POST'])
def post_answer(exercise_id,question_id):
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
        new_obj["option_selected"] = ['c']
        new_obj["notes"] = "notes will be shown here."
        new_obj["submit_time"] = "time will be shown here."
        details.append(new_obj)
        
    db.studentExercises.update_one({'_id': ObjectId(str(exercise_id))}, {'$set': {'details': details}})
    return "1"


if __name__ == '__main__':
    app.run(debug=True)
