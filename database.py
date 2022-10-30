import time
import datetime
import sqlite3 as sqlite

from main import bot, dp, logger


db = sqlite.connect('db.sql')
cur = db.cursor()


def initDB():
    '''
    Инициализация базы данных
    '''

    db.execute(
        '''
        CREATE TABLE IF NOT EXISTS pool(
            id INTEGER PRIMARY KEY AUTOINCREMENT, 
            user_id INT UNIQUE,
            gender INT,
            age INT,
            country TEXT
            )
        '''
    )

    db.execute(  # ВОЗРАСТ ТЕКСТОМ!
        '''
        CREATE TABLE IF NOT EXISTS pool_premium(
            id INTEGER PRIMARY KEY AUTOINCREMENT, 
            user_id INT UNIQUE,
            gender INT,
            age_1 INT,
            age_2 INT,
            country TEXT
            )
        '''
    )

    db.execute(
        '''
        CREATE TABLE IF NOT EXISTS active_chats(
            id INTEGER PRIMARY KEY AUTOINCREMENT, 
            chat_one INT UNIQUE,
            chat_two INT UNIQUE
            )
        '''
    )

    db.execute(
        '''
        CREATE TABLE IF NOT EXISTS users(
            id INTEGER PRIMARY KEY AUTOINCREMENT, 
            user_id INT UNIQUE,
            user_name TEXT,
            gender INT,
            age INT,
            country TEXT,
            balance REAL,
            plan INT,
            msg_counter INT,
            reports INT,
            reg_date INT,
            dialogs INT,
            time_in INT,
            city TEXT
            )
        '''
    )

    db.execute(
        '''
        CREATE TABLE IF NOT EXISTS bills(
            user_id INT PRIMARY KEY,
            bill_id TEXT,
            amount REAL
            )
        '''
    )

    db.execute(
        '''
        CREATE TABLE IF NOT EXISTS stats(
            id INTEGER PRIMARY KEY AUTOINCREMENT, 
            users INT DEFAULT (0),
            blocked INT DEFAULT (0)
            )
        '''
    )

    db.execute(
        '''
        CREATE TABLE IF NOT EXISTS plans(
            id INTEGER PRIMARY KEY AUTOINCREMENT, 
            name TEXT,
            time INT,
            price INT
            )
        '''
    )

    db.execute(
        '''
        CREATE TABLE IF NOT EXISTS ads(
            id INTEGER PRIMARY KEY AUTOINCREMENT, 
            name TEXT,
            time INT,
            url TEXT,
            chat_id INT
            )
        '''
    )

    db.commit()
    logger.info('База данных успешно инициализирована!')


# --- users ---
async def user_exists(user_id: int) -> bool:
    '''
    Проверка на существование пользователя
    в таблице `users`. Вернет True, если пользователь
    существует, либо вернет False, и добавит нового
    пользователя в таблицу
    '''

    data = cur.execute(
        'SELECT * FROM `users` WHERE `user_id` = ?', (user_id,)).fetchone()

    if data:

        return True

    else:
        user_info = await bot.get_chat(user_id)
        date_now = int(time.time())

        t = cur.execute('SELECT `users` FROM `stats`').fetchone()
        t = t[0] + 1
        cur.execute('UPDATE `stats` SET `users` = ?', (t,))
        cur.execute(
            '''
            INSERT OR REPLACE 
            INTO `users`( 
                user_id,
                user_name,
                gender,
                age,
                country,
                balance,
                plan,
                msg_counter,
                reports,
                reg_date,
                dialogs,
                time_in,
                city
                )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''',
            (
                user_id,
                user_info['first_name'],
                None,
                None,
                None,
                0.0,
                0,
                0,
                0,
                date_now,
                0,
                0,
                None
            )
        )

        db.commit()

        return False


async def get_user(user_id) -> bool:
    '''
    Вернет кортеж значений из таблицы `users`,
    либо вернет False, если такого пользователя
    не существует
    '''

    user_exists = cur.execute(
        'SELECT * FROM `users` WHERE `user_id` = ?', (user_id,)).fetchone()

    if not user_exists:
        return False

    return user_exists


