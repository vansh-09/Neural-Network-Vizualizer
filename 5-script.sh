#!/bin/bash

echo "Enter n:"
read n

a=0
b=1

echo "Fibonacci:"
for ((i=0;i<n;i++))
do
    echo -n "$a "
    temp=$((a+b))
    a=$b
    b=$temp
done

echo -e "\nPattern:"
for ((i=1;i<=n;i++))
do
    for ((j=1;j<=i;j++))
    do
        echo -n "$j"
    done
    echo
done