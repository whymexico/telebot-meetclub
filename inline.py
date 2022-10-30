import random
import database as sql

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.callback_data import CallbackData

from typing import Tuple
from collections import namedtuple


Emoji = namedtuple('Emoji', ['unicode', 'subject', 'name'])

emojies = (
    Emoji(unicode=u'\U0001F48D', subject='ring', name='кольцо'),
    Emoji(unicode=u'\U0001F460', subject='shoe', name='туфлю'),
    Emoji(unicode=u'\U0001F451', subject='crown', name='корону'),
    Emoji(unicode=u'\U00002702', subject='scissors', name='ножницы'),
    Emoji(unicode=u'\U0001F941', subject='drum', name='барабан'),

    Emoji(unicode=u'\U0001F48A', subject='pill', name='пилюлю'),
    Emoji(unicode=u'\U0001F338', subject='blossom', name='цветок'),
    Emoji(unicode=u'\U0001F9C0', subject='cheese', name='сыр'),
    Emoji(unicode=u'\U0001F3A7', subject='headphone', name='наушники'),
    Emoji(unicode=u'\U000023F0', subject='clock', name='будильник'),

    Emoji(unicode=u'\U0001F951', subject='avocado', name='авокадо'),
    Emoji(unicode=u'\U0001F334', subject='palm', name='пальму'),
    Emoji(unicode=u'\U0001F45C', subject='handbag', name='сумку'),
    Emoji(unicode=u'\U0001F9E6', subject='socks', name='носки'),
    Emoji(unicode=u'\U0001FA93', subject='axe', name='топор'),

    Emoji(unicode=u'\U0001F308', subject='rainbow', name='радугу'),
    Emoji(unicode=u'\U0001F4A7', subject='droplet', name='каплю'),
    Emoji(unicode=u'\U0001F525', subject='fire', name='огонь'),
    Emoji(unicode=u'\U000026C4', subject='snowman', name='снеговика'),
    Emoji(unicode=u'\U0001F9F2', subject='magnet', name='магнит'),

    Emoji(unicode=u'\U0001F389', subject='popper', name='хлопушку'),
    Emoji(unicode=u'\U0001F339', subject='rose', name='розу'),
    Emoji(unicode=u'\U0000270E', subject='pencil', name='карандаш'),
    Emoji(unicode=u'\U00002709', subject='envelope', name='конверт'),
    Emoji(unicode=u'\U0001F680', subject='rocket', name='ракету'),
)


menu_profile = InlineKeyboardButton(
    text='👁️ Профиль', callback_data='menu_profile')
menu_rules = InlineKeyboardButton(text='📖 Правила', callback_data='menu_rules')
menu_subscribe = InlineKeyboardButton(
    text='⭐ Премиум', callback_data='menu_subscribe')
menu_support = InlineKeyboardButton(
    text='💵 Поддержка', callback_data='menu_support')
menu_help = InlineKeyboardButton(text='❓ Помощь', callback_data='menu_help')
markup_menu = InlineKeyboardMarkup(row_width=2).add(menu_profile).row(
    menu_rules, menu_subscribe).add(menu_support).add(menu_help)
menu_back = InlineKeyboardButton(text='Назад', callback_data='menu_back')

help_send = InlineKeyboardButton(
    text='Написать', url='https://t.me/membersonly5')

profile_settings = InlineKeyboardButton(
    text='⚙️ Настройки', callback_data='profile_settings')
profile_deposit = InlineKeyboardButton(
    text='💰 Пополнить баланс', callback_data='profile_deposit')

settings_name = InlineKeyboardButton(
    text='🧍‍♂️ Никнейм', callback_data='settings_name')
settings_country = InlineKeyboardButton(
    text='🗺️ Страна', callback_data='settings_country')
settings_age = InlineKeyboardButton(
    text='🔞 Возраст', callback_data='settings_age')
settings_gender = InlineKeyboardButton(
    text='♂️ Пол', callback_data='settings_gender')

markup_settings = InlineKeyboardMarkup(row_width=2).add(
    settings_name, settings_country, settings_age, settings_gender, menu_back)

