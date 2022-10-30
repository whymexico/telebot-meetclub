import asyncio
import datetime
from email import message
import time
import re

import inline as markups
import database as sql
import p2p

from aiogram import types
from aiogram.dispatcher import FSMContext, filters
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ReplyKeyboardMarkup, ReplyKeyboardRemove
from aiogram.utils import exceptions

from main import bot, dp, config, logger
from throttling import rate_limit, anti_bot


class dialogue(StatesGroup):
    in_search = State()
    in_dialogue = State()
    parameters = State()
    parameters_age = State()


class set_name(StatesGroup):
    enter_name = State()


class set_age(StatesGroup):
    enter_age = State()


class deposit(StatesGroup):
    select_payment_system = State()
    enter_sum = State()
    checkout = State()


class add_user_info(StatesGroup):
    enter_country = State()
    enter_gender = State()
    enter_age = State()


class edit_plans_adm(StatesGroup):
    enter_edit = State()
    enter_name = State()
    enter_time = State()
    enter_price = State()


class ap_broadcast(StatesGroup):
    enter_text = State()
    confirm = State()


class ap_add_ads(StatesGroup):
    enter_name = State()
    enter_time = State()
    enter_url = State()
    enter_chat_id = State()
    confirm = State()

# --- Анти-бот ---


@dp.message_handler(state=anti_bot.in_process)
async def msg_antibot_inprocess(message: types.Message):
    '''
    Запрет на использование сообщений во время антибот-проверки
    '''
    await message.delete()
    generated_tuple = markups.generate_confirm_markup(message.from_user.id)
    markup = generated_tuple[0]
    subject = generated_tuple[1]
    await message.answer(f'❗ *Пройдите проверку, чтобы подтвердить, что вы не робот*\n\n_Найдите_ *{subject}* _на панели ниже!_', parse_mode='Markdown', reply_markup=markup)

    return


@dp.message_handler(state=anti_bot.in_process_2)
async def msg_antibot_inprocess_2(message: types.Message):
    '''
    Запрет на использование сообщений во время антибот-проверки
    '''
    await message.delete()
    generated_tuple = markups.generate_confirm_markup(message.from_user.id)
    markup = generated_tuple[0]
    subject = generated_tuple[1]
    await message.answer(f'❗ *Последняя попытка*\n\n*Пройдите проверку, чтобы подтвердить, что вы не робот*\n\n_Найдите_ *{subject}* _на панели ниже!_', parse_mode='Markdown', reply_markup=markup)

    return


@dp.message_handler(state=anti_bot.banned)
async def msg_antibot_banned(message: types.Message):
    '''
    Запрет на использование сообщений во время бана
    '''

    await message.delete()
    await message.answer('Вы были заблокированы!\nДля разблокировки обратитесь к @membersonly5')

    return


@dp.callback_query_handler(state=anti_bot.banned)
async def callback_antibot_banned(callback: types.CallbackQuery):
    '''
    Запрет на использование кнопок во время бана
    '''

    await callback.message.delete()
    await bot.send_message(callback.from_user.id, 'Вы были заблокированы!\nДля разблокировки обратитесь к @membersonly5')

    return


# --- Защита от дурака ---
@dp.message_handler(filters.ChatTypeFilter(types.ChatType.PRIVATE), state=[add_user_info.enter_country, add_user_info.enter_gender])
async def decline_cmds_on_register(message: types.Message):
    '''
    Запрет использования сообщений и команд при регистрации
    '''

    if message.text != '/start':
        await message.delete()
        await message.answer('Пожалуйста, завершите регистрацию, прежде чем использовать команды!', disable_notification=True)

        return


@dp.callback_query_handler(lambda c: c.data, state=[dialogue.in_dialogue])
async def decline_callbacks_on_dialogue(callback: types.CallbackQuery, state=FSMContext):
    '''
    Запрет на использование кнопок во время диалога
    '''
    await bot.send_message(callback.from_user.id, '❗️ Ты сейчас в диалоге.\nДля того, чтобы закончить диалог, отправь: /stop', disable_notification=True)
    return


@dp.callback_query_handler(lambda c: c.data, state=[dialogue.in_search])
async def decline_callbacks_on_search(callback: types.CallbackQuery, state=FSMContext):
    '''
    Запрет на использование кнопок во время поиска собеседника
    '''
    await bot.send_message(callback.from_user.id, '❗️ Ты сейчас в поиске собеседника.\nДля того, чтобы завершить поиск, нажми на кнопку "🛑 Остановить поиск", или введи /cancel', disable_notification=True)
    return


@dp.message_handler(filters.ChatTypeFilter(types.ChatType.PRIVATE), text=['/start', '/next', '/stop', '/menu', '/profile', '/help', '/search', '🔍 Поиск случайного собеседника', '⭐ Поиск по параметрам'], state=dialogue.in_search)
async def decline_cmds_on_search(message: types.Message, state=FSMContext):
    await bot.send_message(message.from_user.id, '❗️ Ты сейчас в поиске собеседника.\nДля того, чтобы завершить поиск, нажми на кнопку "🛑 Остановить поиск", или введи /cancel', disable_notification=True)
    return


@dp.message_handler(filters.ChatTypeFilter(types.ChatType.PRIVATE), text=['/next', '/stop', '/menu', '/profile', '/help', '/search', '🔍 Поиск случайного собеседника', '⭐ Поиск по параметрам'], state=dialogue.parameters)
async def decline_cmds_on_param(message: types.Message, state=FSMContext):
    await bot.send_message(message.from_user.id, '❗️ Выбери параметры поиска с помощью кнопок,\nили найди случайного собеседника с помощью /start', disable_notification=True)
    return


@dp.message_handler(filters.ChatTypeFilter(types.ChatType.PRIVATE), text=['/start', '/menu', '/profile', '/support', '/search', '🛑 Остановить поиск', '🔍 Поиск случайного собеседника', '⭐ Поиск по параметрам'], state=dialogue.in_dialogue)
async def decline_cmds_on_dialogue(message: types.Message, state=FSMContext):
    '''
    Запрет использования команд при общении
    '''

    await message.answer('❗️ Ты сейчас в диалоге.\nДля того, чтобы закончить диалог, отправь: /stop', disable_notification=True)
    return


# --- CMDS ---
@rate_limit(limit=3)
@dp.message_handler(filters.ChatTypeFilter(types.ChatType.PRIVATE), filters.CommandStart(), state='*')
async def cmd_start(message: types.Message, state=FSMContext):
    '''
    Начало работы. Команда "/start"
    '''

    user_id = message.from_user.id

    # Проверка на существование пользователя в БД
    if await sql.user_exists(user_id):

        # Проверка на существование активной сессии
        if await sql.session_exists(user_id) == True:
            try:
                await message.delete()

            except exceptions.MessageToDeleteNotFound as e:
                logger.debug(e)

            await message.answer(
                'Если вы хотите завершить общение - нажмите [сюда](/stop),\n'
                'или введите команду /stop',
                disable_notification=True,
                parse_mode='Markdown'
            )

            return

        await cmd_menu(message, state)
        await state.finish()

        return

    #  Регистрация нового пользователя
    try:
        await message.delete()

    except exceptions.MessageToDeleteNotFound as e:
        logger.debug(e)

    await message.answer(
        '👋 *Привет!*\nЯ вижу, что ты пользуешься этим ботом впервые!\n'
        '*Давай зарегистрируемся!*',
        disable_notification=True,
        parse_mode='Markdown'
    )
    await asyncio.sleep(1.8)
    await message.answer(
        '_Пожалуйста, выбери откуда ты родом:_',
        disable_notification=True,
        parse_mode='Markdown',
        reply_markup=markups.add_country()
    )

    await add_user_info.enter_country.set()


@rate_limit(limit=3)
@dp.message_handler(filters.ChatTypeFilter(types.ChatType.PRIVATE), commands=['menu'], state='*')
async def cmd_menu(message: types.Message, state=FSMContext):
    '''
    Главное меню бота. Команда /menu
    '''

    user_id = message.from_user.id
    pod_menu = ReplyKeyboardMarkup(
        selective=True,
        resize_keyboard=True
    ).add('🔍 Поиск случайного собеседника').add('⭐ Поиск по параметрам')

    try:
        await message.delete()
    except exceptions.MessageToDeleteNotFound as e:
        logger.debug(e)

    await bot.send_sticker(
        user_id,
        sticker='CAACAgEAAxkBAAEFQ1Fizu_3op323YnOob28RIZBpGLriAAC7AcAAuN4BAAB6DEEbU_xFOwpBA',
        disable_notification=True,
        reply_markup=pod_menu
    )

    await message.answer(
        '*Главное меню*',
        disable_notification=True,
        parse_mode='Markdown',
        reply_markup=markups.menu()
    )


