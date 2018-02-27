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
settings_file = './settings-sum.json'
logger.debug('settings file : %s' % settings_file)
with open(settings_file, 'r') as settings_fp:
    settings = json.load(settings_fp)

logger.debug('settings: %s' % settings)

input_folder = settings['processed_folder']
# todo fix this
input_file = 'nozeros.csv'

full_input_file = input_folder + input_file

logger.debug('reading input data from %s' % full_input_file)
data = pd.read_csv(full_input_file, parse_dates=['date'], index_col=['tail'])
logger.debug('data read complete.')
logger.debug('our data columns are %s and %s' % (data.columns.values[0], data.columns.values[1]))
logger.debug(data.head(5))

data = data.sort_values(['date'], ascending=[True])
# roll up all annual data
annual = data.groupby(['tail', data.date.dt.year]).sum()
logger.debug(annual.head(5))
annual.to_csv(settings['processed_folder'] + 'annual.csv')

# roll up all monthly data
monthly = data.groupby(['tail', data.date.dt.year, data.date.dt.month]).sum()
monthly.index.names = ['tail', 'year', 'month']
logger.debug(monthly.head(5))
monthly.to_csv(settings['processed_folder'] + 'monthly.csv')

logger.debug('done')
finish_time = time.time()
elapsed_hours, elapsed_remainder = divmod(finish_time - start_time, 3600)
elapsed_minutes, elapsed_seconds = divmod(elapsed_remainder, 60)
logger.info("Time: {:0>2}:{:0>2}:{:05.2f}".format(int(elapsed_hours), int(elapsed_minutes), elapsed_seconds))
