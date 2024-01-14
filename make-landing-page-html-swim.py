import datetime
import sys
import yaml # pyyaml
import unidecode

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

print('<html><head><title>%s</title>' % sys.argv[1])
print('''<style> /* Top-Right-Bottom-Left */
  HTML             { font-family: Helvetica; padding: 20pt 0pt 0pt 20pt; }
  TD               { font-size: 7pt; }
  TD A             { color: white; }
  TABLE            { border-collapse: collapse; }
  H1               { font-size: 10pt; margin-bottom: 20pt; }
  .label           { font-weight: bold; text-transform: capitalize; text-align: center; }
  .col1, .col2     { background: black; color: white; }
  .col1            { width: 16pt; padding-right: 7pt; text-align: right; }
  .col2            { width: 16pt; }
  .col3            { width: 38pt; padding-right: 7pt; text-align: right; }
  .col4            { width: 28pt; text-align: center; }
  .col5            { width: 70pt; padding-left: 4pt; color: white; }
  .col6            { padding-left: 6pt; padding-right: 20pt; }
  .col7            { width: 40pt; }
  .spacious        { background: #88FA4E; }
  .fly200          { background: #3F2859; }
  .fly100          { background: #64408E; }
  .fly50           { background: #A66EF7; }
  .back200         { background: #8C0F59; }
  .back100         { background: #C03789; }
  .back50          { background: #FE48B6; }
  .breast200       { background: #AC3300; }
  .breast100       { background: #D84A10; }
  .breast50        { background: #FE774A; }
  .free200         { background: #006EA2; }
  .free100         { background: #0B90CC; }
  .free50          { background: #56C1FF; }
  .im100           { background: #5E5E5E; }
  .im200           { background: #4B4B4B; }
  .distance        { background: $929292; }
</style>''')
venue_dimensions = 'width="18" height="18"'
print('</head><body>')

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
        print('<h1>%s</h1>' % month)
        print('<table><tbody>')
        block = month

    spacious = False
    try:
        spacious = s['venue']['spacious']
    except KeyError:
        pass

    url = '%s.html' % s['filename'].replace('.yaml', '')
    venue_short = unidecode.unidecode(s['venue']['name']).lower()
    venue_full = s['venue']['name'].encode('ascii', 'xmlcharrefreplace').decode()
    print(
        '<tr>',
        '<td class="col1"><a href="%s">%s</a></td>' % \
            (url, s['start']['date'].strftime('%-d')),
        '<td class="col2"><a href="%s">%s</a></td>' % \
            (url, s['start']['date'].strftime('%a')[0:2]),
        '<td class="col3%s">%s</td>' % \
            (' spacious' if spacious else '',
            time_ampm(datetime.datetime.strptime(s['start']['time'], '%H:%M %Z'))),
        '<td class="col4"><img %s src="%s" alt="%s" title="%s"/></td>' % \
            (venue_dimensions, '%s.png' % venue_short, venue_full, venue_full),
        '<td class="col5 %s">%s %s</td>' % \
            (workset['stroke'] + '200', workset['stroke'], s['kind']),
        '<td class="col6">%s</td>' % workset['summary'],
        '<td class="col7">%dm</td>' % s['volume'],
        '</tr>')
if block:
    print('</tbody></table>')

print('</body></html>')
