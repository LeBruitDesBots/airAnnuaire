#!/usr/bin/env python3
# encoding: utf-8

import praw
from LogInfo import log_info
from datetime import date
import jsonpickle

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
                if sub_name.startswith('#'):
                    continue

                if not any([sub_name == s.name for s in self.subreddits]):
                    self.subreddits.append(Subreddit(sub_name))

    def auto_update(self, post_count=100, comment_count=1000, update_threshold = 0):
        """Automatically crawl the subreddits to update all possible info
        
        parameters:
            post_count: upper limit of posts parsed for activity metrics
            comment_count: upper limit of comments parsed for activity metrics
            update_theshold: subreddits updated within less than this value (in days) will not be updated"""
        today = date.today
        for subreddit in self.subreddits:
            if (subreddit.auto_updated is not None 
                and (today - subreddit.auto_updated).days() >= update_threshold):
                continue
            subreddit.auto_update(self.reddit)
            subreddit.auto_updated = today

    @staticmethod
    def load_from_json(path):
        with open(path, 'r') as f:
            return jsonpickle.decode(f.read())

    def save_to_json(self, path):
        with open(path, 'w') as f:
            f.write(jsonpickle.encode(self,indent=2))

    def export_md(self, format):
        pass
    

def main():
    annuaire = Annuaire(log_info)

    annuaire.process_sub_list('/home/victor/Documents/source/airAnnuaire/test_list.txt')
    annuaire.auto_update()
    annuaire.save_to_json('/home/victor/Documents/source/airAnnuaire/test.json')

    annuaire2 = Annuaire.load_from_json('/home/victor/Documents/source/airAnnuaire/test.json')
    print('ga')


if __name__ == '__main__':
    main()