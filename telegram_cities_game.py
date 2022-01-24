from aiogram import Bot, Dispatcher, executor, types
import wikipedia
import logging
from aiogram.utils.callback_data import CallbackData
import json
import random

API_TOKEN = 'API TOKEN'  # API telegram token
logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN, parse_mode=types.ParseMode.HTML)
dp = Dispatcher(bot)
cb = CallbackData('fabcity', 'city_name')
wikipedia.set_lang("en")


@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    data[message.from_user.id] = {'bot_city': '',
                                  'user_city': '',
                                  'already_been': [],
                                  }
    await message.answer('Hi! My name is CityBot and you can play with me!\n'
                         'The rules are very simple: You say the city, '
                         'I say the city starting with the last letter, and then you do the same!\n\n'
                         'Say the name of any city!\n\n'
                         'To restart send /start')


@dp.message_handler(content_types=['text'])
async def get_user_city(message: types.Message):
    user_id = message.from_user.id
    if user_id in data:
        data[message.from_user.id]['user_city'] = message.text
        user_city = message.text
        already_been = data[message.from_user.id]['already_been']
        bot_city = data[message.from_user.id]['bot_city']
        if user_city in cities_list:
            if user_city not in already_been:
                if bot_city == '' or user_city[0] == bot_city[-1].upper():
                    await answer_next_city(message, user_city, cities_list, already_been)
            else:
                await message.answer('This city has already been!')
        else:
            await message.answer("I don't think it's a city...")
    else:
        await start(message)


async def answer_next_city(message: types.Message, user, cities, already):
    last_letter = user[-1]
    possible_answers = list()
    for city in cities:
        if city not in already and last_letter.upper() == city[0]:
            possible_answers.append(city)
    answer = random.choice(possible_answers)
    data[message.from_user.id]['bot_city'] = answer

    keyboard = types.InlineKeyboardMarkup(row_width=1)
    keyboard.add(types.InlineKeyboardButton(text='Find in Wiki', callback_data=cb.new(city_name=answer)))
    await message.answer(answer, reply_markup=keyboard)


@dp.callback_query_handler(cb.filter())
async def callbacks(call: types.CallbackQuery, callback_data: dict):
    city = callback_data['city_name']
    await get_info_wiki(call.message, city)


async def get_info_wiki(message: types.Message, city):
    try:
        ny = wikipedia.page(city)
        await message.answer(f'Here is info about {city}:\n\n'
                             f'{ny.summary}')
    except Exception as e:
        await message.answer(f'Ugh, name of the city is difficult to search! Try it yourself, please!')


def get_cities():
    with open('cities.json', 'r') as read_file:
        return json.load(read_file)


if __name__ == '__main__':
    cities_list = get_cities()
    cities_list.sort()
    data = {}
    executor.start_polling(dp, skip_updates=True)
