import json
import Queue
import random
import re
import sys

MAX_NGRAM = 10
SAMPLING = 1000000
DICT_SIZE = 4096

def conv_to_binary(string):
    n = 0
    for i in string:
        n = n << 1
        if i == '1':
            n = n + 1
    return n

class HuffmanNode(object):
    def __init__(self, left=None, right=None, root=None):
        self.left = left
        self.right = right
        self.root = root     # Why?  Not needed for anything.

    def children(self):
        return((self.left, self.right))

    @classmethod
    def create_tree(cls, freqs):
        # Map frequencies into a list of tuples, where first element is frequency
        freq_tuples = [(freqs[k], k) for k in freqs]
        p = Queue.PriorityQueue()
        # Sort symbols from lowest freq to highest. Create a leaf node for each
        # symbol and add it to the priority queue.
        for value in freq_tuples:
            p.put(value)
        # While there is more than one node...
        while p.qsize() > 1:
            # Remove two highest nodes and create an internal node, adding these
            # as children.
            l, r = p.get(), p.get()
            node = cls(l, r)
            # Add new node back to priority queue.
            p.put((l[0]+r[0], node))
        # Last remaining node is root; return it.
        return p.get()

    @classmethod
    def create_codes(cls, node, prefix=None, code=dict()):
        # Recursively walk the tree down to the leaves,
        # assigning a code value to each symbol
        try:
            (left, right) = node[1].children()
        except AttributeError:
            code[node[1]] = prefix
            return
        cls.create_codes(left, prefix=prefix + '0', code=code)
        cls.create_codes(right, prefix=prefix + '1', code=code)


class TextToEncode(object):

    def __init__(self, filepath):
        self.full_corpus = ''
        self.text_strs = []
        self.curr_sets = {}
        self.ngram_re_splits = {}
        self.ngram_lists = []
        self.ngram_counts = {}

        print "Loading strings from file..."
        with open(sys.argv[1]) as f:
            for line in f:
                try:
                    page_text = json.loads(line.rstrip())[0]
                    self.full_corpus += page_text
                    self.text_strs.append(page_text)
                except:
                    print "Can't load:\n" + line.rstrip() + '\n'
                    raise

        print "Setting up ngram sets..."
        self.curr_sets = dict()
        for i in range(1, MAX_NGRAM + 1):
            self.curr_sets[i] = set()
            self.ngram_re_splits[i] = None
        print "Getting 1-gram set..."
        self._get_1gram_set()
        print "Initialize ngram set"
        self.ngram_lists = [[] for i in range(len(self.text_strs))]
        for i in range(len(self.text_strs)):
            max_ngram = max([k for k in self.curr_sets if self.curr_sets[k]])
            self.ngram_lists[i] = (self._string_to_ngrams(self.text_strs[i], 
                                                          max_ngram=max_ngram))

        print "Set up frequencies"
        self._count_freq_ngrams()

    def add_ngrams(self, ngrams):
        for ngram in ngrams:
            self.curr_sets[len(ngram)].add(ngram)
        print "Recompiling regex splits..."
        for k in self.curr_sets:
            if self.curr_sets[k]:
                re_str = ur'(' + ur'|'.join(
                    [re.escape(ngram) for ngram in self.curr_sets[k]]
                    ) + ur')'
                self.ngram_re_splits[k] = re.compile(re_str)
            else:
                self.ngram_re_splits[k] = None
        print "Recalculating ngram list..."
        max_ngram = max([k for k in self.curr_sets if self.curr_sets[k]])
        for i in range(len(self.text_strs)):
            self.ngram_lists[i] = (self._string_to_ngrams(self.text_strs[i], 
                                                          max_ngram=max_ngram))
        print "Recalculating counts..."
        self._count_freq_ngrams()
        print "Remove unused ngrams..."
        self._discard_unused_ngrams()

    def remove_ngram(self, ngram):
        self.curr_sets[len(ngram)].remove(ngram)
        self.ngram_list = self._string_to_ngrams(self.text_str,
                                                 max_ngram=max([k for k in 
                                                                self.curr_sets if 
                                                                self.curr_sets[k]
                                                                ]))
        self._count_freq_ngrams()

    def _get_1gram_set(self):
        for string in self.text_strs:
            self.curr_sets[1] = self.curr_sets[1].union(set(string))

    def _string_to_ngrams(self, inputstr, max_ngram=MAX_NGRAM):
        if max_ngram == 1:
            result = list(inputstr)
            return result
        else:
            ngram_range = sorted([k for k in self.curr_sets if 
                                  (self.curr_sets[k] and k >= 1 and k <= max_ngram)],
                                 reverse=True)
            for i in ngram_range:
                if i == 1:
                    return list(inputstr)
                if self.ngram_re_splits[i] and self.ngram_re_splits[i].search(inputstr):
                    splitstr = self.ngram_re_splits[i].split(inputstr)
                    result = []
                    for substr in splitstr:
                        if substr:
                            if substr in self.curr_sets[i] or len(substr) == 1:
                                result += [substr]
                            else:
                                result += self._string_to_ngrams(substr, max_ngram=i-1)
                    return result
            print "Unable to resolve '" + inputstr + "'"
            raise StandardError("Failed to split on any ngram, " +
                                "wrong input passed to function?")

    def _discard_unused_ngrams(self):
        for k in self.curr_sets:
            ngrams_to_remove = []
            for ngram in self.curr_sets[k]:
                if not ngram in self.ngram_counts:
                    ngrams_to_remove.append(ngram)
            print "Removing " + str(ngrams_to_remove)
            for ngram in ngrams_to_remove:
                self.curr_sets[k].remove(ngram)

    def _count_freq_ngrams(self):
        self.ngram_counts = dict()
        for ngram_list in self.ngram_lists:
            for ngram in ngram_list:
                if ngram in self.ngram_counts:
                    self.ngram_counts[ngram] += 1
                else:
                    self.ngram_counts[ngram] = 1

    def get_ngrams_above_threshold(self, sampling=SAMPLING, min_count=2, max_ngram=MAX_NGRAM):
        ngram_counts = dict()
        ngram_range = range(max_ngram, 1, -1)
        total_ngrams = sum([len(ngram_list) for ngram_list in self.ngram_lists])
        print "Performing sampling..."
        for i in range(sampling):
            pos = random.randint(0, len(self.full_corpus) - max_ngram)
            for i in ngram_range:
                ngram_considered = ''.join(self.full_corpus[pos:pos+i])
                if len(ngram_considered) <= max_ngram:
                    if ngram_considered in ngram_counts:
                        ngram_counts[ngram_considered] += 1.0 * sampling / total_ngrams
                    else:
                        ngram_counts[ngram_considered] = 1.0 * sampling / total_ngrams
        ngram_values = dict()
        print "Guessing values..."
        for ngram in [x for x in ngram_counts if ngram_counts[x] >= min_count]:
            sub_ngrams = self._string_to_ngrams(ngram)
            curr_code_len = sum([len(code[x]) for x in sub_ngrams])
            min_count_diff = total_ngrams
            nearest_ngram = None
            for curr_ngram in self.ngram_counts:
                if (abs(self.ngram_counts[curr_ngram] - ngram_counts[ngram]) < min_count_diff):
                    min_count_diff = abs(self.ngram_counts[curr_ngram] - ngram_counts[ngram])
                    nearest_ngram = curr_ngram
                    if min_count_diff == 0:
                        break
            est_new_code_len = len(code[nearest_ngram])
            ngram_values[ngram] = (curr_code_len - est_new_code_len) * ngram_counts[ngram]
        return ngram_values

