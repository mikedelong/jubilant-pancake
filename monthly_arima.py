# https://machinelearningmastery.com/arima-for-time-series-forecasting-with-python/

import datetime
import json
import logging
import time

import numpy as np
import pandas as pd
import pandas.tseries.offsets as offsets
from matplotlib import pyplot
from pandas.plotting import autocorrelation_plot

start_time = time.time()


def make_date(arg_year, arg_month):
    result = pd.to_datetime(datetime.date(arg_year, arg_month, 1) + offsets.MonthEnd(0))
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

input_folder = settings['processed_folder']
full_input_file = input_folder + 'monthly.csv'
logger.debug('reading input data from %s' % full_input_file)
data = pd.read_csv(full_input_file)

# now we want to discard anything before 2010 and after 2016
data = data[data['year'].astype(int) >= 2010]
data = data[data['year'].astype(int) <= 2016]

# todo think about pushing this back into the upstream code
data['date'] = np.vectorize(make_date)(data['year'].astype(int), data['month'].astype(int))
logger.debug('after trimming to the date range of interest we have shape %s ' % str(data.shape))

# to get just the data we want lets throw out the tail, month, and date
data.drop(['tail', 'year', 'month'], axis=1, inplace=True)
logger.debug('after dropping columns we have shape %s ' % str(data.shape))
logger.debug(data.head(5))

t0 = data.groupby(['date'], axis=0).sum()

autocorrelation_plot(t0)
pyplot.show()

logger.debug('done')
finish_time = time.time()
elapsed_hours, elapsed_remainder = divmod(finish_time - start_time, 3600)
elapsed_minutes, elapsed_seconds = divmod(elapsed_remainder, 60)
logger.info("Time: {:0>2}:{:0>2}:{:05.2f}".format(int(elapsed_hours), int(elapsed_minutes), elapsed_seconds))
