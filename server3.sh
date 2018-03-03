#!/bin/bash

for i in $(seq 5041 5060)
do
	iperf3 -s -p $i >> server & 
done
