# encoding: utf-8

from enum import Enum
from datetime import datetime, timedelta
import math
import pprint
from prawcore import exceptions
import langdetect


DAYS_IN_WEEK = 7
DAYS_IN_MONTH = 28

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
        self.post_in_month = None
        self.comments_in_week = None
        self.languages = dict()
        # Manual properties
        self.tags = list()
        
        self.display_name = ''
        self.auto_updated = None
        self.manu_updated = None

    def auto_update(self, reddit, post_limit=100, comment_limit=1000):
        """Automatically crawl the subreddit to update all possible info
        
        parameters:
            reddit: a praw instance
            post_limit: upper limit of posts parsed for activity metrics
            comment_limit: upper limit of comments parsed for activity metrics"""
        # FIXME: parse latest posts and comments for activity metrics
        try:
            sub = reddit.subreddit(self.name)
        except (exceptions.NotFound, exceptions.Redirect):
            self.status = SubredditStatus.DOESNT_EXIST
            return 

        self._set_status(sub)

        if self.status not in [SubredditStatus.PUBLIC, SubredditStatus.RESTRICTED]:
            return

        self.is_nsfw = sub.over18
        self.subscriber_count = sub.subscribers
        self.created_utc = sub.created_utc
        self.description = sub.public_description
        self.official_lang = sub.lang
        self.moderators = [mod.name for mod in sub.moderator()]
        
        
        self._analyse_submissions(sub, post_limit)
        self._analyse_comments(sub, comment_limit)

        return 

    def _set_status(self, praw_sub):
        try:
            subreddit_type = praw_sub.subreddit_type
        except exceptions.NotFound:
            self.status = SubredditStatus.BANNED
            return
        except exceptions.Forbidden:
            # FIXME: Also catches quarantined subs - find a way to differentiate
            # quarantined and private subs.
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
        return

    def _analyse_submissions(self, praw_sub, post_limit):
        post_count = 0
        limit_reached = False
        elapsed = None

        for submission in praw_sub.new(limit=post_limit):
            limit_reached = True
            elapsed = datetime.now() - datetime.fromtimestamp(submission.created_utc)
            if elapsed.days > DAYS_IN_MONTH:
                limit_reached = False
                break
            
            post_count += 1
            self._analyse_lang(submission.title)

        if limit_reached:
            # extrapolate post count over DAYS_IN_MONTH period
            reference_delta = timedelta(days=DAYS_IN_MONTH)
            post_count = post_count * reference_delta.total_seconds() / elapsed.total_seconds()
        
        self.post_in_month = post_count
        return

    def _analyse_comments(self, praw_sub, comment_limit):
        comment_count = 0
        limit_reached = False
        elapsed = None

        for comment in praw_sub.comments(limit=comment_limit):
            limit_reached = True
            elapsed = datetime.now() - datetime.fromtimestamp(comment.created_utc)
            if elapsed.days > DAYS_IN_WEEK:
                limit_reached = False
                break
            
            comment_count += 1
            self._analyse_lang(comment.body)

        if limit_reached:
            # extrapolate post count over DAYS_IN_MONTH period
            reference_delta = timedelta(days=DAYS_IN_WEEK)
            comment_count = comment_count * reference_delta.total_seconds() / elapsed.total_seconds()
        
        self.comments_in_week = comment_count
        return

    def _analyse_lang(self, text):
        try:
            lang = langdetect.detect(text)
        except langdetect.lang_detect_exception.LangDetectException:
            return
        
        if lang in self.languages:
            self.languages[lang] += 1
        else:
            self.languages[lang] = 1

    def get_post_activity_score(self):
        if self.post_in_month is None:
            return None
        return math.log10(1+self.post_in_month * 9)

    def get_comment_activity_score(self):
        if self.comments_in_week is None:
            return None
        return math.log10(1+self.comments_in_week * 9)

    def get_activity_score(self):
        post_score = self.get_post_activity_score()
        comment_score = self.get_comment_activity_score()
        if post_score is None or comment_score is None:
            return
        return post_score + comment_score

    def get_langs(self, threshold):
        val = []
        total = sum(self.languages.values())
        for lang, count in self.languages.items():
            if (count / total) > threshold:
                val.append(lang)
        return val

    def manu_update(self):
        pass

