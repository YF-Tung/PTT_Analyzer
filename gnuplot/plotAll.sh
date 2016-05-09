#!/bin/bash

for brd in $(cat ../boardList.txt); do
    cat __default__.gpl | sed -r "s/__default__/$brd/g" > tmp.gpl
    gnuplot tmp.gpl
    echo $brd
done

rm -rf tmp.gpl