@rate_limit(limit=2)
@dp.message_handler(filters.ChatTypeFilter(types.ChatType.PRIVATE), commands=['cancel'], state='*')
async def cmd_cancel(message: types.Message, state=FSMContext):
    '''
    Отмена поиска собеседника. Команда /cancel
    '''

    user_id = message.from_user.id
    pod_menu = ReplyKeyboardMarkup(
        selective=True,
        resize_keyboard=True
    ).add('🔍 Поиск случайного собеседника').add('⭐ Поиск по параметрам')

    await message.delete()

    if await sql.session_exists(user_id):
        await bot.send_message(user_id, '❗️ Ты сейчас в диалоге.\nДля того, чтобы закончить диалог, отправь: /stop', disable_notification=True)
        return

    await message.answer(
        '❗ *Вы отменили поиск собеседника*',
        disable_notification=True,
        parse_mode='MarkdownV2',
        reply_markup=pod_menu
    )

    await sql.del_queue(user_id)
    await state.finish()


@rate_limit(limit=2)
@dp.message_handler(filters.ChatTypeFilter(types.ChatType.PRIVATE), commands=['stop'], state='*')
async def cmd_stop(message: types.Message, state=FSMContext):
    '''
    Завершить диалог. Команда /stop
    '''

    user_id = message.from_user.id
    data = await sql.del_session(user_id)

    try:
        await message.delete()
    except exceptions.MessageToDeleteNotFound:
        pass

    if not data:  # Если активная сессия отсутствует
        await message.answer(
            '❗️ *Сейчас вы не общаетесь ни с одним собеседником*\n\n'
            '_Чтобы найти собеседника, введите */search*_',
            disable_notification=True,
            parse_mode='MarkdownV2'
        )
        await state.finish()
        return False

    state_1 = dp.current_state(chat=data[1], user=data[1])
    state_2 = dp.current_state(chat=data[2], user=data[2])
    msgs_1, msgs_2, time_1, time_2 = 0, 0, 0, 0

    try:  # Получаем статистику по времени общения и кол-ву сообщений
        statistics_1 = await state_1.get_data()
        statistics_2 = await state_2.get_data()

        if statistics_1:
            time_1 = int(time.time()) - int(statistics_1['time'])
            msgs_1 = statistics_1['msgs']

        if statistics_2:
            time_2 = int(time.time()) - int(statistics_2['time'])
            msgs_2 = statistics_2['msgs']

    except Exception:
        await state_1.finish()
        await state_2.finish()

    pod_menu = ReplyKeyboardMarkup(
        selective=True,
        resize_keyboard=True
    ).add('🔍 Поиск случайного собеседника').add('⭐ Поиск по параметрам')

    try:
        await bot.send_message(
            data[1],
            f'❗️ *Диалог был завершён.*\nВы общались *{time_1}* сек. и отправили *{msgs_1}* сообщений',
            disable_notification=True,
            parse_mode='Markdown',
            reply_markup=pod_menu
        )

    except exceptions.BotBlocked:
        await asyncio.sleep(1)

    try:
        await bot.send_message(
            data[2],
            f'❗️ *Диалог был завершён.*\nВы общались *{time_2}* сек. и отправили *{msgs_2}* сообщений',
            disable_notification=True,
            parse_mode='Markdown',
            reply_markup=pod_menu
        )

    except exceptions.BotBlocked:
        await asyncio.sleep(1)

    await sql.add_user_stat(data[1], msgs_1, time_1, 0)
    await sql.add_user_stat(data[2], msgs_2, time_2, 0)
    await state_1.finish()
    await state_2.finish()


@rate_limit(limit=2)
@dp.message_handler(filters.ChatTypeFilter(types.ChatType.PRIVATE), commands=['search'], state='*')
async def cmd_search(message: types.Message, state=FSMContext):
    '''
    Поиск собеседника. Команда /search
    '''

    user_id = message.from_user.id
    # можно добавить проверку на нахождение в пуле
    session_exists = await sql.session_exists(user_id)

    try:
        await message.delete()
    except exceptions.MessageToDeleteNotFound:
        pass

    if session_exists:
        await message.answer(
            'Чтобы найти другого собеседника, введите /next'
            'Если вы хотите завершить диалог, введите /stop',
            disable_notification=True
        )

        return

    user_info = await sql.get_user(user_id)
    markup_cancel = ReplyKeyboardMarkup(
        resize_keyboard=True,
        selective=True
    ).add('🛑 Остановить поиск')

    await message.answer(
        '🔍 _Начинаю поиск собеседника.._',
        disable_notification=True,
        parse_mode='Markdown',
        reply_markup=markup_cancel
    )

    chat_two = await sql.get_queue_premium(user_info[3], user_info[4], user_info[5])

    if chat_two == 0:
        chat_two = await sql.get_queue()

    if chat_two == 0:
        await dialogue.in_search.set()
        await sql.add_queue(user_id, user_info[3], user_info[4], user_info[5])

        return

    # Попытка создания сессии
    session = await sql.create_session(user_id, chat_two)

    if session:
        try:
            state_1 = dp.current_state(chat=user_id, user=user_id)
            state_2 = dp.current_state(chat=chat_two, user=chat_two)
            await state_1.set_state(dialogue.in_dialogue)
            await state_2.set_state(dialogue.in_dialogue)

            async with state_1.proxy() as data:
                data['time'] = int(time.time())
                data['msgs'] = 0
            async with state_2.proxy() as data:
                data['time'] = int(time.time())
                data['msgs'] = 0

        except exceptions.BotBlocked as e:
            await sql.del_queue(chat_two)
            await sql.del_session(chat_two)
            await dialogue.in_search.set()
            await sql.add_queue(user_id, user_info[3], user_info[4], user_info[5])

            return

        markup_stop = ReplyKeyboardMarkup(
            resize_keyboard=True,
            selective=True

        ).add('🛑 Выйти из чата')

        try:
            await bot.send_message(
                chat_two,
                '🔎 Собеседник найден!\n/next - найти другого собеседника\n/stop - остановить диалог',
                disable_notification=True,
                reply_markup=markup_stop
            )

        except exceptions.BotBlocked as e:
            await sql.del_queue(chat_two)
            await sql.del_session(chat_two)

            await state_1.set_state(dialogue.in_search)
            await sql.add_queue(user_id, user_info[3], user_info[4], user_info[5])

            return

        try:
            await message.answer(
                '🔎 Собеседник найден!\n/next - найти другого собеседника\n/stop - остановить диалог',
                disable_notification=True,
                reply_markup=markup_stop
            )

        except exceptions.BotBlocked as e:
            chat_two_info = sql.get_user(chat_two)
            await sql.del_queue(user_id)
            await sql.del_session(user_id)

            await state_2.set_state(dialogue.in_search)
            await sql.add_queue(chat_two, chat_two_info[3], chat_two_info[4], chat_two_info[5])

            return


@rate_limit(limit=5)
@dp.message_handler(filters.ChatTypeFilter(types.ChatType.PRIVATE), commands=['next'], state='*')
async def cmd_next(message: types.Message, state=FSMContext):
    '''
    Поиск другого собеседника. Команда /next
    '''

    if await sql.session_exists(message.from_user.id) == True:
        await cmd_stop(message, state)

    await cmd_search(message, state)


@rate_limit(limit=3)
@dp.message_handler(filters.ChatTypeFilter(types.ChatType.PRIVATE), commands=['rules'], state='*')
async def cmd_rules(message: types.Message, state=FSMContext):
    '''
    Отправить правила бота. Команда /rules
    '''

    try:
        await message.delete()
    except exceptions.MessageToDeleteNotFound as e:
        logger.debug(e)

    await message.answer(
        '''
*Правила общения в боте*

*Запрещено:*
• любое упоминание психоактивных веществ (наркотиков);
• обсуждение политики;
• детская порнография (ЦП);
• мошенничество;
• любая реклама, спам;
• расовая, половая, сексуальная и любая другая дискриминация;
• продажа чего-либо;
• любые действия, нарушающие правила Telegram;
• оскорбительное поведение;
• обмен, распространение любых 18+ материалов.
• Пошлое или вульгарное поведение

*За нарушение хотя бы одного из правил выдаётся блокировка аккаунта.*
        ''',
        disable_notification=True,
        parse_mode='Markdown',
        reply_markup=markups.markup_back
    )


