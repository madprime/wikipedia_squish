"""Output a list of JSON-encoded page titles and redirects (if they exist)."""

import bz2
import json
import re
import sys
from BeautifulSoup import BeautifulStoneSoup

# Ignore pages which direct to non-main namespaces, e.g. "Wikipedia:Foo"
namespace_list = ['User',
                  'Wikipedia',
                  'File',
                  'MediaWiki',
                  'Help',
                  'Category',
                  'Portal',
                  'Book',
                  'Education Program',
                  'TimedText',
                  'Module',
                  'Special',
                  'Media',
                  'Template',
                  'Talk',]

def process_page(data):
    title = None
    redirect = None
    for line in data.split('\n'):
        re_title = r'    <title>(.*)</title>'
        re_redirect = r'    <redirect title="(.*)" />'
        if re.match(re_title, line) and not title:
            title = re.match(re_title, line).groups()[0]
            title = unicode(BeautifulStoneSoup(title,
                        convertEntities=BeautifulStoneSoup.ALL_ENTITIES))
            title = re.sub('&amp;', '&', title)
        elif re.match(re_redirect, line) and not redirect:
            redirect = re.match(re_redirect, line).groups()[0]
            redirect = unicode(BeautifulStoneSoup(redirect,
                           convertEntities=BeautifulStoneSoup.ALL_ENTITIES))
            redirect = re.sub('&amp;', '&', redirect)
    re_namespace = '^(..:)?(' + '|'.join(namespace_list) + ')( talk)?:'
    if redirect:
        if not re.match(re_namespace, redirect):
            return json.dumps((title, redirect), ensure_ascii=False)
        else:
            return None
    elif title and not re.match(re_namespace, title):
        return json.dumps((title, None), ensure_ascii=False)
    else:
        return None

if __name__ == "__main__":
    output_file = open(sys.argv[2], 'w')
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
                title_data = process_page(page_data)
                if title_data:
                    try:
                        output_file.write((title_data + '\n'))
                    except UnicodeEncodeError:
                        output_file.write((title_data + '\n').encode('utf-8'))
                page_data = ''
            elif in_page:
                page_data += line
