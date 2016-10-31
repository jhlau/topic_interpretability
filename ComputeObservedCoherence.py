"""
Author:         Jey Han Lau
Date:           May 2013
"""

import argparse
import sys
import operator
import math
import codecs
import numpy as np
from collections import defaultdict


#parser arguments
desc = "Computes the observed coherence for a given topic and word-count file."
parser = argparse.ArgumentParser(description=desc)
#####################
#positional argument#
#####################
parser.add_argument("topic_file", help="file that contains the topics")
parser.add_argument("metric", help="type of evaluation metric", choices=["pmi","npmi","lcp"])
parser.add_argument("wordcount_file", help="file that contains the word counts")

###################
#optional argument#
###################
parser.add_argument("-t", "--topns", nargs="+", type=int, default=[10], \
    help="list of top-N topic words to consider for computing coherence; e.g. '-t 5 10' means it " + \
    " will compute coherence over top-5 words and top-10 words and then take the mean of both values." + \
    " Default = [10]")

args = parser.parse_args()

#parameters
colloc_sep = "_" #symbol for concatenating collocations

#input
topic_file = codecs.open(args.topic_file, "r", "utf-8")
wc_file = codecs.open(args.wordcount_file, "r", "utf-8")

#constants
WTOTALKEY = "!!<TOTAL_WINDOWS>!!" #key name for total number of windows (in word count file)

#global variables
window_total = 0 #total number of windows
wordcount = {} #a dictionary of word counts, for single and pair words
wordpos = {} #a dictionary of pos distribution

###########
#functions#
###########
#use utf-8 for stdout
sys.stdout = codecs.getwriter('utf-8')(sys.stdout)

#compute the association between two words
def calc_assoc(word1, word2):
    combined1 = word1 + "|" + word2
    combined2 = word2 + "|" + word1

    combined_count = 0
    if combined1 in wordcount:
        combined_count = wordcount[combined1]
    elif combined2 in wordcount:
        combined_count = wordcount[combined2]
    w1_count = 0
    if word1 in wordcount:
        w1_count = wordcount[word1]
    w2_count = 0
    if word2 in wordcount:
        w2_count = wordcount[word2]

    if (args.metric == "pmi") or (args.metric == "npmi"):
        if w1_count == 0 or w2_count == 0 or combined_count == 0:
            result = 0.0
        else:
            result = math.log((float(combined_count)*float(window_total))/ \
                float(w1_count*w2_count), 10)
            if args.metric == "npmi":
                result = result / (-1.0*math.log(float(combined_count)/(window_total),10))

    elif args.metric == "lcp":
        if combined_count == 0:
            if w2_count != 0:
                result = math.log(float(w2_count)/window_total, 10)
            else:
                result = math.log(float(1.0)/window_total, 10)
        else:
            result = math.log((float(combined_count))/(float(w1_count)), 10)

    return result

#compute topic coherence given a list of topic words
def calc_topic_coherence(topic_words):
    topic_assoc = []
    for w1_id in range(0, len(topic_words)-1):
        target_word = topic_words[w1_id]
        #remove the underscore and sub it with space if it's a collocation/bigram
        w1 = " ".join(target_word.split(colloc_sep))
        for w2_id in range(w1_id+1, len(topic_words)):
            topic_word = topic_words[w2_id]
            #remove the underscore and sub it with space if it's a collocation/bigram
            w2 = " ".join(topic_word.split(colloc_sep))
            if target_word != topic_word:
                topic_assoc.append(calc_assoc(w1, w2))

    return float(sum(topic_assoc))/len(topic_assoc)

######
#main#
######

#process the word count file(s)
for line in wc_file:
    line = line.strip()
    data = line.split("|")
    if len(data) == 2:
        wordcount[data[0]] = int(data[1])
    elif len(data) == 3:
        if data[0] < data[1]:
            key = data[0] + "|" + data[1]
        else:
            key = data[1] + "|" + data[0]
        wordcount[key] = int(data[2])
    else:
        print "ERROR: wordcount format incorrect. Line =", line
        raise SystemExit

#get the total number of windows
if WTOTALKEY in wordcount:
    window_total = wordcount[WTOTALKEY]

#read the topic file and compute the observed coherence
topic_coherence = defaultdict(list) # {topicid: [tc]}
topic_tw = {} #{topicid: topN_topicwords}
for topic_id, line in enumerate(topic_file):
    topic_list = line.split()[:max(args.topns)]
    topic_tw[topic_id] = " ".join(topic_list)
    for n in args.topns:
        topic_coherence[topic_id].append(calc_topic_coherence(topic_list[:n]))

#sort the topic coherence scores in terms of topic id
tc_items = sorted(topic_coherence.items())
mean_coherence_list = []
for item in tc_items:
    topic_words = topic_tw[item[0]].split()
    mean_coherence = np.mean(item[1])
    mean_coherence_list.append(mean_coherence)
    print ("[%.2f] (" % mean_coherence),
    for i in item[1]:
        print ("%.2f;" % i),
    print ")", topic_tw[item[0]]

#print the overall topic coherence for all topics
print "=========================================================================="
print "Average Topic Coherence = %.3f" % np.mean(mean_coherence_list)
print "Median Topic Coherence = %.3f" % np.median(mean_coherence_list)
