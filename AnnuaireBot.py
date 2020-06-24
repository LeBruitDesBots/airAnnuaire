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
    preferences, update_config, output_config = load_config(config_path)

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
        current.auto_update(update_config)
        current.save_to_json(os.path.join(DIRNAME, 
                                          preferences['save_directory'], 
                                          date.today().isoformat()))

    if output: 
        current.export_md(output_config,
                          os.path.join(DIRNAME, preferences['output_directory']))



def load_config(filename = 'config.json'):
    try:
        with open(filename, 'r', encoding="utf-8") as f:
            config = json.load(f)
    except FileNotFoundError:
        with open(os.path.join(DIRNAME, filename)) as f:
            config = json.load(f)

    return (config['preferences'], config['update'], config['outputs'])
    


if __name__ == '__main__':
    main()