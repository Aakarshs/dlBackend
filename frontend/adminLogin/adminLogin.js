$(document).ready(function(){

    var admin = {
        "courses": [{
            "course_title": "Artificial Intelligence",
            "course": { "access_rights": ["asinha16@earlham.edu", "topalovic15@earlham.edu"] },
            "exercises": []
        },
        {
            "course_title": "Machine Learning",
            "course": { "access_rights": ["asinha16@earlham.edu", "topalovic15@earlham.edu"] },
            "exercises": []
        }
        ]
    }

    //State values =====
    var token = "";
    var password = "";
    //====================


    admin.courses.map(item => {return ($('#output').append(`<div id="title_name">${item.course_title}</div>`)) });
    
    $( "#token" ).change(function() { token = this.value});
    $( "#password" ).change(function() { password = this.value});


    $("#login-button").click(function(){
        console.log(password)
        window.location.href = "./teacherDash.html"; 
    });




});