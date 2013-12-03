# coding=UTF-8
import json
import re
import sys
from unidecode import unidecode

allowed = set(['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm',
               'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z',
               '.', ',', '\n', '"', "'", '/', '\\', '(', ')', '!', '?', '|',
               '@', '#', '$', '%', '^', '&', '*', '=', ':', ';', '-', '[', ']',
               '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '+',
               '{', '}', '_', '~', '`', '<', '>', ' ', '\t',
               'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M',
               'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z',
               ])

if __name__ == "__main__":
    outputfile = open(sys.argv[2], 'w')
    with open(sys.argv[1]) as f:
        for line in f:
            data = json.loads(line)[0]
            data = re.sub(r'[ \t]', '', data)
            data_new = ''
            for pos in range(len(data)):
                if data[pos] in allowed:
                    data_new += data[pos].upper()
                else:
                    trans = unidecode(data[pos])
                    for char in trans:
                        if char in allowed:
                            data_new += char.upper()
                        elif char == ' ':
                            continue
                        else:
                            print "Not allowed? " + char
            outputfile.write(json.dumps([data_new]) + '\n')
