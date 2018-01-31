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

# todo fix these
input_folder = './output/'
input_file = 'nozeros.csv'

full_input_file = input_folder + input_file

logger.debug('reading input data from %s' % full_input_file)
data = pd.read_csv(full_input_file, parse_dates=['date'])
logger.debug('data read complete.')
logger.debug(data.columns)
logger.debug(data.head(5))
t0 = data[data[data.columns[0]] == data[data.columns[0]][0]]

t1 = t0.groupby(t0.date.dt.year).sum()
logger.debug(t1)