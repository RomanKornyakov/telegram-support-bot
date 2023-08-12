import sqlite3


class Database:
    def __init__(self, db_file):
        self.connection = sqlite3.connect(db_file)
        self.cursor = self.connection.cursor()

    def getting_questions(self):  # создание словаря с вопросами из базы данных
        with self.connection:
            result = self.cursor.execute('select id, questions from support', ()).fetchall()
            data = {}

            for row in result:
                questions = tuple(row[1].split('/'))
                data[row[0]] = questions

            return data

    def getting_answer(self, answer_id):  # получение ответа на вопрос пользователя
        with self.connection:
            return self.cursor.execute('select answer from support where id = ?', (answer_id,)).fetchone()[0]

    def viewing_data_in_support(self):  # просмотр данных в таблице support
        with self.connection:
            return self.cursor.execute('select * from support').fetchall()

    def viewing_data_in_feedbacks(self):  # просмотр данных в таблице feedbacks
        with self.connection:
            return self.cursor.execute('select * from feedbacks').fetchall()

    def viewing_data_in_user_questions_to_bot(self):  # просмотр данных в таблице user_questions_to_bot
        with self.connection:
            return self.cursor.execute('select * from user_questions_to_bot').fetchall()

    def viewing_data_in_user_questions_to_operator(self):  # просмотр данных в таблице user_questions_to_operator
        with self.connection:
            return self.cursor.execute('select * from user_questions_to_operator').fetchall()

    def auto_adding_feedbacks(self, user_id, username, feedback):  # автоматическое добавление отзывов в базу данных
        with self.connection:
            try:
                id = self.cursor.execute('select id from feedbacks').fetchall()[-1][0] + 1
            except IndexError:
                id = 1
            self.cursor.execute('insert into feedbacks values (?, ?, ?, ?)', (id, user_id, username, feedback))
            self.connection.commit()

    def check_number_of_feedbacks(self, user_id):
        feedbacks = self.cursor.execute('select user_id from feedbacks', ()).fetchall()
        for row in feedbacks:
            if user_id == row[0]:
                return False
        return True

    def getting_feedback(self, user_id):
        feedbacks = self.cursor.execute('select user_id, feedback from feedbacks', ()).fetchall()
        for row in feedbacks:
            if user_id == row[0]:
                return row[1]

    def auto_changing_feedbacks(self, user_id, new_feedback):
        with self.connection:
            self.cursor.execute('update feedbacks set feedback = ? where user_id = ?', (new_feedback, user_id))
            self.connection.commit()

    def auto_adding_user_questions_to_bot(self, user_id, username, question, answer_bot=None):  # автоматическое добавление вопросов от пользователей к боту в базу данных
        with self.connection:
            try:
                id = self.cursor.execute('select id from user_questions_to_bot').fetchall()[-1][0] + 1
            except IndexError:
                id = 1
            self.cursor.execute('insert into user_questions_to_bot values (?, ?, ?, ?, ?)', (id, user_id, username, question, answer_bot))
            self.connection.commit()

    def auto_adding_user_questions_to_operator(self, user_id, username, question, answer_operator=None):  # автоматическое добавление вопросов от пользователей к оператору в базу данных
        with self.connection:
            try:
                id = self.cursor.execute('select id from user_questions_to_operator').fetchall()[-1][0] + 1
            except IndexError:
                id = 1
            self.cursor.execute('insert into user_questions_to_operator values (?, ?, ?, ?, ?)', (id, user_id, username, question, answer_operator))
            self.connection.commit()
            return id

    def auto_adding_answer_operator(self, question_id, answer_operator):
        with self.connection:
            self.cursor.execute('update user_questions_to_operator set answer_operator = ? where id = ?', (answer_operator, question_id))
            self.connection.commit()

    def adding_data_to_support(self, questions, answer):  # добавление данных в таблицу support
        with self.connection:
            try:
                id = self.cursor.execute('select id from support').fetchall()[-1][0] + 1
            except IndexError:
                id = 1
            self.cursor.execute('insert into support values (?, ?, ?)', (id, questions, answer))
            self.connection.commit()

    def deleting_data_from_support(self, id):  # удаление данных из таблицы support
        with self.connection:
            self.cursor.execute('delete from support where id = ?', (id,))
            self.connection.commit()

    def changing_id_in_support(self, new_data, id):  # изменение колонки id в таблице support
        with self.connection:
            self.cursor.execute('update support set id = ? where id = ?', (new_data, id))
            self.connection.commit()

    def changing_questions_in_support(self, new_data, id):  # изменение колонки questions в таблице support
        with self.connection:
            self.cursor.execute('update support set questions = ? where id = ?', (new_data, id))
            self.connection.commit()

    def changing_answer_in_support(self, new_data, id):  # изменение колонки answer в таблице support
        with self.connection:
            self.cursor.execute('update support set answer = ? where id = ?', (new_data, id))
            self.connection.commit()
