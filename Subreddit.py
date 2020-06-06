# encoding: utf-8

from enum import Enum
from datetime import datetime
import pprint
from prawcore import exceptions


class SubredditStatus(Enum):
    UNKNOWN = 0
    PUBLIC = 1
    RESTRICTED = 2
    QUARANTINED = 3
    PRIVATE = 4
    BANNED = 5
    DOESNT_EXIST = 6

    def __str__(self):
        return ['Statut inconnu',
                'Public',
                'Restreint',
                'En quarantaine',
                'Privé',
                'Banni',
                '404'][self.value]



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
        self.moderators = list()
        self.official_lang = ''
        self.post_per_month = None
        self.comments_per_month = None
        # Manual properties
        self.tags = list()
        
        self.display_name = ''
        self.auto_updated = None
        self.manu_updated = None

    def auto_update(self, reddit, post_count=100, comment_count=1000):
        """Automatically crawl the subreddit to update all possible info
        
        parameters:
            reddit: a praw instance
            post_count: upper limit of posts parsed for activity metrics
            comment_count: upper limit of comments parsed for activity metrics"""
        # FIXME: parse latest posts and comments for activity metrics
        try:
            sub = reddit.subreddit(self.name)
        except (exceptions.NotFound, exceptions.Redirect):
            self.status = SubredditStatus.DOESNT_EXIST
            return 

        # get basic sub info
        # potentially useful tags:
        # quarantine: bool
        # subreddit_type: string [public, ???]
        try:
            subreddit_type = sub.subreddit_type
        except exceptions.NotFound:
            self.status = SubredditStatus.BANNED
            return
        except exceptions.Forbidden:
            self.status = SubredditStatus.PRIVATE
            return
        except exceptions.Redirect:
            self.status = SubredditStatus.DOESNT_EXIST
            return
        else:
            if subreddit_type == 'public':
                self.status = SubredditStatus.PUBLIC
            elif subreddit_type == 'restricted':
                self.status = SubredditStatus.RESTRICTED
            else:
                self.status = SubredditStatus.UNKNOWN

        self.is_nsfw = sub.over18
        self.subscriber_count = sub.subscribers
        self.created_utc = sub.created_utc
        self.description = sub.public_description
        self.official_lang = sub.lang
        self.moderators = [mod.name for mod in sub.moderator()]
        # get latest posts

        # get latest comments

        return 

    def manu_update(self):
        pass

