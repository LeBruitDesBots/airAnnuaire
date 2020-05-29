#!/usr/bin/env python3
# encoding: utf-8

import praw
from LogInfo import log_info
import json
from datetime import date

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
    
    def process_sub_list(self, path):

        with open(path, 'r') as f:
            for line in f.readlines():
                sub_name = line.strip()
                if sub_name.startswith('#'):
                    continue

                if not any([sub_name == s.name for s in self.subreddits]):
                    self.subreddits.append(Subreddit(sub_name))






    def auto_update(self, post_count=100, comment_count=1000, update_threshold = 0):
        today = date.today
        for subreddit in self.subreddits:
            if (subreddit.auto_updated is not None 
                and (today - subreddit.auto_updated).days() >= update_threshold):
                continue
            subreddit.auto_update(self.reddit)
            subreddit.auto_updated = today

    def load_json(self, path):
        pass

    def save_json(self, path):
        pass

    def export_md(self, format):
        pass
    

def main():
    annuaire = Annuaire(log_info)

    annuaire.process_sub_list('/home/victor/Documents/source/airAnnuaire/test_list.txt')
    annuaire.auto_update()
    print('ga')


if __name__ == '__main__':
    main()