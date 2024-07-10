import random
from telebot import types, TeleBot, custom_filters
from telebot.storage import StateMemoryStorage
from telebot.handler_backends import State, StatesGroup
import sqlalchemy
from sqlalchemy.orm import sessionmaker
from DATABASE.db_models import create_tables
import configparser
from MyStates import MyStates
from command import Command
from user_command import USER

user_1 = USER(id=1, cid=1)


engine = sqlalchemy.create_engine('postgresql://postgres:5728821q@localhost:5432/TELEGA')
Session = sessionmaker(bind=engine)
session = Session()
create_tables(engine)

print('Бот работает, а я нет')

state_storage = StateMemoryStorage()
config = configparser.ConfigParser()
config.read('config.ini')
token_tg = config['TELEGRAM']['token']
token_bot = token_tg
bot = TeleBot(token_bot, state_storage=state_storage)

known_users = user_1.user_list(engine)
userStep = {}
buttons = []


def show_hint(*lines):
    return '\n'.join(lines)


def show_target(data):
    return f"{data['target_word']} -> {data['translate_word']}"


def get_user_step(uid):
    if uid in userStep:
        return userStep[uid]
    else:
        known_users.append(uid)
        userStep[uid] = 0
        print("New user detected, who hasn't used \"/start\" yet")
        return 0


@bot.message_handler(commands=['cards', 'start'])
def create_cards(message):
    cid = message.chat.id
    if cid not in known_users:
        known_users.append(cid)
        user_1.add_users(engine, cid)
        userStep[cid] = 0
        bot.send_message(cid, 'Hello, stranger, let study English...')
    markup = types.ReplyKeyboardMarkup(row_width=2)

    global buttons
    buttons = []
    get_word = random.sample(user_1.get_words(engine, cid), 4)
    word = get_word[0]
    target_word = word[0]  # брать из БД
    translate = word[1]  # брать из БД
    target_word_btn = types.KeyboardButton(target_word)
    buttons.append(target_word_btn)
    others = [word for word in get_word[1:]]  # брать из БД
    other_words_btns = [types.KeyboardButton(word) for word in others]
    buttons.extend(other_words_btns)
    random.shuffle(buttons)
    next_btn = types.KeyboardButton(Command.NEXT)
    add_word_btn = types.KeyboardButton(Command.ADD_WORD)
    delete_word_btn = types.KeyboardButton(Command.DELETE_WORD)
    buttons.extend([next_btn, add_word_btn, delete_word_btn])

    markup.add(*buttons)

    greeting = f'Выбери перевод слова:\n🇷🇺 {translate}'
    bot.send_message(message.chat.id, greeting, reply_markup=markup)
    bot.set_state(message.from_user.id, MyStates.target_word, message.chat.id)
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['target_word'] = target_word
        data['translate_word'] = translate
        data['other_words'] = others


@bot.message_handler(func=lambda message: message.text == Command.NEXT)
def next_cards(message):
    create_cards(message)


@bot.message_handler(func=lambda message: message.text == Command.DELETE_WORD)
def delete_word(message):
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        print('Удаление', message.chat.id, data['target_word'])  # удалить из БД
        user_1.delete_words(engine, message.chat.id, data['target_word'])
        bot.send_message(message.chat.id, 'Слово удалено')


@bot.message_handler(func=lambda message: message.text == Command.ADD_WORD)
def add_word(message):
    cid = message.chat.id
    userStep[cid] = 1
    bot.send_message(cid, "Введите слово на английском")
    bot.set_state(message.from_user.id, MyStates.target_word, message.chat.id)
    print(message.text)  # сохранить в БД


@bot.message_handler(func=lambda message: True, content_types=['text'])
def message_reply(message):
    text = message.text
    markup = types.ReplyKeyboardMarkup(row_width=2)
    cid = message.chat.id

    if userStep[cid] == 0:
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            target_word = data['target_word']
            if text == target_word:
                hint = show_target(data)
                hint_text = ['Отлично!❤', hint]
                next_btn = types.KeyboardButton(Command.NEXT)
                add_word_btn = types.KeyboardButton(Command.ADD_WORD)
                delete_word_btn = types.KeyboardButton(Command.DELETE_WORD)
                buttons.extend([next_btn, add_word_btn, delete_word_btn])
                hint = show_hint(*hint_text)
            else:
                for btn in buttons:
                    if btn.text == text:
                        btn.text = text + '❌'
                        break
                hint = show_hint("Допущена ошибка!",
                                 f"Попробуй ещё раз вспомнить слово 🇷🇺{data['translate_word']}")
        markup.add(*buttons)
        bot.send_message(message.chat.id, hint, reply_markup=markup)
        create_cards(message)
    elif userStep[cid] == 1:
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['target_word'] = text
            bot.send_message(cid, "Введите перевод слова на русском")
            bot.set_state(message.from_user.id, MyStates.translate_word, message.chat.id)
            userStep[cid] = 2
    elif userStep[cid] == 2:
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['translate_word'] = text
            user_1.add_words(engine, cid, data['target_word'], data['translate_word'])
            bot.send_message(cid, 'Слово добавлено')
            userStep[cid] = 0
            create_cards(message)


bot.add_custom_filter(custom_filters.StateFilter(bot))


bot.infinity_polling(skip_pending=True)
