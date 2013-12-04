"""Output a list of JSON-encoded page titles and redirects (if they exist)."""

import bz2
import json
import re
import sys
from xml.dom import minidom
from BeautifulSoup import BeautifulStoneSoup

def process_page(data, targets=[]):
    target_data = None
    title = ''
    for line in data.split('\n'):
        re_title = r'    <title>(.*)</title>'
        if re.match(re_title, line):
            title = re.match(re_title, line).groups()[0]
            try:
                title = unicode(BeautifulStoneSoup(title,
                                                   convertEntities=BeautifulStoneSoup.ALL_ENTITIES))
            except:
                continue
            title = re.sub('&amp;', '&', title)
            if title in targets:
                target_data = targets[title]
            else:
                break
                return None
    if not target_data:
        return None
    else:
        xml_parsed = minidom.parseString(data)
        return target_data[0], title, target_data[1], xml_parsed.getElementsByTagName('text')[0].firstChild.data

def get_pages(target_pages_filepath, number):
    targets = dict()
    n = 0
    with open(target_pages_filepath, 'r') as f:
        for line in f:
            n += 1
            if n >= number:
                break
            data = json.loads(line)
            targets[data[1]] = [n, data[0]]
    return targets

if __name__ == "__main__":
    targets = get_pages(sys.argv[2], int(sys.argv[3]))
    output_file = open(sys.argv[4], 'w')
    with bz2.BZ2File(sys.argv[1], 'r') as dump:
        in_page = False
        page_data = ''
        for line in dump:
            if re.match('  <page>', line):
                page_data = line
                in_page = True
            elif re.match('  </page>', line):
                in_page = False
                page_data += line
                parsed_data = process_page(page_data, targets=targets)
                if parsed_data:
                    output = json.dumps(parsed_data, ensure_ascii=False) + '\n'
                    try:
                        output_file.write(output)
                    except UnicodeEncodeError:
                        output_file.write(output.encode('utf-8'))
                page_data = ''
            elif in_page:
                page_data += line
