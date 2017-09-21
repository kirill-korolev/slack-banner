from slacker import Slacker
from slacker import Error

slack_client: Slacker = None

def init(api_key):
    global slack_client
    slack_client = Slacker(api_key)

def delete_message(channel, ts):
    try:
        slack_client.chat.delete(channel=channel, ts=ts, as_user=True)
        print("Message was deleted")
    except Error as exc:
        print("Unable to delete message Reason: {0}".format(exc))

def send_message(user_id, text):
    try:
        slack_client.chat.post_message(user_id,
                                       text,
                                       as_user=False)
        user_name = get_slack_name_by_id(user_id)
        print("Sent response to {0}".format(user_name))
    except Error as exc:
        print("Unable to send message to user by ID: {0}. Reason: {1}".format(user_id, exc))

def get_slack_name_by_id(user_id):
    try:
        return get_slack_user_by_id(user_id).get("real_name")
    except Error:
        return user_id


def get_slack_user_by_id(user_id):
    return slack_client.users.info(user_id).body['user']
