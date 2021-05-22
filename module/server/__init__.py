"""Contains message templates"""
import os
from json import load

with open((os.path.join(os.path.dirname(__file__), "static", "messages.json"))) as messages:
    messages = load(messages)
