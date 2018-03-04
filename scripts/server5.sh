#!/bin/bash

for i in $(seq 5081 5100)
do
	iperf3 -s -p $i & 
done
