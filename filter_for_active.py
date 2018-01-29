import json
import logging

import pandas as pd

# set up logging
formatter = logging.Formatter('%(asctime)s : %(name)s :: %(levelname)s : %(message)s')
logger = logging.getLogger('main')
logger.setLevel(logging.DEBUG)
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)
console_handler.setLevel(logging.DEBUG)
logger.debug('started')


# read the input filename from a JSON file
settings_file = './settings.json'
logger.debug('settings file : %s' % settings_file)
with open(settings_file, 'r') as settings_fp:
    settings = json.load(settings_fp)

logger.debug('settings: %s' % settings)

# let's do everything to get our filter data before we load anything else
filter_file = settings['filter_file']
logger.debug('filter file: %s' % filter_file)
filter_sheet_name = settings['filter_sheet_name']
logger.debug('filter sheet name: %s' % filter_sheet_name)
filter_data = pd.read_excel(filter_file, sheet_name=filter_sheet_name)

logger.debug(filter_data.head())

# now let's load the big input file
input_file = settings['input_file']
logger.debug('input file: %s' % input_file)
