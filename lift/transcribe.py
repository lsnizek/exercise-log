import datetime
import dateutil.parser
import packaging.version
import sys
import xml.etree.ElementTree

if len(sys.argv) != 3:
    print('usage: %s OPMLFILE YYYYMMDD' % sys.argv[0])
    sys.exit(2)

if sys.argv[1] == '-':
    tree = xml.etree.ElementTree.parse(sys.stdin)
else:
    tree = xml.etree.ElementTree.parse(sys.argv[1])
root = tree.getroot()

# date supplied on the side as OPML document has it in its file name
date = datetime.datetime.strptime(sys.argv[2], '%Y%m%d')

# run some basic OPML checks as per OPML 2.0 specification plus require TITLE
assert root.tag == 'opml'
assert packaging.version.parse(root.attrib['version']).major == 2
assert not root.find('head') is None
assert not root.find('head').find('title') is None
assert not root.find('body') is None
def check_outline_tags(x):
    for child in x:
        assert child.tag == 'outline'
        assert 'text' in child.attrib
        check_outline_tags(child)
check_outline_tags(root.find('body'))

# use OPML TITLE for session type so it shows nice in Yuji Fujishiro's iOS app
session_type = root.find('head').find('title').text
assert session_type == 'lift'

other = ['time', 'venue', 'warm-up']

# gather outlines following the OPML format (lines one level below labels)
# preprocess 'squat 70kg' into 'squat -> weight: 70kg'
outlines = {'other': {}}
def gather_lines(node):
    lines = []
    for subnode in node:
        assert len(list(subnode)) == 0
        lines.append(subnode.attrib['text'])
    return lines
for child in root.find('body'):
    label = child.attrib['text']
    if label in other:
        assert label not in outlines['other']
        outlines['other'][label] = gather_lines(child)
    else:
        [kind, weight] = label.rsplit(maxsplit=1)
        assert kind not in outlines
        suboutlines = {'weight': [weight]}
        for grandchild in child:
            label = grandchild.attrib['text']
            assert label not in suboutlines
            suboutlines[label] = gather_lines(grandchild)
        outlines[kind] = suboutlines

mandatory = {
    'lifts': ['weight', 'preparation', 'next'],
    'other': ['time', 'venue']
}
simple = ['time', 'weight']

# prepare output XML tree
for label in simple:
    for which in outlines:
        if label in outlines[which]:
            if len(outlines[which][label]) > 1:
                raise NameError('simple outline %s (%s) has %d labels' % \
                    (label, which, len(outlines[which][label])))
for label in mandatory['other']:
    if label not in outlines['other']:
        raise NameError('missing "%s"' % label)
for label in mandatory['lifts']:
    for kind in outlines:
        if kind != 'other':
            if label not in outlines[kind]:
                raise NameError('missing "%s" in %s' % (label, kind))
b = xml.etree.ElementTree.TreeBuilder()
b.start('session', {})
meta = b.start('meta', {'type': 'lift'})
b.end('meta')
venue = b.start('venue', {})
b.end('venue')
warmup = b.start('warmup', {})
b.end('warmup')
work = b.start('work', {})
lifts = b.start('lifting', {})
b.end('lifting')
b.end('work')
b.end('session')

# process outline into the output tree
def insert_el(el, tag):
    return xml.etree.ElementTree.SubElement(el, tag)
def insert_notes(el, notes):
    if len(notes) == 1:
        el.text = notes[0]
    elif len(notes) > 1:
        for note in notes:
            if len(note) == 0:
                print('warning: empty note in "%s"' % el.tag, file=sys.stderr)
            insert_el(el, 'note').text = note
def add_or_get_lift(lifts, kind):
    for l in lifts.findall('lift'):
        if l.get('kind') == kind:
            return l
    l = insert_el(lifts, 'lift')
    l.set('kind', kind)
    return l
for label, lines in outlines['other'].items():
    if label == 'time':
        time = dateutil.parser.parse(lines[0] + ' CEST')
        meta.set('start', str(datetime.datetime.combine(date, time.time())))
    elif label == 'venue':
        venue.set('name', lines[0])
        insert_notes(venue, lines[1:])
    elif label == 'warm-up':
        insert_notes(warmup, lines)
    else:
        raise NameError('unknown outline %s' % label)
for kind in outlines:
    if kind == 'other':
        continue
    for label, lines in outlines[kind].items():
        if label == 'weight':
            add_or_get_lift(lifts, kind).set('weight',
                str(int(lines[0].rstrip('kg'))))
        elif label == 'preparation':
            preparation = insert_el(add_or_get_lift(lifts, kind), 'preparation')
            insert_notes(preparation, lines)
        elif label == 'comments':
            insert_notes(insert_el(add_or_get_lift(lifts, kind), 'comments'), lines)
        elif label == 'video':
            insert_notes(insert_el(add_or_get_lift(lifts, kind), 'video'), lines)
        elif label == 'next':
            insert_notes(insert_el(add_or_get_lift(lifts, kind), 'next'), lines)
        else:
            raise NameError('unknown outline %s' % label)

# convert intermediate tree into XML tree
print(xml.etree.ElementTree.tostring(b.close(),
    encoding='unicode', xml_declaration=True))
