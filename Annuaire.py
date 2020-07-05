# encoding: utf-8

import praw
from datetime import date, datetime
import jsonpickle
import json
import os

from Subreddit import Subreddit


class Annuaire:

    def __init__(self, log_info = None):
        self.subreddits = list()
        if log_info is None:
            self.reddit = None
        else:
            self.reddit = praw.Reddit(client_id=log_info['client_id'],
                                      client_secret=log_info['client_secret'],
                                      user_agent=log_info['user_agent'])

    def __getstate__(self):
        """Copy the instance's state and remove data that shouldn't be serialized"""
        state = self.__dict__.copy()
        # Remove the unpicklable entries.
        del state['reddit']
        return state
    
    def __setstate__(self, state):
        """restore an instance from a serialized state"""
        self.__dict__.update(state)


    def login(self, log_info_path):
        """Login into a praw instance"""
        with open(log_info_path, 'r', encoding="utf-8") as f:
            log_info = json.load(f)['reddit']
        self.reddit = praw.Reddit(client_id=log_info['client_id'],
                                  client_secret=log_info['client_secret'],
                                  user_agent=log_info['user_agent'])

    def _filter_check(self, sub, filters):
        pass_filters = True
        for f in filters:
            if f['type'] == 'whitelist':
                if f['key'] == 'status':
                    if sub.__dict__[f['key']].name not in f['value']:
                        pass_filters = False
                else:
                    if sub.__dict__[f['key']] not in f['value']:
                        pass_filters = False
            elif f['type'] == 'blacklist':
                if f['key'] == 'status':
                    if sub.__dict__[f['key']].name in f['value']:
                        pass_filters = False
                else:
                    if sub.__dict__[f['key']] in f['value']:
                        pass_filters = False
            elif f['type'] == 'min':
                if sub.__dict__[f['key']] < f['value']:
                    pass_filters = False
            elif f['type'] == 'max':
                if sub.__dict__[f['key']] > f['value']:
                    pass_filters = False
            else:
                raise Exception('invalid filter type in config file')
        return pass_filters

    def _check_update_threshold(self, sub, auto_update_frequencies):
        """Returns True if subreddit should be updated according to config file specifications,
        False otherwise"""
        if sub.auto_updated is None:
            return True
        today = date.today()
        for freq in auto_update_frequencies:
            if self._filter_check(sub, freq['filters']):
                return (date.today() - sub.auto_updated).days >= freq['days']
        return False

    def process_sub_list(self, path):

        with open(path, 'r') as f:
            for line in f.readlines():
                sub_name = line.strip()
                if not sub_name or sub_name.startswith('#'):
                    continue

                if not any([sub_name == s.name for s in self.subreddits]):
                    self.subreddits.append(Subreddit(sub_name))

 #   def auto_update(self, post_count=100, comment_count=1000, update_threshold = 0):
    def auto_update(self, config):
        """Automatically crawl the subreddits to update all possible info
        """
        today = date.today()
        for subreddit in self.subreddits:
            if self._check_update_threshold(subreddit, config['auto_update_frequency']):
                subreddit.auto_update(self.reddit)
                subreddit.auto_updated = today
            #debug
            print(subreddit.name)

    @staticmethod
    def load_from_json(path):
        """Load a jsonpickled annuaire from the given path"""
        with open(path, 'r') as f:
            return jsonpickle.decode(f.read())

    def save_to_json(self, path):
        """Export current annuaire to a jsonpickle format"""
        with open(path, 'w') as f:
            f.write(jsonpickle.encode(self,indent=2))

    def export_md(self, config, dirname, reference=None):
        """Export markdown files as specified in config file"""
        if not os.path.exists(dirname):
            os.makedirs(os.path.join(dirname))

        for output in config:
            sort_key = self._get_sort_key(output)
            sort_dir = True if (output['sort_direction'] == 'descending') else False
            self.subreddits.sort(key=sort_key, 
                                 reverse=sort_dir)
            if reference is not None:
                reference.subreddits.sort(key=sort_key,
                                          reverse=sort_dir)

            with open(os.path.join(dirname, output['file_name'],), 
                      'w', encoding='utf-8') as f:
                #write headers and separators
                for col in output['columns']:
                    f.write(f"|{col['header']}")
                f.write("|\n")
                for col in output['columns']:
                    f.write("|")
                    if 'align' in col:
                        if col['align'] == 'left':
                            f.write(":-")
                        elif col['align'] == 'right':
                            f.write("-:")
                        elif col['align'] == 'center':
                            f.write(":-:")
                        else:
                            f.write("-")
                    else:
                        f.write("-")
                f.write("|\n")

                index = 0
                for sub in self.subreddits:
                    # apply filters
                    if not self._filter_check(sub, output['filters']):
                        continue

                    index += 1
                    if output['limit'] > 0 and index > output['limit']:
                        break
                    #write column values
                    for col in output['columns']:
                        f.write("|")
                        f.write(self._format_col(col['value'], sub, index, reference))
                    f.write("|\n")
                    
    def _get_sort_key(self, output_config):
        if output_config['sort_key'] == 'name':
            return lambda s: s.name.lower()
        if output_config['sort_key'] == 'status':
            return lambda s: s.status.name
        if output_config['sort_key'] == 'total_score':
            return lambda s: s.get_activity_score()
        if output_config['sort_key'] == 'post_score':
            return lambda s: s.get_post_activity_score()
        if output_config['sort_key'] == 'comment_score':
            return lambda s: s.get_comment_activity_score()
            
        return lambda s : s.__dict__[output_config['sort_key']]
    
    def _format_col(self, value, sub, index, reference):
        return value.format(index = index,
                            status = str(sub.status),
                            name  = sub.name,
                            is_nsfw  = 'PSPLT' if sub.is_nsfw else '',
                            subscriber_count = sub.subscriber_count,
                            created_utc = sub.created_utc,
                            description = sub.description,
                            top_mod = sub.moderators[0] if sub.moderators else '',
                            all_mods = ', '.join(sub.moderators),
                            official_lang = sub.official_lang,
                            comments_raw = int(sub.comments_in_week),
                            posts_raw = int(sub.post_in_month),
                            comment_score = '{:.1f}'.format(sub.get_comment_activity_score()),
                            post_score = '{:.1f}'.format(sub.get_post_activity_score()),
                            total_score = '{:.1f}'.format(sub.get_activity_score()))
