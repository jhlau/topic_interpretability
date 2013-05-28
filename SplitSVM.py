"""
Split SVM input into 10 partitions for doing 10-fold cross validation.

Usage:          SplitSVM.py <output_dir>
Stdin:          original svm input
Stdout:         N/A
Other Input:    N/A
Other Output:   10 paritions of the original input
Author:         Jey Han Lau
Date:           Nov 10
"""

import sys

if len(sys.argv) != 2:
    print "Usage: SplitSVM.py <output_dir>"
    raise SystemExit

#parameters
output_dir = sys.argv[1]

#constants
NUM_PART = 10

#globals
qids = [] #[ [lines for qid:1], [lines for qid:2], ... ]

curr_grp = []
curr_qid = -1
for line in sys.stdin:
    line = line.strip()
    data = line.split()
    try:
        qid = int(data[1].split(":")[1])
        if curr_qid == qid:
            curr_grp.append(line)
        else:
            if curr_qid != -1:
                qids.append(curr_grp)
            curr_grp = []
            curr_grp.append(line)
            curr_qid = qid
    except:
        print "Bad format for line =", line
        raise SystemExit
#append the last group
if len(curr_grp) != 0:
    qids.append(curr_grp)

num_qid_per_group = float(len(qids))/NUM_PART

for i in range(0, NUM_PART):
    test_start = int(round(float(i)*num_qid_per_group))
    test_end = int(round(float(i+1)*num_qid_per_group))

    train_output = open(output_dir + "/train.dat." + str(i), "w")
    test_output = open(output_dir + "/test.dat." + str(i), "w")

    #write to test
    for qid in qids[test_start:test_end]:
        for line in qid:
            test_output.write(line + "\n")

    #write to train
    for qid in qids[0:test_start]:
        for line in qid:
            train_output.write(line + "\n")
    for qid in qids[test_end:]:
        for line in qid:
            train_output.write(line + "\n")
