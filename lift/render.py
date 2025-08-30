import argparse
import csv
import datetime
import os
import sys
import unidecode
import xml.etree.ElementTree

order = ['squat', 'press', 'bench', 'pull-up', 'deadlift', 'clean']

##############################################################################
# helpers
##############################################################################

def time_ampm(t):
    if t.minute > 0:
        minutes = '.' + t.strftime('%M')
    else:
        minutes = ''
    return '%s%s%s' % (t.strftime('%-I'), minutes, t.strftime('%p').lower())

def capitalise(s):
    return s[0].upper() + s[1:]

##############################################################################
# parsing
##############################################################################

def parse_notes(el):
    if len(el) == 0:
        return el.text # can be None
    else:
        notes = []
        for note in el:
            notes.append(note.text)
        return notes

def parse_meta(el):
    assert 'start' in el.attrib
    assert 'type' in el.attrib
    assert el.attrib['type'] == 'lift'
    start = datetime.datetime.strptime(el.attrib['start'], '%Y-%m-%d %H:%M:%S')
    return start

def parse_venue(el):
    assert 'name' in el.attrib
    venue = {'name': el.attrib['name']}
    notes = parse_notes(el)
    if notes:
        venue['notes'] = notes
    return venue

def parse_warmup(el):
    return parse_notes(el)

def parse_lift(el):
    s = {}
    assert {'kind', 'weight'} <= set(el.attrib)
    s['kind'], s['weight'] = el.attrib['kind'], float(el.attrib['weight'])
    for child in el:
        if child.tag == 'preparation':
            s['preparation'] = parse_notes(child)
        elif child.tag == 'warm-up':
            s['warmup'] = parse_notes(child)
        elif child.tag == 'comments':
            s['comments'] = parse_notes(child)
        elif child.tag == 'next':
            s['next'] = parse_notes(child)
        elif child.tag == 'video':
            s['video'] = parse_notes(child)
        else:
            raise NameError('unknown tag "%s"' % child.tag)
    mandatory = ['preparation', 'next']
    for tag in mandatory:
        assert tag in s
    return s

def parse_work(el):
    assert len(el) == 1
    lifts = []
    for child in next(iter(el)):
        assert child.tag == 'lift'
        lifts.append(parse_lift(child))
    return lifts

def parse(file):
    session = {}
    try:
        tree = xml.etree.ElementTree.parse(file)
    except Exception as e:
        print('in file:', file)
        raise e
    root = tree.getroot()
    assert root.tag == 'session'
    for child in root:
        if child.tag == 'meta':
            session['start'] = parse_meta(child)
        elif child.tag == 'venue':
            session['venue'] = parse_venue(child)
        elif child.tag == 'warmup':
            session['warmup'] = parse_warmup(child)
        elif child.tag == 'work':
            session['lifts'] = parse_work(child)
        else:
            raise NameError('unknown tag "%s"' % child.tag)
    mandatory = ['start', 'venue', 'warmup', 'lifts']
    for tag in mandatory:
        assert tag in session
    session['filename'] = os.path.basename(file)
    return session

##############################################################################
# --landing
##############################################################################

