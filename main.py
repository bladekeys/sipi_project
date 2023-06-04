# -*- coding: utf-8 -*-
import json
import logging
import os
import urllib
import warnings
from datetime import datetime, timedelta

from flask import Flask, render_template, request, redirect, flash, Markup, abort
from flask_bootstrap import Bootstrap
from flask_login import login_required, current_user, login_user, logout_user
from itsdangerous import SignatureExpired
from sqlalchemy import create_engine
from werkzeug.security import generate_password_hash

from mail import Mail, tokens
from models import Users, Coments, Tests_table, login, session

# load_dotenv(os.path.dirname(__file__)+".env")
app = Flask(__name__)
Bootstrap(app)
mail = Mail()
server = '194.58.123.127'
username = 'sa'
root_folder = os.path.dirname(os.path.realpath(__file__))
# password = os.environ.get('vps_mssql_pw')
with open("{}/psswrd.txt".format(root_folder), 'r') as f:
    db_password, email_password = f.readlines()
    db_password = db_password.rstrip()

warnings.filterwarnings("ignore")

logging.basicConfig(filename=root_folder + '/log/log.log',
                    filemode='a',
                    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    level=logging.INFO)

params = urllib.parse.quote_plus(
    f"DRIVER=ODBC Driver 17 for SQL Server;SERVER={server};UID={username};PWD={db_password};Mars_Connection=Yes")

app.secret_key, _ = tokens.secret_key()

app.config['UPLOAD_FOLDER'] = 'static'
app.config['SQLALCHEMY_DATABASE_URI'] = "mssql+pyodbc:///?odbc_connect=%s" % params
app.config['SQLALCHEMY_TRACK_MODIFICATION'] = False
app.config['SESSION_PERMANENT'] = True
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=14)
# app.config['SESSION_COOKIE_SECURE'] = True
# app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
# app.config['USE_X_SENDFILE'] = True

mydb = create_engine(app.config['SQLALCHEMY_DATABASE_URI'])

login.init_app(app)
login.login_view = 'login'
login.login_message = ''
login.login_message_category = 'success'
login.session_protection = 'strong'


def post_coment(func):
    def wrapper(*args, **kwargs):
        return_value = func(*args, **kwargs)
        if request.method == 'POST':
            if current_user.is_authenticated:
                email = current_user.email
            else:
                email = request.form['email']

            text = request.form['text']
            if email == '':
                flash('Напишите почту.',
                      category='error')
            elif text == '':
                flash('Напишите вопрос или комментарий.',
                      category='error')
            else:
                coment = Coments(DT=datetime.now().strftime("%Y-%m-%d %H:%M:%S"), email=email, coment=str(text))
                try:
                    mail.on_comment(email, text)
                    session.add(coment)
                    session.commit()
                except Exception as error:
                    logging.error(error)
                    session.rollback()
        return return_value

    wrapper.__name__ = func.__name__
    return wrapper


@app.before_request
def make_session_permanent():
    session.permanent = True
    app.permanent_session_lifetime = timedelta(days=14)


@app.route('/', methods=['GET', 'POST'])
@post_coment
def start_page():
    """!Главная страница сайта
    """
    return render_template('index.html')


@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    """!Страница профиля пользователя
    в качестве метода POST принимает фотографию"""
    if request.method == 'POST':
        current_user.set_photo(request.files['photo'])

    user_tests_list = []
    user_tests = session.query(Tests_table).filter_by(email=current_user.email).all()
    for test in user_tests:
        user_tests_list.append({"DT": test.DT.strftime("%Y-%m-%d %H:%M:%S"),
                                "name": test.test_name,
                                "value": test.value})

    return render_template('profile.html', user_tests_list=json.dumps(user_tests_list, ensure_ascii=False))


