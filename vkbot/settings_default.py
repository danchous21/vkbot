# GROUP_ID =
# TOKEN = ''
#
# INTENTS = [
#     {
#         "name": "Дата проведения",
#         "tokens": ("когда", "сколько", "дата", "дату"),
#         "scenario": None,
#         "answer": "Конференция проводится 15го апреля, регистрация начнется в 10 утра"
#     },
#     {
#         "name": "Место проведения",
#         "tokens": ("где", "место", "локация", "адрес", "метро"),
#         "scenario": None,
#         "answer": "Конференция пройдет в павильоне 18Г в Экспоцентре"
#     },
#     {
#         "name": "Регистрация",
#         "tokens": ("регистр", "добав"),
#         "scenario": "registration",
#         "answer": None
#     }
# ]
#
# SCENARIOS = {
#     "registration": {
#         "first_step": "step1",
#         "steps": {
#             "step1": {
#                 "text": "Чтобы зарегистрироваться, введите ваше имя. Оно будет написано на бейджике.",
#                 "failure_text": "Имя должно состоять из 3–30 букв и дефиса. Попробуйте еще раз",
#                 "handler": "handle_name",
#                 "next_step": "step2"
#             },
#             "step2": {
#                 "text": "Введите email. Мы отправим на него все данные.",
#                 "failure_text": "Во введенном адресе ошибка. Попробуйте еще раз",
#                 "handler": "handle_email",
#                 "next_step": "step3"
#             },
#             "step3": {
#                 "text": "Спасибо за регистрацию, {name}! Мы отправили на {email} билет, распечатайте его.",
#                 "failure_text": None,
#                 "handler": None,
#                 "next_step": None
#             }
#         }
#     }
# }
#
# DEFAULT_ANSWER = 'Пока не умею отвечать на это((('
#
# DB_CONFIG = dict(
# provider='postgres',
# user='postgres',
# password='',
# host='localhost',
# database='vk_chat_bot',
# client_encoding='UTF8')
