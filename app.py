from flask import Flask, render_template, request, jsonify, flash, redirect, url_for
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
import psycopg2
import random
import string
import re
from datetime import datetime, timedelta
import logging

from forms import LoginForm, RegistrationForm
from models import User, get_db_connection
from telegram_utils import send_telegram_message
import config

logging.basicConfig(level=logging.INFO)

app = Flask(__name__)
app.config['SECRET_KEY'] = config.SECRET_KEY

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

DATABASE_URL = config.DATABASE_URL

@login_manager.user_loader
def load_user(user_id):
    with psycopg2.connect(DATABASE_URL) as conn:
        with conn.cursor() as cursor:
            cursor.execute('SELECT * FROM users WHERE id = %s', (user_id,))
            user_data = cursor.fetchone()
            if user_data:
                return User(user_data[0], user_data[1])
    return None


@app.route('/')
def index():
    return render_template('index.html', form_login=LoginForm(), form_register=RegistrationForm())


@app.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    return 'Logged out', 200


@app.route('/send_message', methods=['POST'])
def send_message():
    data = request.get_json()
    name = data.get('name', '').strip()
    phone = data.get('phone', '').strip()

    if not name or not phone:
        return 'Имя и номер телефона не могут быть пустыми.', 400

    message = f'Имя: {name}\nТелефон: {phone}'
    try:
        send_telegram_message(message)
        return jsonify({'message': 'Сообщение успешно отправлено в Telegram!'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/send_message_offer', methods=['POST'])
def send_message_offer():
    data = request.json
    page_name = data.get('pageName', '')

    if 'prostor' in page_name:
        application_type = "Заявка на подписку"
    elif 'cifrovizaciya' in page_name:
        application_type = "Заявка на цифровизацию"
    else:
        application_type = "Заявка на услугу"

    message_parts = [f"\n{item['description']}: {item['value']}" for item in data['values']]
    message = f"{application_type}: " + ", ".join(message_parts)

    try:
        send_telegram_message(message)
        return jsonify({'message': 'Сообщение успешно отправлено!'})
    except Exception as e:
        logging.error(f"Failed to send message: {str(e)}")
        return jsonify({'error': 'Failed to send message'}), 500


@app.route('/generate_verification_code', methods=['GET'])
def generate_verification_code():
    verification_code = ''.join(random.choices(string.digits, k=4))
    phone = re.sub(r'\D', '', request.args.get('phone'))

    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("DELETE FROM codes WHERE phone=%s", (phone,))
            cursor.execute("INSERT INTO codes (phone, code, start_time) VALUES (%s, %s, %s)",
                           (phone, verification_code, datetime.now()))
            conn.commit()

    # Убрать комментарий при активации модуля notisend
    # sms.sendSMS(f"7{phone[1:]}", f"Код авторизации: {verification_code}")
    return jsonify(success=True, verification_code=verification_code), 200


@app.route('/register', methods=['POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        phone = re.sub(r'\D', '', form.phone.data)
        code = form.code.data

        with psycopg2.connect(DATABASE_URL) as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT * FROM users WHERE phone = %s", (phone,))
                if cursor.fetchone():
                    return jsonify(success=False, message='Пользователь с таким телефоном уже существует')

                cursor.execute("SELECT * FROM codes WHERE phone = %s AND code = %s AND status = 1", (phone, code))
                code_entry = cursor.fetchone()
                if code_entry and datetime.now() - code_entry[3] <= timedelta(minutes=5):
                    cursor.execute("INSERT INTO users (name, company, phone) VALUES (%s, %s, %s) RETURNING id",
                                   (form.name.data, form.company.data or None, phone))
                    user_id = cursor.fetchone()[0]
                    login_user(User(user_id, phone))
                    cursor.execute("UPDATE codes SET status = 0 WHERE phone = %s", (phone,))
                    conn.commit()
                    return jsonify(success=True, redirect=url_for('index'))
                return jsonify(success=False, message='Неправильный или устаревший код')
    return jsonify(success=False, message='Ошибка валидации данных')


@app.route('/login', methods=['POST'])
def login():
    form = LoginForm(request.form)
    if form.validate_on_submit():
        phone = re.sub(r'\D', '', form.phone.data)
        code = form.code.data

        with psycopg2.connect(DATABASE_URL) as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT * FROM codes WHERE phone = %s AND code = %s AND status = 1", (phone, code))
                code_entry = cursor.fetchone()
                if code_entry and datetime.now() - code_entry[3] <= timedelta(minutes=5):
                    cursor.execute("SELECT * FROM users WHERE phone = %s", (phone,))
                    user_entry = cursor.fetchone()
                    if user_entry:
                        login_user(User(user_entry[0], phone))
                        return jsonify(success=True, redirect=url_for('index'))
                return jsonify(success=False, message='Неправильный код или код устарел')
    return jsonify(success=False, message='Ошибка валидации данных')


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
