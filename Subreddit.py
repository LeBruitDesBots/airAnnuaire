# encoding: utf-8

from enum import Enum
from datetime import datetime

class SubredditStatus(Enum):
    UNKNOWN = 1
    ACTIVE = 2
    EMPTY = 3
    PRIVATE = 4

class Language(Enum):
    UNKNOWN = 1
    FRENCH = 2
    MULTILINGUAL = 3
    ENGLISH = 4
    OTHER = 5


class Subreddit:
    """A class to retrieve and store information about subreddits"""

    def __init__(self, name):
        self.name = name
        # Auto-retrieved properties
        self.status = SubredditStatus.UNKNOWN
        self.is_nsfw = False
        self.subscriber_count = 0
        self.created_utc = 0
        self.description = ''
        self.top_mod = ''
        # Manual properties
        self.language = Language.UNKNOWN
        self.tags = list()
        
        self.auto_updated = None
        self.manu_updated = None
