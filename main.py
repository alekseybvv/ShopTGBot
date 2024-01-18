import telebot
import configure
import sqlite3
from telebot import types
import threading
from requests import get
from time import sleep
from SimpleQIWI import *

client = telebot.TeleBot(configure.config['token'])
db = sqlite3.connect('baza.db', check_same_thread=False)
sql = db.cursor()
lock = threading.Lock()
api = QApi(token=configure.config['tokenqiwi'], phone=configure.config['phoneqiwi'])
markdown = """
    *bold text*
    _italic text_
    [text](URL)
    """

#database

sql.execute("""CREATE TABLE IF NOT EXISTS users (id BIGINT, nick TEXT, cash INT, access INT, bought INT)""")
sql.execute("""CREATE TABLE IF NOT EXISTS shop (id INT, name TEXT, price INT, tovar TEXT, whobuy TEXT)""")
db.commit()

@client.message_handler(commands=['start'])
def start(message):
	try:
		getname = message.from_user.first_name
		cid = message.chat.id
		uid = message.from_user.id

		sql.execute(f"SELECT id FROM users WHERE id = {uid}")
		if sql.fetchone() is None:
			sql.execute(f"INSERT INTO users VALUES ({uid}, '{getname}', 0, 0, 0)")
			client.send_message(cid, f"🛒 | Добро пожаловать, {getname}!\nТы попал в бота магазин\nИзмените этот текст!")
			db.commit()
		else:
			client.send_message(cid, f"⛔️ | Ты уже зарегистрирован! Пропиши /help чтобы узнать команды.")
	except:
		client.send_message(cid, f'🚫 | Ошибка при выполнении команды')

@client.message_handler(commands=['profile', 'myinfo', 'myprofile'])
def myprofile(message):
	try:
		cid = message.chat.id
		uid = message.from_user.id
		sql.execute(f"SELECT * FROM users WHERE id = {uid}")
		getaccess = sql.fetchone()[3]
		if getaccess == 0:
			accessname = 'Пользователь'
		elif getaccess == 1:
			accessname = 'Администратор'
		elif getaccess == 777:
			accessname = 'Разработчик'
		for info in sql.execute(f"SELECT * FROM users WHERE id = {uid}"):
			client.send_message(cid, f"*📇 | Твой профиль:*\n\n*👤 | Ваш ID:* {info[0]}\n*💸 | Баланс:* {info[2]} ₽\n*👑 | Уровень доступа:* {accessname}\n*🛒 | Куплено товаров:* {info[4]}\n\n*🗂 Чтобы посмотреть список купленных товаров напишите /mybuy*", parse_mode='Markdown')
	except:
		client.send_message(cid, f'🚫 | Ошибка при выполнении команды')
