#!/bin/bash

#script that computes the observed coherence (pointwise mutual information, normalised pmi or log 
#conditional probability)
#steps:
#1. sample the word counts of the topic words based on the reference corpus
#2. compute the observed coherence using the chosen metric

#parameters
metric="npmi" #evaluation metric: pmi, npmi or lcp
#input
topic_file="data/topics.txt"
ref_corpus_dir="ref_corpus/wiki"
#output
wordcount_file="wordcount/wc-oc.txt"
oc_file="results/topics-oc.txt"

#compute the word occurrences
echo "Computing word occurrence..."
python ComputeWordCount.py $topic_file $ref_corpus_dir > $wordcount_file

#compute the topic observed coherence
echo "Computing the observed coherence..."
python ComputeObservedCoherence.py $topic_file $metric $wordcount_file > $oc_file
