import logging
import random

from pony.orm import db_session
from models import UserState, Registration
import vk_api
from vkbot import handlers
try:
    import vkbot.settings as settings
except ImportError:
    exit('Необходимо создать файл settings.py с параметрами TOKEN, GROUP_ID, INTENTS')
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType

log = logging.getLogger('Bot')

def configure_logging():
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(logging.Formatter('%(levelname)s %(message)s'))
    stream_handler.setLevel(logging.INFO)
    log.addHandler(stream_handler)

    file_handler = logging.FileHandler('bot.log', mode='w', encoding='utf-8')
    file_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(message)s'))
    file_handler.setLevel(logging.DEBUG)
    log.addHandler(file_handler)
    log.setLevel(logging.DEBUG)

class Bot:
    """
    Сценарий регистрации на конференцию через Vk.com.

    Поддерживает ответы на вопросы про дату, место проведения и сценарий регистрации:
    - спрашивает имя
    - спрашивает email
    - говорим об успешной регистрации
    Если шаг не пройден, задаем вопрос пока шаг не будет пройден.
    Echo bot для vk.com
    Use python 3.12
    """

    def __init__(self, group_id, token):
        """
        :param group_id: group id из группы vk
        :param token: секретный токен
        """
        self.group_id = group_id
        self.token = token
        self.vk = vk_api.VkApi(token=token)
        self.long_poller = VkBotLongPoll(self.vk, self.group_id)
        self.api = self.vk.get_api()

    def run(self):
        for event in self.long_poller.listen():
            """Запуск Бота"""
            try:
                log.debug('Получено событие: %s', event)
                self.on_event(event, settings)
            except Exception:
                log.exception('Ошибка в обработке события')

    @db_session
    def on_event(self, event, settings):
        """Отправляет сообщение назад, если это текст

        :param event: VkBotMessageEvent Object
        :param settings: настройки бота
        :return: None
        """
        if event.type != VkBotEventType.MESSAGE_NEW:
            log.info('Мы пока не умеем обрабатывать событие такого типа %s', event.type)
            return

        user_id = str(event.object['message']['peer_id'])  # Приведение user_id к строке
        text = event.object.get('message', {}).get('text')
        state = UserState.get(user_id=user_id)

        if state is not None:
            text_to_send = self.continue_scenario(text, state)
        else:
            for intent in settings.INTENTS:
                log.debug(f'User gets {intent}')
                if any(token in text for token in intent['tokens']):
                    if intent['answer']:
                        text_to_send = intent['answer']
                    else:
                        text_to_send = self.start_scenario(user_id, intent['scenario'])
                    break
            else:
                text_to_send = settings.DEFAULT_ANSWER
        self.api.messages.send(
            message=text_to_send,
            random_id=random.randint(0, 2 ** 20),
            peer_id=user_id,
        )

    def start_scenario(self, user_id, scenario_name):
        scenario = settings.SCENARIOS[scenario_name]
        first_step = scenario['first_step']
        step = scenario['steps'][first_step]
        text_to_send = step['text']
        UserState(user_id=str(user_id), scenario_name=scenario_name, step_name=first_step, context={})
        return text_to_send

    def continue_scenario(self, text, state):
        steps = settings.SCENARIOS[state.scenario_name]['steps']
        step = steps[state.step_name]
        handler = getattr(handlers, step['handler'])

        if handler(text, context=state.context):
            next_step = steps[step['next_step']]
            text_to_send = next_step['text'].format(**state.context)
            if next_step['next_step']:
                state.step_name = step['next_step']
            else:
                if 'name' in state.context and 'email' in state.context:
                    log.info('Зарегистрирован: {name} {email}'.format(**state.context))
                else:
                    log.warning('Попытка завершить регистрацию без всех данных.')
                Registration(name=state.context['name'], email=state.context['email'])
                state.delete()
        else:
            text_to_send = step['failure_text'].format(**state.context)
        return text_to_send

if __name__ == '__main__':
    configure_logging()
    bot = Bot(group_id=settings.GROUP_ID, token=settings.TOKEN)
    bot.run()