@app.route('/admin/users', methods=['GET', 'POST'])
@login_required
def users():
    if current_user.get_verified():
        return render_template('email confirm.html')
    all_users_list = []
    if current_user.get_role() == 'Admin':
        all_users = session.query(Users)
        for user in all_users:
            all_users_list.append({"name": user.name,
                                   "email": user.email,
                                   "role": user.role,
                                   "verified": 'Да' if user.verified else 'Нет'})
    return render_template('users.html',
                           all_users_list=json.dumps(all_users_list, ensure_ascii=False))


@app.route('/admin/coments', methods=['GET', 'POST'])
@login_required
def coments():
    if current_user.get_verified():
        return render_template('email confirm.html')
    all_coments_list = []
    if current_user.get_role() == 'Admin':
        all_coments = session.query(Coments).order_by(Coments.DT)
        for com in all_coments:
            all_coments_list.append({"DT": str(com.DT),
                                     "email": com.email,
                                     "coment": com.coment,
                                     "is_replied": 'Да' if com.replied else 'Нет',
                                     "reply": "<a href='/admin/reply/" + com.email + "/"
                                              + str(com.id) + "'>Ответить</a>"})
    return render_template('coments.html',
                           all_coments_list=json.dumps(all_coments_list, ensure_ascii=False))


@app.route('/admin/reply/<email>/<id>', methods=['GET', 'POST'])
@login_required
def reply(email, id):
    if current_user.get_verified():
        return render_template('email confirm.html')
    session_comment = session.query(Coments.coment).filter_by(email=email, id=id).one_or_none()[0]
    if current_user.get_role() == 'Admin':
        if request.method == 'POST':
            answer = request.form['answer']
            mail.reply(email, session_comment, answer, current_user.name)
            session.query(Coments).filter_by(email=email, id=id).update({"replied": True})
            session.commit()
            return redirect('/admin/coments')

    return render_template('reply.html', email=email, coment=session_comment)


@app.route('/tests/<klass>', methods=['GET', 'POST'])
@login_required
@post_coment
def tests(klass):
    if klass not in ['5klass', '6klass', '7klass', '8klass', '9klass', 'all']:
        abort(404)
    return render_template('tests.html', id=klass)


@app.route('/tests/<klass>/<test_id>', methods=['GET', 'POST'])
@login_required
def test_template(klass, test_id):
    if current_user.get_verified():
        return render_template('email confirm.html')

    if klass not in ['5klass', '6klass', '7klass', '8klass', '9klass', 'all']:
        abort(404)
    else:
        with open("{}/static/tests_json/{}/{}.json".format(root_folder, klass, test_id), 'r',
                  encoding='UTF-8') as f_json:
            json_file = json.load(f_json)

    if request.method == 'POST':
        data = request.get_json()
        value = data['value']
        url = data['url'].split('/')
        name = data['name']
        test = Tests_table(DT=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                           email=current_user.email, klass=url[4],
                           test_name=name, value=value)
        try:
            session.add(test)
            session.commit()
        except Exception as error:
            logging.error(error)
            session.rollback()

    return render_template('quiz.html', questions_json=json_file)


@app.route('/admin/tests', methods=['GET', 'POST'])
@login_required
def admin_test_all():
    return render_template('admin_tests_all.html')


