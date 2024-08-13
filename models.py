from flask_login import UserMixin
import psycopg2

class User(UserMixin):
    def __init__(self, user_id, phone):
        self.id = user_id
        self.phone = phone

    def get_id(self):
        return str(self.id)

def get_db_connection():
    return psycopg2.connect(
        dbname="users",
        user="postgres",
        password="1111",
        host="localhost"
    )
