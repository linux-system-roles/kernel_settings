#!/bin/bash
for i in $(find '/proc/sys' -type f -perm -600)
do
    echo "${i:9}" = $(grep -v '^#' $i 2>&-)
done