@app.route('/admin/tests/<klass>/<test_id>', methods=['GET', 'POST'])
@login_required
def admin_test_template(klass, test_id):
    if klass not in ['5klass', '6klass', '7klass', '8klass', '9klass', 'all']:
        abort(404)
    else:
        with open("{}/static/tests_json/{}/{}.json".format(root_folder, klass, test_id), 'r',
                  encoding='UTF-8') as f_json:
            json_file = json.load(f_json)

    if request.method == 'POST':
        name_of_test = request.form['name_of_test']

        # 1 вопрос
        q1 = request.form['q1']
        q1a1 = request.form['q1a1']
        q1a2 = request.form['q1a2']
        q1a3 = request.form['q1a3']
        q1a4 = request.form['q1a4']
        q1c1 = 0 if request.form.get('q1c1') is None else 1
        q1c2 = 0 if request.form.get('q1c2') is None else 1
        q1c3 = 0 if request.form.get('q1c3') is None else 1
        q1c4 = 0 if request.form.get('q1c4') is None else 1

        # 2 вопрос
        q2 = request.form['q2']
        q2a1 = request.form['q2a1']
        q2a2 = request.form['q2a2']
        q2a3 = request.form['q2a3']
        q2a4 = request.form['q2a4']
        q2c1 = 0 if request.form.get('q2c1') is None else 1
        q2c2 = 0 if request.form.get('q2c2') is None else 1
        q2c3 = 0 if request.form.get('q2c3') is None else 1
        q2c4 = 0 if request.form.get('q2c4') is None else 1

        # 3 вопрос
        q3 = request.form['q3']
        q3a1 = request.form['q3a1']
        q3a2 = request.form['q3a2']
        q3a3 = request.form['q3a3']
        q3a4 = request.form['q3a4']
        q3c1 = 0 if request.form.get('q3c1') is None else 1
        q3c2 = 0 if request.form.get('q3c2') is None else 1
        q3c3 = 0 if request.form.get('q3c3') is None else 1
        q3c4 = 0 if request.form.get('q3c4') is None else 1

        # 4 вопрос
        q4 = request.form['q4']
        q4a1 = request.form['q4a1']
        q4a2 = request.form['q4a2']
        q4a3 = request.form['q4a3']
        q4a4 = request.form['q4a4']
        q4c1 = 0 if request.form.get('q4c1') is None else 1
        q4c2 = 0 if request.form.get('q4c2') is None else 1
        q4c3 = 0 if request.form.get('q4c3') is None else 1
        q4c4 = 0 if request.form.get('q4c4') is None else 1

        # 5 вопрос
        q5 = request.form['q5']
        q5a1 = request.form['q5a1']
        q5a2 = request.form['q5a2']
        q5a3 = request.form['q5a3']
        q5a4 = request.form['q5a4']
        q5c1 = 0 if request.form.get('q5c1') is None else 1
        q5c2 = 0 if request.form.get('q5c2') is None else 1
        q5c3 = 0 if request.form.get('q5c3') is None else 1
        q5c4 = 0 if request.form.get('q5c4') is None else 1

        # запись в файл
        json_file["data"][0]['name'] = name_of_test

        # 1 вопрос
        json_file["data"][0]['question'] = q1
        json_file["data"][0]['answers'][0]['answer'] = q1a1
        json_file["data"][0]['answers'][1]['answer'] = q1a2
        json_file["data"][0]['answers'][2]['answer'] = q1a3
        json_file["data"][0]['answers'][3]['answer'] = q1a4
        json_file["data"][0]['answers'][0]['is_correct'] = q1c1
        json_file["data"][0]['answers'][1]['is_correct'] = q1c2
        json_file["data"][0]['answers'][2]['is_correct'] = q1c3
        json_file["data"][0]['answers'][3]['is_correct'] = q1c4

        # 2 вопрос
        json_file["data"][1]['question'] = q2
        json_file["data"][1]['answers'][0]['answer'] = q2a1
        json_file["data"][1]['answers'][1]['answer'] = q2a2
        json_file["data"][1]['answers'][2]['answer'] = q2a3
        json_file["data"][1]['answers'][3]['answer'] = q2a4
        json_file["data"][1]['answers'][0]['is_correct'] = q2c1
        json_file["data"][1]['answers'][1]['is_correct'] = q2c2
        json_file["data"][1]['answers'][2]['is_correct'] = q2c3
        json_file["data"][1]['answers'][3]['is_correct'] = q2c4

        # 3 вопрос
        try:
            json_file["data"][2]['question'] = q3
            json_file["data"][2]['answers'][0]['answer'] = q3a1
            json_file["data"][2]['answers'][1]['answer'] = q3a2
            json_file["data"][2]['answers'][2]['answer'] = q3a3
            json_file["data"][2]['answers'][3]['answer'] = q3a4
            json_file["data"][2]['answers'][0]['is_correct'] = q3c1
            json_file["data"][2]['answers'][1]['is_correct'] = q3c2
            json_file["data"][2]['answers'][2]['is_correct'] = q3c3
            json_file["data"][2]['answers'][3]['is_correct'] = q3c4
        except Exception as error:
            logging.error(error)
            pass

        try:
            json_file["data"][3]['question'] = q4
            json_file["data"][3]['answers'][0]['answer'] = q4a1
            json_file["data"][3]['answers'][1]['answer'] = q4a2
            json_file["data"][3]['answers'][2]['answer'] = q4a3
            json_file["data"][3]['answers'][3]['answer'] = q4a4
            json_file["data"][3]['answers'][0]['is_correct'] = q4c1
            json_file["data"][3]['answers'][1]['is_correct'] = q4c2
            json_file["data"][3]['answers'][2]['is_correct'] = q4c3
            json_file["data"][3]['answers'][3]['is_correct'] = q4c4
        except Exception as error:
            logging.error(error)
            pass

        try:
            json_file["data"][4]['question'] = q5
            json_file["data"][4]['answers'][0]['answer'] = q5a1
            json_file["data"][4]['answers'][1]['answer'] = q5a2
            json_file["data"][4]['answers'][2]['answer'] = q5a3
            json_file["data"][4]['answers'][3]['answer'] = q5a4
            json_file["data"][4]['answers'][0]['is_correct'] = q5c1
            json_file["data"][4]['answers'][1]['is_correct'] = q5c2
            json_file["data"][4]['answers'][2]['is_correct'] = q5c3
            json_file["data"][4]['answers'][3]['is_correct'] = q5c4
        except Exception as error:
            logging.error(error)
            pass

        with open("{}/static/tests_json/{}/{}.json".format(root_folder, klass, test_id), 'w',
                  encoding='UTF-8') as f_json:
            json.dump(json_file, f_json)

    return render_template('admin_tests_edit.html', questions_json=json_file)


