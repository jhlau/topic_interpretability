#!/bin/bash

input_dir="topics"
output_dir="topics-cleaned"
rm -rf $output_dir
mkdir -p $output_dir 2>/dev/null

for domain in `ls $input_dir`
do
    if [[ -d $input_dir/$domain ]]
    then
        echo -e "\n\n\nDomain = $domain"
        for f in `ls $input_dir/$domain/raw | grep vmin`
        do
            echo -e "\n$f"
            pname=`python clean_name.py $f`
            nlines=`wc -l $input_dir/$domain/raw/$f | cut -f 1-1 -d\ `
            n=`python -c "print $nlines-70"`
            tail -n $n $input_dir/$domain/raw/$f > $output_dir/$domain$pname
        done
    fi
done

rm $output_dir/*topic200*