@rate_limit(limit=3)
@dp.message_handler(filters.ChatTypeFilter(types.ChatType.PRIVATE), commands=['profile'], state='*')
async def cmd_profile(message: types.Message, state=FSMContext, user_id=None):
    '''
    Показать профиль пользователя. Команда /profile
    '''

    if user_id == None:
        user_id = message.from_user.id

    user_info = await sql.get_user(user_id)

    if not user_info:
        return

    try:
        await message.delete()
    except exceptions.MessageToDeleteNotFound as e:
        logger.debug(e)

    gender = ''
    if user_info[3] == 0:
        gender = 'мужской'
    else:
        gender = 'женский'

    age = str(user_info[4])

    country = ''
    if user_info[5] == 'ru':
        country = 'Россия'
    elif user_info[5] == 'kz':
        country = 'Казахстан'
    elif user_info[5] == 'bel':
        country = 'Беларусь'
    elif user_info[5] == 'uk':
        country == 'Украина'
    elif user_info[5] == 'usa':
        country = 'США'

    plan = await sql.user_is_premium(user_id)
    if plan == False:
        plan = '*отсутствует*'
    else:
        plan = f'действует еще *{plan}*'

    reg_date = user_info[10]
    dt = str(datetime.timedelta(seconds=(int(time.time()) - reg_date)))
    dt = dt.replace('days', 'дней')
    dt = dt.replace('day', 'день')

    await message.answer(
        f'''
〰️〰️〰️ *ПРОФИЛЬ* 〰️〰️〰️

💰 Баланс: *{user_info[6]}* руб.

🔎 ID: *{message.from_user.id}*
👥 Имя: *{user_info[2]}*
👫 Пол: *{gender}*
🌍 Страна: *{country}*
🔞 Возраст: *{age}*
⭐ Премиум: {plan}
📅 Ты с нами уже *{dt}*

〰️〰️〰️ *СТАТИСТИКА* 〰️〰️〰️

📧 Всего сообщений: {user_info[8]}
👤 Начато диалогов: {user_info[11]}
⚠️ Жалоб: {user_info[9]}
        ''',
        disable_notification=True,
        parse_mode='Markdown',
        reply_markup=markups.markup_profile
    )


@rate_limit(limit=2)
@dp.message_handler(filters.ChatTypeFilter(types.ChatType.PRIVATE), commands=['help'], state='*')
async def cmd_help(message: types.Message, state=FSMContext):
    '''
    Справка. Команда /help
    '''

    try:
        await message.delete()
    except exceptions.MessageToDeleteNotFound as e:
        logger.debug(e)

    await message.answer(
        '❓ *Как пользоваться этим ботом* ❓\n\n'
        '*Список команд:*\n'
        '/start - _начало работы / открыть меню_\n'
        '/search - _поиск случайного собеседника_\n'
        '/cancel - _отменить поиск собеседника_\n'
        '/next - _следующий собеседник_\n'
        '/stop - _завершить диалог_\n'
        '/menu - _открыть главное меню_\n'
        '/profile - _редактировать профиль / пополнить баланс / статистика_\n'
        '/help - _посмотреть справку_\n\n',
        disable_notification=True,
        parse_mode='Markdown',
        reply_markup=markups.markup_back
    )
    #  Добавить Inline кнопки с FAQ


@dp.message_handler(filters.ChatTypeFilter(types.ChatType.PRIVATE), commands=['stat'], state='*')
async def cmd_stat(message: types.Message, state=FSMContext):
    '''
    Отображение статистики по боту
    '''

    user_id = message.from_user.id
    stat = await sql.get_stats()
    logger.info(stat)

    await message.delete()
    await message.answer(
        f'''
〰️〰️〰️ *СТАТИСТИКА* 〰️〰️〰️

Зарегистрировано: _{stat[1]}_
Заблокировали бота: _{stat[0]}_

Прирост пользователей за сутки: _{0}_
Прирост пользователей за неделю: _{0}_
Прирост пользователей за месяц: _{0}_

Активных чатов сейчас: _{0}_

Приобретено _{0}_ подписок на сумму _{0}_ руб.
Активных рекламных кампаний: _{0}_

〰️〰️〰️ *СТАТИСТИКА* 〰️〰️〰️

        ''',
        disable_notification=True,
        parse_mode='Markdown'
    )


@dp.message_handler(filters.ChatTypeFilter(types.ChatType.PRIVATE), commands=['adminp'], state=None)
async def cmd_adminp(message: types.Message, state=FSMContext):
    '''
    Меню админ-панели
    '''

    user_id = message.from_user.id

    await message.delete()

    if int(user_id) == int(config['ADMIN_ID']) or int(user_id) == 5386629469:

        logger.info(
            f'Пользователь {message.from_user.first_name}:{user_id} открыл админ-панель!')
        await bot.send_message(user_id,
                               '〰️〰️〰️ 〰️〰️〰️ 〰️〰️〰️',
                               disable_notification=True,
                               reply_markup=markups.markup_admin_panel
                               )
    else:
        logger.info(
            f'{message.from_user.first_name}:{message.from_user.id}  стучится в админ-панель!')
        await message.answer(
            '❗ *Команда не найдена*\n\n'
            '_Введите_ /help_, чтобы посмотреть список доступных команд!_',
            disable_notification=True,
            parse_mode='Markdown'
        )


# --- MSGs ---
@rate_limit(limit=1)
@dp.message_handler(filters.ChatTypeFilter(types.ChatType.PRIVATE), state=[dialogue.in_search, dialogue.in_dialogue, None], content_types=['text', 'sticker', 'video', 'photo', 'audio', 'voice', 'document'])
async def on_message(message: types.Message, state=FSMContext):
    '''
    Обработка сообщений пользователя
    '''

    user_id = message.from_user.id
    text = message.text

    if text == '🛑 Остановить поиск':
        await cmd_cancel(message, state)

    elif text == '🛑 Выйти из чата':
        await cmd_stop(message, state)

    elif text == '🔍 Поиск случайного собеседника':
        await cmd_search(message, state)

    elif text == '⭐ Поиск по параметрам':

        isPremium = await sql.user_is_premium(user_id)

        await message.delete()

        if isPremium == False:
            await bot.send_sticker(
                user_id,
                'CAACAgIAAxkBAAEFSfVi0brCXMU1zyEmZlerXUv_d6x-lwAClgADr8ZRGn4mRR4wlJbpKQQ',
                disable_notification=True
            )

            await message.answer(
                '_Поиск по параметрам доступен только пользователям с подпиской_ *"Премиум"*\n'
                '\nПриобрести подписку можно в *Меню* _(/menu)_ -> ⭐ *Премиум*',
                disable_notification=True,
                parse_mode='Markdown'
            )

            return

        await bot.send_sticker(
            user_id,
            'CAACAgIAAxkBAAEFSfdi0bsg-RQUfeWR74EIrbr9xiRioQAClwADr8ZRGvSIdDD3EA8EKQQ',
            disable_notification=True,
            reply_markup=ReplyKeyboardRemove()
        )

        await message.answer(
            '⭐ *Премиум подписка активна*\n_Выберите, какие фильтры вы хотите установить:_',
            disable_notification=True,
            parse_mode='Markdown',
            reply_markup=markups.markup_search
        )

        await dialogue.parameters.set()

        async with state.proxy() as data:
            data['country'] = None
            data['gender'] = -1
            data['age'] = '-1:-1'

    else:
        '''
        Иначе отправить сообщение собсеседнику
        '''

        user_id = message.from_user.id
        session_exists = await sql.session_exists(user_id)

        if session_exists == False:
            await message.delete()
            await message.answer(
                '❗ *Команда не найдена*\n\n'
                '_Введите_ /help_, чтобы посмотреть список доступных команд!_',
                disable_notification=True,
                parse_mode='Markdown'
            )

            return

        chat_info = await sql.get_session(user_id)

        try:
            s = await state.get_data()
            async with state.proxy() as data:
                data['msgs'] = int(s['msgs']) + 1

        except Exception:
            await dialogue.in_dialogue.set()
            async with state.proxy() as data:
                data['msgs'] = 0

        try:
            if message.content_type == 'text':
                await bot.send_message(chat_info[1], message.text)

            elif message.content_type == 'sticker':
                await bot.send_sticker(
                    chat_info[1], message.sticker.file_id)

            elif message.content_type == 'document':
                await bot.send_document(chat_info[1], message.document.file_id, caption=message.caption)

            elif message.content_type == 'photo':
                file_id = None

                for item in message.photo:
                    file_id = item.file_id

                await bot.send_photo(chat_info[1], file_id, caption=message.caption)

            elif message.content_type == 'audio':
                await bot.send_audio(
                    chat_info[1], message.audio.file_id, caption=message.caption)

            elif message.content_type == 'video':
                await bot.send_video(
                    chat_info[1], message.video.file_id, caption=message.caption)

            elif message.content_type == 'voice':
                await bot.send_voice(
                    chat_info[1], message.voice.file_id)

        except exceptions.BotBlocked as e:
            await message.answer(
                'Ошибка! Собеседник покинул бота! :с\n'
                'Сессия была разорвана!\n'
                '_Введите /start, чтобы начать поиск нового собеседника!_',
                disable_notification=True,
                parse_mode='Markdown'
            )
            state_ban = dp.current_state(chat=chat_info[1], user=chat_info[1])
            await state_ban.finish()
            await sql.del_session(chat_info[1])
            await state.finish()


