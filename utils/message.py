'''
    This file defines the blueprint for a message object.
'''
import json, datetime
from utils.file_handler import *

class Message:
    def __init__(self, sender_id, recipient_id, content, sender_role=None, recipient_role=None):
        self.sender_id = sender_id
        self.recipient_id = recipient_id
        self.content = content
        self.timestamp = datetime.datetime.now().isoformat()
        self.sender_role = sender_role
        self.recipient_role = recipient_role
    def send(self):
        try:
            messages = load_json("data/messages.json")
        except Exception:
            messages = []  # In case file is empty or doesn't exist

        messages.append(self.__dict__)
        save_json("data/messages.json", messages)
        
    @classmethod
    def load_all(cls):
        """Return a list of raw message dicts."""
        return load_json("data/messages.json") or []

    @classmethod
    def for_recipient(cls, recipient_id, sender_role=None):
        """
        Filter messages addressed to `recipient_id`.
        Optionally filter by sender role stored in each dict.
        """
        all_msgs = cls.load_all()
        filtered = [
            m for m in all_msgs
            if m.get("recipient_id") == recipient_id
            and (sender_role is None or m.get("sender_role") == sender_role)
        ]
        # Sort newest first
        return sorted(filtered, key=lambda m: m["timestamp"], reverse=True)

