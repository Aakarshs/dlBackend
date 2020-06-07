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

@app.route('/get_course_title/<course_id>', methods=['GET'])
def get_course_title(course_id):
    x = db.admin.find_one({'_id': ObjectId(str(course_id))})
    return JSONEncoder().encode(x["course_title"])


@app.route('/get_student_fullname/<student_id>', methods=['GET'])
def get_student_fullname(student_id):
    x = db.student.find_one({'_id': ObjectId(str(student_id))})
    return JSONEncoder().encode(x["fullname"])


def get_student_details_from_array(array):
    student_detail_array = []
    new_obj = {}
    for i in array:
        get_student_name = db.student.find_one({'_id': i})
        get_student_obj = db.student.find_one({'_id': i})
        new_obj["student_id"] = i
        new_obj["fullname"] = get_student_name["fullname"]
        new_obj["course_details"] = get_student_obj["course_details"]
        student_detail_array.append(new_obj)
        new_obj = {}
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
    return JSONEncoder().encode(x["courses_enrolled_in"])


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


@app.route('/get_student_lesson_by_reference/<student_id>/<original_lesson_reference>', methods=['GET'])
def get_student_lesson_by_reference(student_id, original_lesson_reference):
    x = db.student.find_one({'_id': ObjectId(str(student_id))})
    array_to_send = []
    lesson_reference = ""
    
    for i in x['course_details']:
        if str(i['original_lesson_reference']) == str(original_lesson_reference):
            lesson_reference = i['lesson_reference']
            array_to_send.append(i['lesson_reference'])

    lesson = db.studentLessons.find_one({'_id': ObjectId(str(lesson_reference))})
    
    for i in lesson['lesson_details']:
        if str(i['original_lesson_reference']) == str(original_lesson_reference):
            array_to_send.append(i['student_exercises_reference'])
    print("=============")
    print(lesson['lesson_details'])
    print("=============")
    if(len(array_to_send) != 0):
        return JSONEncoder().encode(array_to_send)
    else:
        return ("0")

#===========Student APIs===============#

@app.route('/get_lesson_by_reference/<student_id>', methods=['GET'])
def get_lesson_by_reference(student_id):
    student = db.student.find_one({'_id': ObjectId(str(student_id))})
    teacher = db.teacher.find_one(
        {'_id': ObjectId(str(student['teachers_id']))})
    data_to_send = []
    for i in teacher['courses_enrolled_in']:
        data_to_send.append({"course_id": str(
            i), "lesson_data": get_original_lesson_by_reference(ObjectId(str(i)))})
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
        else:
            return "0"


def get_student_answers(student_exercise_id):
    x = db.studentExercises.find_one(
        {'_id': ObjectId(str(student_exercise_id))})
    if x != None:
        return ((x['details']))
    return "0"


@app.route('/get_student_answers/<student_exercise_id>/<question_id>', methods=['GET'])
def get_student_answer_details(student_exercise_id, question_id):
    answer_details = get_student_answers(student_exercise_id)
    if answer_details != "0":
        for i in answer_details:
            if str(i['question_id']) == str(question_id):
                return (JSONEncoder().encode(i))
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
