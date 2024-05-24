import csv
import datetime
import sys
import yaml # pyyaml

if len(sys.argv) < 2:
    print('usage: summary-csv-lift.py YAMLFILE ...')
    sys.exit(2)

all = []
for fn in sys.argv[1:]:
    with open(fn) as fh:
        all.extend(yaml.safe_load(fh))

order = ['squat', 'press', 'bench', 'pull-up', 'deadlift', 'power clean']

# iterate through date-sorted lift sessions
# list exercises in order given above
sessions = sorted(filter(lambda s: s['type'] == 'lift', all),
    key=lambda s: s['start']['date'])
writer = csv.writer(sys.stdout)
for s in sessions:
    for ex in sorted(s['work']['weights'],
        key=lambda ex: order.index(ex['exercise'])):
        writer.writerow([
            s['start']['date'],
            ex['exercise'],
            '%dkg' % ex['load'],
            ''
        ])
