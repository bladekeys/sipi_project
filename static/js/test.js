const headElem = document.getElementById("head");
const buttonsElem = document.getElementById("buttons");
const pagesElem = document.getElementById("pages");
const quizName = document.getElementById("name");
//Класс, который представляет сам тест
class Quiz
{
	constructor(type, questions, results)
	{
		//Тип теста: 1 - классический тест с правильными ответами, 2 - тест без правильных ответов
		this.type = type;

		//Массив с вопросами
		this.questions = questions;

		//Массив с возможными результатами
		this.results = results;

		//Количество набранных очков
		this.score = 0;

		//Номер результата из массива
		this.result = 0;

		//Номер текущего вопроса
		this.current = 0;
	}

	Click(index)
	{
		//Добавляем очки
		var value = this.questions[this.current].Click(index);
		this.score += Number(value);

		var correct = -1;

		//Если было добавлено хотя одно очко, то считаем, что ответ верный
		if(value >= 1)
		{
			correct = index;
		}
		else
		{
			//Иначе ищем, какой ответ может быть правильным
			for(var i = 0; i < this.questions[this.current].answers.length; i++)
			{
				if(this.questions[this.current].answers[i].value >= 1)
				{
					correct = i;
					break;
				}
			}
		}

		this.Next();

		return correct;
	}

	//Переход к следующему вопросу
	Next()
	{
		this.current++;

		if(this.current >= this.questions.length)
		{
			this.End();
		}
	}

	//Если вопросы кончились, этот метод проверит, какой результат получил пользователь
	End()
	{
		for(var i = 0; i < this.results.length; i++)
		{
			if(this.results[i].Check(this.score))
			{
				this.result = i;
			}
		}
	}
}

//Класс, представляющий вопрос
class Question
{
	constructor(text, answers)
	{
		this.text = text;
		this.answers = answers;
	}

	Click(index)
	{
		return this.answers[index].value;
	}
}

//Класс, представляющий ответ
class Answer
{
	constructor(text, value)
	{
		this.text = text;
		this.value = value;
	}
}

//Класс, представляющий результат
class Result
{
	constructor(text, value)
	{
		this.text = text;
		this.value = value;
	}

	//Этот метод проверяет, достаточно ли очков набрал пользователь
	Check(value)
	{
		if(this.value <= value)
		{
			return true;
		}
		else
		{
			return false;
		}
	}
}

//Массив с результатами
const results =
[
	new Result("Вам многому нужно научиться", 0),
	new Result("Вы уже неплохо разбираетесь", 2),
	new Result("Ваш уровень средний", 3),
	new Result("Вы в совершенстве знаете тему", 5)
];


function to_js(vars) {
    var questions_json = vars;
    return questions_json
}

var questions_from_json;
questions_from_json = questions_json;

var questions =[];

quizName.innerHTML = questions_from_json.data[0].name

for(var question of questions_from_json.data) {
    questions.push(
    new Question(`${question.question}`,
    [new Answer(`${question.answers[0].answer}`, `${question.answers[0].is_correct}`),
	new Answer(`${question.answers[1].answer}`, `${question.answers[1].is_correct}`),
	new Answer(`${question.answers[2].answer}`, `${question.answers[2].is_correct}`),
	new Answer(`${question.answers[3].answer}`, `${question.answers[3].is_correct}`)]
		)
	)
}



//Массив с вопросами
//const questions =
//[
//
//
//	new Question("2 + 2 = ",
//	[
//		new Answer("2", 0),
//		new Answer("3", 0),
//		new Answer("4", 1),
//		new Answer("0", 0)
//	]),
//
//	new Question("2 * 2 = ",
//	[
//		new Answer("2", 0),
//		new Answer("3", 0),
//		new Answer("4", 1),
//		new Answer("0", 0)
//	]),
//
//	new Question("2 / 2 = ",
//	[
//		new Answer("0", 0),
//		new Answer("1", 1),
//		new Answer("2", 0),
//		new Answer("3", 0)
//	]),
//
//	new Question("2 - 2 = ",
//	[
//		new Answer("0", 1),
//		new Answer("1", 0),
//		new Answer("2", 0),
//		new Answer("3", 0)
//	]),
//
//	new Question("2 + 2 * 2 = ",
//	[
//		new Answer("4", 0),
//		new Answer("6", 1),
//		new Answer("8", 0),
//		new Answer("10", 0)
//	]),
//
//	new Question("2 + 2 / 2 = ",
//	[
//		new Answer("1", 0),
//		new Answer("2", 0),
//		new Answer("3", 1),
//		new Answer("4", 0)
//	])
//];