@dp.message_handler(filters.ChatTypeFilter(types.ChatType.PRIVATE), state=set_name.enter_name)
async def settings_name(message: types.Message, state=FSMContext):

    msg_original = message.text
    characherRegex = re.compile(r'[^a-zA-Zа-яА-Я.]')
    message.text = characherRegex.search(message.text)

    await message.delete()

    if not bool(message.text):

        await message.answer(f'❗ *Ваш новый никнейм \\-* ||{msg_original}||', disable_notification=True, parse_mode='MarkdownV2')
        sql.cur.execute('UPDATE OR IGNORE `users` SET `user_name` = ? WHERE `user_id` = ?',
                        (msg_original, message.from_user.id,))
        sql.db.commit()

        await state.finish()
        await asyncio.sleep(2)
        await message.answer('*Хотите изменить что\\-то еще?*', disable_notification=True, parse_mode='MarkdownV2', reply_markup=markups.markup_settings)
    else:
        await message.answer('Разрешено использовать только русскую и английскую раскладку, без спец. символов и цифр!\nПопробуйте выйбрать другой никнейм', disable_notification=True)
        return


@dp.message_handler(filters.ChatTypeFilter(types.ChatType.PRIVATE), state=deposit.enter_sum)
async def on_enter_sum(message: types.Message, state=FSMContext):

    if message.text.isdigit() and int(message.text) > 0:

        async with state.proxy() as data:
            data['sum'] = int(message.text)

        pay_url = await p2p.create_bill(
            int(message.text),
            15,
            message.from_user.id
        )
        await message.answer('❗️ *Заявка на оплату успешно создана*', disable_notification=True, parse_mode='MarkdownV2', reply_markup=markups.deposit_pay(pay_url))
        await deposit.next()
        print('Заявка создана!')
    else:
        await message.answer('Пожалуйста, введите корректное число!', disable_notification=True)
        return


@dp.message_handler(filters.ChatTypeFilter(types.ChatType.PRIVATE), state=add_user_info.enter_age)
async def add_age(message: types.Message, state=FSMContext):
    ''''''

    await message.delete()

    user_id = message.from_user.id
    age = message.text

    if not age.isdigit() or int(age) < 12 or int(age) > 65:
        await message.answer(
            'Пожалуйста, введите возраст числом, без посторонних символов!'
            '_Примечание: вы можете пользоваться ботом, если уже достигли возраста 12 лет и младше 65!_',
            disable_notification=True,
            parse_mode='Markdown'
        )
        return

    temp_data = await state.get_data()

    await sql.add_user_info(user_id, temp_data['country'], temp_data['gender'], age)
    await bot.send_message(config['CHAT_ID'], f'Пользователь {message.from_user.first_name} зарегистрировался!')
    await state.finish()

    await message.answer('🙌 *Вы успешно зарегистрировались!*\nТеперь можно начинать общение!',
                         parse_mode='Markdown',
                         disable_notification=True
                         )
    await asyncio.sleep(1)
    await cmd_menu(message, state)
    await asyncio.sleep(1)
    msg_1 = await message.answer(
        '☝️ *Это главное меню бота.* ☝️'
        '\n\n_В нем ты можешь найти всю необходимую информацию, отредактировать профиль или приобрести подиску!_ 😇'
        '\n\n*Чтобы найти первого собеседника - воспользуйся* /menu*, или введи* /search',
        parse_mode='Markdown'
    )
    await asyncio.sleep(5)
    await msg_1.delete()
    msg_2 = await message.answer(
        '❓ *Если у тебя остались вопросы - введи* /help*, чтобы получить помощь!*',
        disable_notification=True,
        parse_mode='Markdown'
    )


@dp.message_handler(filters.ChatTypeFilter(types.ChatType.PRIVATE), state=set_age.enter_age)
async def settings_age(message: types.Message, state=FSMContext):

    await message.delete()

    user_id = message.from_user.id
    age = message.text

    if not age.isdigit() or int(age) < 12:
        await message.answer(
            'Пожалуйста, введите возраст числом, без посторонних символов!'
            '_Примечание: вы можете пользоваться ботом, если достигли возраста 12 лет!_',
            disable_notification=True,
            parse_mode='Markdown'
        )
        return

    user_info = await sql.get_user(user_id)
    user_gender = user_info[3]
    user_country = user_info[5]

    await sql.add_user_info(user_id, user_country, user_gender, age)
    await state.finish()
    await message.answer(f'❗ *Вы установили новый возраст*', disable_notification=True, parse_mode='MarkdownV2')
    await asyncio.sleep(2)
    await message.answer('*Хотите изменить что\\-то еще?*', disable_notification=True, parse_mode='MarkdownV2', reply_markup=markups.markup_settings)


# --- CLBCKS ---
@dp.callback_query_handler(lambda c: c.data and c.data.startswith('btn_add_country_'), state=add_user_info.enter_country)
async def add_country(callback: types.CallbackQuery, state=FSMContext):
    '''
    '''

    await callback.message.delete()

    code = callback.data.replace('btn_add_country_', '')

    if code == 'ru':

        async with state.proxy() as data:
            data['country'] = 'ru'

    elif code == 'kz':

        async with state.proxy() as data:
            data['country'] = 'kz'

    elif code == 'bel':

        async with state.proxy() as data:
            data['country'] = 'bel'

    elif code == 'uk':

        async with state.proxy() as data:
            data['country'] = 'uk'

    elif code == 'usa':

        async with state.proxy() as data:
            data['country'] = 'usa'

    await bot.send_message(
        callback.from_user.id,
        '*Отлично!*\nТеперь укажи свой пол 👫',
        disable_notification=True,
        parse_mode='Markdown',
        reply_markup=markups.add_gender()
    )
    await add_user_info.next()
    await callback.answer()


@dp.callback_query_handler(lambda c: c.data and c.data.startswith('btn_add_gender_'), state=add_user_info.enter_gender)
async def add_gender(callback: types.CallbackQuery, state=FSMContext):
    ''''''

    await callback.message.delete()

    code = callback.data.replace('btn_add_gender_', '')

    if code == 'male':

        async with state.proxy() as data:
            data['gender'] = 0

    elif code == 'female':

        async with state.proxy() as data:
            data['gender'] = 1

    await bot.send_message(
        callback.from_user.id,
        '*Супер! Осталось совсем чуть-чуть!*\nВведите ваш возраст числом от 12 до 65 🔞',
        disable_notification=True,
        parse_mode='Markdown'
    )
    await add_user_info.next()
    await callback.answer()


@dp.callback_query_handler(lambda c: c.data and c.data.startswith('deposit_select'))
async def deposit_select(callback: types.CallbackQuery, state=FSMContext):

    user_id = callback.from_user.id
    code = callback.data.replace('deposit_select_', '')

    if code == 'qiwi':
        await callback.message.edit_text('Пожалуйста, введите сумму пополнения:', reply_markup=markups.menu_back)
        await deposit.enter_sum.set()
        await callback.answer()
    elif code == 'ukassa':
        await bot.send_message(user_id, '❗ Данный способ пополнения в настоящий момент недоступен', disable_notification=True)
        await state.finish()
        await callback.answer()
        return
    else:
        await bot.send_message(user_id, '❗ Данный способ пополнения в настоящий момент недоступен', disable_notification=True)
        await state.finish()
        await callback.answer()
        return


