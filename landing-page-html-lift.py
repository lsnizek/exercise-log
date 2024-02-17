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

print('<html><head><title>%s</title>' % sys.argv[1])
print('''<style> /* Top-Right-Bottom-Left */
  HTML             { font-family: Helvetica; padding: 20pt 0pt 0pt 20pt; }
  TD               { font-size: 7pt; padding-top: 4pt; padding-bottom: 4pt; }
  TD A             { color: white; }
  TABLE            { border-collapse: collapse; }
  H1               { font-size: 10pt; margin-top: 20pt; margin-bottom: 10pt; }
  .label           { font-weight: bold; text-transform: capitalize; text-align: center; }
  .col1, .col2     { background: black; color: white; }
  .col1            { width: 16pt; padding-right: 7pt; text-align: right; }
  .col2            { width: 16pt; }
  .col3            { width: 12pt; text-align: center; background: #EBEBEB; }
  .col4            { width: 36pt; text-align: right; padding-right: 4pt; }
  #ex0             { background: #DBDBDB; }
  #ex1, #ex2, #ex3 { background: #C9C9C9; }
  #ex4, #ex5       { background: #B8B8B8; }
</style>''')
print('</head><body>')

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
        print(
            '<h1>%s</h1>' % month,
            '<table><thead><tr><td colspan="3"/>',
            ''.join(('<td class="label">%s</td>') % name for name in order),
            '</tr></thead><tbody>'
        )
        block = month
    day = s['start']['date'].strftime('%-d')
    dayofweek = s['start']['date'].strftime('%a')[0:2]
    url = '%s.html' % s['filename'].replace('.yaml', '')
    print(
        '<tr><td class="col1"><a href="%s">%s</a></td>' % (url, day),
        '<td class="col2"><a href="%s">%s</a></td>' % (url, dayofweek),
        '<td class="col3">%s</td>' % s['kind']
    )
    for exn in range(len(order)):
        ex = next((ex for ex in s['work']['weights'] \
            if order[exn] == ex['exercise']), None)
        print('<td class="col4" id="ex%d">%s</td>' % \
            (exn, ex['load'] if ex else ''), end='')
    print('</tr>')
if block:
    print('</tbody></table>')

print('</body></html>')
