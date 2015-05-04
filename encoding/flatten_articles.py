# coding=utf-8
from __future__ import unicode_literals

import codecs
import os
import re
import sys
from unidecode import unidecode


def trim_article(article_text):
    # Cut articles from References section onwards.
    article_text = re.sub(r'\n\nReferences\n\n.*$', r'\n', article_text,
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
    return article_text

if __name__ == "__main__":
    pages_dir = sys.argv[1]
    flatten_dir = sys.argv[2]
    pages_list = os.listdir(pages_dir)
    for page_filename in pages_list:
        new_filename = page_filename.rstrip('.txt') + '.flat.txt'
        inputpath = os.path.join(pages_dir, page_filename)
        outputpath = os.path.join(flatten_dir, new_filename)
        with codecs.open(inputpath, 'r', encoding='utf-8') as inputfile:
            article = ''.join(inputfile.readlines())
            flattened = trim_article(article)
            with open(outputpath, 'w') as outputfile:
                outputfile.write(flattened)