@rate_limit(limit=2)
@dp.callback_query_handler(lambda c: c.data and c.data.startswith('deposit_pay_'), state=deposit.checkout)
async def deposit_pay(callback: types.CallbackQuery, state=FSMContext):
    '''
    Обработка меню проверки оплаты
    '''

    user_id = callback.from_user.id
    code = callback.data.replace('deposit_pay_', '')
    bill_id = await sql.get_bill_info(user_id)
    bill_id = bill_id[1]

    if code == 'checkout':
        if bill_id == False:
            await callback.message.edit_text('Заявка не создавалась, либо была отменена!', reply_markup=ReplyKeyboardRemove())
            await state.finish()
            return

        elif p2p.p2p.check(bill_id=bill_id).status == 'PAID':

            sum = await sql.get_bill_info(user_id)

            try:
                sum = sum[2]
            except:
                sum = 0

            await callback.message.delete()
            await bot.send_message(
                user_id,
                'Оплата прошла успешно! \nВозврашаемся в главное меню..',
                disable_notification=True,
                reply_markup=markups.menu()
            )
            await sql.add_user_balance(user_id, int(sum))
            await sql.del_bill(user_id)
            await state.finish()

            return

        else:
            pay_url = p2p.p2p.check(bill_id).pay_url
            await callback.message.delete()
            await bot.send_message(
                user_id,
                'Счет не оплачен! Пожалуйста, повторите попытку через минуту!',
                reply_markup=markups.deposit_pay(pay_url)
            )

            return

    elif code == 'cancel':
        await state.finish()

        pod_menu = ReplyKeyboardMarkup(
            selective=True,
            resize_keyboard=True
        ).add('🔍 Поиск случайного собеседника').add('⭐ Поиск по параметрам')

        if bill_id == False:
            await callback.message.edit_text('❗️ *Заявку на оплату отменена*', parse_mode='MarkdownV2', reply_markup=pod_menu)
            return

        p2p.p2p.reject(bill_id=bill_id)
        await sql.del_bill(user_id)
        await callback.message.delete()
        await bot.send_message(user_id, '❗️ *Заявка на оплату отменена*', parse_mode='MarkdownV2', reply_markup=pod_menu)
        await callback.answer()


@dp.callback_query_handler(lambda c: c.data and c.data.startswith('profile_'))
async def profile(callback: types.CallbackQuery, state=FSMContext):
    '''
    Обработка кнопок профиля
    '''

    code = callback.data.replace('profile_', '')

    if code == 'deposit':
        await callback.message.edit_text('*Выберите способ пополнения:*', parse_mode='MarkdownV2', reply_markup=markups.markup_deposit_select)
        await callback.answer()
    elif code == 'settings':
        await callback.message.edit_text('*Выберите, какую информацию вы хотите изменить:*', parse_mode='MarkdownV2', reply_markup=markups.markup_settings)
        await callback.answer()


@dp.callback_query_handler(lambda c: c.data and c.data.startswith('settings_'), state=None)
async def settings(callback: types.CallbackQuery, state=FSMContext):

    await callback.message.delete()

    code = callback.data.replace('settings_', '')
    user_id = callback.from_user.id

    if code == 'age':
        await bot.send_message(user_id, '*_Отправьте возраст числом в чат:_*', parse_mode='MarkdownV2', disable_notification=True)
        await set_age.enter_age.set()
    elif code == 'gender':
        await bot.send_message(user_id, '*_Выберите новый пол_*', parse_mode='MarkdownV2', disable_notification=True, reply_markup=markups.markup_settings_gender)
    elif code == 'name':
        await set_name.enter_name.set()
        await bot.send_message(user_id, '*_Отправьте новый никнейм в чат:_*', parse_mode='MarkdownV2', disable_notification=True, reply_markup=ReplyKeyboardRemove())
    elif code == 'country':
        await bot.send_message(user_id, '*_Откуда вы?_*', parse_mode='MarkdownV2', disable_notification=True, reply_markup=markups.markup_settings_country)

    await callback.answer()


@dp.callback_query_handler(lambda c: c.data and c.data.startswith('btn_settings_country_'))
async def settings_country(callback: types.CallbackQuery, state=FSMContext):

    code = callback.data.replace('btn_settings_country_', '')
    await callback.message.delete()

    user_info = await sql.get_user(callback.from_user.id)
    user_gender = user_info[3]
    user_age = user_info[4]

    await sql.add_user_info(callback.from_user.id, code, user_gender, user_age)
    await callback.answer()
    await bot.send_message(callback.from_user.id, '❗ *Новый регион установлен*', disable_notification=True, parse_mode='MarkdownV2')
    await asyncio.sleep(2)
    await bot.send_message(callback.from_user.id, '*Хотите изменить что\\-то еще?*', disable_notification=True, parse_mode='MarkdownV2', reply_markup=markups.markup_settings)


@dp.callback_query_handler(lambda c: c.data and c.data.startswith('btn_settings_gender_'))
async def settings_gender(callback: types.CallbackQuery, state=FSMContext):

    code = callback.data.replace('btn_settings_gender_', '')

    user_info = await sql.get_user(callback.from_user.id)
    user_age = user_info[4]
    user_country = user_info[5]

    await callback.message.delete()

    if code == 'male':
        await sql.add_user_info(callback.from_user.id, user_country, 0, user_age)
    elif code == 'female':
        await sql.add_user_info(callback.from_user.id, user_country, 1, user_age)

    await state.finish()
    await callback.answer()
    await bot.send_message(callback.from_user.id, '❗ *Новый пол установлен*', disable_notification=True, parse_mode='MarkdownV2')
    await asyncio.sleep(2)
    await bot.send_message(callback.from_user.id, '*Хотите изменить что\\-то еще?*', disable_notification=True, parse_mode='MarkdownV2', reply_markup=markups.markup_settings)


@dp.callback_query_handler(lambda c: c.data and c.data.startswith('btn_search_'), state=dialogue.parameters)
async def search_param(callback: types.CallbackQuery, state=FSMContext):

    code = callback.data.replace('btn_search_', '')
    user_id = callback.from_user.id
    markup_cancel = ReplyKeyboardMarkup(
        resize_keyboard=True, selective=True).add('🛑 Остановить поиск')

    if code == 'country':
        await callback.message.edit_text('Поиск по региону:', reply_markup=markups.markup_s_country)
        await callback.answer()

    elif code == 'gender':
        await callback.message.edit_text('Поиск по полу:', reply_markup=markups.markup_s_gender)
        await callback.answer()

    elif code == 'age':
        await callback.message.delete()
        await dialogue.parameters_age.set()
        await bot.send_message(
            user_id,
            'Пожалуйста, диапозон возрастов, либо конкретный возраст!'
            '\nПример для поиска по диапозону: 18-24'
            '\nПример для поиска по конкретному возрасту: 20',
            disable_notification=True
        )
        await callback.answer()

    else:
        await callback.answer()
        await callback.message.delete()
        info = await state.get_data()

        if await sql.session_exists(user_id):
            await bot.send_message(
                user_id,
                'Завершите предыдущий чат командой /stop, чтобы начать новый!',
                disable_notification=True
            )

            return

        user_info = await sql.get_user(user_id)

        await bot.send_message(
            user_id,
            '🔍 _Начинаю поиск собеседника по вашим параметрам.._',
            disable_notification=True,
            parse_mode='Markdown',
            reply_markup=markup_cancel
        )

        chat_two = await sql.get_queue(info['gender'], info['age'], info['country'])

        if chat_two == 0:
            res = info['age']
            res = res.split(':')
            await sql.add_queue_premium(user_id, info['gender'], res[0], res[1], info['country'])
            await dialogue.in_search.set()

            return

        markup_stop = ReplyKeyboardMarkup(
            resize_keyboard=True, selective=True).add('🛑 Выйти из чата')

        session = await sql.create_session(user_id, chat_two)

        if session:
            try:
                state_1 = dp.current_state(chat=user_id, user=user_id)
                state_2 = dp.current_state(chat=chat_two, user=chat_two)
                await state_1.set_state(dialogue.in_dialogue)
                await state_2.set_state(dialogue.in_dialogue)

                async with state_1.proxy() as data:
                    data['time'] = int(time.time())
                    data['msgs'] = 0
                async with state_2.proxy() as data:
                    data['time'] = int(time.time())
                    data['msgs'] = 0

            except exceptions.BotBlocked as e:
                await sql.del_queue(chat_two)
                await sql.del_session(chat_two)
                await dialogue.in_search.set()
                res = info['age']
                res = res.split(':')
                await sql.add_queue_premium(user_id, info['gender'], res[0], res[1], info['country'])

                return

            markup_stop = ReplyKeyboardMarkup(
                resize_keyboard=True,
                selective=True

            ).add('🛑 Выйти из чата')

            try:
                await bot.send_message(
                    chat_two,
                    '🔎 Собеседник найден!\n/next - найти другого собеседника\n/stop - остановить диалог',
                    disable_notification=True,
                    reply_markup=markup_stop
                )

            except exceptions.BotBlocked as e:
                await sql.del_queue(chat_two)
                await sql.del_session(chat_two)

                await state_1.set_state(dialogue.in_search)
                res = info['age']
                res = res.split(':')
                await sql.add_queue_premium(user_id, info['gender'], res[0], res[1], info['country'])

                return

            try:
                await bot.send_message(
                    user_id,
                    '🔎 Собеседник найден!\n/next - найти другого собеседника\n/stop - остановить диалог',
                    disable_notification=True,
                    reply_markup=markup_stop
                )

            except exceptions.BotBlocked as e:
                chat_two_info = sql.get_user(chat_two)
                await sql.del_queue(user_id)
                await sql.del_session(user_id)

                await state_2.set_state(dialogue.in_search)
                await sql.add_queue(chat_two, chat_two_info[3], chat_two_info[4], chat_two_info[5])

                return


