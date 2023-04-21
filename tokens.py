from itsdangerous import URLSafeSerializer, SignatureExpired
import random
from models import session, Tokens_db
from datetime import datetime


class Tokens:
    @staticmethod
    def secret_key():
        keys = ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m",
                "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z",
                "A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M",
                "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z",
                '1', '2', '3', '4', '5', '6', '7', '8', '9', '0', '_', '-', '@',
                '#', '$', '%', '^', '&', '*', '(', ')', '+', '=', '<', '>', '?',
                '!', '~', '`', '.', ',', '|', '/']
        secret = ''
        for i in 3 * keys:
            secret = secret + keys[random.randint(0, len(keys) - 1)]
        secret_object = URLSafeSerializer(secret)
        return secret, secret_object

    def create(self, email, salt):
        secret, secret_object = self.secret_key()
        token = secret_object.dumps(email, salt=salt)
        try:
            session.add(Tokens_db(DT=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                                  token=token,
                                  secret=secret))
            session.commit()
            return token
        except Exception:
            session.rollback()

    @staticmethod
    def decrypt(token, salt):
        user = session.query(Tokens_db).filter_by(token=token).one()
        if user is not None:
            user_secret = user.secret
            user_token = user.token
            user_secret_object = URLSafeSerializer(user_secret)
            try:
                email = user_secret_object.loads(user_token, salt=salt)
                return email
            except SignatureExpired:
                raise Exception
