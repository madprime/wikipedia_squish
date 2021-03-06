"""Read hourly counts, filter for en, combine and write new file in same dir."""

import gzip
import re
import os
import sys

def main(counts_dir, target_date):
    assert len(target_date) == 8
    year = target_date[0:4]
    month = target_date[4:6]
    month_dir = os.path.join(counts_dir, year + '-' + month)
    output_file = gzip.open(os.path.join(month_dir,
                                         'daycounts-' + target_date + '.gzip'),
                            'w')
    countsfiles = [gzip.open(os.path.join(month_dir, x), 'r')
                   for x in os.listdir(month_dir)
                   if re.match('pagecounts-' + target_date, x)]
    curr_lines = [ None ] * len(countsfiles)
    active_files = [ True ] * len(countsfiles)
    for i in range(len(countsfiles)):
        line = countsfiles[i].readline()
        while not re.match('en ', line):
            line = countsfiles[i].readline()
        curr_lines[i] = line.split()
    while any(active_files):
        earliest_page = min(l[1] for l in curr_lines)
        curr_data = [l for l in curr_lines if l[1] == earliest_page]
        output_file.write(' '.join([curr_data[0][1],
                                    str(sum([int(x[2]) for x in curr_data])),
                                    ]) + '\n')
        for i in range(len(countsfiles)):
            if active_files[i] and curr_lines[i][1] == earliest_page:
                line = countsfiles[i].readline()
                if re.match('en ', line):
                    curr_lines[i] = line.split()
                else:
                    curr_lines[i] = ''
                    active_files[i] = False

if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
