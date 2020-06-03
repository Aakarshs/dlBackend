var teacher_id = '5ebc8992a3f643f9ea3a68f2'
var student_ids = []
var student_data = []

$(document).ready(function () {
    var post;

    // Call the API
    fetch("http://127.0.0.1:5000/get_student_from_teacher/" + teacher_id)
        .then(function (response) {
            if (response.ok) { return response.json(); }
            else { return Promise.reject(response); }
        })
        .then(function (data) {
            for (id of data) {
                fetch("http://127.0.0.1:5000/get_student_fullname/" + id)
                    .then(function (response) {
                        if (response.ok) { return response.json(); }
                        else { return Promise.reject(response); }
                    })
                    .then(function (data) {
                        student_data = data
                    })
            }
            console.log(student_data)
            student_data.map(item => { return ($('#output').append(`<div id="title_name">${item}</div>`)) });

        })


    //state =======
    //functions =======

    /*
        $.get("http://127.0.0.1:5000/get_student_from_teacher/" + teacher_id, function (data, status) {
            student_ids = JSON.parse(data)

            for (id of student_ids) {
                $.get("http://127.0.0.1:5000/get_student_fullname/" + id, function (data, status) {
                    student_data.push(JSON.parse(data))
                })
            }
            console.log(student_data)

    });
    */
}

);

//render =======
function log_len(l) {
    console.log(l.length)
}

//get_student_data();
console.log(student_data)
log_len(student_data);
    //console.log(x.map(function(item){return (item)}))
    //console.log("=========")




    //get teachers students in a certain course.
    //takes in teacher_id and course_enrolled_in

    //get course name
    //get prep from course (Later)
    //go through student ids 
    //get lessons through lesson_id
    //get exercise