deposit_select_qiwi = InlineKeyboardButton(
    text='QIWI', callback_data='deposit_select_qiwi')
deposit_select_ukassa = InlineKeyboardButton(
    text='ЮКасса', callback_data='deposit_select_ukassa')

markup_deposit_select = InlineKeyboardMarkup(row_width=1).add(
    deposit_select_qiwi, deposit_select_ukassa, menu_back)

markup_profile = InlineKeyboardMarkup(row_width=1).add(
    profile_settings, profile_deposit, menu_back)

sub_free = InlineKeyboardButton(
    text='Попробовать бесплатно', callback_data='sub_free')
sub_1 = InlineKeyboardButton(text='24 часа за 79 руб.', callback_data='sub_1')
sub_2 = InlineKeyboardButton(text='7 дней за 169 руб.', callback_data='sub_2')
sub_3 = InlineKeyboardButton(text='Месяц за 199 руб.', callback_data='sub_3')
sub_4 = InlineKeyboardButton(
    text='Навсегда за 469 руб.', callback_data='sub_4')

markup_sub = InlineKeyboardMarkup(row_width=1).add(
    sub_free, sub_1, sub_2, sub_3, sub_4, menu_back)


markup_back = InlineKeyboardMarkup().add(menu_back)
markup_back_help = InlineKeyboardMarkup().add(help_send).add(menu_back)


btn_add_country_ru = InlineKeyboardButton(
    text='🇷🇺 Россия', callback_data='btn_add_country_ru')
btn_add_country_kz = InlineKeyboardButton(
    text='🇰🇿 Казахстан', callback_data='btn_add_country_kz')
btn_add_country_bel = InlineKeyboardButton(
    text='🇧🇾 Беларусь', callback_data='btn_add_country_bel')
btn_add_country_uk = InlineKeyboardButton(
    text='🇺🇦 Украина', callback_data='btn_add_country_uk')
btn_add_country_usa = InlineKeyboardButton(
    text='🇺🇸 США', callback_data='btn_add_country_usa')
markup_add_country = InlineKeyboardMarkup(row_width=1).add(
    btn_add_country_ru,
    btn_add_country_kz,
    btn_add_country_bel,
    btn_add_country_uk,
    btn_add_country_usa
)

btn_add_gender_male = InlineKeyboardButton(
    text='👦 Мужской', callback_data='btn_add_gender_male')
btn_add_gender_female = InlineKeyboardButton(
    text='👧 Женский', callback_data='btn_add_gender_female')
markup_add_gender = InlineKeyboardMarkup(row_width=2).row(
    btn_add_gender_male).row(btn_add_gender_female)

btn_add_age_0 = InlineKeyboardButton(
    text='Мне меньше 18 лет', callback_data='btn_add_age_0')
btn_add_age_18 = InlineKeyboardButton(
    text='Мне 18 лет, или больше', callback_data='btn_add_age_18')
markup_add_age = InlineKeyboardMarkup(
    row_width=2).row(btn_add_age_0).row(btn_add_age_18)

btn_settings_gender_male = InlineKeyboardButton(
    text='👦 Мужской', callback_data='btn_settings_gender_male')
btn_settings_gender_female = InlineKeyboardButton(
    text='👧 Женский', callback_data='btn_settings_gender_female')
markup_settings_gender = InlineKeyboardMarkup(row_width=2).row(
    btn_settings_gender_male).row(btn_settings_gender_female)

#btn_settings_age_0 = InlineKeyboardButton(text='Мне меньше 18 лет', callback_data='btn_settings_age_0')
#btn_settings_age_18 = InlineKeyboardButton(text='Мне 18 лет, или больше', callback_data='btn_settings_age_18')
#markup_settings_age = InlineKeyboardMarkup(row_width=2).row(btn_settings_age_0).row(btn_settings_age_18)

btn_settings_country_ru = InlineKeyboardButton(
    text='🇷🇺 Россия', callback_data='btn_settings_country_ru')
btn_settings_country_kz = InlineKeyboardButton(
    text='🇰🇿 Казахстан', callback_data='btn_settings_country_kz')
btn_settings_country_bel = InlineKeyboardButton(
    text='🇧🇾 Беларусь', callback_data='btn_settings_country_bel')