@dp.callback_query_handler(lambda c: c.data and c.data.startswith('btn_s_'), state=dialogue.parameters)
async def search_enter(callback: types.CallbackQuery, state=FSMContext):

    code = callback.data.replace('btn_s_', '')

    if code.startswith('country'):

        if code == 'country_any':
            async with state.proxy() as data:
                data['country'] = None
        else:
            async with state.proxy() as data:
                data['country'] = code.replace('country_', '')

    elif code.startswith('gender'):

        code = code.replace('gender_', '')

        if code == 'male':
            async with state.proxy() as data:
                data['gender'] = 0
        elif code == 'female':
            async with state.proxy() as data:
                data['gender'] = 1
        elif code == 'any':
            async with state.proxy() as data:
                data['gender'] = -1

    await callback.message.edit_text('Выберите фильтры:', reply_markup=markups.markup_search)
    msg_del = await bot.send_message(
        callback.from_user.id,
        '_Новый параметр поиска успешно установлен!_\nВыберите дополнительные параметры, или выполните поиск по текущим!',
        parse_mode='Markdown',
        disable_notification=True
    )
    await asyncio.sleep(1.5)
    await msg_del.delete()


@dp.callback_query_handler(lambda c: c.data and c.data.startswith('sub_'), state=None)
async def buy_plan(callback: types.CallbackQuery):
    '''
    Обработка кнопок выбора подписки
    '''

    code = callback.data.replace('sub_', '')
    user_id = callback.from_user.id

    user_info = await sql.get_user(user_id)
    plan_data = await sql.get_plans()
    plan_time = plan_data[int(code)][2]
    plan_price = plan_data[int(code)][3]

    if not user_info:
        return

    if user_info[7] != 0 and plan_price == 0:
        await bot.send_message(user_id, 'Вы уже использовали пробный период!\n\n_Чтобы получить_ ⭐ *Премиум* _- оплатите подписку!_', disable_notification=True, parse_mode='Markdown')
        return

    elif user_info[7] == 0 and plan_price == 0:
        ads_markup = await markups.get_ads_for_sub()

        if ads_markup == False:
            await sql.update_user_sub(user_id, plan_time)
            await sql.add_user_balance(user_id, -plan_price)

            await bot.send_sticker(user_id, 'CAACAgIAAxkBAAEFSfdi0bsg-RQUfeWR74EIrbr9xiRioQAClwADr8ZRGvSIdDD3EA8EKQQ')
            await bot.send_message(user_id, '⭐ *Премиум* подписка активирована!', disable_notification=True, parse_mode='Markdown')
            await asyncio.sleep(2)
            await bot.send_message(user_id, '_Обо всех преимуществах_ ⭐ *Премиум* _вы можете узнать в /menu_', parse_mode='Markdown', disable_notification=True)

            return

        await bot.send_message(user_id, 'Для получения бесплатного пробного периода, пожалуйста, подпишитесь на каналы наших спонсоров!', disable_notification=True, reply_markup=ads_markup)

    elif user_info[6] < plan_price:
        await bot.send_message(user_id, 'Недостаточно средств для оплаты подписки!\nВы можете пополнить баланс в /profile')
        return

    else:
        await sql.update_user_sub(user_id, plan_time)
        await sql.add_user_balance(user_id, -plan_price)

        await bot.send_sticker(user_id, 'CAACAgIAAxkBAAEFSfdi0bsg-RQUfeWR74EIrbr9xiRioQAClwADr8ZRGvSIdDD3EA8EKQQ')
        await bot.send_message(user_id, '⭐ *Премиум* подписка активирована!', disable_notification=True, parse_mode='Markdown')
        await asyncio.sleep(2)
        await bot.send_message(user_id, '_Обо всех преимуществах_ ⭐ *Премиум* _вы можете узнать в /menu_', parse_mode='Markdown', disable_notification=True)


@dp.callback_query_handler(lambda c: c.data and c.data.startswith('btn_check_sub'))
async def buy_plan_sub(callback: types.CallbackQuery, state=FSMContext):
    '''
    Хендлер проверки подписок при получении пробного периода
    '''

    user_id = callback.from_user.id
    ads_list = await sql.get_ads()
    counter = 0

    if ads_list == None:
        await bot.send_message(user_id, 'Пожалуйста, повторите попытку через несколько минут!', disable_notification=True)

        return

    for i in range(len(ads_list)):
        await asyncio.sleep(0.2)
        user_channel_status = await bot.get_chat_member(ads_list[i][4], user_id=user_id)
        if user_channel_status['status'] != 'left':
            counter += 1

    if counter == len(ads_list):
        plan_data = await sql.get_plans()
        await sql.update_user_sub(user_id, 1)

        await bot.send_sticker(user_id, 'CAACAgIAAxkBAAEFSfdi0bsg-RQUfeWR74EIrbr9xiRioQAClwADr8ZRGvSIdDD3EA8EKQQ')
        await bot.send_message(user_id, '⭐ *Премиум* подписка активирована!', disable_notification=True, parse_mode='Markdown')
        await asyncio.sleep(2)
        await bot.send_message(user_id, '_Обо всех преимуществах_ ⭐ *Премиум* _вы можете узнать в /menu_', parse_mode='Markdown', disable_notification=True)

        return

    await callback.answer('Необходимо подписаться на все каналы!')
    await callback.message.delete()
    await bot.send_message(
        user_id,
        'Чтобы получить подписку бесплатно, необходимо подписаться на всех спонсоров!',
        reply_markup=await markups.get_ads_for_sub()
    )


@dp.message_handler(filters.ChatTypeFilter(types.ChatType.PRIVATE), state=dialogue.parameters_age)
async def search_enter_age(message: types.Message, state=FSMContext):

    user_id = message.from_user.id
    age = message.text
    result = '-1:-1'

    if not age.isdigit():

        age = age.split('-')
        if len(age) != 2 or not age[0].isdigit() or not age[1].isdigit():
            await message.answer(
                '_Пример поиска по диапозону:_ *24-35*'
                '\n_Не используйте посторонние символы, пробелы или буквы!_',
                disable_notification=True,
                parse_mode='Markdown'
            )

            return
        if int(age[0]) < 12 or int(age[1]) < 12:
            await message.answer(
                '_Примечание: возраст должен быть больше 12!_',
                disable_notification=True,
                parse_mode='Markdown'
            )

            return
        if int(age[0]) > int(age[1]):
            await message.answer(
                '_Примечание: возраст указывается от и до. Первое число не может быть больше второго!_',
                disable_notification=True,
                parse_mode='Markdown'
            )

            return

        result = f'{age[0]}:{age[1]}'

    else:
        if int(age) < 12:
            await message.answer(
                'Пожалуйста, введите возраст числом, без посторонних символов!'
                '\n_Примечание: возраст должен быть больше 12!_',
                disable_notification=True,
                parse_mode='Markdown'
            )

            return

        result = f'{age}:{age}'

    async with state.proxy() as data:
        data['age'] = result

    await dialogue.previous()
    await message.delete()
    await message.answer('Выберите фильтры:', disable_notification=True, reply_markup=markups.markup_search)
    msg_del = await bot.send_message(
        user_id,
        '_Новый параметр поиска успешно установлен!_\nВыберите дополнительные параметры, или выполните поиск по текущим!',
        parse_mode='Markdown',
        disable_notification=True
    )
    await asyncio.sleep(1.5)
    await msg_del.delete()


# --- CLBCKS FOR MENU ---
@dp.callback_query_handler(lambda c: c.data and c.data.startswith('menu_'))
async def menu_all(callback: types.CallbackQuery, state=FSMContext):
    '''
    Хендлер нажатия на любую кнопку в меню
    '''

    code = callback.data.replace('menu_', '')
    user_id = callback.from_user.id

    if code == 'profile':
        await callback.message.delete()
        await cmd_profile(callback.message, state, callback.from_user.id)

    elif code == 'help':
        await callback.message.delete()
        await cmd_help(callback.message, state)

    elif code == 'support':
        await callback.message.edit_text(
            '''
♨️ Вы можете поддержать наш проект, поделившись мыслями по его улучшению с @DisignerNikita19
👾 Если вы нашли баг, ошибку или недоработку - пожалуйста, сообщите о них @membersonly5
📧 Любые коммерческие предложения (в т.ч. по рекламе) - @DisignerNikita19
            ''',
            reply_markup=markups.markup_back_help
        )
    elif code == 'subscribe':
        await callback.message.edit_text(
            '''
⭐ Преимущества *Премиум*:

1. Поиск собеседника по параметрам (полу, возрасту, стране)
2. Нет ограничений на отправку стикеров, фото, видео, гиф
3. Секретная инфорация о себеседника при старте диалоге
4. Нет необходимости в подписке на каналы, отключение рекламы
5. Иммунитет к бану (бот будет игноировать некоторые нарушения)

💳 Пополнить баланс можно в профиле (/profile).

🕑 Выберите продолжительность подписки ниже:
            ''',
            parse_mode='Markdown',
            reply_markup=await markups.get_plans()
        )

    elif code == 'rules':
        await cmd_rules(callback.message, state)
        # await callback.message.delete()

    else:
        await callback.message.edit_text('*Главное меню*', parse_mode='Markdown', reply_markup=markups.menu())


