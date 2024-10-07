import asyncio
import time
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardButton, InlineKeyboardMarkup
from datetime import datetime, timedelta

TOKEN = '7256493186:AAH3bxgu7gG9cu_yEF5JHsBZX51I3fhhs4s'
ADMIN_ID = 324663088
tariff_active = False
# Инициализация бота и диспетчера
bot = Bot(token=TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)
num_month = ""
n = 0
user_id = []

# Словарь для хранения данных о пользователях (счётчик сообщений и время сброса)
user_data = {}

# Приветственное сообщение и создание кнопок для выбора тарифов
async def send_welcome(message: Message):
    chat_id = message.chat.id
    if chat_id not in user_data:
        user_data[chat_id] = {"count": 0, "reset_time": datetime.now()}
        print(user_data)
    
    # Приветственное сообщение
    await message.answer("Привет, я AllBoost Bot!👋 У вас есть 10 бесплатных сообщений.")


# Логика обработки сообщений с лимитом 10 сообщений
async def gpt_message(message: Message):
    chat_id = message.chat.id
    user_info = user_data.get(chat_id, {"count": 0, "reset_time": 0, "expiry_time": None, "tariff_active": False})

    current_time = datetime.now()

    # Проверка истечения тарифа
    if "expiry_time" not in user_info:
        user_info["expiry_time"] = None  # Установим default значение

    if user_info["expiry_time"] is not None and current_time >= user_info["expiry_time"]:
        user_info["tariff_active"] = False  # Устанавливаем флаг на False
        user_info["expiry_time"] = None  # Обнуляем expiry_time
        await message.answer("📛 Ваш тариф истёк. Пожалуйста, продлите его.", reply_markup=generate_tariff_buttons())
        user_data[chat_id] = user_info
        return

    # Проверка наличия активного тарифа
    if user_info.get("tariff_active"):
        # Тариф активен, обрабатываем сообщение через GPT
        gpt_response = "Ваше сообщение обработано GPT (с активным тарифом)."
        await message.answer(gpt_response)
        return

    # Проверяем лимит на количество сообщений
    if user_info["count"] < 9 or current_time >= user_info["reset_time"]:
        if current_time >= user_info["reset_time"] and user_info["reset_time"] != current_time + timedelta(minutes=1):
            # Сбрасываем счётчик после истечения времени сброса
            user_info["count"] = 0
            user_info["reset_time"] = current_time + timedelta(minutes=1)

        user_info["count"] += 1  # Увеличиваем счётчик сообщений
        if user_info["count"] == 9:
            user_info["reset_time"] = current_time + timedelta(minutes=1)

        # Ответ GPT
        if user_info["count"] not in [9,8,7,6]:
            gpt_response = f"Ваше сообщение обработано GPT.\nОсталось {10 - user_info["count"]} сообщений."
            await message.answer(gpt_response)
        if user_info["count"] in [8, 7, 6]:
            gpt_response = f"Ваше сообщение обработано GPT.\nОсталось {10 - user_info["count"]} сообщения."
            await message.answer(gpt_response)
        if user_info["count"] == 9:
            gpt_response = f"Ваше сообщение обработано GPT.\nОсталось {10 - user_info["count"]} сообщение."
            await message.answer(gpt_response)

        # Обновляем данные пользователя в словаре
        user_data[chat_id] = user_info
    else:
        # Лимит исчерпан, предлагаем выбрать тариф
        await message.answer("📛 Вы отправили более 10 сообщений.\n👉 Выберите тариф или подождите 1 сутки.", reply_markup=generate_tariff_buttons())

# Функция для проверки истечения тарифов
async def check_tariffs():
    global user_data
    while True:
        current_time = datetime.now()
        print(f"Проверка тарифов: {current_time}")
        for chat_id, user_info in list(user_data.items()):
            # Проверяем наличие "expiry_time" и неистёкший тариф
            if user_info.get("expiry_time") is not None and current_time >= user_info["expiry_time"]:
                print(f"Тариф истек для пользователя {chat_id} в {user_info["expiry_time"]}")
                user_info["tariff_active"] = False
                user_info["expiry_time"] = None  # Обнуляем expiry_time
                await bot.send_message(chat_id, "📛 Ваш тариф истёк. Пожалуйста, продлите его.", reply_markup=generate_tariff_buttons())
                user_data[chat_id] = user_info  # Сохраняем обновлённые данные
            else:
                print(f"Тариф активен для пользователя {chat_id}, истекает в {user_info.get("expiry_time")}")
        
        await asyncio.sleep(10)  # Проверяем каждые 10 секунд

