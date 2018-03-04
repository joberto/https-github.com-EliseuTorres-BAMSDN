#!/bin/bash

for i in $(seq 5001 5020)
do
	iperf3 -s -p $i & 
done
