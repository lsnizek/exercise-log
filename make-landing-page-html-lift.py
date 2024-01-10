import datetime
import sys
import yaml # pyyaml

if len(sys.argv) < 2:
    print('usage: make-landing-page-html-lift.py TITLE YAMLFILE ...')
    sys.exit(2)

all = []
for fn in sys.argv[2:]:
    with open(fn) as fh:
        for s in yaml.safe_load(fh):
            s['filename'] = fn
            all.append(s)

order = ['squat', 'press', 'bench', 'pull-up', 'deadlift', 'power clean']
year = datetime.datetime.now().year

print('<html><head><title>%s</title></head><body>' % sys.argv[1])

# iterate through date-sorted lift sessions for given year
# list exercises in order given above
sessions = sorted(filter(lambda s: s['type'] == 'lift' and
    s['start']['date'].year == year, all), key=lambda s: s['start']['date'])
block = None
for s in sessions:
    month = s['start']['date'].strftime('%B')
    if block != month:
        if block:
            print('</tbody></table>')
        print('<h3>%s</h3>' % month)
        print('<table><thead><tr>')
        print('<td width="5%">')
        print('<td width="5%">')
        print('<td width="5%">')
        width = 85 / len(order) - 1
        print(''.join(('<td width="%d%%%%">%%s</td>' % width) % \
            name for name in order))
        print('</tr></thead><tbody>')
        block = month
    day = s['start']['date'].strftime('%-d')
    dayofweek = s['start']['date'].strftime('%a')[0:2]
    url = '%s.html' % s['filename'].replace('.yaml', '')
    print('<tr><td><a href="%s">%s</a></td><td>%s</td><td>%s</td>' % \
        (url, day, dayofweek, s['kind']))
    for name in order:
        ex = next((ex for ex in s['work']['weights'] \
            if name == ex['exercise']), None)
        print('<td>%s</td>' % (ex['load'] if ex else ''), end='')
    print('</tr>')
if block:
    print('</tbody></table>')

print('</body></html>')
