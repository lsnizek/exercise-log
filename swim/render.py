import argparse
import csv
import datetime
import os
import sys
import unidecode
import xml.etree.ElementTree

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
    assert el.attrib['type'] == 'swim'
    start = datetime.datetime.strptime(el.attrib['start'], '%Y-%m-%d %H:%M:%S')
    kind = el.attrib['kind']
    if 'volume' in el.attrib:
        volume = int(el.attrib['volume'])
    else:
        volume = 0
    return start, kind, volume

def parse_venue(el):
    assert 'name' in el.attrib
    venue = {'name': el.attrib['name']}
    notes = parse_notes(el)
    if notes:
        venue['notes'] = notes
    if 'spacious' in el.attrib:
        venue['spacious'] = bool(el.attrib['spacious'])
    return venue

def parse_warmup(el):
    return parse_notes(el)

def parse_set(el):
    s = {}
    if 'stroke' in el.attrib:
        s['stroke'] = el.attrib['stroke']
    for child in el:
        if child.tag == 'preparation':
            s['preparation'] = parse_notes(child)
        elif child.tag == 'structure':
            s['structure'] = parse_notes(child)
        elif child.tag == 'summary':
            s['summary'] = parse_notes(child)
        elif child.tag == 'comments':
            s['comments'] = parse_notes(child)
        elif child.tag == 'times':
            s['times'] = parse_notes(child)
        elif child.tag == 'next':
            s['next'] = parse_notes(child)
        elif child.tag == 'video':
            s['video'] = parse_notes(child)
        else:
            raise NameError('unknown tag "%s"' % child.tag)
    mandatory = ['preparation', 'summary', 'next']
    for tag in mandatory:
        assert tag in s
    return s

def parse_work(el):
    assert len(el) == 1
    sets = []
    for child in next(iter(el)):
        assert child.tag == 'set'
        sets.append(parse_set(child))
    return sets

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
            session['start'], session['kind'], session['volume'] = \
                parse_meta(child)
        elif child.tag == 'venue':
            session['venue'] = parse_venue(child)
        elif child.tag == 'warmup':
            session['warmup'] = parse_warmup(child)
        elif child.tag == 'work':
            session['sets'] = parse_work(child)
        else:
            raise NameError('unknown tag "%s"' % child.tag)
    mandatory = ['start', 'kind', 'venue', 'warmup', 'sets']
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
    year = datetime.datetime.now().year
    sessions = sorted(filter(lambda s: s['start'].year == year,
        sessions), key=lambda s: s['start'])

    print('<html><head><title>%s</title>' % title)
    print('<link rel="icon" type="image/x-icon" href="favicon.ico">')
    print('''<style> /* Top-Right-Bottom-Left */
      TD.link:hover    { cursor: pointer; }
      HTML             { font-family: Helvetica; padding: 20pt 0pt 0pt 20pt; }
      TD               { font-size: 7pt; }
      TD A             { color: white; }
      P                { font-size: 9pt; }
      TABLE            { border-collapse: collapse; }
      H1               { font-size: 10pt; margin-top: 16pt; margin-bottom: 10pt; }
      .label           { font-weight: bold; text-transform: capitalize; text-align: center; }
      .col1, .col2     { background: black; color: white; }
      .col1            { width: 16pt; padding-right: 7pt; text-align: right; }
      .col2            { width: 16pt; }
      .col3            { width: 38pt; padding-right: 7pt; text-align: right; }
      .col4            { width: 28pt; text-align: center; }
      .col5            { width: 70pt; padding-left: 4pt; color: white; }
      .col6            { width: 200pt; padding-left: 4pt; padding-right: 20pt; }
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
      .other           { background: black; }
    </style>''')
    venue_dimensions = 'width="18" height="18"'
    print('</head><body>')

    block = None
    for s in sessions:
        month = s['start'].strftime('%B')
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

        url = url_generator(s)
        venue_short = unidecode.unidecode(s['venue']['name']).lower()
        venue_full = s['venue']['name'].encode('ascii', 'xmlcharrefreplace').decode()
        summary = []
        strokes = []
        for workset in s['sets']:
            summary.append(workset['summary'])
            if 'stroke' in workset:
                strokes.append(workset['stroke'])
        stroke_color = 'other' # could support multi-stroke sessions, etc
        stroke_prefix = ''
        if len(list(set(strokes))) == 1:
            stroke = list(set(strokes))[0]
            if stroke in ['fly', 'back', 'breast', 'free']:
                stroke_color = stroke + '200'
                stroke_prefix = stroke + ' '
            elif stroke == 'IM':
                stroke_color = 'im200'
                stroke_prefix = 'IM '
        print(
            '<tr>',
            '<td class="col1">%s</td>' % \
                (s['start'].strftime('%-d')),
            '<td class="col2">%s</td>' % \
                (s['start'].strftime('%a')[0:2]),
            '<td class="col3%s">%s</td>' % \
                (' spacious' if spacious else '',
                time_ampm(s['start'])),
            '<td class="col4"><img %s src="%s" alt="%s" title="%s"/></td>' % \
                (venue_dimensions, '%s.png' % venue_short, venue_full, venue_full),
            '<td onclick="window.location=\'%s\';" class="col5 link %s">' \
                '<a href="%s">%s%s</a></td>' % \
                (url, stroke_color, url, stroke_prefix, s['kind']),
            '<td class="col6">%s</td>' % ', '.join(summary),
            '<td class="col7">%dm</td>' % s['volume'],
            '</tr>')
    if block:
        print('</tbody></table>')

    print('<p><a href="..">../</a></p>')
    print('</body></html>')