@app.route('/admin')
@login_required
def admin():
    """!Админ панель"""
    if not current_user.get_role() == 'Admin':
        return redirect('/login')
    new_users = session.query(Users.id).filter(Users.DT_reg >= (datetime.now() - timedelta(days=1))
                                               .strftime("%Y-%m-%d %H:%M:%S")).count()
    day_tests = session.query(Tests_table.id).filter(Tests_table.DT >= (datetime.now() - timedelta(days=1))
                                                     .strftime("%Y-%m-%d %H:%M:%S")).count()
    unreplied = session.query(Coments.id).filter_by(replied=False).count()
    return render_template('admin_index.html', new_users=new_users, unreplied=unreplied, day_tests=day_tests)


@app.route('/books/<id>', methods=['GET', 'POST'])
@post_coment
def books_klass(id):
    if id not in ['5klass', '6klass', '7klass', '8klass', '9klass', 'all']:
        abort(404)
    return render_template('books.html', id=id)


@app.route('/articles/<klass>/<theme>', methods=['GET', 'POST'])
@post_coment
def article_klass(klass, theme):
    if klass not in ['5klass', '6klass', '7klass', '8klass', '9klass']:
        abort(404)
    return render_template('{}_{}.html'.format(klass, theme))


@app.route('/articles/<klass>', methods=['GET', 'POST'])
@post_coment
def all_articles_klass(klass):
    if klass not in ['5klass', '6klass', '7klass', '8klass', '9klass', 'all']:
        abort(404)
    return render_template('articles.html', id=klass)


