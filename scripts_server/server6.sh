#!/bin/bash

for i in $(seq 5101 5120)
do
	iperf3 -s -p $i >> server & 
done