def landing(files, title, url_generator):
    sessions = []
    for file in files:
        sessions.append(parse(file))
    sessions = sorted(sessions, key=lambda s: s['start'])
    year = ''

    print('<html><head><title>%s</title>' % title)
    print('<link rel="icon" type="image/x-icon" href="favicon.ico">')
    print('''<style> /* Top-Right-Bottom-Left */
      HTML             { font-family: Helvetica; padding: 20pt 0pt 0pt 20pt; }
      TD               { font-size: 7pt; padding-top: 4pt; padding-bottom: 4pt; }
      TD A             { color: white; }
      P                { font-size: 9pt; padding-top: 6pt; }
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

    block = None
    for s in sessions:
        year_suffix = ' %d' % s['start'].year if year != s['start'].year else ''
        month = s['start'].strftime('%B')
        year = s['start'].year
        if block != month:
            if block:
                print('</tbody></table>')
            print(
                '<h1>%s%s</h1>' % (month, year_suffix),
                '<table><thead><tr><td colspan="2"/>',
                ''.join(('<td class="label">%s</td>') % name for name in order),
                '</tr></thead><tbody>'
            )
            block = month

        url = url_generator(s)
        venue_short = unidecode.unidecode(s['venue']['name']).lower()
        venue_full = s['venue']['name'].encode('ascii', 'xmlcharrefreplace').decode()
        print(
            '<tr><td class="col1"><a href="%s">%s</a></td>' % \
                (url, s['start'].strftime('%-d')),
            '<td class="col2"><a href="%s">%s</a></td>' % \
                (url, s['start'].strftime('%a')[0:2])
        )
        for pos in range(len(order)):
            lift = next((l for l in s['lifts'] \
                if order[pos] == l['kind']), None)
            print('<td class="col4" id="ex%d">%s</td>' % \
                (pos, lift['weight'] if lift else ''), end='')
        print('</tr>')
    if block:
        print('</tbody></table>')

    print('<p><a href="..">../</a></p>')
    print('</body></html>')

##############################################################################
# --single
##############################################################################

def single(file, pictures):
    session = parse(file)

    shortdate = session['start'].strftime('%b %-d')
    print('<html><head><meta charset="utf-8">')
    print('<link rel="icon" type="image/x-icon" href="favicon.ico">')
    print('<title>%s</title></head><body><main>' % shortdate)
    print('<header><h2>%s</h2>' % shortdate)

    # explicit encoding: encode('ascii', 'xmlcharrefreplace').decode()
    print('<p>%s, %s</p></header>' % \
        (time_ampm(session['start']), session['venue']['name']))

    def p_or_ul(obj, prefix):
        if type(obj) == list:
            print('<section>%s<ul>' % prefix)
            for bullet in obj:
                print('<li>%s</li>' % bullet)
            print('</ul></section>')
        else:
            print('<section><p>%s%s</p></section>' % (prefix, capitalise(obj)))

    if 'notes' in session['venue']:
        p_or_ul(session['venue']['notes'], '')

    p_or_ul(session['warmup'], 'Warm-up: ')

    for l in session['lifts']:
        print('<h3>%gkg %s</h3>' % (l['weight'], l['kind']))

        p_or_ul(l['preparation'], '')
        if 'warmup' in l:
            p_or_ul(l['warmup'], 'Warm-up: ')
        if 'comments' in l:
            p_or_ul(l['comments'], 'Comments: ')
        if 'video' in l:
            p_or_ul(l['video'], 'Video: ')
        p_or_ul(l['next'], 'Next: ')

        if l['kind'] in pictures:
            print('<section><p><img width="200" src="%s" alt="%s"></p></section>' % \
                (pictures[l['kind']], shortdate))

    # mobile Safari reader mode seems to require the 'main' semantic HTML tag
    print('</main></body></html>')

##############################################################################
# --summary
##############################################################################

def summary(files):
    sessions = []
    for file in files:
        sessions.append(parse(file))
    sessions = sorted(sessions, key=lambda s: s['start'])
    writer = csv.writer(sys.stdout)
    for s in sessions:
        for l in s['lifts']:
            writer.writerow([
                s['start'].strftime('%Y-%m-%d'),
                l['kind'],
                '%gkg' % l['weight'],
                ''
            ])

##############################################################################
# --database
##############################################################################

def database(files):
    sessions = []
    for file in files:
        sessions.append(parse(file))
    sessions = sorted(sessions, key=lambda s: s['start'])
    writer = csv.writer(sys.stdout, delimiter='\t', lineterminator='\n')
    for s in sessions:
        venue_short = unidecode.unidecode(s['venue']['name']).lower()

        lifts = {
            'squat': -1.0,
            'press': -1.0,
            'bench': -1.0,
            'pull-up': -1.0,
            'deadlift': -1.0,
            'clean': -1.0
        }
        for l in s['lifts']:
            assert l['kind'] in lifts
            lifts[l['kind']] = l['weight']

        writer.writerow([
            s['start'],
            venue_short,
            s['venue']['name'],
            lifts['squat'],
            lifts['press'],
            lifts['bench'],
            lifts['pull-up'],
            lifts['deadlift'],
            lifts['clean']
        ])

##############################################################################
# main
##############################################################################

parser = argparse.ArgumentParser()
parser.add_argument('-t', '--title',
    metavar='TITLE', help='HTML title')
parser.add_argument('-p', '--picture', action='append', nargs=2,
    metavar=('JPGFILE', 'KIND'),
    help='Picture to reference from HTML (with lift of given kind)')
parser.add_argument('-l', '--landing', nargs='+',
    metavar='XMLFILE', help='HTML landing page (HTML filenames from XML ones)')
parser.add_argument('-s', '--summary', nargs='+',
    metavar='XMLFILE', help='CSV summary')
parser.add_argument('-d', '--database', nargs='+',
    metavar='XMLFILE', help='Database-friendly summary with some detail')
parser.add_argument('-1', '--single',
    metavar='XMLFILE', help='HTML diary page')
args = vars(parser.parse_args())
if len(sys.argv) == 1:
    parser.print_usage()
    sys.exit(2)

if args['landing']:
    title = args['title']
    if not title:
        title = 'Swimming'
        print('warning: --title not specifed, will use default "%s"' % title,
            file=sys.stderr)
    landing(args['landing'], args['title'],
        lambda s: '%s.html' % s['filename'].replace('.xml', ''))
elif args['summary']:
    summary(args['summary'])
elif args['database']:
    database(args['database'])
elif args['single']:
    pictures = {}
    if args['picture']:
        pictures = {kind: jpgfile for [jpgfile, kind] in args['picture']}
    single(args['single'], pictures)
else:
    print('must specify --landing, --summary or --single', file=sys.stderr)
    sys.exit(2)
