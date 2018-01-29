import csv
import datetime
import json
import logging

import pandas as pd

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

# now let's load the big input file
input_file = settings['input_file']
logger.debug('input file: %s' % input_file)

do_missing_year_fix = bool(settings['do_missing_year_fix'])
if do_missing_year_fix:
    logger.debug('we are moving data with no year field to the year 2000')
else:
    logger.debug('we are dropping data with no year field')
output_folder = settings['output_folder']

if do_missing_year_fix:
    # todo move filename to settings
    output_file = output_folder + 'filtered.csv'
else:
    # todo move filename to settings
    output_file = output_folder + 'filtered-no-missing-date.csv'

progress_logging_frequency = int(settings['progress_logging_frequency'])
read_count = 0
with open(output_file, 'w', newline='') as output_fp:
    writer = csv.writer(output_fp)
    headings = [settings['heading_one'], settings['heading_two'], settings['heading_three']]
    logger.debug('headings: %s' % headings)
    writer.writerow(headings)
    with open(input_file, 'r') as input_fp:
        reader = csv.reader(input_fp)
        # skip the header row
        next(reader)
        for row in reader:
            read_count += 1
            if read_count % progress_logging_frequency == 0:
                logger.debug('%d : %s' % (read_count, row))
            tail = row[0].strip()
            if len(tail) != 10:
                logger.warning('troublesome %s: %s' % (headings[0], tail))

            if tail in active_values:
                tail = '-'.join([tail[0:2], tail[-4:]])
                day = int(row[2])
                hours = float(row[3])
                if day > 366:
                    date_day = int(row[2][-3:])
                    date_year = int(row[2][0:-3])
                    year = 1900 + date_year if date_year > 50 else 2000 + date_year
                    date = datetime.date(year, 1, 1) + datetime.timedelta(days=date_day)
                else:
                    date_day = int(row[2])
                    date = datetime.date(2000, 1, 1) + datetime.timedelta(days=date_day)

                # only always write if we're doing the missing year fix
                if not do_missing_year_fix:
                    if day > 366:
                        writer.writerow([tail, date, hours])
                else:
                    writer.writerow([tail, date, hours])

logger.debug('read %d rows' % read_count)
