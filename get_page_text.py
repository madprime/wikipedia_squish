from __future__ import unicode_literals
import os
import random
import re
import subprocess
import sys
import time
import urllib

with open(sys.argv[1]) as input:
    for line in input:
        page = line.decode('utf-8').rstrip('\n')
        page_quote = re.sub(r'\/', '%2F', urllib.quote(page.encode('utf-8')))
        output_path = os.path.join(sys.argv[2], page_quote + '.txt')
        if os.path.exists(output_path):
            print "Page exists: " + output_path
            continue
        print "Trying to get: " + output_path
        try:
            subprocess.call('rm -r %s' % sys.argv[3], shell=True)
        except OSError:
            pass
        try:
            subprocess.call('rm %s' % sys.argv[3], shell=True)
        except OSError:
            pass
        command = ('mediawiki-extensions-Collection-OfflineContentGenerator-bundler/bin/mw-ocg-bundler' +
                   ' -o %s --prefix enwiki "%s"' % (sys.argv[3], page))
        subprocess.call(command, shell=True)
        command = ('mw-ocg-texter/bin/mw-ocg-texter -o "%s/%s.txt" %s' % (sys.argv[2], page_quote, sys.argv[3]))
        subprocess.call(command, shell=True)
        print "Attempt complete"
        time.sleep(8 * random.random())
