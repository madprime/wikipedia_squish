from __future__ import unicode_literals
import codecs
import gzip
import re
import sys
import urllib

outfile = codecs.open(sys.argv[2], encoding='utf-8', mode='w')

with gzip.open(sys.argv[1]) as sorted_top_pages:
    n = 0
    for line in sorted_top_pages:
        data = line.split()
        page_name = urllib.unquote(data[0]).decode('utf-8')
        page_name = re.sub(r'_', r' ', page_name)
        if re.match(r'^Main Page$', page_name):
            continue
        if re.match(r'^(index\.html|(w\/|W|\/|\/w\/|W\/|)index\.php|)$', page_name):
            continue
        if re.match(r'^(Special|Portal|Wikipedia|Help|Talk|File|Category|Template|Template talk|User):', page_name):
            continue
        outfile.write(page_name + '\n')
        n += 1
        if n >= 100000:
            break
