import database

from aiogram import Bot, Dispatcher, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from dotenv import dotenv_values
from pyqiwip2p import QiwiP2P
from loguru import logger
from sys import stderr  # stdin, stdout or stderr


config = dotenv_values('.env')

bot = Bot(config['API_KEY'])
dp = Dispatcher(bot, storage=MemoryStorage())
p2p = QiwiP2P(auth_key=config['P2P_PRIVATE_KEY'])


def main():
    '''
    Запуск бота.
    '''

    # Настройка логгера
    logger.remove()
    logger.add(sink=stderr, level='DEBUG', colorize=True, enqueue=True)

    logger.info('Инициализация обработчиков..\n')
    from commands import dp
    database.initDB()

    logger.info("Установка middlewares...")
    from throttling import ThrottlingMiddleware
    dp.middleware.setup(ThrottlingMiddleware())

    logger.info('Бот успешно запущен!\n')

    try:
        executor.start_polling(dp)
    finally:
        database.db.close()
        logger.info('Бот остановлен!')


if __name__ == '__main__':
    main()
