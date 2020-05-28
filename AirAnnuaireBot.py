import praw
from LogInfo import log_info
import json

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
        pass

    def auto_update(self, path):
        pass

    def load_json(self, path):
        pass

    def save_json(self, path):
        pass

    def export_md(self, format):
        pass
    
