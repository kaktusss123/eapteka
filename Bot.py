import requests
import traceback
from json import dumps

from config import MY_ID


class BotHandler:

    def __init__(self, token):
        self.token = token
        self.api_url = "https://api.telegram.org/bot{}/".format(token)

    def get_updates(self, offset=None, timeout=30):
        """
        Get updates by longpoll
        :param offset: Offset for messages
        :param timeout: Timeout for longpolling
        :return: json with updates
        """
        method = 'getUpdates'
        params = {'timeout': timeout, 'offset': offset}
        resp = requests.get(self.api_url + method, params)
        result_json = resp.json()['result']
        return result_json

    def send_message(self, chat_id, text, keyboard=None):
        """
        Method for sending messages from bot to user
        :param chat_id: Chat id
        :param text: Text of message
        :param keyboard: (Optional) json keyboard
        :return: response
        """
        params = {'chat_id': chat_id, 'text': text, 'reply_markup': keyboard, 'parse_mode': 'Markdown'}
        method = 'sendMessage'
        resp = requests.post(self.api_url + method, params)
        return resp

    def send_photo(self, chat_id, photo, caption, keyboard=None):
        params = {'chat_id': chat_id, 'photo': photo, 'caption': caption, 'reply_markup': keyboard}
        method = 'sendPhoto'
        resp = requests.post(self.api_url + method, params)
        return resp 


    def forward_message(self, chat_id, from_chat_id, message_id, disable_notification=False):
        """
        Method for forwarding messages user2user
        :param chat_id: Chat id
        :param from_chat_id: Forwarding chat id
        :param message_id: Message id
        :param disable_notification: (Optionally) If you want to disable notification
        :return: Response
        """
        params = {'chat_id': chat_id, 'from_chat_id': from_chat_id, 'message_id': message_id,
                  'disable_notification': disable_notification}
        method = 'forwardMessage'
        resp = requests.post(self.api_url + method, params)
        return resp

    def get_last_update(self):
        get_result = self.get_updates()

        if len(get_result) > 0:
            return get_result[-1]
        else:
            return self.get_last_update()

    def error(self, update):
        self.send_message(MY_ID, traceback.format_exc())
        self.send_message(MY_ID, dumps(update, ensure_ascii=False))
