import random

import vk_api
import vk_api.bot_longpoll
from config import token

group_id = 221518988


class Bot:
    def __init__(self, group_id, token):
        self.group_id = group_id
        self.token = token
        self.vk = vk_api.VkApi(token=token)
        self.long_poller = vk_api.bot_longpoll.VkBotLongPoll(self.vk, self.group_id)
        self.api = self.vk.get_api()

    def run(self):
        for event in self.long_poller.listen():
            try:
                self.on_event(event)
            except Exception as exc:
                print(exc)

    def on_event(self, event):
        if event.type == vk_api.bot_longpoll.VkBotEventType.MESSAGE_NEW:
            print(event.object.text)
            self.api.messages.send(
                message=event.object.text,
                random_id=random.randint(0, 2 ** 20)
            peer_id = event.object.peer_id)
            else:
            print('Мы пока не умеем обрабатывать событие такого типа', event.type)


if __name__ == '__main__':
    bot = Bot(group_id, token)
    bot.run()