function end_function(){
    var value = quiz.score;
    $.ajax({
                url: window.location.href,
                type: 'POST',
                contentType: 'application/json',
                data: JSON.stringify({ 'value': value,
                                        'url': window.location.href,
                                        'name': questions_from_json.data[0].name}),
                success: function() {
                    document.location.href = '/tests/all'
                },
                error: function(error) {
                    console.log(error);
                }
            });
    };

function restart_function(){
    $.ajax({
                url: window.location.href,
                type: 'GET',
                success: function() {
                    document.location.href = window.location.href
                },
                error: function(error) {
                    console.log(error);
                }
            });
    };


//Сам тест
var quiz = new Quiz(1, questions, results);

Update();

//Обновление теста
function Update()
{
	//Проверяем, есть ли ещё вопросы
	if(quiz.current < quiz.questions.length)
	{
		//Если есть, меняем вопрос в заголовке
		headElem.innerHTML = quiz.questions[quiz.current].text;

		//Удаляем старые варианты ответов
		buttonsElem.innerHTML = "";

		//Создаём кнопки для новых вариантов ответов
		for(var i = 0; i < quiz.questions[quiz.current].answers.length; i++)
		{
			var btn = document.createElement("button");
			btn.className = "button";

			btn.innerHTML = quiz.questions[quiz.current].answers[i].text;

			btn.setAttribute("index", i);

			buttonsElem.appendChild(btn);
		}

		//Выводим номер текущего вопроса
		pagesElem.innerHTML = (quiz.current + 1) + " / " + quiz.questions.length;

		//Вызываем функцию, которая прикрепит события к новым кнопкам
		Init();
	}
	else
	{
		//Если это конец, то выводим результат
		buttonsElem.innerHTML = "";
		headElem.innerHTML = quiz.results[quiz.result].text;
		pagesElem.innerHTML = "Очки: " + quiz.score;

		var btn = document.createElement("button");
		btn.className = "button";
		btn.innerHTML = 'Переделать тест';
		btn.setAttribute("index", 1);
		btn.onclick = function(){
		    restart_function();
		}
		buttonsElem.appendChild(btn);

		var btn = document.createElement("button");
		btn.className = "button";
		btn.innerHTML = 'Завершить тест';
		btn.setAttribute("index", 0);
		btn.onclick = function(){
		    end_function();
		}
		buttonsElem.appendChild(btn);
	}
}

function Init()
{
	//Находим все кнопки
	var btns = document.getElementsByClassName("button");

	for(var i = 0; i < btns.length; i++)
	{
		//Прикрепляем событие для каждой отдельной кнопки
		//При нажатии на кнопку будет вызываться функция Click()
		btns[i].addEventListener("click", function (e) { Click(e.target.getAttribute("index")); });
	}
}

function Click(index)
{
	//Получаем номер правильного ответа
	var correct = quiz.Click(index);

	//Находим все кнопки
	var btns = document.getElementsByClassName("button");

	//Делаем кнопки серыми
	for(var i = 0; i < btns.length; i++)
	{
		btns[i].className = "button button_passive";
	}

	//Если это тест с правильными ответами, то мы подсвечиваем правильный ответ зелёным, а неправильный - красным
	if(quiz.type == 1)
	{
		if(correct >= 0)
		{
			btns[correct].className = "button button_correct";
		}

		if(index != correct)
		{
			btns[index].className = "button button_wrong";
		}
	}
	else
	{
		//Иначе просто подсвечиваем зелёным ответ пользователя
		btns[index].className = "button button_correct";
	}

	//Ждём секунду и обновляем тест
	setTimeout(Update, 1000);
}