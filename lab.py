#!/usr/bin/python

# Copyright 2014 Eliseu Silva Torres
#
# This file is part of BAMSDN.
#
# BAMSDN is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# MininetWeb is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with MininetWeb.  If not, see <http://www.gnu.org/licenses/>.





from mininet.net import Mininet
from mininet.node import Controller,OVSKernelSwitch
from mininet.link import TCLink
from mininet.cli import CLI
from mininet.log import setLogLevel
from mininet.node import RemoteController
import os

def topology():
	
	"Create a network."
	net = Mininet( link=TCLink, switch=OVSKernelSwitch )

	print "*** Creating nodes"
	h1 = net.addHost( 'h1', ip='10.0.0.1/8')
	h2 = net.addHost( 'h2', ip='10.0.0.2/8')
	h3 = net.addHost( 'h3', ip='10.0.0.3/8')
	h4 = net.addHost( 'h4', ip='10.0.0.4/8')
	h5 = net.addHost( 'h5', ip='10.0.0.5/8')
	h6 = net.addHost( 'h6', ip='10.0.0.6/8')
	
	
	s1 = net.addSwitch('s1')
	s2 = net.addSwitch('s2')
	s3 = net.addSwitch('s3')
	
	c1 = net.addController( 'c1', controller=RemoteController, ip='127.0.0.1', port=6633)
	#c1 = net.addController('c1', controller=Controller)

	print "*** Associating and Creating links"
	net.addLink(h1, s1)
	net.addLink(h2, s1)
	net.addLink(h3, s1)
	net.addLink(s1, s2)
	net.addLink(s2, h4)
	net.addLink(h5, s3)
	net.addLink(h6, s3)
	net.addLink(s3, s2)
	
	

	print "*** Starting network"
	net.build()
	net.start()
	   	
	

	print "*** Running CLI"
	CLI( net )

	print "*** Stopping network"
	net.stop()

if __name__ == '__main__':
	setLogLevel( 'info' )
	topology()
 
