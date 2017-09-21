import slack_utils
from message_event import MessageEvent
from utils import *
from banner import Banner

KEYWORDS = ['Pre-sale Contract Address', 'Bitclave Pre-sale is open now', 'myetherwallet',
            'Important Notification from the ICO Security team', 'Please visit http', 'myetherwalletn']
CHANNEL_ID = 'C5W3120AX'

banner = Banner()

class MessageProcessor:
    """Process incoming message events and schedule response if required"""

    def __init__(self):
        pass

    def process_incoming_event(self, event_json):
        """:param event_json: json representing slack message.im event"""
        if not MessageEvent.is_message_event(event_json):
            print("Got hidden event")
            return

        event = MessageEvent(event_json)
        print("Got standard message: {0}".format(event.text))

        found_in_keywords = False
        found_wallet = False
        already_banned = False

        nickname = slack_utils.get_slack_user_by_id(event.sender)['name']

        print('Event channel %s' % event.channel)
        print('Event sender %s' % event.sender)
        print('Event nickname %s' % nickname)
        print('Event ts %s' % event.time)

        with open('banned.txt', 'r') as f:
            print("READ FROM FILE")
            for line in f:
                if line.rstrip() == nickname:
                    already_banned = True
                    break
            f.close()

        if not already_banned:
            for keyword in KEYWORDS:
                if is_keyword_in_string(keyword, event.text):
                    found_in_keywords = True
                    break

            if is_wallet_in_string(event.text) is True:
                found_wallet = True

            if found_in_keywords or found_wallet:

                if banner.ban(nickname=nickname) is True:
                    slack_utils.delete_message(event.channel, event.time)
                    slack_utils.send_message(event.channel, '<@%s> is a scammer. Unfortunately, has been banned.' % event.sender)

                    with open('banned.txt', 'a') as f:
                        f.write("{0}\n".format(nickname))
                        f.close()
                        print("WRITE TO FILE")


    def ban_with_command(self, user_name: str):

        already_banned = False

        with open('banned.txt', 'r') as f:
            print("READ FROM FILE")
            for line in f:
                if line.rstrip() == user_name:
                    already_banned = True
                    break
            f.close()

        if not already_banned:
            slack_utils.send_message(CHANNEL_ID, '<@%s> is a scammer. Unfortunately, has been banned.' % user_name)

            with open('banned.txt', 'a') as f:
                f.write("{0}\n".format(user_name))
                f.close()
                print("WRITE TO FILE")
            return True
        else:
            return False