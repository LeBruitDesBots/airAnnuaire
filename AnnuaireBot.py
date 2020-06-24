#!/usr/bin/env python3
# encoding: utf-8

import json
import os
import sys
from datetime import date

from LogInfo import log_info
from Annuaire import Annuaire
from Subreddit import Subreddit


DIRNAME = os.path.dirname(__file__)


def main(update = True, output = True, config_path = 'config.json'):
    preferences, output_config = load_config(config_path)

    # browse save dir, load 2 latest annuaires
    files = []
    for f in os.listdir(os.path.join(DIRNAME, preferences['save_directory'])):
        fullpath = os.path.join(DIRNAME, preferences['save_directory'], f)
        if os.path.isfile(fullpath):
            files.append(fullpath)
    files.sort(key=lambda f: os.path.getmtime(f),
               reverse=True)

    if len(files) > 1:
        current = Annuaire.load_from_json(files[0])
        reference = Annuaire.load_from_json(files[1])
    elif len(files) == 1:
        current = Annuaire.load_from_json(files[0])
        reference = None
    else:
        current = Annuaire()
        reference = None

    if update:
        current.login(log_info)
        current.process_sub_list(os.path.join(DIRNAME, 
                                              preferences['sub_list']))
        current.auto_update()
        current.save_to_json(os.path.join(DIRNAME, 
                                          preferences['save_directory'], 
                                          date.today().isoformat()))

    if output: 
        current.export_md(output_config,
                          os.path.join(DIRNAME, preferences['output_directory']))


#    annuaire = Annuaire(log_info) 
#    annuaire.process_sub_list(os.path.join(dirname, 'test_list.txt'))
#    annuaire.auto_update()
#    annuaire.save_to_json(os.path.join(dirname, 'json_dumps/test_lang.json'))

#    annuaire = Annuaire.load_from_json(os.path.join(dirname, 'json_dumps/test_lang.json'))

#    for sub in annuaire.subreddits:
#        print(sub.get_langs(0.1))
#    with open(os.path.join(dirname, 'config.json'), 'r', encoding='utf-8') as f:
#        config = json.load(f)

#    annuaire.export_md(config)

def load_config(filename = 'config.json'):
    try:
        with open(filename, 'r', encoding="utf-8") as f:
            config = json.load(f)
    except FileNotFoundError:
        with open(os.path.join(DIRNAME, filename)) as f:
            config = json.load(f)

    return (config['preferences'], config['outputs'])
    


if __name__ == '__main__':
    main()