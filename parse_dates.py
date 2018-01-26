import collections
import csv
import datetime
import json

# read the input filename from a JSON file
with open('./settings.json', 'r') as settings_fp:
    settings = json.load(settings_fp)

input_file = settings['input_file']

count = 0
with open('./output/clean.csv', 'w') as output_fp:
    writer = csv.writer(output_fp)
    writer.writerow(['tail', 'date', 'hours'])
    with open(input_file, 'r') as input_fp:
        reader = csv.reader(input_fp)
        # skip the header row
        next(reader)
        for row in reader:
            count += 1
            if count % 10000 == 0:
                print(('%d : %s') % (count, row))
            tail = row[0].strip()
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
            writer.writerow([tail, date, hours])

if False:
    with open(input_file, 'r') as input_fp:
        reader = csv.reader(input_fp)
        # skip the header row
        next(reader)
        tails = [row[0].strip() for row in reader if row[2] == '0']

    t = collections.Counter(tails)
    print(len(t))

    print(t)

if False:
    with open(input_file, 'r') as input_fp:
        reader = csv.reader(input_fp)
        # skip the header row
        next(reader)

        days = [int(row[2][-3:]) for row in reader]

        print(len(days))
        print(min(days))
        print(max(days))

if False:
    with open(input_file, 'r') as input_fp:
        reader = csv.reader(input_fp)
        # skip the header row
        next(reader)

        years = list()
        for row in reader:
            try:
                year = int(row[2][0:-3])
            except ValueError as valueError:
                print(row)
                year = 0

            years.append(year)
            # years = [int(row[2][0:-3]) for row in reader]

        print(min(years))
        print(max(years))
