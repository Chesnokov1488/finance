import sqlite3
import telebot
from telebot import types

bot = telebot.TeleBot('6055269871:AAF08pDzj_aaVLJGY_q156XhQnpwyZQnZCg')

START_TEXT = """Привет, я бот-финансист, который будет личным ассистентом в твоих финансах 🤑
Для того, чтобы ознакомиться с руководством, как пользоваться ботом, нажми на кнопку /help"""

HELP_TEXT = """Я пока что в разработке, и понятный интерфейс будет не скоро. Поэтому сейчас лучше всего если вы прочтёте руководство по использованию😅
✅Пример работы команды доход: /доход 1000 Зарплата 
✅Пример работы команды расход: /расход 500 еда
✅Для просмотра своего баланса просто нажми на кнопку баланс
🦾Для жалоб, сотрудничества, и тд напиши разработчику бота: @alekseychesnokov
"""

@bot.message_handler(commands=['help'])
def help(message):
    bot.send_message(message.chat.id,HELP_TEXT)

@bot.message_handler(commands=['start'])
def start(message):
    conn = sqlite3.connect('finance.db', check_same_thread=False)
    cursor = conn.cursor()


    cursor.execute('''
        CREATE TABLE IF NOT EXISTS income (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            amount REAL,
            description TEXT
        )
    ''')
    conn.commit()
    markup = types.ReplyKeyboardMarkup()
    btn1 = types.KeyboardButton('/help')
    btn2 = types.KeyboardButton('/баланс')
    markup.row(btn1,btn2)

    bot.send_message(message.chat.id, START_TEXT,reply_markup=markup)

@bot.message_handler(commands=['доход'])
def add_income(message):
    try:
        amount = float(message.text.split()[1])
    except (ValueError, IndexError):
        bot.reply_to(message, "Такие команды у нас не принимаются. Как пользоваться ботом нажмите /help")
        return
    
    description = ' '.join(message.text.split()[2:])
    
    thread_conn = sqlite3.connect('finance.db', check_same_thread=False)
    thread_cursor = thread_conn.cursor()
    
    thread_cursor.execute('INSERT INTO income (amount, description) VALUES (?, ?)', (amount, description))
    thread_conn.commit()
    
    # Close the thread-specific connection and cursor
    thread_cursor.close()
    thread_conn.close()
    
    bot.reply_to(message, f"Доход в размере {amount:.2f} рублей успешно добавлен")

@bot.message_handler(commands=['расход'])
def add_expense(message):
    try:
        amount = float(message.text.split()[1])
    except (ValueError, IndexError):
        bot.reply_to(message, "Такие команды у нас не принимаются. Как пользоваться ботом нажмите /help")
        return
    
    description = ' '.join(message.text.split()[2:])
    
    # Create a new connection and cursor for the current thread
    thread_conn = sqlite3.connect('finance.db', check_same_thread=False)
    thread_cursor = thread_conn.cursor()
    
    # Create the expenditure table if it doesn't exist
    thread_cursor.execute('''
        CREATE TABLE IF NOT EXISTS expenditure (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            amount REAL,
            description TEXT
        )
    ''')
    
    # Add expense to the database using the thread-specific cursor
    thread_cursor.execute('INSERT INTO expenditure (amount, description) VALUES (?, ?)', (amount, description))
    thread_conn.commit()
    
    # Close the thread-specific connection and cursor
    thread_cursor.close()
    thread_conn.close()
    
    bot.reply_to(message, f"Расход в размере {amount:.2f} рублей успешно добавлен")

@bot.message_handler(commands=['баланс'])
def calculate_balance(message):
    # Create a new connection and cursor for the current thread
    thread_conn = sqlite3.connect('finance.db', check_same_thread=False)
    thread_cursor = thread_conn.cursor()

    # Calculate balance by subtracting total expenditure from total income
    thread_cursor.execute('SELECT COALESCE(SUM(amount), 0) FROM income')
    total_income = thread_cursor.fetchone()[0]

    thread_cursor.execute('SELECT COALESCE(SUM(amount), 0) FROM expenditure')
    total_expenditure = thread_cursor.fetchone()[0]
    
    balance = total_income - total_expenditure

    # Close the thread-specific connection and cursor
    thread_cursor.close()
    thread_conn.close()

    bot.send_message(message.chat.id, f"Ваш текущий баланс составляет: {balance:.2f} рублей")


bot.polling(none_stop=True)
