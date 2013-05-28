#!/bin/bash

#script that runs the word intrusion task
#steps:
#1. sample the word counts of the topic words based on the reference corpus
#2. generate the svm features (input for svm)
#3. run svm
#4. compute the model precision using the system's prediction of intruder words

#parameters
pmi_type="npmi" #pmi type: pmi or npmi
svm_input_dir="svm_rank/input_files" #path to store generated svm input
#input
topic_file="data/topics-with-intruder.txt"
intruder_file="data/intruder.txt"
ref_corpus_dir="ref_corpus/wiki"
#output
wordcount_file="wordcount/wc-wi.txt"
wi_file="results/topics-wi.txt"

#compute the word occurrences
echo "Computing word occurrence..."
python ComputeWordCount.py $topic_file $ref_corpus_dir > $wordcount_file

#generate the svm input files
echo "Generating SVM input..."
rm -rf $svm_input_dir 2>/dev/null
mkdir $svm_input_dir
python GenSVMInput.py $topic_file $intruder_file $pmi_type $wordcount_file > $svm_input_dir/orig.dat

#split the data into ten partitions (for ten-fold cross validations)
echo "Splitting the SVM input ten partitions..."
python SplitSVM.py $svm_input_dir < $svm_input_dir/orig.dat

#start svm
echo "Starting SVM..."
for i in `seq 0 9`
do
    ./svm_rank/svm_rank_learn -c 0.01 $svm_input_dir/train.dat.$i \
        $svm_input_dir/model.dat.$i 1>/dev/null
    ./svm_rank/svm_rank_classify $svm_input_dir/test.dat.$i $svm_input_dir/model.dat.$i \
        $svm_input_dir/predictions.$i 1>/dev/null
done

for i in `seq 0 9`
do
    cat $svm_input_dir/test.dat.$i >> $svm_input_dir/test.dat
    cat $svm_input_dir/predictions.$i >> $svm_input_dir/predictions
done

#compute the model precision
echo "Computing the model precision..."
python ComputeWordIntrusion.py $topic_file $svm_input_dir/test.dat $svm_input_dir/predictions > \
    $wi_file
