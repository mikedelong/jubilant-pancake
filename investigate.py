import json
import logging
import time

import numpy as np
import pandas as pd

start_time = time.time()


def make_tail(arg_serial):
    arg_serial = arg_serial.strip()
    result = '-'.join([arg_serial[0:2], arg_serial[-4:]])
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
settings_file = './investigate.json'
logger.debug('settings file : %s' % settings_file)
with open(settings_file, 'r') as settings_fp:
    settings = json.load(settings_fp)

logger.debug('settings: %s' % settings)

# now let's load the big input file
input_folder = settings['input_folder']
logger.debug('input folder: %s' % input_folder)
input_file = settings['input_file']
logger.debug('input file: %s' % input_file)
full_input_file = input_folder + input_file
logger.debug('reading input data from %s' % full_input_file)

columns_to_use = settings['columns_to_use']
str_converters = settings['str_converters']
reference_date = settings['reference_date']
converters = dict()
for item in str_converters:
    converters[item] = str

data = pd.read_csv(full_input_file, converters=converters, skip_blank_lines=True, skipinitialspace=True,
                   usecols=columns_to_use)
logger.debug('read complete: columns are %s' % str(data.columns))
logger.debug('data shape is %d x %d' % data.shape)
for column in data.columns:
    unique_value_count = data[column].nunique()
    logger.debug('column %s has %d values and %d unique values.' % (column, len(data[column]), data[column].nunique()))
    if unique_value_count < 101:
        logger.debug('and here they are: %s' % data[column].unique())

serial = settings['serial']
# make the tail number
data['tail'] = np.vectorize(make_tail)(data[serial])

# now let's look for cases where we can fill in the year
bad_date_records = data[data[reference_date].astype(int) < 366]
logger.debug('rows with bad date have shape: %d x %d' % bad_date_records.shape)
year_field = settings['year_field']
logger.debug('Rows with bad dates have %s unique year-field values' % bad_date_records[year_field].unique())
logger.debug('Rows with bad dates have the following year-field value counts: %s' %
             bad_date_records[year_field].value_counts())
bad_date_year_valid = bad_date_records[bad_date_records[year_field].astype(int) > 1947]

zero_date_records = data[data[reference_date].astype(int) == 0]
logger.debug('rows with zero date have shape %d x %d' % zero_date_records.shape)
logger.debug('Rows with zero dates have the following year-field value counts: %s' %
             zero_date_records[year_field].value_counts())

if False:
    logger.debug('rows with bad date and not-null year have shape: %d x %d' % bad_date_year_valid.shape)
    month_field = settings['month_field']
    logger.debug('rows with bad date and not-null month have shape: %d x %d' % data[
        data[reference_date].astype(int) < 366 & ~data[month_field].empty].shape)
    logger.debug('rows with bad date and not-null start date shape: %d x %d' % data[
        data[reference_date].astype(int) < 366 & ~data['start_date_and_time'].empty].shape)
    logger.debug('rows with bad date and not-null process timestamp shape: %d x %d' % data[
        data[reference_date].astype(int) < 366 & ~data['PROCESS_TIMESTAMP'].empty].shape)

logger.debug('so we have %d rows with missing year and %d with no date' %
             (bad_date_records.shape[0], zero_date_records.shape[0]))
logger.debug('done')
finish_time = time.time()
elapsed_hours, elapsed_remainder = divmod(finish_time - start_time, 3600)
elapsed_minutes, elapsed_seconds = divmod(elapsed_remainder, 60)
logger.info("Time: {:0>2}:{:0>2}:{:05.2f}".format(int(elapsed_hours), int(elapsed_minutes), elapsed_seconds))
