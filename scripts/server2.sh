#!/bin/bash

for i in $(seq 5021 5040)
do
	iperf3 -s -p $i & 
done
