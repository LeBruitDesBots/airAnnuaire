#!/usr/bin/env python3
# encoding: utf-8

import praw
from LogInfo import log_info
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
                                      user_agent='u/LeBruitDesBots indexing subreddits')

    def __getstate__(self):
        """Copy the instance's state and remove data that shouldn't be serialized"""
        state = self.__dict__.copy()
        # Remove the unpicklable entries.
        del state['reddit']
        return state
    
    def __setstate__(self, state):
        """restore an instance from a serialized state"""
        self.__dict__.update(state)

    def process_sub_list(self, path):

        with open(path, 'r') as f:
            for line in f.readlines():
                sub_name = line.strip()
                if not sub_name or sub_name.startswith('#'):
                    continue

                if not any([sub_name == s.name for s in self.subreddits]):
                    self.subreddits.append(Subreddit(sub_name))

    def auto_update(self, post_count=100, comment_count=1000, update_threshold = 0):
        """Automatically crawl the subreddits to update all possible info
        
        parameters:
            post_count: upper limit of posts parsed for activity metrics
            comment_count: upper limit of comments parsed for activity metrics
            update_theshold: subreddits updated within less than this value (in days) will not be updated"""
        today = date.today()
        for subreddit in self.subreddits:
            if (subreddit.auto_updated is not None 
                and (today - subreddit.auto_updated).days() >= update_threshold):
                continue
            subreddit.auto_update(self.reddit)
            subreddit.auto_updated = today
            #debug
            print(subreddit.name)

    @staticmethod
    def load_from_json(path):
        with open(path, 'r') as f:
            return jsonpickle.decode(f.read())

    def save_to_json(self, path):
        with open(path, 'w') as f:
            f.write(jsonpickle.encode(self,indent=2))

    def export_md(self, config):
        for output in config['outputs']:
            sort_dir =  True if (output['sort_direction'] == 'descending') else False
            self.subreddits.sort(key=lambda s: s.__dict__[output['sort_key']], 
                                 reverse=sort_dir)
            with open(os.path.join(dirname, output['file_name']), 'w') as f:
                #headers
                for col in output['columns']:
                    f.write(f"|{col['header']}")
                f.write("|\n")
                for col in output['columns']:
                    f.write(f"|-")
                f.write("|\n")

                for sub in self.subreddits:
                    for col in output['columns']:
                        f.write(f"|{sub.__dict__[col['value']]}")
                    f.write("|\n")
    

def main():
#    annuaire = Annuaire(log_info) 
#    annuaire.process_sub_list(os.path.join(dirname, 'partial_list.txt'))
#    annuaire.auto_update()
#    annuaire.save_to_json(os.path.join(dirname, 'json_dumps/partial.json'))

    annuaire = Annuaire.load_from_json(os.path.join(dirname, 'json_dumps/partial.json'))

    with open(os.path.join(dirname, 'output config.json'), 'r') as f:
        config = json.load(f)

    annuaire.export_md(config)


dirname = os.path.dirname(__file__)
filename = os.path.join(dirname, 'relative/path/to/file/you/want')
if __name__ == '__main__':
    main()