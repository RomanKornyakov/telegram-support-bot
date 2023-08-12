import aiogram
from aiogram import Dispatcher, Bot, types, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from db import Database

db = Database('')  # название файла базы данных

token = ''  # токен тг бота

bot = Bot(token=token, parse_mode='HTML')

storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

operators_chat =   # id чата операторов


class AddingData(StatesGroup):
    questions = State()
    answer = State()


class DeletingData(StatesGroup):
    id = State()


class ChangingData(StatesGroup):
    id = State()
    column = State()
    new_data = State()


class Feedback(StatesGroup):
    feedback = State()


class QuestionToOperator(StatesGroup):
    question = State()


class AnswerOperator(StatesGroup):
    question_id = State()
    user_id = State()
    answer = State()


buttons_list_help = [
    [
        KeyboardButton(text='О нас'),
        KeyboardButton(text='Наши контакты')
    ]
]
buttons_help = ReplyKeyboardMarkup(keyboard=buttons_list_help, resize_keyboard=True)  # кнопки

inlinebuttons_list_need_more_help = [
    [
        InlineKeyboardButton(text='Да', callback_data='need_more_help'),
        InlineKeyboardButton(text='Нет', callback_data='not_need_more_help')
    ]
]
inlinebuttons_need_more_help = InlineKeyboardMarkup(inline_keyboard=inlinebuttons_list_need_more_help)  # inline кнопки

inlinebuttons_list_need_operator = [
    [
        InlineKeyboardButton(text='Да', callback_data='need_operator'),
        InlineKeyboardButton(text='Нет', callback_data='not_need_operator')
    ]
]
inlinebuttons_need_operator = InlineKeyboardMarkup(inline_keyboard=inlinebuttons_list_need_operator)  # inline кнопки

inlinebuttons_list_change_feedback = [
    [
        InlineKeyboardButton(text='Да', callback_data='change_feedback'),
        InlineKeyboardButton(text='Нет', callback_data='not_change_feedback')
    ]
]
inlinebuttons_change_feedback = InlineKeyboardMarkup(inline_keyboard=inlinebuttons_list_change_feedback)  # inline кнопки

inlinebuttons_list_viewing_data = [
    [
        InlineKeyboardButton(text='support', callback_data='viewing_data_in_support'),
        InlineKeyboardButton(text='feedbacks', callback_data='viewing_data_in_feedbacks')
    ],
    [
        InlineKeyboardButton(text='user_questions_to_bot', callback_data='viewing_data_in_user_questions_to_bot'),
        InlineKeyboardButton(text='user_questions_to_operator', callback_data='viewing_data_in_user_questions_to_operator')
    ]
]
inlinebuttons_viewing_data = InlineKeyboardMarkup(inline_keyboard=inlinebuttons_list_viewing_data)  # inline кнопки

inlinebuttons_list_changing_data = [
    [
        InlineKeyboardButton(text='id', callback_data='changing_id_in_support'),
        InlineKeyboardButton(text='questions', callback_data='changing_questions_in_support'),
        InlineKeyboardButton(text='answer', callback_data='changing_answer_in_support')
    ]
]
inlinebuttons_changing_data = InlineKeyboardMarkup(inline_keyboard=inlinebuttons_list_changing_data)  # inline кнопки


@dp.message_handler(Text('Наши контакты'))
async def button_contacts(message: types.Message):
    if message.chat.id != operators_chat:
        await message.answer('Наш сайт: https://bot.ru/')


@dp.message_handler(Text('О нас'))
async def button_information_about_company(message: types.Message):
    if message.chat.id != operators_chat:
        await message.answer('Мы любим кодить.')


@dp.message_handler(commands=['add_data'])
async def command_add_data(message: types.Message):
    if message.chat.id == operators_chat:
        await message.answer('Введите данные для столбца questions.')
        await AddingData.questions.set()


@dp.message_handler(state=AddingData.questions)
async def adding_questions_to_support(message: types.Message, state: FSMContext):
    await state.update_data(questions=message.text)
    await message.answer('Введите данные для столбца answers.')
    await AddingData.next()


@dp.message_handler(state=AddingData.answer)
async def adding_answer_to_support(message: types.Message, state: FSMContext):
    await state.update_data(answer=message.text)
    data = await state.get_data()
    db.adding_data_to_support(data['questions'], data['answer'])  # добавление данных в таблицу support
    await message.answer('Данные добавлены.\n'
                         'Увидеть их можно, введя команду /view_data.')
    await state.finish()


@dp.message_handler(commands=['delete_data'])
async def command_delete_data(message: types.Message):
    if message.chat.id == operators_chat:
        await message.answer('Введите id строки, которую нужно удалить.')
        await DeletingData.id.set()


