"""Download traffic data files from dumsp.wikimedia.org, check md5sums."""

import hashlib
import os
import re
import sys
import urllib

START_YEAR = 2013
START_MONTH = 8
END_YEAR = 2013
END_MONTH = 10

def generate_month_list(start_year, start_month, end_year, end_month):

    def format_month(monthnum):
        if monthnum < 10:
            return '0' + str(monthnum)
        else:
            return str(monthnum)

    month_list = []
    if start_year == end_year:
        month_list = [(str(start_year), format_month(x))
                       for x in range(start_month,end_month + 1)]
    else:
        month_list = [(str(start_year), format_month(x))
                       for x in range(start_month, 13)]
        if (end_year - start_year) > 1:
            for year in range(start_year + 1, end_year):
                month_list += [(str(year), format_month(x))
                               for x in range(1, 13)]
        month_list += [(str(end_year), format_month(x))
                       for x in range(1, end_month + 1)]
    return month_list


def get_month_counts(year, month, local_dir):
    """Get or check for traffic files for a given month.

    Checks if files are locally present. If so, check md5sum.
    If not present or md5sum mismatch, download file.
    """
    url = ('http://dumps.wikimedia.org/other/pagecounts-raw/' +
           year + '/' + year + '-' + month + '/')

    # Get or load filenames and hashes
    hashes = dict()
    hashes_filepath = os.path.join(local_dir, 'md5sums.txt')
    if not os.path.exists(hashes_filepath):
        hashes_url = url + 'md5sums.txt'
        print "Retrieving remote hash data from " + hashes_url
        urllib.urlretrieve(hashes_url, hashes_filepath)
    with open(hashes_filepath, 'r') as hash_data:
        for line in hash_data:
            data = line.split()
            if re.match('pagecounts', data[1]):
                hashes[data[1]] = data[0]

    # Hash checking function
    def checkhash(filepath, expected):
        print "Checking hash for: " + filepath
        try:
            with open(counts_filepath, 'r') as f:
                m = hashlib.md5()
                filedata = f.read(8192)
                while filedata:
                    m.update(filedata)
                    filedata = f.read(8192)
                if m.hexdigest() == expected:
                    return True
                else:
                    return False
        except IOError:
            return False

    # Get and/or check count files
    for filename in sorted(hashes):
        counts_filepath = os.path.join(local_dir, filename)
        counts_url = url + filename
        if not os.path.exists(counts_filepath):
            print "Downloading: " + counts_url
            urllib.urlretrieve(counts_url, counts_filepath)
        if not checkhash(counts_filepath, hashes[filename]):
            counts_url = url + filename
            print "Incomplete or corrupted file, trying again: " + counts_url
            urllib.urlretrieve(counts_url, counts_filepath)
            if not checkhash(counts_filepath, hashes[filename]):
                print "Hash still doesn't match. Giving up on: " + counts_url

if __name__ == "__main__":
    target_directory = sys.argv[1]
    assert os.path.exists(target_directory)
    month_counts = []

    # Months are tuples of year and month number as strings, e.g. ('2013', '09')    
    for month in generate_month_list(START_YEAR, START_MONTH, END_YEAR, END_MONTH):
        month_directory = os.path.join(target_directory, month[0] + '-' + month[1])
        if not os.path.exists(month_directory):
            print "Making directory for " + month_directory
            os.makedirs(month_directory)
        get_month_counts(month[0], month[1], month_directory)
