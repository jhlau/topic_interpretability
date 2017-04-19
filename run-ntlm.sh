#!/bin/bash

input_dir="topics"
ref_corpus_dir="ref_corpus/wiki_full"
wordcount_file="$input_dir/wordcount.txt"
topns="5 10 15 20"

prepare_data=0
gather_stats=0
compute_coherence=1

#prepare data
if [ $prepare_data -eq 1 ]
then
    echo "Preparing data..."
    rm $input_dir/merged.txt 2>/dev/null
    #extract topics from ntlm
    for domain in `ls $input_dir`
    do
        if [[ -d $input_dir/$domain ]]
        then
            echo -e "\tprocessing domain = $domain"
            rm -rf $input_dir/$domain/processed 2>/dev/null
            mkdir -p $input_dir/$domain/processed 2>/dev/null

            #ntlm topics
            for f in `ls $input_dir/$domain/raw/ | grep vmin`
            do
                grep "^Topic " $input_dir/$domain/raw/$f  | cut -f 2-2 -d : > $input_dir/$domain/processed/$f
                cat $input_dir/$domain/processed/$f >> $input_dir/merged.txt
            done

            #lda topics
            for f in `ls $input_dir/$domain/raw/ | grep lda`
            do
                cp $input_dir/$domain/raw/$f $input_dir/$domain/processed/$f
                cat $input_dir/$domain/processed/$f >> $input_dir/merged.txt
            done

            #sntm topics
            for f in `ls $input_dir/$domain/raw/ | grep topics`
            do
                cp $input_dir/$domain/raw/$f $input_dir/$domain/processed/$f
                cat $input_dir/$domain/processed/$f >> $input_dir/merged.txt
            done
        fi
    done
fi

#gather word statistics
if [ $gather_stats -eq 1 ]
then
    echo "Gathering word statistics..."
    python ComputeWordCount.py $input_dir/merged.txt $ref_corpus_dir > $wordcount_file
fi

#compute coherence
if [ $compute_coherence -eq 1 ]
then
    for domain in `ls $input_dir`
    do
        if [[ -d $input_dir/$domain ]]
        then
            echo -e "\n\n\nDomain = $domain"
            for f in `ls $input_dir/$domain/processed | grep 100`
            do
                echo -e "\n$f"
                pname=`python clean_name.py $f`
                python ComputeObservedCoherence.py $input_dir/$domain/processed/$f npmi $wordcount_file -t $topns \
                   -s scores/$domain-$pname | tail -n 2
            done
        fi
    done
fi
