"""
Generates SVM input file, containing PMI, condprob, etc features.

Usage:          GenSVMInput.py <topic> <testing type> [normalised_pmi=True(1), default=False(0)]
Stdin:          N/A
Stdout:         SVM input file (orig.dat)
Other Input:    pos_file, cbc_file, topic_file, topic_file_lemmatized, intruder_file,
                hypernym_files, meronym_files, wordcount_files
Other Output:   N/A
Author:         Jey Han Lau
Date:           Apr 10
"""

import sys
import argparse
import operator
import pickle
import subprocess
import math
from collections import defaultdict

#parser arguments
desc = "Generates the feature files for SVM rank."
parser = argparse.ArgumentParser(description=desc)
#####################
#positional argument#
#####################
parser.add_argument("topic_file", help="file that contains the topics")
parser.add_argument("intruder_file", help="file that contains the intruder words for the topics")
parser.add_argument("pmi_type", help="pmi or normalised pmi", choices=["pmi","npmi"])
parser.add_argument("wordcount_file", help="file that contains the word counts")
args = parser.parse_args()

#parameters
debug = False

#input
topic_file = open(args.topic_file)
intruder_file = open(args.intruder_file)
wc_file = open(args.wordcount_file)

#global variables
topics = [] #a list of topics, with each topic being a list of words
intruders = [] #a list of human best words for each topic
wordcount = {} #a dictionary of word counts
window_total = 0
normalised_pmi = False
if args.pmi_type == "npmi":
    normalised_pmi = True

#constants
WTOTALKEY = "!!<TOTAL_WINDOWS>!!" #key name for total number of windows (in wordcount)

###########
#functions#
###########

#conditional probability
#p(x|y) = p(x, y)/p(y)
def calc_condprob(f_xy, f_y):
    f_xy = float(f_xy)
    f_y = float(f_y)

    if f_y == 0:
        return 0.0

    return f_xy/f_y

#calculate the pointwise mutual information score
#log( P(xy) / (P(x*)*P(*y)) )
#if normalise, divide result by (-log P(xy))
def calc_pmi(f_x, f_y, f_xy):
    f_x = float(f_x)
    f_y = float(f_y)
    f_xy = float(f_xy)

    if (f_x == 0) or (f_y == 0) or (f_xy == 0):
        return 0.0

    result = (math.log((f_xy*window_total)/(f_x*f_y), 2))
    if normalised_pmi:
        result = result / (-1.0*math.log(f_xy/window_total, 2))

    return result


def get_wc(word):
    if word in wordcount:
        return wordcount[word]
    else:
        return 0

def get_wc2(w1, w2):
    if w1 == w2:
        return get_wc(w1)

    combined = ""
    if w1 > w2:
        combined = w2 + "|" + w1
    else:
        combined = w1 + "|" + w2
    if combined in wordcount:
        return wordcount[combined]
    else:
        return 0

def get_word_pos(bestword, target_word):
    if target_word == bestword:
        return 2
    else:
        return 1

def normalize(val, min, max):
    #result = (((1-alpha)*(float(val) - float(min)) + alpha) / (float(max) - float(min)))
    #result = (float(val) - float(min) + alpha) / (float(max) - float(min) + alpha)
    if max == min:
        return val

    result = (float(val) - float(min)) / (float(max) - float(min))
    if debug:
        print "\n\t\tnormalizing: val =", val, " min =", min, " max =", max
        print "\t\t\tresult =", result

    return result

######
#main#
######

#process topic_file
for line in topic_file.readlines():
    topics.append(line.strip().split())

#process intruder_file
for line in intruder_file.readlines():
    intruders.append(int(line.strip())-1)

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

for i, topic_list in enumerate(topics):
    intruder_id = intruders[i]
    intruder_word = topic_list[intruder_id]

    #calculate the feature values
    cp1 = defaultdict(lambda:defaultdict(float))
    cp2 = defaultdict(lambda:defaultdict(float))
    pmi = defaultdict(lambda:defaultdict(float))
    #store the values (for finding min and max later)
    pmi_values = []
    cp1_values = []
    cp2_values = []
   
    #calculate the cond probabilities
    for j, w1 in enumerate(topic_list):
        if debug:
            print "\nword1 =", w1

        for k, w2 in enumerate(topic_list):
            if j!= k:
                cp1[w1][w2] = calc_condprob(get_wc2(w1, w2), get_wc(w2))
                cp2[w1][w2] = calc_condprob(get_wc2(w1, w2), get_wc(w1))
                pmi[w1][w2] = calc_pmi(get_wc(w1), get_wc(w2), get_wc2(w1, w2))
                cp1_values.append(cp1[w1][w2])
                cp2_values.append(cp2[w1][w2])
                pmi_values.append(pmi[w1][w2])
           
                if debug:
                    print "\tword2 =", w2
                    print "\t\ttype1 =", cp1[w1][w2], "\ttype2 =", cp2[w1][w2]

    #print the topic features
    wordlist = [intruder_word]
    for topic_word in topic_list:
        if topic_word not in wordlist:
            wordlist.append(topic_word)

    #get the min and max values of the features
    pmi_min = min(pmi_values)
    pmi_max = max(pmi_values)
    cp1_min = min(cp1_values)
    cp1_max = max(cp1_values)
    cp2_min = min(cp2_values)
    cp2_max = max(cp2_values)

    if debug:
        print "pmi_max =", pmi_max, "\tpmi_min =", pmi_min
        print "condprob_type1_max =", cp1_max , "\tmin =", cp1_min
        print "condprob_type2_max =", cp2_max, "\tmin =", cp2_min

    #print the features
    for target_word in wordlist:
        print get_word_pos(intruder_word, target_word),
        print "qid:" + str(i+1),
        feature_id = 1

        #pmi, condprob features with other words
        for topic_word in topic_list:

            if target_word == topic_word:
                continue
        
            if debug:
                print "\n\nPair = (", target_word, topic_word, ")"

            #pmi feature
            val = 0.0
            if target_word != topic_word:
                val = normalize(pmi[topic_word][target_word], pmi_min, pmi_max)
            if debug:
                print "#pmi(" + target_word + "," + topic_word + ")",
            print str(feature_id) + ":" + str(val),
            feature_id += 1

            #cp1 feature
            val = 0.0
            if target_word != topic_word:
                val = normalize(cp1[target_word][topic_word], cp1_min, cp1_max)
            if debug:
                print "#P(" + target_word + "|" + topic_word + ")",
            print str(feature_id) + ":" + str(val),
            feature_id += 1

            #cp2 feature
            val = 0.0
            if target_word != topic_word:
                val = normalize(cp2[target_word][topic_word], cp2_min, cp2_max)
            if debug:
                    print "#P(" + topic_word + "|" + target_word + ")",
            print str(feature_id) + ":" + str(val),
            feature_id += 1

        #comment for the target word
        print "#" + target_word
