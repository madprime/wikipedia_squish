from __future__ import unicode_literals
import subprocess
import sys
import urllib

with open(sys.argv[1]) as input:
    for line in input:
        try:
            subprocess.call('rm -r %s' % sys.argv[3], shell=True)
        except OSError:
            pass
        try:
            subprocess.call('rm %s' % sys.argv[3], shell=True)
        except OSError:
            pass
        page = line.decode('utf-8').rstrip('\n')
        page_quote = urllib.quote(page.encode('utf-8'))
        command = ('mediawiki-extensions-Collection-OfflineContentGenerator-bundler/bin/mw-ocg-bundler' +
                   ' -o %s --prefix enwiki "%s"' % (sys.argv[3], page))
        subprocess.call(command, shell=True)
        command = ('mw-ocg-texter/bin/mw-ocg-texter -o "%s/%s.txt" %s' % (sys.argv[2], page_quote, sys.argv[3]))
        subprocess.call(command, shell=True)
