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

if False:
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
    input_file = settings['input_file']
    logger.debug('input file: %s' % input_file)

    # todo make the input headings a list
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
    logger.debug('before dropping not-actives we have shape %s ' % str(data.shape))

    # drop all the tails that are not in the active set
    data[input_heading_one] = np.vectorize(str.strip)(data[input_heading_one])
    # data.drop(data[data[input_heading_one] not in active_values].index, inplace=True)
    data = data[data[input_heading_one].isin(active_values)]
    logger.debug('after dropping not-actives we have shape %s ' % str(data.shape))

    # now remove the rows where the date is zero
    data.drop(data[data[input_heading_two] == '0'].index, inplace=True)
    logger.debug('after dropping zero dates we have shape %s ' % str(data.shape))

    # now add the date column
    data['date'] = np.vectorize(make_date)((data[date_column].astype(int) / 1000).astype(int),
                                           (data[date_column].astype(int) % 1000).astype(int))

    # fix the tail
    data['tail'] = np.vectorize(make_tail)(data[input_heading_one])

    logger.debug(data.head())

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
