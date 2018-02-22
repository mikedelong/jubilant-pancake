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
settings_file = './settings-arima.json'
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
pre_totals = data[data['year'].astype(int) < 2010].groupby(['tail']).sum()
pre_totals = pre_totals.drop(['year', 'month'], axis=1)
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

output_folder = settings['output_folder']

# this will get us the last date (in 2010-2016) for each tail
max_dates = data[['tail', 'date']].groupby(['tail']).max()
max_dates_file = settings['max_dates_file']
full_max_dates_filename = output_folder + max_dates_file
max_dates.to_csv(full_max_dates_filename)

pre_2016_count = max_dates[(max_dates['date'].dt.year != 2016)].shape[0]
logger.debug('we have %d tails with a max date before 2016' % pre_2016_count)

reference_date = datetime.date(year=2016, month=9, day=30)
months_count = 'months_count'
max_dates[months_count] = ((max_dates['date'].dt.date - reference_date) / np.timedelta64(1, 'M')).astype(int)

# let's calculate how many additional months we would need to get to the end of 2017
order_d = 4
stale_count = 0
senior_count = 0
forecast_senior_count = 0
forecast_count = 0
tails = max_dates[max_dates[months_count] > 0].index.values.tolist()
ey2016 = list()
ey2017 = list()
ey2018 = list()
for tail in tails:
    # todo review this
    tail_data = data.loc[data['tail'] == tail]
    tail_data = tail_data[['date', 'HOURS']]
    tail_data.set_index('date', inplace=True)
    before_value = tail_data['HOURS'].sum() + pre_totals.get_value(tail, 'HOURS')
    ey2016.extend([before_value])
    # exclude senior tails with more than 8000 flight hours as of the end of 2016
    if before_value > 8000:
        senior_count += 1
        logger.debug('count: %d tail %s has %.1f hours and will be excluded.' % (senior_count, tail, before_value))
        ey2017.extend([before_value])
        ey2018.extend([before_value])
    else:
        forecast_count += 1
        # for the model to work properly we need the dates to be the index
        model_2017 = ARIMA(tail_data, order=(order_d, 1, 0))
        model_2017_fit = model_2017.fit(disp=0)
        # now let's forecast for 2017
        forecast_2017 = model_2017_fit.forecast(steps=max_dates.loc[tail, months_count] + 12)
        # this will give us the pre-2010 hours plus the ARIMA model's training data hours
        after_value_2017 = before_value + forecast_2017[0].sum()
        ey2017.extend([after_value_2017])
        if after_value_2017 > 8000:
            forecast_senior_count += 1
            after_value_2018 = after_value_2017
        else:

            # for the model to work properly we need the dates to be the index
            model_2018 = ARIMA(tail_data, order=(order_d, 1, 0))
            model_2018_fit = model_2018.fit(disp=0)
            # now let's forecast for 2018
            forecast_2018 = model_2018_fit.forecast(steps=max_dates.loc[tail, months_count] + 24)
            # this will give us the pre-2010 hours plus the ARIMA model's training data hours
            after_value_2018 = before_value + forecast_2018[0].sum()
            if after_value_2018 > 8000:
                forecast_senior_count += 1
        ey2018.extend([after_value_2018])
        logger.debug('tail %s EY2016: %.1f EY2017: %.1f EY2018: %.1f' %
                     (tail, before_value, after_value_2017, after_value_2018))

ey2016_over_8000 = [item > 8000 for item in ey2016]
ey2017_over_8000 = [item > 8000 for item in ey2017]
ey2018_over_8000 = [item > 8000 for item in ey2018]

output = pd.DataFrame.from_dict(
    {'tail': tails,
     'EY2016': ey2016, 'EY16over8k': ey2016_over_8000,
     'EY2017': ey2017, 'EY17over8k': ey2017_over_8000,
     'EY2018': ey2018, 'EY18over8k': ey2018_over_8000,
     })

logger.debug('forecast: %d, over 8000 hours: %d, not flown recently: %d.' % (forecast_count, senior_count, stale_count))
logger.debug('forecast %d will be over 8000 hours at end of year.' % (senior_count + forecast_senior_count))
logger.debug('we have %d unique tails and our output object will be %d x %d' %
             (data['tail'].unique().size, output.shape[0], output.shape[1]))
output_file = settings['output_file']
full_output_file = output_folder + output_file
logger.debug('writing modeled results to output file %s' % full_output_file)
output.to_csv(full_output_file, index=True, header=True)
logger.debug('done')
finish_time = time.time()
elapsed_hours, elapsed_remainder = divmod(finish_time - start_time, 3600)
elapsed_minutes, elapsed_seconds = divmod(elapsed_remainder, 60)
logger.info("Time: {:0>2}:{:0>2}:{:05.2f}".format(int(elapsed_hours), int(elapsed_minutes), elapsed_seconds))
