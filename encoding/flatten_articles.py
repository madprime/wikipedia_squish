# coding=utf-8
from __future__ import unicode_literals

import codecs
import os
import re
import sys
import urllib
from unidecode import unidecode

# Abort checking for pages after this many don't exist in the dir - we've
# almost certainly run past the number that have been pulled from Wikipedia.
SKIP_THRESHOLD = 1000


def get_pages_list(pagelist_filepath, pages_dir):
    """
    Returns list of non-duplicate pages with files in target directory.

    Duplicates are determined based on a hash of all but the first line;
    duplicate pages originate from grabbing text for targets that were
    actually redirects to another page. The first page in the inputed page
    list (i.e. with the most traffic) is considered the primary page.
    """
    content_hashes = set()
    pagelist = list()
    skipped = 0
    with open(pagelist_filepath) as pagelist_file:
        for line in pagelist_file:
            article = line.decode('utf-8').rstrip('\n')
            article = re.sub(r'\/', '%2F', urllib.quote(article.encode('utf-8')))
            filename = article + '.txt'
            inputpath = os.path.join(pages_dir, filename)
            if not os.path.exists(inputpath):
                skipped += 1
                if skipped >= SKIP_THRESHOLD:
                    break
                else:
                    continue
            with codecs.open(inputpath, 'r', encoding='utf-8') as inputfile:
                content = ''.join(inputfile.readlines()[1:])
                content_hash = hash(content)
                if content_hash in content_hashes:
                    continue
                else:
                    skipped = 0
                    content_hashes.add(content_hash)
                    pagelist.append(filename)
    return pagelist


def trim_article(article_text):
    # Cut articles from References section onwards.
    article_text = re.sub(r'\n\nReferences\n\n.*$', r'\n', article_text,
                          flags=re.S)
    article_text = re.sub(r'\n\nSource notes\n.*$', r'\n', article_text,
                          flags=re.S)
    # Try to preserve usage of superscript in equations.
    while re.search(r'([¹²³⁴⁵⁶⁷⁸⁹⁰]+)\}', article_text):
        exponent = unidecode(
            re.search(r'([¹²³⁴⁵⁶⁷⁸⁹⁰]+)\}', article_text).groups()[0])
        article_text = re.sub(r'([¹²³⁴⁵⁶⁷⁸⁹⁰]+)\}', '^' + exponent + '}', article_text,
                              count=1)
    # Remove all other superscript numbers as likely to be footnotes.
    article_text = re.sub(r'[¹²³⁴⁵⁶⁷⁸⁹⁰]+ (?=[¹²³⁴⁵⁶⁷⁸⁹⁰])','', article_text)
    article_text = re.sub(r'[¹²³⁴⁵⁶⁷⁸⁹⁰]+','', article_text)
    article_text = unidecode(article_text)
    # Convert multiline paragraphs to one line, and double linebreaks to single
    article_text = re.sub(r'\n(?!\n)', '', article_text)
    article_text = re.sub(r'\n+', '\n', article_text)
    # Remove all spaces and convert to uppercase.
    article_text = article_text.upper()
    article_text = re.sub(r'[ \t]', '', article_text)
    # Unidecode and other steps should has assured this, but script has failed
    # on a unicode errors so we'll explicitly filter on valid characters.
    article_text_2 = re.sub(r'[^A-Z0-9\,\.\n\-\"\'\(\)\:\[\]\;\/\\\%\{\}\&' +
                            r'\+\$\_\?\=\!\*\#\^\<\>\|\@\`\~]', '',
                            article_text)
    return article_text_2


if __name__ == "__main__":
    pagelist_filepath = sys.argv[1]
    pages_dir = sys.argv[2]
    flatten_dir = sys.argv[3]
    pages_list = get_pages_list(pagelist_filepath, pages_dir)
    print len(pages_list)
    for page_filename in pages_list:
        new_filename = page_filename[0:-4] + '.flat.txt'
        inputpath = os.path.join(pages_dir, page_filename)
        outputpath = os.path.join(flatten_dir, new_filename)
        with codecs.open(inputpath, 'r', encoding='utf-8') as inputfile:
            article = ''.join(inputfile.readlines())
            flattened = trim_article(article)
            with open(outputpath, 'w') as outputfile:
                outputfile.write(flattened)
