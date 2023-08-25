from functions import *
from comparison import comparison


@dp.message_handler(commands=['start'])
async def start_message(message: types.Message):
    if message.chat.id != operators_chat:
        await message.answer('Добрый день! Чем могу помочь?\n'
                             'О функционале бота Вы можете узнать введя команду /help',
                             reply_markup=buttons_help)


@dp.message_handler(commands=['help'])
async def command_help(message: types.Message):
    if message.chat.id == operators_chat:
        await message.answer('Нужные команды:\n'
                             '/view_data - просмотр данных из таблиц\n'
                             '/add_data - добавление данных в таблицу support\n'
                             '/delete_data - удаление данных из таблицы support\n'
                             '/change_data - изменение данных в таблице support\n\n'
                             '/answer_operator - ответ на вопрос пользователя\n')
    else:
        await message.answer('Как же работает бот? Вы отправляете ему свой вопрос, и он отвечает на него. '
                             'Если вас не устраивает ответ бота, или если бот не смог ответить на ваш вопрос, '
                             'то вы можете позвать оператора командой /operator. Для вашего удобства в боте есть меню команд и кнопок.',
                             reply_markup=buttons_help)


@dp.message_handler()
async def answer_to_question(message: types.Message):  # ответ на вопрос пользователя
    if message.chat.id != operators_chat:
        try:
            answer_id = comparison(message.text, db.getting_questions())

            await message.answer(db.getting_answer(answer_id), reply_markup=buttons_help)
            db.auto_adding_user_questions_to_bot(message.chat.id, f'@{message.chat.username}', message.text,
                                                 db.getting_answer(answer_id))
        except TypeError:
            db.auto_adding_user_questions_to_bot(message.chat.id, f'@{message.chat.username}', message.text)
            await message.answer('Я не могу ответить на этот вопрос. Позвать оператора?', reply_markup=inlinebuttons_need_operator)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
    await message.answer('Бот работает!')
