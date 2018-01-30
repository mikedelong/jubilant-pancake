import datetime
import json
import logging
import time

import numpy as np
import pandas as pd

start_time = time.time()


def make_date(arg_year, arg_day):
    year = 1900 + arg_year if arg_year > 50 else 2000 + arg_year
    result = datetime.date(year, 1, 1) + datetime.timedelta(days=int(arg_day))
    return result


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

input_heading_one = settings['input_heading_one']
input_heading_two = settings['input_heading_two']
input_heading_three = settings['input_heading_three']
converters = {input_heading_one: str, input_heading_two: str, input_heading_three: float}
data = pd.read_csv(input_file, converters=converters)
logger.debug('input file read complete.')

# we want to remove the second column because it doesn't tell us anything
data_columns = data.columns
logger.debug('our big data frame has column headers %s' % data.columns)

# todo reconcile this with the fact that our headings are data instead of code now
column_to_drop = data.columns[1]
date_column = data.columns[2]  # note that this is before we drop the column above
logger.debug('before looking for duplicates we are going to drop column %s' % column_to_drop)
data.drop(column_to_drop, axis=1, inplace=True)

# how many columns do we have before dropping?
logger.debug('before dropping duplicates we have shape %s ' % str(data.shape))
count_before = data.shape[0]

logger.debug('input heading two is %s' % input_heading_two)
logger.debug('date column is %s' % date_column)
do_drop_duplicates = False
if do_drop_duplicates:
    data.drop_duplicates(keep='first', inplace=True)
    logger.debug('after dropping duplicates we have shape %s ' % str(data.shape))
    count_after = data.shape[0]

    logger.debug('this means we have %d duplicate rows' % (count_before - count_after))

# now remove the rows where the date is zero
data.drop(data[data[input_heading_two] == '0'].index, inplace=True)
logger.debug('after dropping zero dates we have shape %s ' % str(data.shape))

# now add the date column
data['date'] = np.vectorize(make_date)((data[date_column].astype(int) / 1000).astype(int),
                                       (data[date_column].astype(int) % 1000).astype(int))

logger.debug(data.head())

logger.debug('done')
finish_time = time.time()
elapsed_hours, elapsed_remainder = divmod(finish_time - start_time, 3600)
elapsed_minutes, elapsed_seconds = divmod(elapsed_remainder, 60)
logger.info("Time: {:0>2}:{:0>2}:{:05.2f}".format(int(elapsed_hours), int(elapsed_minutes), elapsed_seconds))