@app.route('/login', methods=['GET', 'POST'])
def login():
    """!Авторизация пользователя"""
    if current_user.is_authenticated:
        return redirect('/')
    try:
        if request.method == 'POST':
            email = request.form['email']
            user = session.query(Users).filter_by(email=email).first()
            if user is None:
                flash('Некорректный логин или пароль', category='error')
            elif not user.check_password(request.form['password']):
                flash('Некорректный логин или пароль', category='error')
            elif user is not None and user.check_password(request.form['password']):
                login_user(user)
                return redirect('/')
    except Exception as error:
        logging.error(error)
        return redirect('/login')

    return render_template("login.html")


@app.route('/registration', methods=['GET', 'POST'])
def registration():
    """!Регистрация пользователя"""
    if request.method == 'POST':
        email = request.form['email']
        role = 'User'

        name = request.form['name']
        user_password = request.form['password']

        if session.query(Users).filter_by(email=email).first() is not None:
            flash('Учетная запись уже существует. Обратитесь к администраторам в случае проблемы.',
                  category='error')
        else:
            mail.register(email)

            user = Users(email=email, name=name, role=role,
                         verified=False,
                         DT_reg=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            user.set_password(user_password)
            try:
                session.add(user)
                session.commit()
            except Exception as error:
                logging.error(error)
                session.rollback()
            return redirect('/login')

    return render_template("registration.html")


@app.route('/forget_password', methods=['GET', 'POST'])
def forget_password():
    if current_user.is_authenticated:
        return redirect('/')
    try:
        if request.method == 'POST':
            email = request.form['email']
            user = session.query(Users).filter_by(email=email).first()
            if user is None:
                back_to_reg = Markup(
                    '<br> <a style="color:inherit" href="/registration">Вернуться к регистрации</a>')
                flash("Почта отсутствует в базе данных" + back_to_reg, category='error')
            else:
                mail.recovery(email)
                try:
                    session.add(user)
                    session.commit()
                except Exception as error:
                    logging.error(error)
                    session.rollback()
                    render_template('error.html', name=current_user.get_id())
                return redirect('/login')

    except Exception as error:
        logging.error(error)
        return redirect('/login')

    return render_template("forget_password.html")


@app.route('/new_password/<token_forget_password>', methods=['GET', 'POST'])
def new_password(token_forget_password):
    try:
        email_forget = tokens.decrypt(token_forget_password, salt='forgetpassword')
    except SignatureExpired:
        return redirect('/registration')
    else:
        if request.method == 'POST':
            password = str(request.form['password'])
            password_repeat = str(request.form['password_repeat'])
            if password != password_repeat:
                flash('Пароли не совпадают', category='error')
            else:
                try:
                    session.query(Users).filter_by(email=email_forget).update(
                        {'password': generate_password_hash(password)})
                    session.commit()
                except Exception as error:
                    logging.error(error)
                    session.rollback()
                    flash('Что-то пошло не так', category='error')
                return redirect('/login')

        return render_template("new_password.html")


@app.route('/confirm_email/<token>')
def confirm_email(token):
    """! Подтверждение почты"""
    try:
        email_token = tokens.decrypt(token, salt='email-confirm')
    except SignatureExpired:
        return render_template('/registration')
    else:
        try:
            session.query(Users).filter_by(email=email_token).update({'verified': True})
            session.commit()
        except Exception as error:
            logging.error(error)
            session.rollback()
        return redirect('/')


@app.route('/help', methods=['GET', 'POST'])
def help_page():
    """!Страница пользователя"""
    return render_template('help_page.html')


@app.route('/logout')
@login_required
def logout():
    """!Выход"""
    logout_user()
    return redirect('/')


# @app.route('/5klass/1')
# def klass5_1():
#     return render_template('5klass_1.html')
#
#
# @app.route('/5klass/2')
# def klass5_2():
#     return render_template('5klass_2.html')


@app.errorhandler(404)
def page_not_found(error):
    logging.error(error)
    return render_template('access denied.html'), 404


if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)
