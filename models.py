import os
import urllib
from base64 import b64encode as enc64

import sqlalchemy as sa
from flask_login import UserMixin, LoginManager
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, declarative_base
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

login = LoginManager()

server = '194.58.123.127'
username = 'sa'

# load_dotenv(os.path.dirname(__file__) + ".env")
# password = os.environ.get('vps_mssql_pw')
root_folder = os.path.dirname(os.path.realpath(__file__))
# password = os.environ.get('vps_mssql_pw')
with open("{}/psswrd.txt".format(root_folder), 'r') as f:
    db_password = f.readline().rstrip()

database = 'MATH_WEB'

params = urllib.parse.quote_plus(
    f"DRIVER=ODBC Driver 17 for SQL Server;SERVER={server};DATABASE={database};UID={username};"
    f"PWD={db_password};Mars_Connection=Yes")

engine = create_engine("mssql+pyodbc:///?odbc_connect=%s" % params)
Base = declarative_base()

metadata = Base.metadata
metadata.reflect(engine)

Session = sa.orm.sessionmaker(engine)
session = Session()


class Tests_table(Base):
    """! Класс тестов пользователей"""
    __tablename__ = sa.Table('Tests', metadata, autoload_with=engine)
    id = sa.Column(sa.Integer, primary_key=True)
    DT = sa.Column(sa.DateTime)
    email = sa.Column(sa.String)
    klass = sa.Column(sa.String)
    test_name = sa.Column(sa.String)
    value = sa.Column(sa.Integer)

    def __init__(self, *, DT, email, klass, test_name, value):
        """! Конструктор класса тестов"""
        super().__init__()
        self.DT = DT
        self.email = email
        self.klass = klass
        self.test_name = test_name
        self.value = value


class Coments(Base):
    """! Класс комментариев для записи и выгрузки из БД"""
    __tablename__ = sa.Table('Coments', metadata, autoload_with=engine)
    id = sa.Column(sa.Integer, primary_key=True)
    DT = sa.Column(sa.DateTime)
    email = sa.Column(sa.String)
    coment = sa.Column(sa.String)
    replied = sa.Column(sa.Boolean)

    def __init__(self, *, DT, email, coment):
        """! Конструктор класса комментариев"""
        super().__init__()
        self.DT = DT
        self.email = email
        self.coment = coment
        self.replied = False


class Tokens_db(Base):
    """! Класс токенов для записи и выгрузки из БД"""
    __tablename__ = sa.Table('Tokens', metadata, autoload_with=engine)
    id = sa.Column(sa.Integer, primary_key=True)
    DT = sa.Column(sa.DateTime)
    token = sa.Column(sa.String)
    secret = sa.Column(sa.String)

    def __init__(self, *, DT, token, secret):
        """! Конструктор класса токенов"""
        super().__init__()
        self.DT = DT
        self.token = token
        self.secret = secret


class Users(UserMixin, Base):
    """! Класс пользователей для записи и выгрузки из БД"""
    __tablename__ = sa.Table("Users", metadata, autoload_with=engine)
    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String)
    email = sa.Column(sa.String)
    password = sa.Column(sa.String)
    role = sa.Column(sa.String)
    verified = sa.Column(sa.Boolean)
    img = sa.Column(sa.BLOB)
    img_name = sa.Column(sa.String)
    mimetype = sa.Column(sa.String)
    DT_reg = sa.Column(sa.DateTime)

    def __init__(self, *, name, email, role, verified, DT_reg):
        """! Конструктор класса пользователей"""
        super().__init__()
        self.name = name
        self.email = email
        self.role = role
        self.verified = verified
        self.DT_reg = DT_reg

    def set_password(self, user_password):
        self.password = generate_password_hash(user_password)

    def check_password(self, user_password):
        return check_password_hash(self.password, user_password)

    def get_name(self):
        return self.name

    def get_role(self):
        return str(self.role)

    def get_verified(self):
        return not self.verified

    def get_photo(self):
        if self.img is None:
            return None
        else:
            binary = enc64(self.img).decode()
            return binary

    def set_photo(self, photo):
        session.query(Users) \
            .filter_by(email=self.email) \
            .update({'img': photo.read(),
                     'img_name': secure_filename(photo.filename),
                     'mimetype': photo.mimetype})
        session.commit()


@login.user_loader
def load_user(id):
    try:
        return session.query(Users).get(int(id))
    except Exception:
        session.rollback()
