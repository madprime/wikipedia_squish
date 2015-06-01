from __future__ import unicode_literals

import codecs
import csv
import os
import re
import sys
import urllib

CANONICAL_CODE_CSV = 'to_canonical_code.csv'
LINE_LENGTH = 80

# Abort checking for pages after this many don't exist in the dir - we've
# almost certainly run past the number that have been pulled from Wikipedia.
SKIP_THRESHOLD = 1000


def get_pages_list(pagelist_filepath, flatpages_dir):
    """
    Returns list of pages with files in target directory, in order of traffic.
    """
    pagelist = list()
    skipped = 0
    with open(pagelist_filepath) as pagelist_file:
        for line in pagelist_file:
            article = line.decode('utf-8').rstrip('\n')
            article = re.sub(r'\/', '%2F', urllib.quote(article.encode('utf-8')))
            filename = article + '.flat.txt'
            inputpath = os.path.join(flatpages_dir, filename)
            if not os.path.exists(inputpath):
                print "Can't find " + inputpath
                skipped += 1
                if skipped >= SKIP_THRESHOLD:
                    break
                else:
                    continue
            else:
                skipped = 0
                pagelist.append(filename)
    return pagelist


def get_huffman_code():
    huffman_code = dict()
    with open(CANONICAL_CODE_CSV) as inputfile:
        csv_reader = csv.reader(inputfile)
        csv_reader.next()
        for row in csv_reader:
            char = row[0]
            if char == '\\n':
                char = '\n'
            huffman_code[char] = row[4]
    return huffman_code


if __name__ == "__main__":
    pagelist_filepath = sys.argv[1]
    flatpages_dir = sys.argv[2]
    binary_dir = sys.argv[3]
    pagelist = get_pages_list(pagelist_filepath, flatpages_dir)
    huffman_code = get_huffman_code()
    for page_filename in pagelist:
        new_filename = page_filename[0:-9] + '.binary.txt'
        print page_filename
        print new_filename
        inputpath = os.path.join(flatpages_dir, page_filename)
        outputpath = os.path.join(binary_dir, new_filename)
        if os.path.exists(outputpath):
            continue
        with codecs.open(inputpath, 'r', encoding='utf-8') as inputfile:
            article = ''.join(inputfile.readlines())
            binary = ''.join([huffman_code[x] for x in article])
            with open(outputpath, 'w') as outputfile:
                while len(binary) > 80:
                    bin_line = binary[0:80]
                    binary = binary[80:]
                    outputfile.write(bin_line + '\n')
                outputfile.write(binary + '\n')
        print "Done with " + page_filename