btn_settings_country_uk = InlineKeyboardButton(
    text='🇺🇦 Украина', callback_data='btn_settings_country_uk')
btn_settings_country_usa = InlineKeyboardButton(
    text='🇺🇸 США', callback_data='btn_settings_country_usa')
markup_settings_country = InlineKeyboardMarkup(row_width=1).add(
    btn_settings_country_ru,
    btn_settings_country_kz,
    btn_settings_country_bel,
    btn_settings_country_uk,
    btn_settings_country_usa
)

btn_search_country = InlineKeyboardButton(
    text='Поиск по региону', callback_data='btn_search_country')
btn_search_gender = InlineKeyboardButton(
    text='Поиск по полу', callback_data='btn_search_gender')
btn_search_age = InlineKeyboardButton(
    text='Поиск по возрасту', callback_data='btn_search_age')
btn_search_confirm = InlineKeyboardButton(
    text='🔍 Найти собеседника', callback_data='btn_search_confirm')
markup_search = InlineKeyboardMarkup(row_width=1).add(
    btn_search_country, btn_search_gender, btn_search_age, btn_search_confirm)

btn_s_country_ru = InlineKeyboardButton(
    text='🇷🇺 Россия', callback_data='btn_s_country_ru')
btn_s_country_kz = InlineKeyboardButton(
    text='🇰🇿 Казахстан', callback_data='btn_s_country_kz')
btn_s_country_bel = InlineKeyboardButton(
    text='🇧🇾 Беларусь', callback_data='btn_s_country_bel')
btn_s_country_uk = InlineKeyboardButton(
    text='🇺🇦 Украина', callback_data='btn_s_country_uk')
btn_s_country_usa = InlineKeyboardButton(
    text='🇺🇸 США', callback_data='btn_s_country_usa')
btn_s_country_any = InlineKeyboardButton(
    text='Любая страна', callback_data='btn_s_country_any')
markup_s_country = InlineKeyboardMarkup(row_width=1).add(
    btn_s_country_ru,
    btn_s_country_kz,
    btn_s_country_bel,
    btn_s_country_uk,
    btn_s_country_usa,
    btn_s_country_any
)

btn_s_gender_male = InlineKeyboardButton(
    text='👦 Мужской', callback_data='btn_s_gender_male')
btn_s_gender_female = InlineKeyboardButton(
    text='👧 Женский', callback_data='btn_s_gender_female')
btn_s_gender_any = InlineKeyboardButton(
    text='Любой пол', callback_data='btn_s_gender_any')
markup_s_gender = InlineKeyboardMarkup(row_width=2).row(
    btn_s_gender_male).row(btn_s_gender_female).add(btn_s_gender_any)


# --- ADMIN MENU ---
admin_menu_editplan = InlineKeyboardButton(
    text='⭐ Настрока подписок', callback_data='admin_menu_editplan')
admin_menu_stat = InlineKeyboardButton(
    text='📈 Статистика', callback_data='admin_menu_stat')
admin_menu_broadcast = InlineKeyboardButton(
    text='📢 Отправить сообщение', callback_data='admin_menu_broadcast')
admin_menu_ads = InlineKeyboardButton(
    text='♨️ Рекламный кабинет', callback_data='admin_menu_ads')
admin_menu_rules = InlineKeyboardButton(
    text='⚠️ Редактировать правила', callback_data='admin_menu_rules')
admin_menu_support = InlineKeyboardButton(
    text='💵 Кнопка "Поддержка"', callback_data='admin_menu_support')
admin_menu_help = InlineKeyboardButton(
    text='❓ Кнопка "Помощь"', callback_data='admin_menu_help')

markup_admin_panel = InlineKeyboardMarkup(row_width=1).add(
    admin_menu_editplan, admin_menu_stat, admin_menu_broadcast, admin_menu_ads, admin_menu_rules, admin_menu_support, admin_menu_help)

btn_confirm = InlineKeyboardButton(
    text='✅ Подтвердить', callback_data='btn_confirm')
