#!/bin/bash

for i in $(seq 5141 5150)
do
	iperf3 -s -p $i & 
done
