from fuzzywuzzy import fuzz


def comparison(question_user, questions_dict):
    min_match_percentage =   # какой должен быть минимальный процент совпадения вопроса пользователя с вопросом в базе данных
    max_match = {'id': '', 'percent': min_match_percentage}

    for key, value in questions_dict.items():  # сравнение вопроса пользователя с вопросами в базе данных
        for question in value:
            match_percentage = fuzz.WRatio(question_user, question)
            if match_percentage >= max_match['percent']:
                max_match['id'] = key
                max_match['percent'] = match_percentage

    return max_match['id']
