import datetime
import sys
import yaml # pyyaml

if len(sys.argv) < 2:
    print('usage: make-landing-page-html-swim.py TITLE YAMLFILE ...')
    sys.exit(2)

all = []
for fn in sys.argv[2:]:
    with open(fn) as fh:
        for s in yaml.safe_load(fh):
            s['filename'] = fn
            all.append(s)

year = datetime.datetime.now().year

def time_ampm(t):
    if t.minute > 0:
        minutes = '.' + t.strftime('%M')
    else:
        minutes = ''
    return '%s%s%s' % (t.strftime('%-I'), minutes, t.strftime('%p').lower())

print('<html><head><title>%s</title></head><body>' % sys.argv[1])

# iterate through date-sorted lift sessions for given year
sessions = sorted(filter(lambda s: s['type'] == 'swim' and
    s['start']['date'].year == year, all), key=lambda s: s['start']['date'])
block = None
for s in sessions:
    assert len(s['work']['swimming']) == 1 # only support single-set sessions
    workset = s['work']['swimming'][0]

    month = s['start']['date'].strftime('%B')
    if block != month:
        if block:
            print('</tbody></table>')
        print('<h3>%s</h3>' % month)
        print('<table><tbody>')
        block = month

    print(
        '<tr>',
        '<td width="5%%"><a href="%s">%s</a></td>' % \
            ('%s.html' % s['filename'].replace('.yaml', ''),
             s['start']['date'].strftime('%-d')),
        '<td width="5%%">%s</td>' % s['start']['date'].strftime('%a')[0:2],
        '<td width="5%%">%s</td>' % time_ampm(datetime.datetime.strptime(s['start']['time'],
            '%H:%M %Z')),
        '<td width="10%%">%s</td>' % \
            s['venue']['name'].encode('ascii', 'xmlcharrefreplace').decode(),
        '<td width="5%%">%s</td>' % workset['stroke'],
        '<td width="15%%">%s</td>' % s['kind'],
        '<td width="50%%">%s</td>' % workset['summary'],
        '<td width="5%%">%dm</td>' % s['volume'],
        '</tr>')
if block:
    print('</tbody></table>')

print('</body></html>')