async def add_user_info(user_id, country: str, gender: int, age: int):
    '''
    Добавить информацию при регистрации пользователя
    '''

    user_exists = cur.execute(
        'SELECT `user_id` FROM `users` WHERE `user_id` = ?', (user_id,)).fetchone()

    if not user_exists:

        return False

    else:
        cur.execute('UPDATE `users` SET `country` = ?, `gender` = ?, `age` = ? WHERE `user_id` = ?',
                    (country, gender, age, user_id,))
        db.commit()

        return True


async def add_user_stat(user_id, msgs=0, sec=0, reports=0):
    ''''''

    user_exists = cur.execute(
        'SELECT * FROM `users` WHERE `user_id` = ?', (user_id,)).fetchone()

    if not user_exists:
        return False

    msgs = msgs + user_exists[8]
    sec = sec + user_exists[12]
    reports = reports + user_exists[9]
    dialogs = user_exists[11] + 1

    cur.execute('UPDATE `users` SET `msg_counter` = ?, `reports` = ?, `time_in` = ?, `dialogs` = ? WHERE `user_id` = ?',
                (msgs, reports, sec, dialogs, user_id))
    db.commit()

    return True


async def add_user_balance(user_id, sum: int):

    user_exists = cur.execute(
        'SELECT `user_id` FROM `users` WHERE `user_id` = ?', (user_id,)).fetchone()

    if not user_exists:
        return False

    else:
        old_bal = cur.execute(
            'SELECT `balance` FROM `users` WHERE `user_id` = ?', (user_id,)).fetchone()
        old_bal = old_bal[0]
        new_bal = int(old_bal) + sum

        cur.execute(
            'UPDATE `users` SET `balance` = ? WHERE `user_id` = ?', (new_bal, user_id,))
        db.commit()

        return True


async def update_user_sub(user_id, time_sub: int):
    '''
    Добавляет пользователю time_sub дней подписки.
    Вернет False, если пользователя не существует
    '''

    user_exists = cur.execute(
        'SELECT * FROM `users` WHERE `user_id` = ?', (user_id,)).fetchone()

    if not user_exists:
        return False

    time_sub = time_sub * 24 * 60 * 60 + int(time.time())

    cur.execute('UPDATE `users` SET `plan` = ? WHERE `user_id` = ?',
                (time_sub, user_id,))
    db.commit()

    return True


async def user_is_premium(user_id):
    '''
    Вернет кол-во времени до истечения, если подписка еще действует,
    Вернет False, если подписка истекла, или пользователя не существует
    '''

    plan = cur.execute(
        'SELECT `plan` FROM `users` WHERE `user_id` = ?', (user_id,)).fetchone()

    if not plan:
        return False

    if plan[0] > int(time.time()):
        dt = str(datetime.timedelta(seconds=(plan[0]-int(time.time()))))
        dt = dt.replace('days', 'дней')
        dt = dt.replace('day', 'день')

        return dt

    return False


async def get_user_list():
    '''
    Вернет список ID всех зарегистрированных пользователей
    '''

    users = cur.execute('SELECT `user_id` FROM `users`').fetchall()

    return users


# --- pool ---
async def add_queue(user_id: int, gender: int, age: int, country: str) -> bool:
    '''
    Добавить пользователя `user_id` с параметрами в пул ожидания
    '''

    user_exists = cur.execute(
        'SELECT `user_id` FROM `pool` WHERE `user_id` = ?', (user_id,)).fetchone()

    if user_exists:
        return False

    cur.execute('INSERT OR REPLACE INTO `pool`(user_id, gender, age, country) VALUES (?, ?, ?, ?)',
                (user_id, gender, age, country,))
    db.commit()

    return True


async def add_queue_premium(user_id, search_gender=-1, search_age=-1, search_age_2=-1, search_country=None) -> bool:
    '''
    Добавить пользователя `user_id` в премиум пул
    '''

    user_exists = cur.execute(
        'SELECT `user_id` FROM `pool` WHERE `user_id` = ?', (user_id,)).fetchone()

    if user_exists:
        return False

    cur.execute('INSERT OR REPLACE INTO `pool_premium`(user_id, gender, age_1, age_2, country) VALUES (?, ?, ?, ?, ?)',
                (user_id, search_gender, search_age, search_age_2, search_country,))
    db.commit()

    return True


