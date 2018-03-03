#!/bin/bash

for i in $(seq 5151 5180)
do
	iperf3 -s -p $i >> server & 
done
