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

# read the input file into a data frame
# now let's load the big input file
input_file = settings['input_file']
logger.debug('input file: %s' % input_file)

data = pd.read_csv(input_file)
logger.debug('input file read complete.')

# we want to remove the second column because it doesn't tell us anything
column_to_drop = data.columns[1]
logger.debug('before looing for duplicates we are going to drop column %s' % column_to_drop)
data.drop(column_to_drop, axis=1, inplace=True)

# how many columns do we have before dropping?
logger.debug('before dropping duplicates we have shape %s ' % str(data.shape))

logger.debug('done')
finish_time = time.time()
elapsed_hours, elapsed_remainder = divmod(finish_time - start_time, 3600)
elapsed_minutes, elapsed_seconds = divmod(elapsed_remainder, 60)
logger.info("Time: {:0>2}:{:0>2}:{:05.2f}".format(int(elapsed_hours), int(elapsed_minutes), elapsed_seconds))
