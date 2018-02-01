import json
import logging
import time

import pandas as pd

start_time = time.time()

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

# todo fix these
input_folder = settings['output_folder']
input_file = 'nozeros.csv'

full_input_file = input_folder + input_file

logger.debug('reading input data from %s' % full_input_file)
data = pd.read_csv(full_input_file, parse_dates=['date'])
logger.debug('data read complete.')
logger.debug(data.columns)
logger.debug(data.head(5))
t0 = data[data[data.columns[0]] == data[data.columns[0]][0]]

t1 = t0.groupby(t0.date.dt.year).sum()
logger.debug(t1)
