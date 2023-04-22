# -*- coding: utf-8 -*-
import logging
from werkzeug.security import generate_password_hash
from dotenv import load_dotenv
import os
import warnings
from flask import Flask, render_template, Response, request, redirect, flash, Markup
import pandas as pd
from datetime import datetime, timedelta
import urllib
import json
from sqlalchemy import create_engine
from flask_bootstrap import Bootstrap
from flask_login import login_required, current_user, login_user, logout_user
from models import Users, Coments, login, session
from mail import Mail, tokens
from itsdangerous import URLSafeSerializer, SignatureExpired

# load_dotenv(os.path.dirname(__file__)+".env")
app = Flask(__name__, subdomain_matching=True)
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

logging.basicConfig(filename='./log/log.log',
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
#app.config['SERVER_NAME'] = 'domain.dom:5000'
# app.config['SESSION_COOKIE_SECURE'] = True
# app.config['SESSION_COOKIE_HTTPONLY'] = True
# app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
# app.config['USE_X_SENDFILE'] = True

mydb = create_engine(app.config['SQLALCHEMY_DATABASE_URI'])

login.init_app(app)
login.login_view = 'login'
login.login_message = ''
login.login_message_category = 'success'
login.session_protection = 'strong'


@app.before_request
def make_session_permanent():
    session.permanent = True
    app.permanent_session_lifetime = timedelta(days=14)


@app.route('/', methods=['GET', 'POST'])
def start_page():
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
            coment = Coments(DT=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                             email=email, coment=text)
            try:
                session.add(coment)
                session.commit()
            except Exception:
                session.rollback()

    return render_template('index.html')

#
# @app.route('/', subdomain='admin')
# def start_page_admin():
#     return render_template('index.html')


@app.route('/profile')
@login_required
def profile():
    return render_template('profile.html')


@app.route('/tests/<id>')
@login_required
def tests(id):
    return render_template('tests.html', id=id)


# @app.route('/books')
# def books():
#     return render_template('books.html')


@app.route('/books/<id>')
def books_klass(id):
    return render_template('books.html', id=id)


@app.route('/articles/<id>')
def articles_klass(id):
    return render_template('articles.html', id=id)


@app.route('/login', methods=['GET', 'POST'])
def login():
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
    except Exception:
        return redirect('/login')

    return render_template("login.html")


@app.route('/registration', methods=['GET', 'POST'])
def registration():
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

            user = Users(email=email, name=name, role=role, verified=False)
            user.set_password(user_password)
            try:
                session.add(user)
                session.commit()
            except Exception:
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
                except:
                    session.rollback()
                    render_template('error.html', name=current_user.get_id())
                return redirect('/login')

    except Exception:
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
                except Exception:
                    session.rollback()
                    flash('Что-то пошло не так', category='error')
                return redirect('/login')

        return render_template("new_password.html")


@app.route('/confirm_email/<token>')
def confirm_email(token):
    try:
        email_token = tokens.decrypt(token, salt='email-confirm')
    except SignatureExpired:
        return render_template('/registration')
    else:
        try:
            session.query(Users).filter_by(email=email_token).update({'verified': True})
            session.commit()
        except Exception:
            session.rollback()
        return redirect('/')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/')


@app.route('/5klass/1')
def klass5_1():
    return render_template('5klass_1.html')


@app.route('/5klass/2')
def klass5_2():
    return render_template('5klass_2.html')


@app.errorhandler(404)
def page_not_found(e):
    return render_template('access denied.html'), 404


if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)
