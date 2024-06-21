import logging
import random

import vk_api
from config import token
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType

group_id = 221518988
log = logging.getLogger('Bot')

def configure_logging():
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(logging.Formatter('%(levelname)s %(message)s'))
    stream_handler.setLevel(logging.INFO)
    log.addHandler(stream_handler)

    file_handler = logging.FileHandler('bot.log')
    file_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(message)s'))
    file_handler.setLevel(logging.DEBUG)
    log.addHandler(file_handler)
    log.setLevel(logging.DEBUG)

class Bot:
    def __init__(self, group_id, token):
        self.group_id = group_id
        self.token = token
        self.vk = vk_api.VkApi(token=token)
        self.long_poller = VkBotLongPoll(self.vk, self.group_id)
        self.api = self.vk.get_api()

    def run(self):
        for event in self.long_poller.listen():
            try:
                log.debug('Получено событие: %s', event)
                self.on_event(event)
            except Exception:
                log.exception('Ошибка в обработке события')

    def on_event(self, event):
        if event.type == VkBotEventType.MESSAGE_NEW:
            self.handle_message_new(event)
        elif event.type == VkBotEventType.MESSAGE_REPLY:
            self.handle_message_reply(event)
        else:
            log.info('Мы пока не умеем обрабатывать событие такого типа %s', event.type)

    def handle_message_new(self, event):
        message = event.object.get('message', {})
        message_text = message.get('text')
        peer_id = message.get('peer_id')

        log.debug('Получено новое сообщение: %s', message)
        if message_text and peer_id:
            log.debug('Отправляем сообщение назад')
            self.api.messages.send(
                message=message_text,
                random_id=random.randint(0, 2 ** 20),
                peer_id=peer_id,
            )
        else:
            log.warning('Пустое сообщение или отсутствует peer_id. Сообщение не будет отправлено.')

    def handle_message_reply(self, event):
        log.info('Получен ответ на сообщение: %s', event.object)

if __name__ == '__main__':
    configure_logging()
    bot = Bot(group_id=group_id, token=token)
    bot.run()
