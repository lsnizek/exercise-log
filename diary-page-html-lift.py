import datetime
import sys
import yaml # pyyaml

if len(sys.argv) != 2:
    print('usage: make-diary-page-html-lift.py YAMLFILE')
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

# explicit encoding: encode('ascii', 'xmlcharrefreplace').decode()
print('<p>%s, %s</p>' % (\
    time_ampm(datetime.datetime.strptime(session['start']['time'], '%H:%M %Z')),
    session['venue']['name']))

for (i, j) in [('venue', 'note'), ('warmup', 'note')]:
    try:
        print('<p>%s</p>' % capitalise(session[i][j]))
    except KeyError:
        pass

for ex in session['work']['weights']:
    print('<h3>%.4gkg %s</h3>' % (ex['load'], ex['exercise']))

    for section in ['preparation', 'note', 'video']:
        try:
            if type(ex[section]) == list:
                print('<ul>')
                for bullet in ex[section]:
                    print('<li>%s</li>' % bullet)
                print('</ul>')
            else:
                print('<p>%s</p>' % capitalise(ex[section]))
        except KeyError:
            pass

    if 'thumbnail' in ex:
        print('<p><img width="200" src="%s"/></p>' % ex['thumbnail'])

print('</body></html>')