btn_cancel = InlineKeyboardButton(text='❌ Отмена', callback_data='btn_cancel')
markup_confirm = InlineKeyboardMarkup(
    row_width=1).add(btn_confirm).add(btn_cancel)
markup_cancel = InlineKeyboardMarkup(row_width=1).add(btn_cancel)

btn_new_ads = InlineKeyboardButton(
    text='🆕 Создать рекламную кампанию', callback_data='ap_ads_add')
btn_cancel_ads = InlineKeyboardButton(
    text='🔙 Выйти в админ-меню', callback_data='ap_ads_cancel')


confirming_callback = CallbackData(
    "confirm", "subject", "necessary_subject", "user_id")


def generate_confirm_markup(user_id: int) -> Tuple[InlineKeyboardMarkup, str]:
    '''
    Функция, создающая клавиатуру для подтверждения, что пользователь не является ботом
    '''

    confirm_user_markup = InlineKeyboardMarkup(row_width=5)
    subjects = random.sample(emojies, 5)
    necessary_subject = random.choice(subjects)

    for emoji in subjects:
        button = InlineKeyboardButton(
            text=emoji.unicode,
            callback_data=confirming_callback.new(
                subject=emoji.subject, necessary_subject=necessary_subject.subject, user_id=user_id)
        )
        confirm_user_markup.insert(button)

    return confirm_user_markup, necessary_subject.name


def menu():
    ''''''

    return markup_menu


def add_country():
    ''''''

    return markup_add_country


def add_gender():
    ''''''

    return markup_add_gender


def add_age():
    ''''''

    return markup_add_age


def deposit_pay(url):
    deposit_pay_url = InlineKeyboardButton(text='Перейти к оплате', url=url)
    deposit_pay_checkout = InlineKeyboardButton(
        text='Я оплатил', callback_data='deposit_pay_checkout')
    deposit_pay_cancel = InlineKeyboardButton(
        text='Отменить оплату', callback_data='deposit_pay_cancel')

    markup_deposit_pay = InlineKeyboardMarkup(row_width=1).add(
        deposit_pay_url, deposit_pay_checkout, deposit_pay_cancel)

    return markup_deposit_pay


async def get_plans(back_btn: bool = True):
    data = await sql.get_plans()
    id_list = dict()
    buttons_list = list()

    if data == False:
        return InlineKeyboardMarkup().add(menu_back)

    for i in range(len(data)):
        id_list.setdefault(data[i][0], data[i][1])

    for k, v in id_list.items():
        buttons_list.append([InlineKeyboardButton(
            text=v, callback_data=('sub_' + str(k)))])

    if back_btn:
        buttons_list.append([InlineKeyboardButton(
            text='Назад', callback_data='menu_back')])

    return InlineKeyboardMarkup(inline_keyboard=buttons_list)


async def get_ads():
    data = await sql.get_ads()
    id_list = dict()
    buttons_list = list()

    if data == None:
        return InlineKeyboardMarkup().add(btn_new_ads).add(btn_cancel)

    for i in range(len(data)):
        id_list.setdefault(data[i][0], data[i][1])

    for k, v in id_list.items():
        buttons_list.append([InlineKeyboardButton(
            text=v, callback_data=('ap_ads_' + str(k)))])

    return InlineKeyboardMarkup(inline_keyboard=buttons_list).add(btn_new_ads).add(btn_cancel)


async def get_ads_for_sub():
    btn_check_sub = InlineKeyboardButton(
        text='Проверить подписку', callback_data='btn_check_sub')

    data = await sql.get_ads()
    id_list = dict()
    buttons_list = list()

    if data == None:
        return False

    for i in range(len(data)):
        id_list.setdefault(f'Спонсор #{i+1}', data[i][3])

    for k, v in id_list.items():
        buttons_list.append([InlineKeyboardButton(
            text=k, url=v)])

    return InlineKeyboardMarkup(inline_keyboard=buttons_list).add(btn_check_sub)


async def markup_company(company_id):
    callback = 'ap_ads_del_' + company_id
    btn_del = InlineKeyboardButton(
        text='Удалить кампанию', callback_data=callback)

    return InlineKeyboardMarkup(row_width=1).add(btn_del, menu_back)
