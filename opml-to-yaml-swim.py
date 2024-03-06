import datetime
import sys
import xml.etree.ElementTree
import yaml # pyyaml

if len(sys.argv) != 3:
    print('usage: opmn-to-yaml-swim.py OPMLFILE YYYY-MM-DD')
    sys.exit(2)

if sys.argv[1] == '-':
    root = xml.etree.ElementTree.fromstring(''.join(sys.stdin.readlines()))
else:
    tree = xml.etree.ElementTree.parse(sys.argv[1])
    root = tree.getroot()
assert root.tag == 'opml'

result = {'work': {'swimming': [{}]}}
result['start'] = {'date': sys.argv[2]} # stick to string

for child in root:
    if child.tag == 'head':
        for grandchild in child:
            if grandchild.tag == 'title':
                result['type'] = grandchild.text
    elif child.tag == 'body':
        for grandchild in child:
            if grandchild.tag == 'outline':
                assert 'text' in grandchild.attrib
                lines = []
                for line in grandchild:
                    if line.tag == 'outline':
                        assert 'text' in line.attrib
                        lines += [line.attrib['text']]
                label = grandchild.attrib['text']
                contents = ''
                if len(lines) == 1:
                    contents = lines[0]
                else:
                    contents = lines
                if label == 'time':
                    time = datetime.datetime.strptime(contents, '%H:%M')
                    result['start']['time'] = '%s CEST' % time.strftime('%H:%M')
                elif label == 'kind':
                    result['kind'] = contents
                elif label == 'volume':
                    result['volume'] = int(contents)
                elif label == 'venue':
                    result['venue'] = {'name': contents[0]}
                    if len(contents) == 2:
                        result['venue']['note'] = contents[1]
                    elif len(contents) > 2:
                        result['venue']['note'] = contents[1:]
                elif label == 'warm-up':
                    result['warmup'] = {'note': contents}
                elif label == 'preparation':
                    result['work']['preparation'] = contents
                elif label == 'stroke':
                    result['work']['swimming'][0]['stroke'] = contents
                elif label == 'summary':
                    result['work']['swimming'][0]['summary'] = contents
                elif label == 'structure':
                    result['work']['swimming'][0]['structure'] = contents
                elif label == 'note':
                    result['work']['swimming'][0]['note'] = contents
                elif label == 'times':
                    result['work']['swimming'][0]['times'] = contents
                elif label == 'next':
                    result['next'] = contents

assert result['type'] == 'swim'

print(yaml.dump([result], allow_unicode=True))
