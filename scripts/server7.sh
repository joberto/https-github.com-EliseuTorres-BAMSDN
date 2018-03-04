#!/bin/bash

for i in $(seq 5121 5140)
do
	iperf3 -s -p $i & 
done
