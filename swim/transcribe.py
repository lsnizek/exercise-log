import datetime
import dateutil.parser
import packaging.version
import sys
import xml.etree.ElementTree

def insert(el, tag):
    return xml.etree.ElementTree.SubElement(el, tag)

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
assert root.find('head') != None
assert root.find('head').find('title') != None
assert root.find('body') != None
def check_outline_tags(x):
    for child in x:
        assert child.tag == 'outline'
        assert 'text' in child.attrib
        check_outline_tags(child)
check_outline_tags(root.find('body'))

# use OPML TITLE for session type so it shows nice in Yuji Fujishiro's iOS app
session_type = root.find('head').find('title').text

# gather outlines with labels at level 0 and lines at level 1
outlines = {}
for child in root.find('body'):
    label = child.attrib['text']
    assert label not in outlines
    lines = []
    for grandchild in child:
        assert len(list(grandchild)) == 0
        lines.append(grandchild.attrib['text'])
    outlines[label] = lines

# prepare output XML tree
session_types = {'swim': 'swimming', 'lift': 'weights'}
assert session_type in session_types
for simple in ['time', 'kind', 'volume', 'stroke', 'summary']:
    if simple in outlines:
        assert len(outlines[simple]) == 1
    else:
        assert len(outlines[simple]) >= 1
for mandatory in ['time', 'kind', 'venue', 'warm-up']:
    assert mandatory in outlines
if session_type == 'swim':
    for mandatory in ['preparation', 'summary', 'times', 'next']:
        assert mandatory in outlines
b = xml.etree.ElementTree.TreeBuilder()
b.start('session', {})
meta = b.start('meta', {'type': session_type})
b.end('meta')
venue = b.start('venue', {})
b.end('venue')
warmup = b.start('warmup', {})
b.end('warmup')
work = b.start('work', {})
sets = b.start(session_types[session_type], {})
b.end(session_types[session_type])
b.end('work')
b.end('session')

# process outline into the output tree
def insert_one_or_more_notes(el, notes):
    if len(notes) == 1:
        el.text = notes[0]
    elif len(notes) > 1:
        for note in notes:
            insert(el, 'note').text = note
def add_or_get_swim_set(sets):
    s = sets.find('set')
    if s != None:
        return s
    else:
        return insert(sets, 'set')
for label, lines in outlines.items():
    if label == 'time':
        time = dateutil.parser.parse(lines[0] + ' CEST')
        meta.set('start', str(datetime.datetime.combine(date, time.time())))
    elif label == 'kind':
        meta.set('kind', lines[0])
    elif label == 'volume':
        meta.set('volume', str(int(lines[0])))
    elif label == 'venue':
        venue.set('name', lines[0])
        insert_one_or_more_notes(venue, lines[1:])
        for note in lines[1:]:
            if note.find('spacious') >= 0:
                venue.set('spacious', True)
    elif label == 'warm-up':
        insert_one_or_more_notes(warmup, lines)
    elif label == 'preparation':
        assert session_type == 'swim'
        preparation = insert(add_or_get_swim_set(sets), 'preparation')
        insert_one_or_more_notes(preparation, lines)
    elif label == 'stroke':
        assert session_type == 'swim'
        add_or_get_swim_set(sets).set('stroke', lines[0])
    elif label == 'summary':
        assert session_type == 'swim'
        insert(add_or_get_swim_set(sets), 'summary').text = lines[0]
    elif label == 'structure':
        assert session_type == 'swim'
        insert_one_or_more_notes(insert(add_or_get_swim_set(sets),
            'structure'), lines)
    elif label == 'comments':
        insert_one_or_more_notes(insert(add_or_get_swim_set(sets),
            'comments'), lines)
    elif label == 'times':
        insert_one_or_more_notes(insert(add_or_get_swim_set(sets),
            'times'), lines)
    elif label == 'next':
        assert session_type == 'swim'
        insert_one_or_more_notes(insert(add_or_get_swim_set(sets),
            'next'), lines)
    else:
        raise NameError('unknown outline %s' % label)

# convert intermediate tree into XML tree
print(xml.etree.ElementTree.tostring(b.close(),
    encoding='unicode', xml_declaration=True))