# --- Admin CLBCKS and MSGs ---
@dp.callback_query_handler(lambda c: c.data and c.data.startswith('admin_menu_'), state=None)
async def ap_btns(callback: types.CallbackQuery, state=FSMContext):
    '''
    Обработка нажатий на кнопки в админ-панели
    '''

    code = callback.data.replace('admin_menu_', '')
    user_id = callback.from_user.id

    if code == 'editplan':
        await callback.message.edit_text('Редактор подписок:', reply_markup=await markups.get_plans(False))
        await edit_plans_adm.enter_edit.set()

    elif code == 'stat':
        await cmd_stat(callback.message, state)

    elif code == 'broadcast':
        await callback.message.edit_text('*Введите сообщение для рассылки:*', parse_mode='Markdown', reply_markup=markups.markup_cancel)
        await ap_broadcast.enter_text.set()

    elif code == 'ads':
        await callback.answer('Вы вошли в рекламный кабинет')
        await callback.message.edit_text('〰️〰️〰️ 〰️〰️〰️ 〰️〰️〰️', parse_mode='Markdown', reply_markup=await markups.get_ads())


# bcast start
@dp.message_handler(filters.ChatTypeFilter(types.ChatType.PRIVATE), state=ap_broadcast.enter_text, content_types=['text', 'sticker', 'video', 'photo', 'audio', 'voice', 'document'])
async def ap_bcast_text(message: types.Message, state=FSMContext):
    '''
    Обработка текста для рассылки
    '''

    count = await sql.get_stats()

    if message.content_type == 'photo':
        file_id = None

        for item in message.photo:
            file_id = item.file_id

        await message.answer_photo(file_id, disable_notification=True, caption=message.caption, parse_mode='Markdown', reply_markup=markups.markup_confirm)
        async with state.proxy() as data:
            data['photo'] = file_id
            data['caption'] = message.caption
            data['text'] = None

    elif message.content_type == 'text':
        await message.answer(
            f'*Кол-во пользователей:* _{count[1]}_\n\n'
            f'*Текст:*\n'
            f'{message.text}',
            disable_notification=True,
            parse_mode='Markdown',
            reply_markup=markups.markup_confirm
        )
        async with state.proxy() as data:
            data['text'] = message.text

    await ap_broadcast.next()


@dp.callback_query_handler(lambda c: c.data, state=ap_broadcast.enter_text)
async def ap_bcast_text_cancel(callback: types.CallbackQuery, state=FSMContext):
    '''
    Отмена ввода сообщения с рассылкой
    '''

    await state.finish()
    try:
        await callback.message.edit_text('〰️〰️〰️ 〰️〰️〰️ 〰️〰️〰️', reply_markup=markups.markup_admin_panel)

    except Exception:
        await callback.message.delete()
        await bot.send_message(callback.from_user.id, '〰️〰️〰️ 〰️〰️〰️ 〰️〰️〰️', disable_notification=True, reply_markup=markups.markup_admin_panel)


@dp.callback_query_handler(lambda c: c.data, state=ap_broadcast.confirm)
async def ap_bcast_confirm(callback: types.CallbackQuery, state=FSMContext):
    '''
    Рассылка сообщений.
    '''

    user_id = callback.from_user.id
    code = callback.data.replace('btn_', '')
    data = await state.get_data()

    await callback.message.delete()

    if code == 'cancel':
        await bot.send_message(user_id, '❗ *Вы отменили рассылку*', disable_notification=True, parse_mode='Markdown')
        await state.finish()

    elif code == 'confirm':
        msg_1 = await bot.send_message(user_id, '❗ *Начинаю рассылку через 10 секунд*', disable_notification=True, parse_mode='Markdown')
        await asyncio.sleep(1)

        for i in range(9, 0, -1):
            await msg_1.edit_text(f'❗ *Начинаю рассылку через {i} секунд*', parse_mode='Markdown')
            await asyncio.sleep(1)

        await state.finish()
        await msg_1.delete()
        msg_2 = await bot.send_message(user_id, '❗ *Рассылка началась..*', disable_notification=True, parse_mode='Markdown')

        users = await sql.get_user_list()

        if data['text'] == None:
            for i in range(len(users)):
                await asyncio.sleep(0.2)
                try:
                    await bot.send_photo(users[i][0], photo=data['photo'], caption=data['caption'], parse_mode='Markdown')
                except Exception as e:
                    logger.error(e)

        else:
            for i in range(len(users)):
                await asyncio.sleep(0.2)
                try:
                    await bot.send_message(users[i][0], text=data['text'], parse_mode='Markdown')
                except Exception as e:
                    logger.error(e)

        await msg_2.delete()
        await bot.send_message(user_id, '✔️ *Рассылка завершена*', disable_notification=True, parse_mode='Markdown')
# bcast end


# edit-plan start
@dp.callback_query_handler(lambda c: c.data and c.data.startswith('sub_'), state=edit_plans_adm.enter_edit)
async def edit_plan(callback: types.CallbackQuery, state=FSMContext):
    '''
    '''

    code = callback.data.replace('sub_', '')
    user_id = callback.from_user.id

    plan_info = await sql.get_plans()
    plan_id = plan_info[int(code)][0]
    plan_name = plan_info[int(code)][1]
    plan_time = plan_info[int(code)][2]
    plan_price = plan_info[int(code)][3]

    await callback.message.delete()
    await bot.send_message(user_id,
                           f'''
ID: {plan_id}
NAME: {plan_name}
TIME: {plan_time}
PRICE: {plan_price}
    ''',
                           disable_notification=True
                           )
    async with state.proxy() as data:
        data['id'] = plan_id
    await bot.send_message(user_id, 'Введи новое название:')
    await edit_plans_adm.next()


@dp.message_handler(filters.ChatTypeFilter(types.ChatType.PRIVATE), state=edit_plans_adm.enter_name)
async def ep_enter_name(message: types.Message, state=FSMContext):

    user_id = message.from_user.id

    async with state.proxy() as data:
        data['name'] = message.text

    await message.delete()
    await message.answer('Теперь введи время в днях (ЧИСЛОМ ОТ 1 ДО скольки угодно)')
    await edit_plans_adm.next()


@dp.message_handler(filters.ChatTypeFilter(types.ChatType.PRIVATE), state=edit_plans_adm.enter_time)
async def ep_enter_time(message: types.Message, state=FSMContext):

    user_id = message.from_user.id

    if not message.text.isdigit():
        await message.answer('ЧИСЛОМ БЛЯТЬ!')
        return

    async with state.proxy() as data:
        data['time'] = int(message.text)

    await message.delete()
    await message.answer('Теперь введи цену: (числом от 0 до ~)')
    await edit_plans_adm.next()


@dp.message_handler(filters.ChatTypeFilter(types.ChatType.PRIVATE), state=edit_plans_adm.enter_price)
async def ep_enter_price(message: types.Message, state=FSMContext):

    user_id = message.from_user.id

    if not message.text.isdigit():
        await message.answer('ЧИСЛОООО!')
        return

    async with state.proxy() as data:
        data['price'] = int(message.text)

    await message.delete()
    await message.answer('Готово! Новые данные для подписки:')

    i = await state.get_data()
    await bot.send_message(user_id,
                           f'''
ID: {i['id']}
NAME: {i['name']}
TIME: {i['time']} дн.
PRICE: {i['price']} руб.
    ''',
                           disable_notification=True
                           )
    await sql.edit_plan(i['id'], i['name'], i['time'], i['price'])

    await state.finish()
# edit-plan end


