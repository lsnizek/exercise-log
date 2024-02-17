import datetime
import sys
import yaml # pyyaml

if len(sys.argv) != 2:
    print('usage: make-diary-page-html-lift.py YAMLFILE')
    sys.exit(2)

with open(sys.argv[1]) as fh:
    all = yaml.safe_load(fh)
assert(len(all) == 1) # only support single-session files
session = all[0]

def capitalise(s):
    return s[0].upper() + s[1:]

shortdate = session['start']['date'].strftime('%b %-d')
print('<html><meta charset="utf-8">')
print('<head><title>%s</title></head><body>' % shortdate)
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

    print(capitalise(ex['preparation'].replace('\n', '<br/>')))

    for section in ['note', 'video']:
        try:
            print('<p>%s</p>' % capitalise(ex[section]))
        except KeyError:
            pass

    if 'thumbnail' in ex:
        print('<p><img width="200" src="%s"/></p>' % ex['thumbnail'])

print('</body></html>')
