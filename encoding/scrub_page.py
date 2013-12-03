import json
import re
import sys
from unidecode import unidecode

def remove_lang_templates(string):
    # Preserves text inside template, as it is displayed in the page.
    re_str_lang = ur'{{lang\|.*?\|(.*?)}}'
    return re.sub(re_str_lang, r'\1', string, re.U | re.S)

def remove_all_templates(string):
    re_str_templates = ur'(\{\{[^{}]*?\}\})'
    while re.search(re_str_templates, string, re.U | re.S):
        string = re.sub(re_str_templates, ur'', string, flags=re.U | re.S)
    return string

def remove_refs(string):
    re_str_refs = ur'(<ref.*?(>.*?</ref>|/>))'
    while re.search(re_str_refs, string, re.U | re.S | re.M):
        string = re.sub(re_str_refs, '', string, flags=re.U | re.S | re.M)
    return string

def remove_html_tags(string):
    re_str_html_tags = ur'<[^<>]*?>'
    return re.sub(re_str_html_tags, '', string, flags=re.U | re.S)

def remove_nonimage_wikilinks(string):
    # Removes in a manner that preserves link as word in text.
    re_str_nonimage_wikilinks = ur'\[\[(?![Ii]mage:).*?\|?([^|]*?)\]\]'
    while re.search(re_str_nonimage_wikilinks, string, re.U | re.S):
        string = re.sub(re_str_nonimage_wikilinks, ur'\1', string, 
                        flags=re.U | re.S)
    return string

def remove_image_wikilinks(string):
    # Removes all content
    re_str_image_wikilinks = ur'\[\[[Ii]mage:.*?\]\]'
    while re.search(re_str_image_wikilinks, string, re.U | re.S):
        string = re.sub(re_str_image_wikilinks, '', string, 
                        flags=re.U | re.S)
    return string

def remove_wikitables(string):
    re_str_wikitables = ur'\{\|.*?\|\}'
    while re.search(re_str_wikitables, string, re.U | re.S | re.M):
        string = re.sub(re_str_wikitables, '', string,
                        flags=re.U | re.S | re.M)
    return string

def compress_newlines(string):
    re_str_dbl_newline = ur'\n\n'
    while re.search(re_str_dbl_newline, string, re.U | re.S):
        string = re.sub(re_str_dbl_newline, '\n', string, flags=re.U | re.S)
    return string

def scrub_page(page):
    page = remove_refs(page)
    page = remove_html_tags(page)
    page = remove_lang_templates(page)
    page = remove_all_templates(page)
    page = remove_nonimage_wikilinks(page)
    page = remove_image_wikilinks(page)
    page = remove_wikitables(page)
    page = compress_newlines(page)
    page = unidecode(page)
    return page

if __name__ == "__main__":
    with open(sys.argv[1]) as f:
        for line in f:
            data = json.loads(line)
            page = '=' + data[1] + '=\n' + data[3]
            data_out = json.dumps([scrub_page(page)])
            json.loads(data_out)
            try:
                print data_out
            except UnicodeEncodeError:
                print data_out.encode('utf-8')
