import csv
import datetime
import sys
import yaml # pyyaml

if len(sys.argv) < 2:
    print('usage: make-totals-csv-swim.py YAMLFILE ...')
    sys.exit(2)

all = []
for fn in sys.argv[1:]:
    with open(fn) as fh:
        all.extend(yaml.safe_load(fh))

year = datetime.datetime.now().year

# iterate through date-sorted lift sessions for given year
sessions = sorted(filter(lambda s: s['type'] == 'swim' and
    s['start']['date'].year == year, all), key=lambda s: s['start']['date'])
writer = csv.writer(sys.stdout)
block, volume, count = None, 0, 0
for s in sessions:
    month = s['start']['date'].strftime('%B')
    volume += s['volume']
    count += 1
    if block != month:
        if block:
            writer.writerow([block, volume, count])
        block = month
writer.writerow([block, volume, count])
