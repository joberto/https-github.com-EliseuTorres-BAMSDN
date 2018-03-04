#!/bin/bash

for i in $(seq 5061 5080)
do
	iperf3 -s -p  $i & 
done
