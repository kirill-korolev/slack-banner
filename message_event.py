from datetime import datetime
from enum import Enum

from cached_property import cached_property

FIELD_EVENT = "event"
FIELD_TIME = "event_ts"

EVENT_FIELD_TYPE = "type"
EVENT_TYPE_MESSAGE = "message"

EVENT_FIELD_CHANNEL = "channel"
EVENT_FIELD_SUBTYPE = "subtype"
EVENT_FIELD_TEXT = "text"
EVENT_FIELD_USER = "user"
EVENT_FIELD_MESSAGE = "message"
EVENT_FIELD_PREVIOUS_MESSAGE = "previous_message"


class EventSubtype(Enum):
    MESSAGE = ""
    MESSAGE_CHANGED = "message_changed"
    MESSAGE_DELETED = "message_deleted"


class MessageEvent:
    """Represent message from Slack chat"""

    @staticmethod
    def is_message_event(event_json):
        event = event_json.get(FIELD_EVENT)
        return event and MessageEvent._is_type_supported(event)

    @staticmethod
    def _is_type_supported(event):
        return MessageEvent._get_event_type(event) is not None

    @staticmethod
    def _get_event_type(event):
        if event.get(EVENT_FIELD_TYPE) != EVENT_TYPE_MESSAGE:
            return None

        subtype = None
        if EVENT_FIELD_TEXT in event and EVENT_FIELD_SUBTYPE not in event:  # subtype is absent in new message events
            subtype = EventSubtype.MESSAGE
        elif EVENT_FIELD_SUBTYPE in event:
            subtype_name = event.get(EVENT_FIELD_SUBTYPE)
            if subtype_name == EventSubtype.MESSAGE_CHANGED.value:
                subtype = EventSubtype.MESSAGE_CHANGED
            elif subtype_name == EventSubtype.MESSAGE_DELETED.value:
                subtype = EventSubtype.MESSAGE_DELETED

        return subtype

    def __init__(self, event_json):
        self.event_root = event_json
        self.event = event_json.get(FIELD_EVENT)

    @cached_property
    def channel(self):
        return self.event.get(EVENT_FIELD_CHANNEL)

    @cached_property
    def sender(self):
        if self.subtype == EventSubtype.MESSAGE:
            return self.event.get(EVENT_FIELD_USER)
        else:
            return self.event.get(EVENT_FIELD_PREVIOUS_MESSAGE).get(EVENT_FIELD_USER)

    @cached_property
    def text(self):
        if self.subtype == EventSubtype.MESSAGE:
            return self.event.get(EVENT_FIELD_TEXT)
        elif self.subtype == EventSubtype.MESSAGE_CHANGED:
            return self.event.get(EVENT_FIELD_MESSAGE).get(EVENT_FIELD_TEXT)
        elif self.subtype == EventSubtype.MESSAGE_DELETED:
            return None
        else:
            return None

    @cached_property
    def previous_text(self):
        if self.subtype == EventSubtype.MESSAGE:
            return None
        else:
            return self.event.get(EVENT_FIELD_PREVIOUS_MESSAGE).get(EVENT_FIELD_TEXT)

    @cached_property
    def subtype(self):
        return MessageEvent._get_event_type(self.event)

    @cached_property
    def time(self):
        return self.event_root.get(FIELD_EVENT).get(FIELD_TIME)