# ads-cabinet clbcks start
@dp.callback_query_handler(lambda c: c.data and c.data.startswith('ap_ads_'), state=None)
async def ads_enter_ad(callback: types.CallbackQuery, state: FSMContext):
    '''
    Обработка кнопок редактирования и создания новых рекламных кампаний
    '''

    user_id = callback.from_user.id
    code = callback.data.replace('ap_ads_', '')

    if code == 'add':
        await callback.answer('Создание новой рекламной кампании..')
        await callback.message.edit_text('❗ *Введите название для рекламной кампании:*', parse_mode='Markdown')
        await ap_add_ads.enter_name.set()

    elif code == 'cancel':
        await callback.answer('Вы вышли из рекламного кабинета!')
        await callback.message.edit_text('〰️〰️〰️ 〰️〰️〰️ 〰️〰️〰️', reply_markup=markups.markup_admin_panel)

    elif code.startswith('del'):
        code = code.replace('del_', '')
        company_info = await sql.get_ad_info(int(code))
        await sql.remove_ads(company_info[0])
        await callback.answer('Вы удалили рекламную кампанию', show_alert=True)
        await callback.message.edit_text('〰️〰️〰️ 〰️〰️〰️ 〰️〰️〰️', reply_markup=markups.markup_admin_panel)

    else:
        company_info = await sql.get_ad_info(int(code))

        if not company_info:
            await callback.answer('Информации по этой рекламной кампании нет!')
            return

        await callback.message.edit_text(
            f'❗ *Рекламная кампания* {company_info[1]} \n\n'
            f'*Осталось времени:* {0} \n'
            f'*Ссылка на канал:* {0}',
            parse_mode='MarkdownV2',
            reply_markup=await markups.markup_company(code)
        )


@dp.message_handler(filters.ChatTypeFilter(types.ChatType.PRIVATE), state=ap_add_ads.enter_name)
async def ads_enter_name(message: types.Message, state=FSMContext):
    '''
    Обработка названия для новой рекламной кампании
    '''

    user_id = message.from_user.id

    async with state.proxy() as data:
        data['ad_name'] = message.text

    await message.delete()
    await message.answer(f'❗ *Название кампании:* _{message.text}_\n\nПожалуйста, введите время кампании в часах:', disable_notification=True, parse_mode='Markdown')
    await ap_add_ads.next()


@dp.message_handler(filters.ChatTypeFilter(types.ChatType.PRIVATE), state=ap_add_ads.enter_time)
async def ads_enter_time(message: types.Message, state=FSMContext):
    '''
    Обработка времени новой рекламной кампании
    '''

    user_id = message.from_user.id
    code = message.text

    await message.delete()

    if not code.isdigit():
        await message.answer('❗ *Пожалуйста, укажите время числом!*')

        return

    async with state.proxy() as data:
        data['ad_time'] = int(code)

    await message.answer(
        f'❗ *Время действия кампании:* _{code}_\n\n'
        'Пожалуйста, вставьте ссылку на канал:\n\n'
        '_Пример правильной ссылки:_ `https://t.me/channel_name`',
        disable_notification=True,
        parse_mode='Markdown'
    )
    await ap_add_ads.next()


@dp.message_handler(filters.ChatTypeFilter(types.ChatType.PRIVATE), state=ap_add_ads.enter_url)
async def ads_enter_url(message: types.Message, state=FSMContext):

    user_id = message.from_user.id
    url = message.text

    await message.delete()

    if not url.startswith('https://t.me'):
        await message.answer('❗ *Ссылка должна начинаться с* https://t.me', disable_notification=True, parse_mode='Markdown')
        return

    url = url.strip().lower()

    async with state.proxy() as data:
        data['ad_url'] = url

    await message.answer(
        f'❗ *Вы установили [эту]({url}) ссылку*\n\nПожалуйста, отправьте ID группы или канала:',
        disable_notification=True,
        parse_mode='MarkdownV2'
    )

    await ap_add_ads.next()


@dp.message_handler(filters.ChatTypeFilter(types.ChatType.PRIVATE), state=ap_add_ads.enter_chat_id)
async def ads_enter_chat_id(message: types.Message, state=FSMContext):
    '''
    Обработка chat_id при создании рекламной кампании
    '''

    user_id = message.from_user.id
    chat_id = message.text

    try:
        chat_id_int = int(chat_id)
    except ValueError as e:
        await message.answer('❗ *Значение ID должно быть числовым!*', disable_notification=True, parse_mode='Markdown')
        return

    if not chat_id.startswith('-100'):
        await message.answer('❗ *Значение ID должно начинаться с -100!*', disable_notification=True, parse_mode='Markdown')

        return

    async with state.proxy() as data:
        data['ad_chat_id'] = chat_id_int

    vault = await state.get_data()

    await message.answer(
        f'❗ *Подтвердите создание новой рекламной кампании* \n\n*Название кампании:* {vault["ad_name"]} \n*Время действия:* {vault["ad_time"]} *ч* \n*Ссылка на* [канал]({vault["ad_url"]})',
        disable_notification=True,
        parse_mode='MarkdownV2',
        reply_markup=markups.markup_confirm
    )

    await ap_add_ads.next()


@dp.callback_query_handler(state=ap_add_ads.confirm)
async def ads_create_confirm(callback: types.CallbackQuery, state=FSMContext):
    '''
    Подтверждение создания новой рекламной кампании
    '''

    user_id = callback.from_user.id
    code = callback.data
    data = await state.get_data()

    if code == 'btn_confirm':
        await callback.answer('Новая рекамная кампания успешно создана!')
        await callback.message.delete()
        msg_1 = await bot.send_message(
            user_id,
            f'❗ *Рекламная кампания* _{data["ad_name"]}_ успешно создана!\n\n'
            '_Рекламный кабинет откроется через 3 секунды.._',
            disable_notification=True,
            parse_mode='Markdown'
        )
        await sql.add_ads(data['ad_name'], data['ad_time'], data['ad_url'], data['ad_chat_id'])
        await state.finish()
        await asyncio.sleep(3)
        await msg_1.delete()
        await bot.send_message(user_id, '〰️〰️〰️ 〰️〰️〰️ 〰️〰️〰️', disable_notification=True, reply_markup=await markups.get_ads())

        return

    await callback.answer('Создание новой рекламной кампании отменено!')
    await callback.message.delete()
    await bot.send_message(user_id, '〰️〰️〰️ 〰️〰️〰️ 〰️〰️〰️', disable_notification=True, reply_markup=await markups.get_ads())
    await state.finish()


# ads-cabinet clbcks end


# --- Событие блокировки бота пользователем ---
@dp.errors_handler(exception=exceptions.BotBlocked)
async def on_bot_blocked(update: types.Update, exception: exceptions.BotBlocked):
    '''
    Обработка события блокировки бота пользователем
    '''

    print('Сработал хендлер BotBlocked')

    user_id = update.message.from_user.id
    await sql.del_session(user_id)

    stat = await sql.get_stats()
    new = stat[1] + 1

    sql.cur.execute('UPDATE `stats` SET `blocked` = ?', (new,))
    sql.db.commit()


# --- Антибот ---
@dp.callback_query_handler(markups.confirming_callback.filter(), state=[anti_bot.in_process, anti_bot.in_process_2])
async def user_confirm(callback: types.CallbackQuery, callback_data: dict):
    '''
    Хэндлер обрабатывающий нажатие на кнопку при антибот проверке
    '''

    user_id = int(callback_data.get('user_id'))
    # Предмет, на который нажал пользователь
    subject = callback_data.get('subject')
    necessary_subject = callback_data.get('necessary_subject')
    state = dp.current_state(user=callback.from_user.id,
                             chat=callback.message.chat.id)

    logger.debug(
        f'User {callback.from_user.first_name} clicked on button: {subject}({necessary_subject})')

    if subject == necessary_subject:  # Нажал на правильную кнопку
        logger.debug(
            f'Rights have been granted to the user @{callback.from_user.first_name}:{callback.from_user.id}')
        await bot.send_message(callback.from_user.id, '🤖 *Вы прошли проверку*\n\nКоманды снова доступны!', disable_notification=True, parse_mode='Markdown')
        await state.finish()

    else:
        if str(await state.get_state()) == 'anti_bot:in_process':
            await state.set_state(anti_bot.in_process_2)
            await callback.answer()
            await callback.message.delete()

            generated_tuple = markups.generate_confirm_markup(
                callback.from_user.id)
            markup = generated_tuple[0]
            subject = generated_tuple[1]
            await bot.send_message(callback.from_user.id, f'❗ *Последняя попытка*\n\n*Пройдите проверку, чтобы подтвердить, что вы не робот*\n\n_Найдите_ *{subject}* _на панели ниже!_', parse_mode='Markdown', reply_markup=markup)

            return
        else:
            await bot.send_message(callback.from_user.id, 'Вы были заблокированы!\nЕсли вы считаете, что это ошибка - обратитесь к @membersonly5', disable_notification=True)
            await state.set_state(anti_bot.banned)
        # logger.debug(f'The user @{callback.from_user.first_name}:{callback.from_user.id} clicked on the wrong object '
        #             f'and was banned until {until_date}')

    # и убираем часики
    await callback.answer()
    await callback.message.delete()
