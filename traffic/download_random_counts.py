"""Download traffic data files from dumsp.wikimedia.org, check md5sums."""

import hashlib
import os
import random
import re
import subprocess
import sys
import urllib

START_YEAR = 2008
START_MONTH = 1
END_YEAR = 2014
END_MONTH = 12
NUM_PAGES = 12


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
        print "Retrieving remote hash data from '" + hashes_url + "'"
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

    # Get daily pagecount prefixes
    daily_pagecount_prefixes = sorted(set([re.match('(pagecounts-[0-9]{8})-',
                                                    x).groups()[0] for
                                           x in hashes if
                                           re.match('pagecounts-[0-9]{8}-',x)]))
    rand_day_index = random.randint(0, len(daily_pagecount_prefixes) - 1)
    rand_day_prefix = daily_pagecount_prefixes[rand_day_index]
    daily_filenames = [x for x in sorted(hashes) if
                       re.match(rand_day_prefix, x)]
    rand_hour_index = random.randint(0, len(daily_filenames) - 1)
    rand_hour_filename = daily_filenames[rand_hour_index]
    counts_filepath = os.path.join(local_dir, rand_hour_filename)
    sorted_filepath = re.sub('.gz', '_sorted.gz', counts_filepath)
    sort_command = ('zcat ' + counts_filepath + ' | ' +
                    'LC_ALL=C sort --key=1,1 --key=2,2  | gzip -c > ' +
                    sorted_filepath)
    if os.path.exists(sorted_filepath) and not os.path.exists(counts_filepath):
        print "Download and sort complete for " + sorted_filepath
    elif (os.path.exists(counts_filepath) and
          checkhash(counts_filepath, hashes[daily_filenames[i]])):
        print "Sorting " + counts_filepath
        sortfiles = subprocess.call(sort_command, shell=True)
        # sortfiles should be 0 to represent success
        if sortfiles == 0:
            print "Sorting complete for " + sorted_filepath
            os.remove(counts_filepath)
        else:
            print "Sorting ailure for " + counts_filepath
            os.remove(sorted_filepath)
    else:
        print "Download " + counts_filepath
        counts_url = url + rand_hour_filename
        print "Downloading: " + counts_url
        urllib.urlretrieve(counts_url, counts_filepath)
        print "Download complete for " + counts_filepath
        if checkhash(counts_filepath, hashes[rand_hour_filename]):
            print "Sorting " + counts_filepath
            sortfiles = subprocess.call(sort_command, shell=True)
            if sortfiles == 0:
                print "Sorting complete for " + sorted_filepath
                os.remove(counts_filepath)
            else:
                print "Sorting failure for " + counts_filepath
                os.remove(sorted_filepath)


if __name__ == "__main__":
    target_directory = os.path.abspath(sys.argv[1])
    assert os.path.exists(target_directory)
    month_counts = []

    # Months are tuples of year and month number as strings, eg. ('2013', '09')
    month_list = generate_month_list(
        START_YEAR, START_MONTH, END_YEAR, END_MONTH)
    for i in range(0, NUM_PAGES):
        random_month = month_list[random.randint(0, len(month_list) - 1)]
        month_directory = os.path.join(target_directory,
                                       random_month[0] + '-' + random_month[1])
        if not os.path.exists(month_directory):
            print "Making directory for " + month_directory
            os.makedirs(month_directory)
        get_month_counts(random_month[0], random_month[1], month_directory)