@dp.message_handler(state=DeletingData.id)
async def deleting_data(message: types.Message, state: FSMContext):
    await state.update_data(id=message.text)
    data = await state.get_data()
    db.deleting_data_from_support(data['id'])  # удаление данных из таблицы support
    await message.answer('Данные удалены.\n'
                         'Увидеть изменения можно, введя команду /view_data.')
    await state.finish()


@dp.message_handler(commands=['change_data'])
async def command_change_data(message: types.Message):
    if message.chat.id == operators_chat:
        await message.answer('Введите id строки, которую нужно изменить.')
        await ChangingData.id.set()


@dp.message_handler(state=ChangingData.id)
async def choosing_column(message: types.Message, state: FSMContext):
    await state.update_data(id=message.text)
    await message.answer('Выберите какие данные нужно изменить.',
                         reply_markup=inlinebuttons_changing_data)
    await ChangingData.next()


@dp.callback_query_handler(text='changing_id_in_support', state=ChangingData.column)
async def changing_id(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()

    id_list = [
        [
            InlineKeyboardButton(text='id', callback_data='id'),
        ]
    ]
    id = InlineKeyboardMarkup(inline_keyboard=id_list)
    await bot.edit_message_reply_markup(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        reply_markup=id)

    await state.update_data(column='id')
    await callback.message.answer('Введите новые данные.')
    await ChangingData.next()


@dp.callback_query_handler(text='changing_questions_in_support', state=ChangingData.column)
async def changing_questions(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()

    questions_list = [
        [
            InlineKeyboardButton(text='questions', callback_data='questions'),
        ]
    ]
    questions = InlineKeyboardMarkup(inline_keyboard=questions_list)
    await bot.edit_message_reply_markup(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        reply_markup=questions)

    await state.update_data(column='questions')
    await callback.message.answer('Введите новые данные.')
    await ChangingData.next()


@dp.callback_query_handler(text='changing_answer_in_support', state=ChangingData.column)
async def changing_answer(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()

    answer_list = [
        [
            InlineKeyboardButton(text='answer', callback_data='answer'),
        ]
    ]
    answer = InlineKeyboardMarkup(inline_keyboard=answer_list)
    await bot.edit_message_reply_markup(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        reply_markup=answer)

    await state.update_data(column='answer')
    await callback.message.answer('Введите новые данные.')
    await ChangingData.next()


@dp.message_handler(state=ChangingData.new_data)
async def changing_data(message: types.Message, state: FSMContext):
    await state.update_data(new_data=message.text)
    data = await state.get_data()
    if data['column'] == 'id':
        db.changing_id_in_support(data['new_data'], data['id'])  # изменение колонки id в таблице support
    elif data['column'] == 'questions':
        db.changing_questions_in_support(data['new_data'], data['id'])  # изменение колонки questions в таблице support
    elif data['column'] == 'answer':
        db.changing_answer_in_support(data['new_data'], data['id'])  # изменение колонки answer в таблице support
    else:
        await message.answer('Данные не изменены.')
    await message.answer('Данные изменены.\n'
                         'Увидеть изменения можно, введя команду /view_data.')
    await state.finish()


@dp.message_handler(commands=['view_data'])
async def command_view_data(message: types.Message):
    if message.chat.id == operators_chat:
        await message.answer('Выберите таблицу, в которой нужно посмотреть данные.',
                             reply_markup=inlinebuttons_viewing_data)


@dp.callback_query_handler(text='viewing_data_in_support')
async def viewing_data_in_support(callback: types.CallbackQuery):
    await callback.answer()

    support_list = [
        [
            InlineKeyboardButton(text='support', callback_data='support'),
        ]
    ]
    support = InlineKeyboardMarkup(inline_keyboard=support_list)
    await bot.edit_message_reply_markup(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        reply_markup=support)

    data = ''
    for row in db.viewing_data_in_support():  # создание сообщения с данными
        data += f'{str(row)}\n\n'

    await callback.message.answer(data[:-2])  # отправка данных из таблицы support


@dp.callback_query_handler(text='support')
async def inlinebutton_support(callback: types.CallbackQuery):
    await callback.answer()


@dp.callback_query_handler(text='viewing_data_in_feedbacks')
async def viewing_data_in_feedbacks(callback: types.CallbackQuery):
    await callback.answer()

    feedbacks_list = [
        [
            InlineKeyboardButton(text='feedbacks', callback_data='feedbacks'),
        ]
    ]
    feedbacks = InlineKeyboardMarkup(inline_keyboard=feedbacks_list)
    await bot.edit_message_reply_markup(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        reply_markup=feedbacks)

    data = ''
    for row in db.viewing_data_in_feedbacks():  # создание сообщения с данными
        data += f'{str(row)}\n\n'

    await callback.message.answer(data[:-2])  # отправка данных из таблицы feedbacks


@dp.callback_query_handler(text='feedbacks')
async def inlinebutton_feedbacks(callback: types.CallbackQuery):
    await callback.answer()


@dp.callback_query_handler(text='viewing_data_in_user_questions_to_bot')
async def viewing_data_in_user_questions_to_bot(callback: types.CallbackQuery):
    await callback.answer()

    user_questions_to_bot_list = [
        [
            InlineKeyboardButton(text='user_questions_to_bot', callback_data='user_questions_to_bot'),
        ]
    ]
    user_questions_to_bot = InlineKeyboardMarkup(inline_keyboard=user_questions_to_bot_list)
    await bot.edit_message_reply_markup(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        reply_markup=user_questions_to_bot)

    data = ''
    for row in db.viewing_data_in_user_questions_to_bot():  # создание сообщения с данными
        data += f'{str(row)}\n\n'

    await callback.message.answer(data[:-2])  # отправка данных из таблицы user_questions_to_bot


@dp.callback_query_handler(text='user_questions_to_bot')
async def inlinebutton_user_questions_to_bot(callback: types.CallbackQuery):
    await callback.answer()


@dp.callback_query_handler(text='viewing_data_in_user_questions_to_operator')
async def viewing_data_in_user_questions_to_operator(callback: types.CallbackQuery):
    await callback.answer()

    user_questions_to_operator_list = [
        [
            InlineKeyboardButton(text='user_questions_to_operator', callback_data='user_questions_to_operator'),
        ]
    ]
    user_questions_to_operator = InlineKeyboardMarkup(inline_keyboard=user_questions_to_operator_list)
    await bot.edit_message_reply_markup(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        reply_markup=user_questions_to_operator)

    data = ''
    for row in db.viewing_data_in_user_questions_to_operator():  # создание сообщения с данными
        data += f'{str(row)}\n\n'

    await callback.message.answer(data[:-2])  # отправка данных из таблицы user_questions_to_operator


@dp.callback_query_handler(text='user_questions_to_operator')
async def inlinebutton_user_questions_to_operator(callback: types.CallbackQuery):
    await callback.answer()


@dp.message_handler(commands=['feedback'])
async def command_feedback(message: types.Message):
    if db.check_number_of_feedbacks(message.chat.id):
        await message.answer('Напишите пожалуйста свой отзыв о работе бота.')
        await Feedback.feedback.set()
    else:
        await message.answer(f'Вы уже писали отзыв. Вот ваш прошлый отзыв:\n{db.getting_feedback(message.chat.id)}\n\nХотите изменить его?',
                             reply_markup=inlinebuttons_change_feedback)


@dp.message_handler(state=Feedback.feedback)
async def sending_feedback_to_operator(message: types.Message, state: FSMContext):
    await state.update_data(feedback=message.text)
    data = await state.get_data()
    if db.check_number_of_feedbacks(message.chat.id):
        await bot.send_message(operators_chat, f'Новый отзыв от @{message.chat.username}:\n{data["feedback"]}')  # отправка отзыва в чат операторов
        await message.answer('Спасибо за Ваш отзыв!')
        db.auto_adding_feedbacks(message.chat.id, f'@{message.chat.username}', data['feedback'])  # добавление отзыва в базу данных
    else:
        await bot.send_message(operators_chat, f'Новый изменённый отзыв от @{message.chat.username}:\n{data["feedback"]}')  # отправка отзыва в чат операторов
        await message.answer('Отзыв был изменён.')
        db.auto_changing_feedbacks(message.chat.id, data['feedback'])  # изменение отзыва в базе данных
    await bot.send_message(operators_chat,
                           'Отзыв добавлен в базу. Увидеть это можно, введя команду /view_data')
    await state.finish()


@dp.callback_query_handler(text='change_feedback')
async def inlinebutton_change_feedback(callback: types.CallbackQuery):
    await callback.answer()

    yes_list = [
        [
            InlineKeyboardButton(text='Да', callback_data='yes'),
        ]
    ]
    yes = InlineKeyboardMarkup(inline_keyboard=yes_list)
    await bot.edit_message_reply_markup(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        reply_markup=yes)

    await callback.message.answer('Напишите отзыв.')
    await Feedback.feedback.set()


@dp.callback_query_handler(text='not_change_feedback')
async def inlinebutton_not_change_feedback(callback: types.CallbackQuery):
    await callback.answer()

    no_list = [
        [
            InlineKeyboardButton(text='Нет', callback_data='no'),
        ]
    ]
    no = InlineKeyboardMarkup(inline_keyboard=no_list)
    await bot.edit_message_reply_markup(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        reply_markup=no)


@dp.message_handler(commands=['operator'])
async def command_operator(message: types.Message):
    await message.answer('Введите свой вопрос к оператору. Когда он подключится, он вам ответит.')
    await QuestionToOperator.question.set()


@dp.message_handler(state=QuestionToOperator.question)
async def sending_question_to_operator(message: types.Message, state: FSMContext):
    await state.update_data(question=message.text)
    data = await state.get_data()
    await message.answer('Ожидайте, оператор скоро ответит.')
    await bot.send_message(operators_chat, f'Новый ВОПРОС К ОПЕРАТОРУ:\n{data["question"]}\n\n'
                                           f'id вопроса в базе данных - <code>{db.auto_adding_user_questions_to_operator(message.chat.id, message.chat.username, data["question"])}</code>,\n'
                                           f'имя пользователя - @{message.chat.username},\n'
                                           f'id пользователя - <code>{message.chat.id}</code>,\n'
                                           f'Команда - /answer_operator')    # отправка вопроса пользователя в чат операторов и добавление вопроса в базу данных
    await state.finish()


@dp.message_handler(commands=['answer_operator'])
async def command_answer_operator(message: types.Message):
    if message.chat.id == operators_chat:
        await message.answer('Введите id вопроса в базе данных.')
        await AnswerOperator.next()


@dp.message_handler(state=AnswerOperator.question_id)
async def entering_user_id(message: types.Message, state: FSMContext):
    await state.update_data(question_id=message.text)
    await message.answer('Введите id пользователя')
    await AnswerOperator.next()


@dp.message_handler(state=AnswerOperator.user_id)
async def entering_answer_to_user(message: types.Message, state: FSMContext):
    await state.update_data(user_id=message.text)
    await message.answer('Введите ответ')
    await AnswerOperator.next()


@dp.message_handler(state=AnswerOperator.answer)
async def sending_answer_to_user(message: types.Message, state: FSMContext):
    await state.update_data(answer=message.text)
    data = await state.get_data()
    try:
        await bot.forward_message(data['user_id'], message.chat.id, message.message_id)  # отправка ответа оператора на вопрос пользователя
        db.auto_adding_answer_operator(data['question_id'], data['answer'])  # добавление ответа оператора на вопрос пользователя в базу данных

        await bot.send_message(data['user_id'], 'Вам нужна ещё помощь оператора?', reply_markup=inlinebuttons_need_more_help)
    except aiogram.utils.exceptions.ChatNotFound:
        await bot.send_message(operators_chat, 'Неправильно введено id!')
    finally:
        await state.finish()


@dp.callback_query_handler(text='need_more_help')
async def inlinebutton_need_help(callback: types.CallbackQuery):
    await callback.answer()

    yes_list = [
        [
            InlineKeyboardButton(text='Да', callback_data='yes'),
        ]
    ]
    yes = InlineKeyboardMarkup(inline_keyboard=yes_list)
    await bot.edit_message_reply_markup(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        reply_markup=yes)

    await callback.message.answer('Задавайте свой вопрос.')
    await QuestionToOperator.question.set()


@dp.callback_query_handler(text='not_need_more_help')
async def inlinebutton_not_need_help(callback: types.CallbackQuery):
    await callback.answer()

    no_list = [
        [
            InlineKeyboardButton(text='Нет', callback_data='no'),
        ]
    ]
    no = InlineKeyboardMarkup(inline_keyboard=no_list)
    await bot.edit_message_reply_markup(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        reply_markup=no)

    await callback.message.answer('Тогда можете задавать вопрос мне.')


@dp.callback_query_handler(text='need_operator')
async def inlinebutton_need_operator(callback: types.CallbackQuery):
    await callback.answer()

    yes_list = [
        [
            InlineKeyboardButton(text='Да', callback_data='yes'),
        ]
    ]
    yes = InlineKeyboardMarkup(inline_keyboard=yes_list)
    await bot.edit_message_reply_markup(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        reply_markup=yes)

    await callback.message.answer('Введите свой вопрос к оператору. Когда он подключится, он вам ответит.')
    await QuestionToOperator.question.set()


@dp.callback_query_handler(text='not_need_operator')
async def inlinebutton_not_need_operator(callback: types.CallbackQuery):
    await callback.answer()

    no_list = [
        [
            InlineKeyboardButton(text='Нет', callback_data='no')
        ]
    ]
    no = InlineKeyboardMarkup(inline_keyboard=no_list)
    await bot.edit_message_reply_markup(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        reply_markup=no)

    await callback.message.answer('Тогда можете задать мне другой вопрос.')


@dp.callback_query_handler(text='yes')
async def inlinebutton_yes(callback: types.CallbackQuery):
    await callback.answer()


@dp.callback_query_handler(text='no')
async def inlinebutton_no(callback: types.CallbackQuery):
    await callback.answer()