async def get_queue(gender=-1, age='-1:-1', country=None) -> int:
    '''
    Если передать -1, вернет пользователя с любым параметром!
    Вернет int(id) первого пользователя с полом `gender` из пула
    Вернет 0, если список пуст, или пользователя с таким
    полом нет в пуле
    '''

    s_string = 'SELECT `user_id` FROM `pool`'
    counter = 0

    if gender != -1:
        s_string += f' WHERE `gender` = {gender}'
        counter += 1

    if country != None:
        if counter > 0:
            s_string += f' AND `country` = "{country}"'
        else:
            s_string += f' WHERE `country` = "{country}"'
        counter += 1

    if age != '-1:-1':
        age = age.split(':')
        if counter > 0:
            s_string += f' AND (`age` BETWEEN {age[0]} AND {age[1]})'
        else:
            s_string += f' WHERE `age` BETWEEN {age[0]} AND {age[1]}'
        counter += 1

    logger.info(s_string)

    user_exists = cur.execute(s_string).fetchmany(1)
    if not user_exists:
        return 0

    user_exists = user_exists[0]

    return user_exists[0]


async def get_queue_premium(gender: int, age: int, country: str) -> int:
    '''
    '''

    user_id = cur.execute(
        'SELECT `user_id` '
        'FROM `pool_premium` '
        'WHERE `gender` = ? OR `gender` = ? AND (`age_1` <= ? AND `age_2` >= ?) OR `age_1` = ? AND `country` = ? OR `country` = ?',
        (gender, -1, age, age, -1, country, None,)
    ).fetchmany(1)

    if not user_id:
        return 0

    user_id = user_id[0]

    return user_id[0]


async def del_queue(user_id: int) -> bool:
    '''
    Удалить пользователя `user_id` из пула ожидания
    '''

    cur.execute('DELETE FROM `pool` WHERE `user_id` = ?', (user_id,))
    cur.execute('DELETE FROM `pool_premium` WHERE `user_id` = ?', (user_id,))

    db.commit()

    return True


async def del_queue_premium(user_id: int) -> bool:
    '''
    Удалить пользователя `user_id` из пула ожидания
    '''

    user_exists = cur.execute(
        'SELECT `user_id` FROM `pool_premium` WHERE `user_id` = ?', (user_id,)).fetchone()

    if not user_exists:
        return False

    cur.execute('DELETE FROM `pool_premium` WHERE `user_id` = ?', (user_id,))
    db.commit()

    return True


# --- active chats ---
async def create_session(chat_one: int, chat_two: int):
    ''''''

    user_exists = await get_session(chat_one)

    if user_exists == False:

        if chat_two == chat_one:
            return False

        cur.execute(
            'DELETE FROM `active_chats` WHERE `chat_one` = ? OR `chat_two` = ?', (chat_one, chat_one,))
        cur.execute('DELETE FROM `pool` WHERE `user_id` = ?', (chat_two,))
        cur.execute(
            'DELETE FROM `pool_premium` WHERE `user_id` = ?', (chat_two,))
        cur.execute(
            'INSERT OR REPLACE INTO `active_chats`(chat_one, chat_two) VALUES (?, ?)', (chat_one, chat_two,))

        db.commit()

        return True
    else:
        return False


async def del_session(user_id: int):
    ''''''

    data = cur.execute(
        'SELECT * FROM `active_chats` WHERE `chat_one` = ?', (user_id,)).fetchone()

    if not data:
        data = cur.execute(
            'SELECT * FROM `active_chats` WHERE `chat_two` = ?', (user_id,)).fetchone()

    cur.execute(
        'DELETE FROM `active_chats` WHERE `chat_one` = ? OR `chat_two` = ?', (user_id, user_id,))

    db.commit()

    return data


