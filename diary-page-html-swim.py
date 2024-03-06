import datetime
import sys
import yaml # pyyaml

if len(sys.argv) != 2:
    print('usage: make-diary-page-html-swim.py YAMLFILE')
    sys.exit(2)

if sys.argv[1] == '-':
    all = yaml.safe_load(sys.stdin)
else:
    with open(sys.argv[1]) as fh:
        all = yaml.safe_load(fh)
assert(len(all) == 1) # only support single-session files
session = all[0]

def capitalise(s):
    return s[0].upper() + s[1:]

shortdate = datetime.datetime.strptime(session['start']['date'],
    '%Y-%m-%d').strftime('%b %-d') # stick to string
print('<html><head><meta charset="utf-8">')
print('<link rel="icon" type="image/x-icon" href="favicon.ico">')
print('<title>%s</title></head><body>' % shortdate)
print('<h2>%s</h2>' % shortdate)

def time_ampm(t):
    if t.minute > 0:
        minutes = '.' + t.strftime('%M')
    else:
        minutes = ''
    return '%s%s%s' % (t.strftime('%-I'), minutes, t.strftime('%p').lower())

assert len(session['work']['swimming']) == 1 # only support single-set sessions
workset = session['work']['swimming'][0]

# explicit encoding: encode('ascii', 'xmlcharrefreplace').decode()
print('<p>%s, %s, %s%s, %dm</p>' % (\
    time_ampm(datetime.datetime.strptime(session['start']['time'], '%H:%M %Z')),
    session['venue']['name'],
    '' if 'stroke' not in workset else workset['stroke'] + ', ',
    session['kind'],
    session['volume']))

print('<h3>%s</h3>' % workset['summary'])

for (i, j, k) in [('venue', 'note', ''), ('warmup', 'note', 'Warm-up: ')]:
    try:
        if type(session[i][j]) == list:
            print('%s<ul>' % k)
            for bullet in session[i][j]:
                print('<li>%s</li>' % bullet)
            print('</ul>')
        else:
            print('<p>%s%s</p>' % (k, capitalise(session[i][j])))
    except KeyError:
        pass

if type(session['work']['preparation']) == list:
    print('<ul>')
    for bullet in session['work']['preparation']:
        print('<li>%s</li>' % bullet)
    print('</ul>')
else:
    print('<p>%s</p>' % capitalise(session['work']['preparation']))

for section in ['note', 'structure', 'times']:
    try:
        if type(workset[section]) == list:
            print('<ul>')
            for bullet in workset[section]:
                print('<li>%s</li>' % bullet)
            print('</ul>')
        else:
            print('<p>%s</p>' % capitalise(workset[section]))
    except KeyError:
        if section == 'times':
            raise KeyError

i, j, k = 'cooldown', 'note', 'Cool-down: '
try:
    print('<p>%s%s</p>' % (k, capitalise(session[i][j])))
except KeyError:
    pass

try:
    if type(session['next']) == list:
        print('<ul>')
        for bullet in session['next']:
            print('<li>%s</li>' % bullet)
        print('</ul>')
    else:
        print('<p>%s</p>' % capitalise(session['next']))
    print()
except KeyError:
    pass

if 'picture' in session:
    print('<p><img width="480" src="%s"/></p>' % session['picture'])

print('</body></html>')
