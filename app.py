from flask import Flask
from flask import redirect
from flask import request
from flask import make_response

from urllib.parse import urlencode
import httplib2

import os
import json

from message_processor import MessageProcessor
import slack_utils
import utils

from contextlib import contextmanager

from banner import Banner

EVENT_API_FIELD_TYPE = "type"
EVENT_API_FIELD_CHALLENGE = "challenge"

EVENT_API_REQ_TYPE_URL_VERIFICATION = "url_verification"
EVENT_API_REQ_TYPE_EVENT = "event_callback"


SLACK_APP_API_KEY = "xoxb-241837748225-MZ9SgESli64vpVtUbbkWTMJR"

message_processor = MessageProcessor()
app = Flask(__name__)
banner = Banner()

class UnsupportedRequestException(BaseException):
    pass


def handle_errors(func):
    """Decorator for functions that take single request argument and return dict response."""
    def error_handling_wrapper(req):
        try:
            response = func(req)
            print("Responding:", response)
        except UnsupportedRequestException:
            print("UnsupportedRequestException:", req)
            response = make_response("Unsupported request %s" % req, 400)
        except Exception as exc:
            print("Exception", exc)
            response = make_response("Unknown error", 500)
        return response

    return error_handling_wrapper


def wrap_plain_json(func):
    """Make a proper response object of plain dict/json.
    Wraps function that takes single request argument and return dict response"""
    def json_wrapper(req):
        # main call performed here
        response_body_json = func(req)

        response_body = json.dumps(response_body_json)
        response = make_response(response_body)
        response.headers['Content-Type'] = 'application/json'
        return response

    return json_wrapper

@app.route('/webhook', methods=['POST', 'GET'])
def webhook():
    """Endpoint for event callbacks from slack"""
    req = request.get_json(silent=True, force=True)

    if req is None:
        return process_commands(dictionary=request.form)
    else:
        print("Got WebHook Request:", json.dumps(req, indent=4))
        return process_event_api_request(req)


def process_commands(dictionary: dict):
    user_id = dictionary['user_id']
    user_name = dictionary['user_name']
    command = dictionary['command']
    text = dictionary['text']

    if command == "/ban":
        return ban_command(user_executer=user_name, user_to_ban=text)
    elif command == "/add":
        return add_command(user_executer=user_name, user_to_add=text)
    return {}


def add_command(user_executer: str, user_to_add: str):
    success: bool = False

    with open('superadmins.txt', 'r') as file:
        for line in file:
            if user_executer == line.rstrip():
                success = True
                break
        file.close()


    if not success:
        return "Oops, something went wrong. Probably, you don't have permissions."
    else:
        converted_text = utils.get_user_name(user_to_add)

        if converted_text is None:
            return "Oops, something went wrong. Probably, you mistyped a command."
        else:
            print("{0} is converted!".format(converted_text))
            with open('superadmins.txt', 'a') as file:
                file.write("{0}\n".format(user_to_add))
                file.close()
            return "Admin has been successfully added to config."


def ban_command(user_executer: str, user_to_ban: str):

    success: bool = False

    with open('admins.txt', 'r') as file:
        for line in file:
            if user_executer == line.rstrip():
                success = True
                break
        file.close()


    if not success:
        return "Oops, something went wrong. Probably, you don't have permissions."
    else:
        converted_text = utils.get_user_name(user_to_ban)

        if converted_text is None:
            return "Oops, something went wrong. Probably, you mistyped a command."
        else:
            print("{0} is converted!".format(converted_text))
            res = message_processor.ban_with_command(user_name=converted_text)

            if res is True:
                if banner.ban(nickname=converted_text) is True:
                    return "{0} has been banned.".format(converted_text)
                else:
                    return "Cannot ban this user."
            else:
                return "Cannot ban this user."

@handle_errors
@wrap_plain_json
def process_event_api_request(req):
    request_type = req.get(EVENT_API_FIELD_TYPE)
    if request_type == EVENT_API_REQ_TYPE_URL_VERIFICATION:
        return process_handshake_request(req)
    elif request_type == EVENT_API_REQ_TYPE_EVENT:
        print("RETURNED FROM EVENT REQUEST")
        return process_event_request(req)
    else:
        raise UnsupportedRequestException

def process_handshake_request(req):
    """Process handshake request from Slack Events API"""
    return {"challenge": req.get(EVENT_API_FIELD_CHALLENGE)}


@contextmanager
def process_event_request(req):
    """Process even received request from Slack Events API"""
    message_processor.process_incoming_event(req)
    return {}


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    slack_utils.init(SLACK_APP_API_KEY)
    app.run(debug=False, port=port, host='0.0.0.0')