# Создание клавиатуры для выбора тарифов
def generate_tariff_buttons():
    one_month = InlineKeyboardButton(
        text="✨ 1 месяц",
        callback_data='1_month'
    )
    three_months = InlineKeyboardButton(
        text="✨ 3 месяца", 
        callback_data='3_months'
    )
    six_months = InlineKeyboardButton(
        text="✨ 6 месяцев", 
        callback_data='6_months'
    )
    nine_months = InlineKeyboardButton(
        text="✨ 9 месяцев", 
        callback_data='9_months'
    )
    twelve_month = InlineKeyboardButton(
        text="✨ 12 месяцев", 
        callback_data='12_months'
    )
    rows = [
        [one_month],
        [three_months],
        [six_months],
        [nine_months],
        [twelve_month]
    ]

    markup = InlineKeyboardMarkup(inline_keyboard=rows)

    return markup

async def pay_tariff1(callback_query: CallbackQuery):
    global num_month, n
    num_month += "1"
    n += 1
    await callback_query.message.answer("💸 Оплата 299 рублей через СБП на телефон +79063493152 (Озон Банк).\n‼️После оплаты пришлите скриншот для подтверждения оплаты.")

async def pay_tariff2(callback_query: CallbackQuery):
    global num_month, n
    num_month += "3"
    n += 1
    await callback_query.message.answer("💸 Оплата 799 рублей через СБП на телефон +79063493152 (Озон Банк).\n‼️После оплаты пришлите скриншот для подтверждения оплаты.")

async def pay_tariff3(callback_query: CallbackQuery):
    global num_month, n
    num_month += "6"
    n += 1
    await callback_query.message.answer("💸 Оплата 1699 рублей через СБП на телефон +79063493152 (Озон Банк).\n‼️После оплаты пришлите скриншот для подтверждения оплаты.")

async def pay_tariff4(callback_query: CallbackQuery):
    global num_month, n
    num_month += "9"
    n += 1
    await callback_query.message.answer("💸 Оплата 2599 рублей рублей через СБП на телефон +79063493152 (Озон Банк).\n‼️После оплаты пришлите скриншот для подтверждения оплаты.")

async def pay_tariff5(callback_query: CallbackQuery):
    global num_month
    num_month += "12"
    n += 1
    await callback_query.message.answer("💸 Оплата 3499 рублей через СБП на телефон +79063493152 (Озон Банк).\n‼️После оплаты пришлите скриншот для подтверждения оплаты.")

def confirm_admin_pay():
    complite_admin_btn = InlineKeyboardButton(
        text = "✅ Подтвердить оплату",
        callback_data = 'complite_admin'
    )
    error_admin_btn = InlineKeyboardButton(
        text = "❌ Отказать",
        callback_data = 'error_admin'
    )
    row1 = [complite_admin_btn]
    row2 = [error_admin_btn]
    rows = [row1, row2]
    markup = InlineKeyboardMarkup(inline_keyboard=rows)
    return markup

async def confirm_pay_user(message: types.Message):
    global user_id
    user_id.append(message.chat.id)
    # Пересылаем фото админу
    await bot.send_message(ADMIN_ID, f"Пользователь {message.from_user.username} отправил фото:")
    await bot.send_photo(ADMIN_ID, photo=message.photo[-1].file_id)
    await bot.send_message(ADMIN_ID,f"Подтвердите оплату от пользователя {message.from_user.username}", reply_markup = confirm_admin_pay())
    # Ответ пользователю
    await message.answer("Ожидайте, платёж проверяется.")

