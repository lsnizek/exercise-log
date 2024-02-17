import datetime
import sys
import yaml # pyyaml

if len(sys.argv) < 2:
    print('usage: make-summary-ascii-lift.py YAMLFILE ...')
    sys.exit(2)

all = []
for fn in sys.argv[1:]:
    with open(fn) as fh:
        all.extend(yaml.safe_load(fh))

order = ['squat', 'press', 'bench', 'pull-up', 'deadlift', 'power clean']
year = datetime.datetime.now().year

# iterate through date-sorted lift sessions for given year
# list exercises in order given above
sessions = sorted(filter(lambda s: s['type'] == 'lift' and
    s['start']['date'].year == year, all), key=lambda s: s['start']['date'])
block = None
for s in sessions:
    month = s['start']['date'].strftime('%B')
    if block != month:
        print(month)
        print('%7s' % '', ''.join(' %11s' % name for name in order))
        block = month
    day = s['start']['date'].strftime('%-d')
    dayofweek = s['start']['date'].strftime('%a')[0:2]
    print('%2s %-2s  %s' % (day, dayofweek, s['kind']), end='')
    for name in order:
        ex = next((ex for ex in s['work']['weights'] \
            if name == ex['exercise']), None)
        print(' %11s' % (ex['load'] if ex else ''), end='')
    print()
