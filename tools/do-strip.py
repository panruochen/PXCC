#!/usr/bin/python
#
#  Strip files based on the conditional-value file
#

import sys, os, re, shutil
import ConfigParser, optparse
from collections import deque

class CCond :
    def __init__(self, type, value, begin, boff, end) :
        self.type  = type
        self.value = value
        self.begin = begin
        self.boff  = boff
        self.end   = end

class CodeBlock :
    def __init__(self, begin, end, type) :
        self.begin = begin
        self.end   = end
        self.type  = type
        self.mode  = 0

def iv_compare(x, y) :
    if x.end < y.begin :
        return -1;
    elif y.end < x.begin :
        return 1;
    return 0

def check_against(key, array) :
    a = 0
    b = len(array) - 1
    while a <= b :
        m = int((a + b) / 2)
        cb = array[m]
        if key < cb.begin :
            b = m - 1
        elif key > cb.end :
            a = m + 1
        else :
            return cb
    return None

def strip_file(file, c_blocks, fdump) :
    global patterns, sub_patterns
    for i in options.ignlist :
        if file.find(i) >= 0 :
            return
    c_blocks.sort(iv_compare)
    if fdump is not None :
        print >>fdump, "Process file %s" % file
        for cb in c_blocks :
            print >>fdump, "  %s [%u, %u]" % (cb.type, cb.begin, cb.end)
    lnr = 0
    fdr = open(file,  "r")
    fdw = open(file+'.NEW', "w")
    for line in fdr :
        lnr += 1
        cb = check_against(lnr, c_blocks)
        if not cb :
            fdw.write(line)
        else :
            if lnr == cb.begin and not patterns[cb.type].search(line) :
                print >>sys.stderr, "On %s:%u" % (file, lnr)
                print >>sys.stderr, "%s" % line.rstrip('\r\n')
                print >>sys.stderr, " failed to match pattern \'%s\'" % cb.type
                exit(1)
            if cb.mode == 1 :
                line2 = sub_patterns[1].sub('#if', line)
                fdw.write(line2)
    fdr.close()
    fdw.close()
    shutil.move(file, file + '.hbak')
    shutil.move(file + '.NEW', file)
    print "%s stripped" % file

def proc_if(c_blocks, q) :
    tmplist = deque([])
    has_x = False
    first_elif = None
    no_if = False
    while True :
        c = q.pop()
        tmplist.appendleft(c)
        if c.type == 'if' :
            break
    for c in tmplist :
        if c.type == 'elif' :
            first_elif = c
        if c.value == 1 :
            cb = CodeBlock(c.begin + c.boff, c.begin, c.type)
            c_blocks.append(cb)
        elif c.value == 0 :
            cb = CodeBlock(c.begin + c.boff, c.end, c.type)
            c_blocks.append(cb)
            if c.type == 'if' :
                no_if = True
        elif c.value == -1:
            has_x = True
        else :
            print >>sys.stderr, "Unexpected error %d" % c.value
    if not has_x :
        end = tmplist[-1].end
#        print >>sys.stderr, "keep endif on %u" % end
        cb = CodeBlock(end, end, "endif")
        c_blocks.append(cb)
    else :
        if no_if :
            cb = CodeBlock(first_elif.begin + first_elif.boff, first_elif.begin, first_elif.type)
            cb.mode = 1 ## Transform: #elif xx --> #if xx
            c_blocks.append(cb)
        if tmplist[-1].value == 0 :
            c_blocks[-1].end -= 1 ## keep the #endif

def run(cerfile, fdump) :
    fd = open(cerfile, "r")
    if not fd :
        print >>sys.stderr, "Cannot open %s to analyze" % cerfile

    hfile = None
    c_blocks = []
    levels = dict()
    for line in fd :
        if len(line) == 0 :
            continue
        line = line.rstrip('\r\n')
        if line[0] in (' ', '\t') :
            fx = line.split()
            if len(fx) < 5 :
                continue
            nh = int(fx[0])
            if nh not in levels :
                levels[nh] = deque([])

            q  = levels[nh]
            if fx[3].find(',') >= 0 :
                fz = fx[3].split(',')
                a1 = int(fz[0])
                a2 = int(fz[1])
            else :
                a1 = int(fx[3])
                a2 = 0
            c = CCond(fx[1], int(fx[2]), a1, a2, int(fx[4]))
            t = fx[1]
            if t == "if" :
                if len(q) > 0 and q[-1].type == 'if' :
                    proc_if(c_blocks, q)
                q.append(c)
            elif t in ("elif", 'else'):
                prev = q[-1]
                if prev.type != 'if' and prev.type != 'elif' :
                    print >> sys.stderr, "Unmatched %s on \"%s\"" % (t, hfile)
                    print >> sys.stderr, " %s" % line
                    exit(1)
                q.append(c)
                if t == 'else' :
                    proc_if(c_blocks, q)
        else :
            if len(c_blocks) > 0:
                strip_file(hfile, c_blocks, fdump)
            elif hfile is not None and fdump is not None:
                print >>fdump, "Nothing to do for \"%s\"" % hfile
            hfile = line
            del c_blocks[:]
            levels.clear()

    if len(c_blocks) > 0:
        strip_file(hfile, c_blocks, fdump)
        del c_blocks

optionsparser = optparse.OptionParser()

optionsparser.add_option("-c", "--cer-file", action='store', help="Specify the conditional evaluation result file", dest='cerfile', default=None)
optionsparser.add_option("-d", "", action='store', help="Specify the file to dump", dest='dumpfile', default=None)
optionsparser.add_option("-i", "--yz-ignore", action='append', help="Specify the file to be ignored", dest='ignlist', default=[])

(options, args) = optionsparser.parse_args()

if options.cerfile is None :
    print >>sys.stderr, "Usage: %s CONDITIONAL_RESULT_FILE" % os.path.basename(sys.argv[0])
    exit(1)

fdump = None
if options.dumpfile is not None :
    fdump = open(options.dumpfile, "w")

patterns = {}
for i in ('if', 'else', 'elif', 'endif') :
    patterns[i] = re.compile('#\s*' + i)
sub_patterns = [ None, re.compile('#\s*elif') ]

run(options.cerfile, fdump)
if fdump is not None :
    fdump.close()
