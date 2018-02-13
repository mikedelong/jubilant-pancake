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
settings_file = './investigate.json'
logger.debug('settings file : %s' % settings_file)
with open(settings_file, 'r') as settings_fp:
    settings = json.load(settings_fp)

logger.debug('settings: %s' % settings)

# first let's load up our airport data
data_folder = settings['data_folder']
airports_file = settings['airports_file']
full_airports_file = data_folder + airports_file
logger.debug('airports data file: %s' % full_airports_file)
columns_to_use = ['airport', 'city', 'country', 'icao', 'latitude', 'longitude']
airports_data = pd.read_csv(full_airports_file, index_col=['icao'], header=None, names=columns_to_use,
                            usecols=[1, 2, 3, 5, 6, 7])
logger.debug('airports shape: %s' % str(airports_data.shape))


# now let's load the big input file
input_folder = settings['input_folder']
logger.debug('input folder: %s' % input_folder)
input_file = settings['input_file']
logger.debug('input file: %s' % input_file)
full_input_file = input_folder + input_file
logger.debug('reading input data from %s' % full_input_file)
data = pd.read_csv(full_input_file)
logger.debug('read complete: columns are %s' % str(data.columns))
for column in data.columns:
    unique_value_count = data[column].nunique()
    if unique_value_count > 10:
        logger.debug('column %s has %d values and %d unique values.' %
                     (column, len(data[column]), data[column].nunique()))
    else:
        unique_values = data[column].unique()
        values = [item.strip() for item in unique_values]
        logger.debug('column %s has the following unique values: %s' % (column, values))

for column in data.columns:
    if 'location' in column.lower():
        unique_values = data[column].unique()
        logger.debug('column %s includes values %s' % (column, unique_values[0:10]))
        test_data = unique_values[:10]
        for item in test_data:
            t0 = airports_data.loc[item]
            logger.debug(t0[['latitude', 'longitude']])

logger.debug('done')
finish_time = time.time()
elapsed_hours, elapsed_remainder = divmod(finish_time - start_time, 3600)
elapsed_minutes, elapsed_seconds = divmod(elapsed_remainder, 60)
logger.info("Time: {:0>2}:{:0>2}:{:05.2f}".format(int(elapsed_hours), int(elapsed_minutes), elapsed_seconds))
