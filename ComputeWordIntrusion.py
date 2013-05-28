"""
Author:         Jey Han Lau
Date:           May 2013
"""

import argparse
import sys
from collections import defaultdict

#parser arguments
desc = "Computes the model precision for the word intrusion task."
parser = argparse.ArgumentParser(description=desc)

#####################
#positional argument#
#####################
#str positional argument
parser.add_argument("topic_file", help="file that contains the topics")
parser.add_argument("test_data", help="test data input for SVM")
parser.add_argument("predictions_output", help="predictions output from SVM")

args = parser.parse_args()

#parameters
debug = True

#input
topic_file = open(args.topic_file)
test_file = open(args.test_data)
predictions_file = open(args.predictions_output)

#global variables
prediction_scores = []
qid_line_id = defaultdict(list) #which lines for which qid
line_id_word = defaultdict(str) #map from line id to words in test.dat
qid_tw = defaultdict(list) #topic words for each qid

###########
#functions#
###########


######
#main#
######

#process prediction file
for line in predictions_file:
    prediction_scores.append(float(line.strip()))

#process the test file
for (line_id, line) in enumerate(test_file):
    qid = int(line.strip().split()[1].split(":")[1])
    qid_line_id[qid].append(line_id)
    line_id_word[line_id] = line.strip().split()[-1][1:] #remove hash in front

#process the topic file
for (line_id, line) in enumerate(topic_file):
    qid_tw[line_id + 1] = line.strip().split()

#compute the model precision for each topic (binary in this case, 1 or 0)
for (qid, line_ids) in sorted(qid_line_id.items()):
    actual_ww_score = prediction_scores[line_ids[0]]
    hit = 1.0
    ww_id = line_ids[0]
    for line_id in line_ids[1:]:
        if prediction_scores[line_id] > actual_ww_score:
            actual_ww_score = prediction_scores[line_id]
            hit = 0.0
            ww_id = line_id
    
    if debug:
        print ("[%.1f]" % hit), " ".join(qid_tw[qid])
        print "\tSystem Chosen Intruder Word =", line_id_word[ww_id]
        print "\tTrue Intruder Word =", line_id_word[line_ids[0]]
        print
    else:
        print hit
