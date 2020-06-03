
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
print("MongoDB Database:", mongo.db)

# {"username":{"_id":ObjectId(str(datetime.datetime.now()))}}


@app.route('/insert_course', methods=['POST'])
def insert_course():
    mongo.db.admin.insert_one(
        {
            "course_title": "Artificial Intelligence",
            "course": {"access_rights": ["asinha16@earlham.edu", "topalovic15@earlham.edu"]},
            "lessons": [
                {
                    "lesson_id": ObjectId(),
                    "lesson_title": "Intro to AI",
                    "exercises": [
                        {"exercise_id": ObjectId(), "type": "video",
                         "video_url": "youtbe.com", },
                        {"exercise_id": ObjectId(), "type": "mutliple_choice", "question_text": "This is the question",
                         "optional_image": "", "options": ["a", "b", "c", "d"], "correct_answers": ["b", "c"]},
                        {"exercise_id": ObjectId(), "type": "mutliple_choice", "question_text": "This is the question",
                         "optional_image": "", "options": ["a", "b", "c", "d"], "correct_answers": ["b", "c"]},
                        {"exercise_id": ObjectId(), "type": "upload_answer", "question_text": "This is the question",
                         "optional_image": "", "answer_uploaded_link": "www.somewehere.com/fawefwef"}
                    ]
                },
                {
                    "lesson_id": ObjectId(),
                    "lesson_title": "AI Part 2",
                    "exercises": [
                        {"exercise_id": ObjectId(), "type": "video",
                         "video_url": "youtbe.com", },
                        {"exercise_id": ObjectId(),  "type": "mutliple_choice", "question_text": "This is the question",
                         "optional_image": "", "options": ["a", "b", "c", "d"], "correct_answers": ["b", "c"]},
                        {"exercise_id": ObjectId(),  "type": "mutliple_choice", "question_text": "This is the question",
                         "optional_image": "", "options": ["a", "b", "c", "d"], "correct_answers": ["b", "c"]},
                        {"exercise_id": ObjectId(),  "type": "upload_answer", "question_text": "This is the question",
                         "optional_image": "", "answer_uploaded_link": "www.somewehere.com/fawefwef"}
                    ]
                }
            ]
        }

    )
    return "success"


@app.route('/insert_teacher/', methods=['POST'])
def insert_teacher():
    mongo.db.teacher.insert_one(
        {
            "teacher_id": ObjectId(),
            "is_loggedin": True,
            "username": "",
            "password": "",
            "students": [],

        })
    return "success"


@app.route('/insert_student/', methods=['POST'])
def insert_student():
    mongo.db.student.insert_one(
        {
            "student_id": ObjectId(),
            "is_loggedin": True,
            "courses_enrolled_in": [ObjectId("5ebc8152c3f42f33a3d98bea"),ObjectId("5ebde36fc5ee4dd1b8d3aaec")],
            "fullname" : "Ronnie Radke",
            "username": "student",
            "password": "password",
            "course_details": [{
                "course_id": ObjectId("5ebc8152c3f42f33a3d98bea"),
                "lesson_details": [{
                    "lesson_id": ObjectId(),
                    "lesson_name": "Intro to AI",
                    "on_exercise": ObjectId(),
                    "exercise_details": [{
                        "excercise_id": ObjectId(),
                        "type": "mutliple_choice",
                        "option_selected": ["a", "c"],
                        "grade": 0,
                        "submit_time":"19:00",
                        "notes": "These are the notes for the first exercise."
                    },
                        {
                        "excercise_id": ObjectId(),
                        "type": "mutliple_choice",
                        "option_selected": ["b", "a"],
                        "grade": 0,
                        "submit_time":"19:00",
                        "notes": "These are the notes for the second exercise."
                    }]
                }]
            },
            {
              "course_id": ObjectId("5ebde36fc5ee4dd1b8d3aaec"),
                "lesson_details": [{
                    "lesson_id": ObjectId(),
                    "lesson_name": "Intro to AI",
                    "on_exercise": ObjectId(), 
                    "exercise_details": [{
                        "excercise_id": ObjectId(),
                        "type": "mutliple_choice",
                        "option_selected": ["a", "c"],
                        "grade": 0,
                        "submit_time":"19:00",
                        "notes": "These are the notes for the first exercise."
                    },
                        {
                        "excercise_id": ObjectId(),
                        "type": "mutliple_choice",
                        "option_selected": ["b", "a"],
                        "grade": 0,
                        "submit_time":"19:00",
                        "notes": "These are the notes for the second exercise."
                    }]
                }]
            }
    
            ]
        })
    return "success"

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
        get_student_name =  db.student.find_one({'_id': i})
        get_student_obj = db.student.find_one({'_id': i})
        new_obj["student_id"]=i
        new_obj["fullname"]=get_student_name["fullname"]
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
    x = (db.student.find( { 'courses_enrolled_in': { '$all': [ObjectId(str(course_id))] }}))
    for i in x:
        cursor_array.append(i)
    return JSONEncoder().encode(cursor_array)

@app.route('/get_student_details_by_course/<student_id>/<course_id>', methods=['GET'])
def get_student_details_by_course(student_id,course_id):
    x = db.student.find_one( { '$and': [ { '_id': ObjectId(str(student_id)) }, { 'course_details.course_id':ObjectId(str(course_id)) } ] } )
    if (x):
        for i in x['course_details']:
            if (i['course_id'] == ObjectId(str(course_id))):
                return JSONEncoder().encode(get_lesson_detail_by_id(i['lesson_reference'])) 
    else:
         return "0"

def get_lesson_detail_by_id(lesson_id):
    x = db.studentLessons.find_one( { 'lesson_id':lesson_id } )  
    return x 
 

#get_lesson_detail_by_id

@app.route('/get_student_exercises_by_exercise_reference/<exercise_reference>', methods=['GET'])
def get_student_exercises_by_lesson_id(exercise_reference):
    cursor_array = []
    x = db.studentExercises.find_one({'exercise_id':ObjectId(str(exercise_reference))})
    return (JSONEncoder().encode(x)) 



#===========Student APIs===============#

def get_student_lesson_by_student_id(student_id):
    x = db.student.find_one({'_id':ObjectId(str(student_id))})
    return (x['course_details']) 

@app.route('/get_lesson_by_reference/<student_id>', methods=['GET'])
def get_lesson_by_reference(student_id):
    student_courses = get_student_lesson_by_student_id(student_id)
    print("=====")
    print(student_courses)
    print("=====")
    temp_array = []
    for i in student_courses:
        temp_array.append(db.studentLessons.find_one({'lesson_id':ObjectId(str(i['lesson_reference']))}))
    return (JSONEncoder().encode(temp_array)) 



#=======
@app.route('/get_exercise_by_reference/<exercise_reference>', methods=['GET'])
def get_exercise_by_reference(exercise_reference):
    x = db.studentExercises.find_one({'exercise_id':ObjectId(str(exercise_reference))})
    return (JSONEncoder().encode(x['exercise_details'])) 

if __name__ == '__main__':
    app.run(debug=True)
