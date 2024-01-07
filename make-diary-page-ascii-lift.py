import datetime
import sys
import yaml # pyyaml

if len(sys.argv) != 2:
    print('usage: make-diary-page-ascii-lift.py YAMLFILE')
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

print('%s, %s' % (\
    time_ampm(datetime.datetime.strptime(session['start']['time'], '%H:%M %Z')),
    session['venue']['name']))
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

for ex in session['work']['weights']:
    print('%dkg %s' % (ex['load'], ex['exercise']))
    print('===============================')
    print()

    print(capitalise(ex['preparation'].rstrip()))
    print()

    for section in ['note', 'video']:
        try:
            print(capitalise(ex[section]))
            print()
        except KeyError:
            pass
