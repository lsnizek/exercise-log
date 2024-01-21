import datetime
import sys
import yaml # pyyaml

if len(sys.argv) != 2:
    print('usage: make-diary-page-html-swim.py YAMLFILE')
    sys.exit(2)

with open(sys.argv[1]) as fh:
    all = yaml.safe_load(fh)
assert(len(all) == 1) # only support single-session files
session = all[0]

def capitalise(s):
    return s[0].upper() + s[1:]

shortdate = session['start']['date'].strftime('%b %-d')
print('<html><head><title>%s</title></head><body>' % shortdate)
print('<h2>%s</h2>' % shortdate)

def time_ampm(t):
    if t.minute > 0:
        minutes = '.' + t.strftime('%M')
    else:
        minutes = ''
    return '%s%s%s' % (t.strftime('%-I'), minutes, t.strftime('%p').lower())

assert len(session['work']['swimming']) == 1 # only support single-set sessions
workset = session['work']['swimming'][0]

print('<p>%s, %s, %s%s, %dm</p>' % (\
    time_ampm(datetime.datetime.strptime(session['start']['time'], '%H:%M %Z')),
    session['venue']['name'].encode('ascii', 'xmlcharrefreplace').decode(),
    '' if 'stroke' not in workset else workset['stroke'] + ', ',
    session['kind'],
    session['volume']))

print('<h3>%s</h3>' % workset['summary'])

for (i, j, k) in [('venue', 'note', ''), ('warmup', 'note', 'Warm-up: ')]:
    try:
        print('<p>%s%s</p>' % (k, capitalise(session[i][j])))
    except KeyError:
        pass

print(capitalise(session['work']['preparation'].replace('\n', '<br/>')))

for section in ['note', 'structure', 'times']:
    try:
        print('<p>%s</p>' % capitalise(workset[section]).replace('\n', '<br/>'))
        print()
    except KeyError:
        pass

try:
    print('<p>%s</p>' % capitalise(session['next']))
    print()
except KeyError:
    pass

print('</body></html>')
