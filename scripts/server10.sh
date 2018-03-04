#!/bin/bash

for i in $(seq 5181 5200)
do
	iperf3 -s -p $i & 
done
