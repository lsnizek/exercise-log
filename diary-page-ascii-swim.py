import datetime
import sys
import yaml # pyyaml

if len(sys.argv) != 2:
    print('usage: make-diary-page-ascii-swim.py YAMLFILE')
    sys.exit(2)

with open(sys.argv[1]) as fh:
    all = yaml.safe_load(fh)
assert(len(all) == 1) # only support single-session files
session = all[0]

def capitalise(s):
    return s[0].upper() + s[1:]

print(session['start']['date'].strftime('%b %-d'))
print()

def time_ampm(t):
    if t.minute > 0:
        minutes = '.' + t.strftime('%M')
    else:
        minutes = ''
    return '%s%s%s' % (t.strftime('%-I'), minutes, t.strftime('%p').lower())

assert len(session['work']['swimming']) == 1 # only support single-set sessions
workset = session['work']['swimming'][0]

print('%s, %s, %s, %s, %dm' % (\
    time_ampm(datetime.datetime.strptime(session['start']['time'], '%H:%M %Z')),
    session['venue']['name'],
    workset['stroke'],
    session['kind'],
    session['volume']))
print()

print(workset['summary'])
print('=======================================================================')
print()

try:
    print(capitalise(session['venue']['note']))
    print()
except KeyError:
    pass

try:
    print(capitalise(session['warmup']['note']))
    print()
except KeyError:
    pass

print(capitalise(session['work']['preparation'].rstrip()))
print()

for section in ['note', 'structure', 'times']:
    try:
        print(capitalise(workset[section]))
        print()
    except KeyError:
        pass

try:
    print(capitalise(session['next']))
    print()
except KeyError:
    pass
