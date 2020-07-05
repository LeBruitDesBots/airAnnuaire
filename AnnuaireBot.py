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


def main(config_path = 'config.json'):
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
    
    process(current, reference,
            preferences, update_config, output_config)

def load_config(filename = 'config.json'):
    try:
        with open(filename, 'r', encoding="utf-8") as f:
            config = json.load(f)
    except FileNotFoundError:
        with open(os.path.join(DIRNAME, filename)) as f:
            config = json.load(f)

    return (config['preferences'], config['update'], config['outputs'])
    

def process(working_annuaire, reference_annuaire, 
            preferences, update_config, output_config):
    
    if preferences['update']:
        updated_flag = False
        if update_config['update_list']:
            working_annuaire.process_sub_list(os.path.join(DIRNAME, preferences['sub_list']))
            updated_flag = True
        if update_config['update_subs']:
            working_annuaire.login(os.path.join(DIRNAME, preferences['log_info_path']))
            working_annuaire.auto_update(update_config)
            updated_flag = True
        if updated_flag:
            working_annuaire.save_to_json(os.path.join(DIRNAME, 
                                                       preferences['save_directory'], 
                                                       date.today().isoformat()))
    
    if preferences['output']:
        working_annuaire.export_md(output_config,
                                   os.path.join(DIRNAME, preferences['output_directory'], date.today().isoformat()))

    


if __name__ == '__main__':
    main()