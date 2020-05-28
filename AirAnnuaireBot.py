#!/usr/bin/env python3
# encoding: utf-8

import praw
from LogInfo import log_info
import json

from Subreddit import Subreddit


class Annuaire:

    def __init__(self, log_info = None):
        self.subreddits = list()
        if log_info is None:
            self.reddit = None
        else:
            self.reddit = praw.reddit(client_id=log_info['client_id'],
                                      client_secret=log_info['client_secret'],
                                      user_agent=['u/LeBruitDesBots indexing subreddits'])
    
    def process_sub_list(self, path):

        with open(path, 'r') as f:
            sub_name = f.readline()
            while sub_name:
                if sub_name.startswith('#'):
                    sub_name = f.readline()
                    continue

                if not any([sub_name == s.name for s in self.subreddits]):
                    self.subreddits.append(Subreddit(sub_name))

                sub_name = f.readline()



    def auto_update(self, path):
        pass

    def load_json(self, path):
        pass

    def save_json(self, path):
        pass

    def export_md(self, format):
        pass
    

def main():
    annuaire = Annuaire()

    annuaire.process_sub_list('/home/victor/Documents/source/airAnnuaire/test_list.txt')
    annuaire.process_sub_list('/home/victor/Documents/source/airAnnuaire/test_list.txt')

if __name__ == '__main__':
    main()