# Функция обработки оплаты тарифа
async def process_tariff(callback_query: CallbackQuery):
    global num_month
    chat_id = user_id[0]  # Берем chat_id пользователя
    user_info = user_data.get(chat_id, {"count": 0, "reset_time": datetime.now(), "expiry_time": None, "tariff_active": False})

    # Логирование callback_data для отладки
    print(f"Получены данные: {callback_query.data}", timedelta(minutes=1))

    # Обработка разных тарифов
    if callback_query.data == 'complite_admin' and (num_month == "1" or num_month == "1"*n):
        user_info["expiry_time"] = datetime.now() + timedelta(days=30)  # Устанавливаем время действия тарифа на 1 минуту для тестирования
    elif callback_query.data == 'complite_admin' and (num_month == "3" or num_month == "1"*n):
        user_info["expiry_time"] = datetime.now() + timedelta(days=90)
    elif callback_query.data == 'complite_admin' and (num_month == "6" or num_month == "1"*n):
        user_info["expiry_time"] = datetime.now() + timedelta(days=180)
    elif callback_query.data == 'complite_admin' and (num_month == "9" or num_month == "1"*n):
        user_info["expiry_time"] = datetime.now() + timedelta(days=270)
    elif callback_query.data == 'complite_admin' and (num_month == "12" or num_month == "1"*n):
        user_info["expiry_time"] = datetime.now() + timedelta(days=365)
    else:
        print("Неизвестное значение callback_data:", callback_query.data)  # На случай, если что-то пойдет не так

    # Логируем обновление данных тарифа
    print(f"Тариф оплачен: {chat_id}, истекает в {user_info["expiry_time"]}")

    # Устанавливаем флаг активного тарифа
    user_info["tariff_active"] = True

    # Обновляем данные пользователя в словаре
    user_data[chat_id] = user_info

    # Сообщение пользователю
    await bot.send_message(chat_id, "✅ Оплата прошла успешно. Тариф подключён.", reply_markup=support_continue_buttons())
    await callback_query.answer("Оплата подтверждена")

async def error_pay(callback_query: CallbackQuery):
    chat_id = user_id[0]
    await bot.send_message(chat_id, "❌ Произошла ошибка.\nПроверьте оплату и отправьте скриншот снова.")


# Создание клавиатуры для продолжения общения с ботом или связи с поддержкой
def support_continue_buttons():
    url_admin_btn = InlineKeyboardButton(
        text="🆘 Написать в поддержку", 
        url="https://t.me/AlexchelZzz"
    )
    continue_chat_btn = InlineKeyboardButton(
        text="💬 Продолжить общение", 
        callback_data='continue_chat'
    )
    row1 = [url_admin_btn]
    row2 = [continue_chat_btn]
    rows = [row1, row2]
    markup = InlineKeyboardMarkup(inline_keyboard = rows)
    return markup

# Обработка нажатия кнопки "Продолжить общение"
async def continue_chat(callback_query: CallbackQuery):
    chat_id = callback_query.message.chat.id
    # Сбрасываем счётчик сообщений для данного пользователя
    user_data[chat_id]["count"] = 0
    user_data[chat_id]["reset_time"] = datetime.now() + timedelta(days=1)
    
    await callback_query.answer()
    await callback_query.message.answer("💬 Продолжаем общение с ботом! Вы можете снова отправлять сообщения.")

# Основная функция для запуска бота
async def main():
    asyncio.create_task(check_tariffs())
    asyncio.create_task(check_tariffs())
    # Регистрация обработчиков
    dp.message.register(send_welcome, Command(commands=["start"]))
    dp.message.register(confirm_pay_user, F.photo)
    dp.message.register(gpt_message)
    dp.callback_query.register(pay_tariff1, lambda c: c.data == '1_month')
    dp.callback_query.register(pay_tariff2, lambda c: c.data == '3_months')
    dp.callback_query.register(pay_tariff3, lambda c: c.data == '6_months')
    dp.callback_query.register(pay_tariff4, lambda c: c.data == '9_months')
    dp.callback_query.register(pay_tariff5, lambda c: c.data == '12_months')
    dp.callback_query.register(process_tariff, lambda c: c.data == 'complite_admin')
    dp.callback_query.register(error_pay, lambda c: c.data == 'error_admin')
    dp.callback_query.register(continue_chat, lambda c: c.data == 'continue_chat')

    # Запуск long-polling
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
