import logging
import random

import vk_api

try:
    from settings import TOKEN, GROUP_ID
except ImportError:
    exit('Необходимо создать файл settings.py с параметрами TOKEN и GROUP_ID')
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
    Echo bot для vk.com
    Use python 3.12
    """

    def __init__(self, GROUP_ID, TOKEN):
        """
        :param GROUP_ID: group id из группы vk
        :param TOKEN: секретный токен
        """
        self.group_id = GROUP_ID
        self.token = TOKEN
        self.vk = vk_api.VkApi(token=TOKEN)
        self.long_poller = VkBotLongPoll(self.vk, self.group_id)
        self.api = self.vk.get_api()

    def run(self):
        for event in self.long_poller.listen():
            """Запуск Бота"""
            try:
                log.debug('Получено событие: %s', event)
                self.on_event(event)
            except Exception:
                log.exception('Ошибка в обработке события')

    def on_event(self, event: VkBotEventType):
        """Отправляет сообщение назад, если это текст

        :param event: VkBotMessageEvent Object
        :return: None
        """
        if event.type == VkBotEventType.MESSAGE_NEW:
            log.debug('Отправляем сообщение назад')
            self.api.messages.send(
                message=event.object.get('message', {}).get('text'),
                random_id=random.randint(0, 2 ** 20),
                peer_id=event.object['message']['peer_id'],
            )
        else:
            log.info('Мы пока не умеем обрабатывать событие такого типа %s', event.type)


if __name__ == '__main__':
    configure_logging()
    bot = Bot(GROUP_ID=GROUP_ID, TOKEN=TOKEN)
    bot.run()
