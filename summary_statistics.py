import json

import pandas as pd

# read the input filename from a JSON file
with open('./settings.json', 'r') as settings_fp:
    settings = json.load(settings_fp)

headings = [settings['heading_one'], settings['heading_two'], settings['heading_three']]

# todo fix FutureWarning here
data = pd.read_csv('./output/clean.csv', dtype={headings[0]: 'str', headings[1]: 'str', headings[2]: 'float'},
                   date_parser=pd.datetools.to_datetime)

print(data.head())

for heading in headings:
    print('%s : nunique: %d' % (heading, data[heading].nunique()))
    print('%s : min: %s' % (heading, str(data[heading].min())))
    print('%s : max: %s' % (heading, str(data[heading].max())))

print(data.describe(percentiles=[0.01, 0.985]))
