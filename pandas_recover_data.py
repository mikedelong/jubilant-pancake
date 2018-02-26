import datetime
import json
import logging
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

start_time = time.time()


def make_date(arg_year, arg_day):
    year = 1900 + arg_year if arg_year > 50 else 2000 + arg_year
    result = datetime.date(year, 1, 1) + datetime.timedelta(days=int(arg_day))
    return result


def make_date2(arg_year, arg_day, arg_alt_year, arg_alt_month):
    if arg_year != 0:
        year = 1900 + arg_year if arg_year > 50 else 2000 + arg_year
        result = datetime.date(year, 1, 1) + datetime.timedelta(days=int(arg_day))
    else:
        year = 1900 + arg_alt_year if arg_alt_year > 50 else 2000 + arg_alt_year
        month = arg_alt_month
        result = datetime.date(year, month, 15)
    return result


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
settings_file = './settings-recover.json'
logger.debug('settings file : %s' % settings_file)
with open(settings_file, 'r') as settings_fp:
    settings = json.load(settings_fp)

logger.debug('settings: %s' % settings)

# let's do everything to get our filter data before we load anything else
filter_file = settings['filter_file']
logger.debug('filter file: %s' % filter_file)
filter_sheet_name = settings['filter_sheet_name']
logger.debug('filter sheet name: %s' % filter_sheet_name)
filter_column = settings['filter_column']
converters = {filter_column: str}
filter_data = pd.read_excel(filter_file, sheet_name=filter_sheet_name, converters=converters)
logger.debug(filter_data.head())
active = filter_data[filter_column]
logger.debug(active.values)
active_values = set(active.values)

# read the input file into a data frame
# now let's load the big input file
input_folder = settings['input_folder']
input_file = settings['input_file']
full_input_file = input_folder + input_file
logger.debug('input file: %s' % full_input_file)

input_file_check = Path(full_input_file)
if not input_file_check.is_file():
    logger.warning('input file %s does not exist; quitting.')
    sys.exit()

input_headings = settings['input_headings']
columns_to_use = input_headings
str_headings = settings['str_headings']
# todo this is kind of clumsy; find a better way to do this
converters = {}
for heading in input_headings:
    if heading in str_headings:
        converters[heading] = str
    else:
        converters[heading] = float
logger.debug(converters)
data = pd.read_csv(full_input_file, usecols=converters.keys(), converters=converters)
logger.debug('input file read complete.')

# we want to remove the second column because it doesn't tell us anything
data_columns = data.columns
logger.debug('our big data frame has column headers %s' % data.columns)
for index in range(3, 5):
    logger.debug(input_headings[index])
    logger.debug(data[input_headings[index]].value_counts())

for index in range(3, 5):
    heading = input_headings[index]
    data[heading] = data[heading].astype(int)

# how many columns do we have before dropping?
logger.debug('before dropping not-actives we have shape %s ' % str(data.shape))
# drop all the tails that are not in the active set
serial = input_headings[0]
data[serial] = np.vectorize(str.strip)(data[serial])
data = data[data[serial].isin(active_values)]
logger.debug('after dropping not-actives we have shape %s ' % str(data.shape))

# fix the tail
data['tail'] = np.vectorize(make_tail)(data[serial])
logger.debug(data.head())

year = input_headings[3]
input_date = input_headings[2]
# drop everything where the date is invalid and the year is 1947
data = data[~((data[year].astype(float) == 1947) & (data[input_date].astype(int) < 366))]
logger.debug('after dropping 1947s our shape is %d x %d' % data.shape)

if False:
    # now remove the rows where the date is zero
    data.drop(data[data[input_heading_two] == '0'].index, inplace=True)
    logger.debug('after dropping zero dates we have shape %s ' % str(data.shape))

    # now add the date column
    data['date'] = np.vectorize(make_date)((data[date_column].astype(int) / 1000).astype(int),
                                           (data[date_column].astype(int) % 1000).astype(int))



    output_folder = settings['processed_folder']
    output_file = settings['output_file']
    full_output_file = output_folder + output_file
    logger.debug('writing output to %s' % full_output_file)
    data.to_csv(full_output_file, columns=['tail', 'date', input_heading_three], index=False)

logger.debug('done')
finish_time = time.time()
elapsed_hours, elapsed_remainder = divmod(finish_time - start_time, 3600)
elapsed_minutes, elapsed_seconds = divmod(elapsed_remainder, 60)
logger.info("Time: {:0>2}:{:0>2}:{:05.2f}".format(int(elapsed_hours), int(elapsed_minutes), elapsed_seconds))