if __name__ == "__main__":
    # Get page data
    page = TextToEncode(sys.argv[1])

    # Report baseline Huffman
    print "Creating Huffman codes..."
    root = HuffmanNode.create_tree(page.ngram_counts)
    code = dict()
    HuffmanNode.create_codes(root, prefix='', code=code)
    print "Converting page to initial code..."
    # Get binary strings for each page as joined codes, then join these.
    binstring_page = ''.join([''.join([code[x] for x in ngram_list]) for ngram_list in page.ngram_lists])
    print "Starting " + str(len(binstring_page) / 8) + " bytes with single char dictionary."

    print "Creating potential dict..."
    est_values = page.get_ngrams_above_threshold()
    print "Done... potential dict has " + str(len(est_values)) + " entries"

    while len(page.ngram_counts) < DICT_SIZE and est_values:
        print "Currently we have " + str(len(page.ngram_counts)) + " entries"
        print "Adding top " + str(DICT_SIZE - len(page.ngram_counts)) + " entries"
        next_ngrams = sorted(est_values, key=lambda n: est_values[n], 
                             reverse=True)[0:DICT_SIZE - len(page.ngram_counts)]
        page.add_ngrams(next_ngrams)
        print "Removing these from potential dict..."
        for ngram in next_ngrams:
            del est_values[ngram]

        root = HuffmanNode.create_tree(page.ngram_counts)
        code = dict()
        HuffmanNode.create_codes(root, prefix='', code=code)
        new_binstring_page = ''.join([
                ''.join([code[x] for x in ngram_list])
                for ngram_list in page.ngram_lists
                ])
        print "... " + str(len(new_binstring_page) / 8) + " bytes now."

        ngram_counts = page.ngram_counts
        for ngram in sorted(ngram_counts, key=lambda k: ngram_counts[k], reverse=True):
            print "'" + ngram.encode('utf-8') + "'\t" + str(ngram_counts[ngram]) + '\t' + code[ngram]

    
    ngram_counts = page.ngram_counts
    for ngram in sorted(ngram_counts, key=lambda k: ngram_counts[k], reverse=True):
        print "'" + ngram.encode('utf-8') + "'\t" + str(ngram_counts[ngram]) + '\t' + code[ngram]
    print json.dumps(ngram_counts)

"""    
    combined = dict()
    for k in counts:
        combined.update(counts[k])
    values = weighted_value(combined)
    #selected = select_dictionary(values)
    for k in sorted(values, key=lambda k: values[k], reverse=True):
        output = u"'" + unicode(k) + u"'\t" + unicode(values[k])
        print output.encode('utf-8')
    root = HuffmanNode.create_tree(counts[1])
    code = dict()
    HuffmanNode.create_codes(root, prefix='', code=code)
    with open(sys.argv[1]) as f:
        binstring_page = conv_to_binstring(page, code)
        print len(binstring_page) / 8
"""
