var questions_from_json;
questions_from_json = questions_json;
var quizName = document.getElementById('name_of_test').value = questions_from_json.data[0].name;
var q1 = document.getElementById('q1').value = questions_from_json.data[0].question;
var q1a1 = document.getElementById('q1a1').value = questions_from_json.data[0].answers[0].answer;
var q1a2 = document.getElementById('q1a2').value = questions_from_json.data[0].answers[1].answer;
var q1a3 = document.getElementById('q1a3').value = questions_from_json.data[0].answers[2].answer;
var q1a4 = document.getElementById('q1a4').value = questions_from_json.data[0].answers[3].answer;

var q1c1 = document.getElementById('q1c1').checked  = questions_from_json.data[0].answers[0].is_correct;
var q1c2 = document.getElementById('q1c2').checked  = questions_from_json.data[0].answers[1].is_correct;
var q1c3 = document.getElementById('q1c3').checked  = questions_from_json.data[0].answers[2].is_correct;
var q1c4 = document.getElementById('q1c4').checked  = questions_from_json.data[0].answers[3].is_correct;


// 2 вопрос
var q2 = document.getElementById('q2').value = questions_from_json.data[1].question;
var q2a1 = document.getElementById('q2a1').value = questions_from_json.data[1].answers[0].answer;
var q2a2 = document.getElementById('q2a2').value = questions_from_json.data[1].answers[1].answer;
var q2a3 = document.getElementById('q2a3').value = questions_from_json.data[1].answers[2].answer;
var q2a4 = document.getElementById('q2a4').value = questions_from_json.data[1].answers[3].answer;

var q2c1 = document.getElementById('q2c1').checked  = questions_from_json.data[1].answers[0].is_correct;
var q2c2 = document.getElementById('q2c2').checked  = questions_from_json.data[1].answers[1].is_correct;
var q2c3 = document.getElementById('q2c3').checked  = questions_from_json.data[1].answers[2].is_correct;
var q2c4 = document.getElementById('q2c4').checked  = questions_from_json.data[1].answers[3].is_correct;


//3 вопрос
var q3 = document.getElementById('q3').value = questions_from_json.data[2].question;
var q3a1 = document.getElementById('q3a1').value = questions_from_json.data[2].answers[0].answer;
var q3a2 = document.getElementById('q3a2').value = questions_from_json.data[2].answers[1].answer;
var q3a3 = document.getElementById('q3a3').value = questions_from_json.data[2].answers[2].answer;
var q3a4 = document.getElementById('q3a4').value = questions_from_json.data[2].answers[3].answer;

var q3c1 = document.getElementById('q3c1').checked  = questions_from_json.data[2].answers[0].is_correct;
var q3c2 = document.getElementById('q3c2').checked  = questions_from_json.data[2].answers[1].is_correct;
var q3c3 = document.getElementById('q3c3').checked  = questions_from_json.data[2].answers[2].is_correct;
var q3c4 = document.getElementById('q3c4').checked  = questions_from_json.data[2].answers[3].is_correct;


//4 вопрос
var q4 = document.getElementById('q4').value = questions_from_json.data[3].question;
var q4a1 = document.getElementById('q4a1').value = questions_from_json.data[3].answers[0].answer;
var q4a2 = document.getElementById('q4a2').value = questions_from_json.data[3].answers[1].answer;
var q4a3 = document.getElementById('q4a3').value = questions_from_json.data[3].answers[2].answer;
var q4a4 = document.getElementById('q4a4').value = questions_from_json.data[3].answers[3].answer;

var q4c1 = document.getElementById('q4c1').checked  = questions_from_json.data[3].answers[0].is_correct;
var q4c2 = document.getElementById('q4c2').checked  = questions_from_json.data[3].answers[1].is_correct;
var q4c3 = document.getElementById('q4c3').checked  = questions_from_json.data[3].answers[2].is_correct;
var q4c4 = document.getElementById('q4c4').checked  = questions_from_json.data[3].answers[3].is_correct;

//5 вопрос
var q5 = document.getElementById('q5').value = questions_from_json.data[4].question;
var q5a1 = document.getElementById('q5a1').value = questions_from_json.data[4].answers[0].answer;
var q5a2 = document.getElementById('q5a2').value = questions_from_json.data[4].answers[1].answer;
var q5a3 = document.getElementById('q5a3').value = questions_from_json.data[4].answers[2].answer;
var q5a4 = document.getElementById('q5a4').value = questions_from_json.data[4].answers[3].answer;

var q5c1 = document.getElementById('q5c1').checked  = questions_from_json.data[4].answers[0].is_correct;
var q5c2 = document.getElementById('q5c2').checked  = questions_from_json.data[4].answers[1].is_correct;
var q5c3 = document.getElementById('q5c3').checked  = questions_from_json.data[4].answers[2].is_correct;
var q5c4 = document.getElementById('q5c4').checked  = questions_from_json.data[4].answers[3].is_correct;

