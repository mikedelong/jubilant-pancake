# https://machinelearningmastery.com/arima-for-time-series-forecasting-with-python/

import datetime
import json
import logging
import time

import numpy as np
import pandas as pd
import pandas.tseries.offsets as offsets
from statsmodels.tsa.arima_model import ARIMA

start_time = time.time()


def make_date(arg_year, arg_month):
    result = pd.to_datetime(datetime.date(arg_year, arg_month, 1) + offsets.MonthEnd(0))
    return result


def project_dates(arg_base, arg_count):
    result = [pd.to_datetime(datetime.date(arg_base.year, arg_base.month, 1) + offsets.MonthEnd(month)) for month in
              range(1, arg_count + 1)]
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

# first total up the total hours per tail
totals = data[['tail', 'HOURS']].groupby(['tail']).sum()
logger.debug('we have hours totals for %d tails.' % totals.shape[0])
# now we want to discard anything before 2010 and after 2016
data = data[np.logical_and(data['year'].astype(int) >= 2010, data['year'].astype(int) <= 2016)]

data['date'] = np.vectorize(make_date)(data['year'].astype(int), data['month'].astype(int))
logger.debug('after trimming to the date range of interest we have shape %s ' % str(data.shape))

# to get just the data we want lets throw out the month and date
data.drop(['year', 'month'], axis=1, inplace=True)
logger.debug('after dropping columns we have shape %s ' % str(data.shape))
logger.debug('raw data minimum: %.2f, mean: %.2f, maximum: %.2f' % (
    data['HOURS'].min(), data['HOURS'].mean(), data['HOURS'].max()))
logger.debug(data.head(20))

order_d = 4
stale_count = 0
senior_count = 0
forecast_count = 0
for tail in data['tail'].unique():
    # todo review this
    tail_data = data.loc[data['tail'] == tail]
    tail_data = tail_data[['date', 'HOURS']]
    last_date = tail_data['date'].max()
    tail_data.set_index('date', inplace=True)
    current_hours = totals.get_value(tail, 'HOURS')

    # exclude senior tails with more than 8000 flight hours
    if current_hours > 8000:
        senior_count += 1
        logger.debug('count: %d tail %s has %d hours and will be excluded.' % (senior_count, tail, current_hours))
    elif last_date.year != 2016 and last_date.month != 12:
        stale_count += 1
        logger.debug('count: %d the last day for tail %s is %s' % (stale_count, tail, last_date))
    else:
        forecast_count += 1
        # for the model to work properly we need the dates to be the index
        model = ARIMA(tail_data, order=(order_d, 1, 0))
        model_fit = model.fit(disp=0)
        # now let's forecast for 2017
        steps = 12
        forecast = model_fit.forecast(steps=steps)
        logger.debug('count: %d forecast values: %s' % (forecast_count, str(forecast[0])))
        logger.debug(
            'pre and post: %.1f %.1f' % (tail_data['HOURS'].sum(), tail_data['HOURS'].sum() + forecast[0].sum()))

logger.debug('forecast: %d, over 8000 hours: %d, not flown recently: %d.' % (forecast_count, senior_count, stale_count))
logger.debug('done')
finish_time = time.time()
elapsed_hours, elapsed_remainder = divmod(finish_time - start_time, 3600)
elapsed_minutes, elapsed_seconds = divmod(elapsed_remainder, 60)
logger.info("Time: {:0>2}:{:0>2}:{:05.2f}".format(int(elapsed_hours), int(elapsed_minutes), elapsed_seconds))