##############################################################################
# --single
##############################################################################

def single(file, picture):
    session = parse(file)

    shortdate = session['start'].strftime('%b %-d')
    print('<html><head><meta charset="utf-8">')
    print('<link rel="icon" type="image/x-icon" href="favicon.ico">')
    print('<title>%s</title></head><body><main>' % shortdate)
    print('<header><h2>%s</h2>' % shortdate)

    strokes = []
    for s in session['sets']:
        if 'stroke' in s:
            strokes.append(s['stroke'])

    # explicit encoding: encode('ascii', 'xmlcharrefreplace').decode()
    print('<p>%s, %s, %s%s, %dm</p></header>' % (\
        time_ampm(session['start']),
        session['venue']['name'],
        '-'.join(strokes) + ', ' if len(strokes) > 0 else '',
        session['kind'],
        session['volume']))

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

    for s in session['sets']:
        print('<h3>%s</h3>' % s['summary'])

        p_or_ul(s['preparation'], '')
        if 'comments' in s:
            p_or_ul(s['comments'], 'Comments: ')
        if 'structure' in s:
            p_or_ul(s['structure'], 'Structure: ')
        if 'times' in s:
            p_or_ul(s['times'], 'Times: ')
        if 'video' in s:
            p_or_ul(s['video'], 'Video: ')
        p_or_ul(s['next'], 'Next: ')

    if picture:
        print('<p><img width="480" src="%s"/></p>' % picture)

    # mobile Safari reader mode seems to require the 'main' semantic HTML tag
    print('</main></body></html>')

##############################################################################
# --totals
##############################################################################

def totals(files):
    sessions = []
    for file in files:
        sessions.append(parse(file))
    year = datetime.datetime.now().year
    sessions = sorted(filter(lambda s: s['start'].year == year,
        sessions), key=lambda s: s['start'])
    volume = {}
    for s in sessions:
        volume.setdefault(s['start'].month, [])
        volume[s['start'].month].append(s['volume'])
    writer = csv.writer(sys.stdout)
    for month in volume:
        writer.writerow([datetime.date(year, month, 1).strftime('%B %Y'),
            sum(volume[month]), len(volume[month])])

##############################################################################
# main
##############################################################################

parser = argparse.ArgumentParser()
parser.add_argument('-t', '--title',
    metavar='TITLE', help='HTML title')
parser.add_argument('-p', '--picture',
    metavar='JPGFILE', help='Picture to reference from HTML')
parser.add_argument('-l', '--landing', nargs='+',
    metavar='XMLFILE', help='HTML landing page (HTML filenames from XML ones)')
parser.add_argument('-s', '--totals', nargs='+',
    metavar='CSVFILE', help='Totals listing')
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
elif args['totals']:
    totals(args['totals'])
elif args['single']:
    single(args['single'], args['picture'])
else:
    print('must specify --landing, --totals or --single', file=sys.stderr)
    sys.exit(2)