async def get_session(user_id: int):
    ''''''

    data = cur.execute(
        'SELECT * FROM `active_chats` WHERE `chat_one` = ?', (user_id,))

    id_chat = 0
    for row in data:
        id_chat = row[0]
        chat_info = [row[0], row[2]]
    if id_chat == 0:
        data = cur.execute(
            'SELECT * FROM `active_chats` WHERE `chat_two` = ?', (user_id,))

        for row in data:
            id_chat = row[0]
            chat_info = [row[0], row[1]]

        if id_chat == 0:
            return False
        else:
            return chat_info
    else:
        return chat_info


async def session_exists(user_id: int) -> bool:
    data = cur.execute(
        'SELECT * FROM `active_chats` WHERE `chat_one` = ?', (user_id,)).fetchone()
    if data == None:
        data = cur.execute(
            'SELECT * FROM `active_chats` WHERE `chat_two` = ?', (user_id,)).fetchone()
        if data == None:
            return False
        else:
            return True
    else:
        return True


# --- bill ---
async def add_bill(user_id, bill_id, amount: int) -> bool:

    cur.execute('INSERT OR REPLACE INTO `bills` VALUES (?, ?, ?)',
                (user_id, bill_id, amount,))
    db.commit()

    return True


async def del_bill(user_id):

    cur.execute('DELETE FROM `bills` WHERE `user_id` = ?', (user_id,))

    db.commit()


async def get_bill_info(user_id):
    '''
    Возвращает кореж user_id, bill_id, amount, или False
    '''

    user_exists = cur.execute(
        'SELECT * FROM `bills` WHERE `user_id` = ?', (user_id,)).fetchone()

    if user_exists == None:
        return False

    bill_data = cur.execute(
        'SELECT * FROM `bills` WHERE `user_id` = ?', (user_id,)).fetchone()
    db.commit()

    return bill_data


# --- Plans ---
async def get_plans():
    '''
    Получить список всех подписок и информации о них
    '''

    data = cur.execute('SELECT * FROM `plans`').fetchall()

    return data


async def add_plan(name: str, day_time: int = 1, price: int = 0):
    '''
    Добавить новый план
    '''

    if day_time < 1 or price < 0:
        print('SQL add_plan() day_time < 1 or price < 0')
        return False

    data = cur.execute(
        'INSERT OR REPLACE INTO `plans`(name, time, price) VALUES (?, ?, ?)', (name, day_time, price))
    db.commit()

    return data


async def edit_plan(id, name, time, price):
    '''
    Редактировать план
    '''

    data = cur.execute(
        'UPDATE `plans` SET `name` = ?, `time` = ?, `price` = ? WHERE `id` = ?', (name, time, price, id,))
    db.commit()

    return True


async def del_plan(day_time: int):
    '''
    Удалить план с временем подписи day_time
    '''

    cur.execute('DELETE FROM `plans` WHERE `time` = ?', (day_time,))
    db.commit()


# --- STATS ---
async def get_stats():

    count = cur.execute('SELECT * FROM `stats`').fetchone()

    if not count:
        return False

    return count


# --- ADS ---
async def get_ads():
    '''
    Вернет список кортежей всех рекламных записей
    Если список пуст, вернет "None"
    '''

    ads = cur.execute('SELECT * FROM `ads`').fetchall()

    return ads


async def add_ads(name: str, time: int, url: str, chat_id: int) -> bool:
    '''
    Добавить рекламное объявление
    '''

    try:
        cur.execute('INSERT OR IGNORE INTO `ads`(name, time, url, chat_id) VALUES (?, ?, ?, ?)',
                    (name, time, url, chat_id,))

    except Exception as e:
        logger.error(e)

        return False

    db.commit()

    return True


async def remove_ads(id: int) -> bool:
    '''
    Удалить рекламное объявление
    '''

    try:
        cur.execute('DELETE FROM `ads` WHERE `id` = ?', (id,))

    except Exception as e:
        logger.error(e)

        return False

    db.commit()

    return True


async def get_ad_info(id: int):
    '''
    Вернет информацию о рекламной кампании по ее айди, или None
    '''

    company_info = cur.execute(
        'SELECT * FROM `ads` WHERE `id` = ?', (id,)).fetchone()

    return company_info
