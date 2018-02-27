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
input_file = settings['input_file']

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
annual_output_file = settings['annual_output_file']
output_folder = settings['processed_folder']
full_annual_output_file = output_folder + annual_output_file
logger.debug('writing annual hours to %s' % full_annual_output_file)
annual.to_csv(full_annual_output_file)

# roll up all monthly data
monthly = data.groupby(['tail', data.date.dt.year, data.date.dt.month]).sum()
monthly.index.names = ['tail', 'year', 'month']
logger.debug(monthly.head(5))
monthly_output_file = settings['monthly_output_file']
full_monthly_output_file = output_folder + monthly_output_file
logger.debug('writing monthly hours to %s' % full_monthly_output_file)
monthly.to_csv(full_monthly_output_file)

logger.debug('done')
finish_time = time.time()
elapsed_hours, elapsed_remainder = divmod(finish_time - start_time, 3600)
elapsed_minutes, elapsed_seconds = divmod(elapsed_remainder, 60)
logger.info("Time: {:0>2}:{:0>2}:{:05.2f}".format(int(elapsed_hours), int(elapsed_minutes), elapsed_seconds))
