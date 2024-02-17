import datetime
import sys
import yaml # pyyaml

if len(sys.argv) < 2:
    print('usage: make-summary-ascii-swim.py YAMLFILE ...')
    sys.exit(2)

all = []
for fn in sys.argv[1:]:
    with open(fn) as fh:
        all.extend(yaml.safe_load(fh))

year = datetime.datetime.now().year

def time_ampm(t):
    if t.minute > 0:
        minutes = '.' + t.strftime('%M')
    else:
        minutes = ''
    return '%s%s%s' % (t.strftime('%-I'), minutes, t.strftime('%p').lower())

# iterate through date-sorted swim sessions for given year
sessions = sorted(filter(lambda s: s['type'] == 'swim' and
    s['start']['date'].year == year, all), key=lambda s: s['start']['date'])
block = None
for s in sessions:
    month = s['start']['date'].strftime('%B')
    if block != month:
        print(month)
        block = month

    assert len(s['work']['swimming']) == 1 # only support single-set sessions
    workset = s['work']['swimming'][0]

    print(
        '%2s' % s['start']['date'].strftime('%-d'),
        '%-2s' % s['start']['date'].strftime('%a')[0:2],
        ' %7s' % time_ampm(datetime.datetime.strptime(s['start']['time'],
            '%H:%M %Z')),
        '%-7s' % s['venue']['name'],
        '%-8s' % workset['stroke'],
        '%10s' % s['kind'],
        '%-60s' % workset['summary'],
        '%7dm' % s['volume'])
