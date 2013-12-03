import gzip
import json
import os
import re
import sys
import urllib

page_list = dict()
page_traffic = dict()

def load_pagetitles(filepath):
    with gzip.open(filepath) as f:
        for line in f:
            data = json.loads(line)
            page_list[data[0].encode('utf-8')] = data[1]

def process_traffic(dirpath, datestr, language):
    re_target = r'pagecounts-' + datestr + '.*\.gz'
    filepaths = sorted([os.path.join(dirpath, x) for x in
                        os.listdir(dirpath) if re.match(re_target, x)])
    outputfile = open(os.path.join(dirpath, 'pagecounts_' + language +
                                        '_' + datestr + '.txt'), 'w')
    for fp in filepaths:
        print "Processing " + fp
        with gzip.open(fp) as f:
            for line in f:
                if not re.match(language + ' ', line):
                    continue
                data = line.split()
                # Should be 4 entries.
                # This line in pagecounts-20130301-000000.gz failed to replace
                # spaces with underscores, prompting a concatenation hack:
                # 'en 2000 United States Census 1 655'
                if len(data) > 4:
                    data[1] = '_'.join(data[1:-2])
                    data[2] = data[-2]
                    data[3] = data[-1]
                # Convert to Unicode.
                target = re.sub('&amp;', '&',
                                re.sub('_', ' ', urllib.unquote(data[1])))
                if target in page_list:
                    title = target
                    # If redirect exists, use that as title.
                    if page_list[title]:
                        title = page_list[title]
                        # Not using a while loop to avoid circular loops.
                        # Just attempt three times.
                        if title in page_list and page_list[title]:
                            title = page_list[title]
                            if title in page_list and page_list[title]:
                                title = page_list[title]
                    if title in page_traffic:
                        page_traffic[title] += int(data[2])
                    else:
                        page_traffic[title] = int(data[2])

    for pagetitle in page_traffic:
        output = json.dumps((pagetitle, page_traffic[pagetitle]), ensure_ascii=False)
        try:
            outputfile.write((output + '\n'))
        except UnicodeEncodeError:
            outputfile.write((output + '\n').encode('utf-8'))

if __name__ == "__main__":
    print "Loading page traffic data"
    load_pagetitles(sys.argv[1])
    print "Done loading"
    datestrings = ['20130301',
                   '20130302',
                   '20130303',
                   '20130304',
                   '20130305',
                   '20130306',
                   '20130307',
                   '20130308',
                   '20130309',
                   '20130310',
                   '20130311',
                   '20130312',
                   '20130313',
                   '20130314',
                   ]
    for datestr in datestrings:
        process_traffic(sys.argv[2], datestr, 'en')
