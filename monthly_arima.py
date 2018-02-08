# https://machinelearningmastery.com/arima-for-time-series-forecasting-with-python/

import datetime
import json
import logging
import time

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pandas.tseries.offsets as offsets
from pandas.plotting import autocorrelation_plot
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

# now we want to discard anything before 2010 and after 2016
data = data[data['year'].astype(int) >= 2010]
data = data[data['year'].astype(int) <= 2016]

# todo think about pushing this back into the upstream code
data['date'] = np.vectorize(make_date)(data['year'].astype(int), data['month'].astype(int))
logger.debug('after trimming to the date range of interest we have shape %s ' % str(data.shape))

# to get just the data we want lets throw out the tail, month, and date
data.drop(['tail', 'year', 'month'], axis=1, inplace=True)
logger.debug('after dropping columns we have shape %s ' % str(data.shape))
logger.debug('raw data minimum: %.2f, mean: %.2f, maximum: %.2f' % (
    data['HOURS'].min(), data['HOURS'].mean(), data['HOURS'].max()))

fleet_monthly = data.groupby(['date'], axis=0).sum()
logger.debug(fleet_monthly.head(20))

logger.debug('total hours from monthly: %.2f' % fleet_monthly['HOURS'].sum())

# before we go on to the prediction let's look at the summary statistics for the monthly data
logger.debug('raw monthly data minimum: %.2f, mean: %.2f, maximum: %.2f' % (fleet_monthly.min(), fleet_monthly.mean(),
                                                                            fleet_monthly.max()))
for order_d in range(4, 5):
    model = ARIMA(fleet_monthly, order=(order_d, 1, 0))
    model_fit = model.fit(disp=0)
    logger.debug(model_fit.summary())
    # now let's forecast for 2017
    steps = 12
    forecasted = model_fit.forecast(steps=steps)
    logger.debug('forecast values: %s' % str(forecasted[0]))

    monthly_with_forecast = fleet_monthly.append(pd.DataFrame.from_dict(
        {'date': project_dates(fleet_monthly.index.max(), steps),
         'HOURS': forecasted[0],
         'hours_min': [item[0] for item in forecasted[2]],
         'hours_max': [item[1] for item in forecasted[2]]}).set_index(['date']))

    logger.debug('monthly with forecast total hours: %.2f' % monthly_with_forecast['HOURS'].sum())
    residuals = pd.DataFrame(model_fit.resid)
    logger.debug(residuals.describe())

    figure, axes = plt.subplots(nrows=5, figsize=(9, 16))
    axis = 0
    fleet_monthly.plot(ax=axes[axis], style='.')
    axis += 1
    axes[axis].errorbar(monthly_with_forecast.index, monthly_with_forecast['HOURS'],
                        yerr=[monthly_with_forecast['hours_min'], monthly_with_forecast['hours_max']], marker='.')
    axis += 1
    autocorrelation_plot(fleet_monthly, ax=axes[axis])
    axis += 1
    residuals.plot(ax=axes[axis], style='.')
    axis += 1
    residuals.plot(kind='kde', ax=axes[axis])
    axis += 1
    logger.debug('ARIMA residuals minimum: %.2f, mean: %.2f, maximum: %.2f' % (residuals.min(), residuals.mean(),
                                                                               residuals.max()))
    autocorrelation_plot_file = '{}autocorrelation_plot_{}.png'.format(settings['output_folder'], order_d)
    logger.debug('saving ARIMA plots to %s', autocorrelation_plot_file)
    plt.tight_layout()
    plt.savefig(autocorrelation_plot_file)
    del figure

logger.debug('done')
finish_time = time.time()
elapsed_hours, elapsed_remainder = divmod(finish_time - start_time, 3600)
elapsed_minutes, elapsed_seconds = divmod(elapsed_remainder, 60)
logger.info("Time: {:0>2}:{:0>2}:{:05.2f}".format(int(elapsed_hours), int(elapsed_minutes), elapsed_seconds))
