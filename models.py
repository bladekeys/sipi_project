import os
from flask_login import UserMixin, LoginManager
from werkzeug.security import generate_password_hash, check_password_hash
import urllib
import sqlalchemy as sa
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, declarative_base
import logging

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


class Coments(Base):
    __tablename__ = sa.Table('Coments', metadata, autoload_with=engine)
    id = sa.Column(sa.Integer, primary_key=True)
    DT = sa.Column(sa.DateTime)
    email = sa.Column(sa.String)
    coment = sa.Column(sa.String)

    def __init__(self, *, DT, email, coment):
        super().__init__()
        self.DT = DT
        self.email = email
        self.coment = coment


class Tokens_db(Base):
    __tablename__ = sa.Table('Tokens', metadata, autoload_with=engine)
    id = sa.Column(sa.Integer, primary_key=True)
    DT = sa.Column(sa.DateTime)
    token = sa.Column(sa.String)
    secret = sa.Column(sa.String)

    def __init__(self, *, DT, token, secret):
        super().__init__()
        self.DT = DT
        self.token = token
        self.secret = secret


class Users(UserMixin, Base):
    __tablename__ = sa.Table("Users", metadata, autoload_with=engine)
    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String)
    email = sa.Column(sa.String)
    password = sa.Column(sa.String)
    role = sa.Column(sa.String)
    verified = sa.Column(sa.Boolean)

    def __init__(self, *, name, email, role, verified):
        super().__init__()
        self.name = name
        self.email = email
        self.role = role
        self.verified = verified

    def set_password(self, user_password):
        self.password = generate_password_hash(user_password)

    def check_password(self, user_password):
        return check_password_hash(self.password, user_password)

    def get_name(self):
        return self.name


@login.user_loader
def load_user(id):
    try:
        return session.query(Users).get(int(id))
    except Exception:
        session.rollback()
