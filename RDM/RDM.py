# Copyright 2014 Eliseu Silva Torres
#
# This file is part of BAMSDN.
#
# BANSDN is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# BANSDN is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with MininetWeb.  If not, see <http://www.gnu.org/licenses/>.


from pox.core import core
import pox.openflow.libopenflow_01 as of
from pox.openflow.flow_table import *
from pox.lib.util import dpidToStr
from queue_manager import QueueManager
from lsp import LSP, LSPManager



 
log = core.getLogger()
s1_dpid=0
s2_dpid=0
s3_dpid=0

IDLE_TIMEOUT = 450
HARD_TIMEOUT = 600

"""*****************************************************************************************"""
"""***************Bloco de coidigo adicionado para alocacao de banda dinamica***************"""
"""*****************************************************************************************"""


"""Declaracao de variaveis"""

#Largura de banda maxima do link
TOTAL_BANDWIDTH = 500000000

#lista de match
match_list = []


#Representacao de portas por CTs
ct0_port = [port for port in range(5001, 5101)]
ct1_port = [port for port in range(5101, 5151)]
ct2_port = [port for port in range(5151, 5201)]

CT0_PORT = tuple(ct0_port)
CT1_PORT = tuple(ct1_port)
CT2_PORT = tuple(ct2_port)


#Largura de banda de cada BC
queue_bw = {"BC0":5000000, "BC1":10000000, "BC2":20000000}



#Instancia da classe link manager
lsp_manager = LSPManager()
qos_link = QueueManager("s1-eth4")
qos_link.set_max_bw(TOTAL_BANDWIDTH)

CT0 = "CT0"
CT1 = "CT1"
CT2 = "CT2"
#definicao do CT
def define_CT(src_ip, dst_ip, src_port,dst_port):
	global CT0_PORT, CT1_PORT, CT2_PORT
	global queue_bw, qos_link
	global CT0, CT1, CT2
	global lsp_manager
	class_value = None
	
	
	if dst_port in CT0_PORT:
		class_value = CT0
	elif dst_port in CT1_PORT:
			class_value = CT1
	elif dst_port in CT2_PORT:
		class_value = CT2
	
	print "class value", class_value
	lsp = LSP(src_ip, dst_ip, src_port,dst_port, class_value)

	queue = lsp_manager.add_lsp(lsp)
	#print "queue da classe define_ct ", queue
	return queue
	
def reserve_bw():
	global lsp_manager, qos_link
	list_queue = []
	list_bw = []
	
	#testando antes de tratar o erro.
	maped_list = lsp_manager._maped_list
	for each in maped_list:
		if each != None:
			list_queue.append(each.queue)
			list_bw.append(each.bw)
	
	print "tamanho da lista de filas ", len(list_queue)
	print "tamanho da lista de largura de banda ", len(list_bw)
	
	print "Lista de filas"		
	for each in list_queue:
		print each
		
	for each in list_bw:
		print each
		
	qos_link.set_list_queue(list_queue)
	qos_link.set_queue_bw(list_bw)
	qos_link.update_queue()	







"""*****************************************************************************************"""
"""****************************************Fim do bloco*************************************"""
"""*****************************************************************************************"""

def _handle_ConnectionUp (event):
	global s1_dpid, s2_dpid, s3_dpid
	print "ConnectionUp: ", dpidToStr(event.connection.dpid)
	#remember the connection dpid for switch
	for m in event.connection.features.ports:
		if m.name == "s1-eth1":
			s1_dpid = event.connection.dpid
			print "s1_dpid=", s1_dpid
		elif m.name == "s2-eth1":
			s2_dpid = event.connection.dpid
			print "s2_dpid=", s2_dpid
		elif m.name == "s3-eth1":
			s3_dpid = event.connection.dpid
			print "s3_dpid=", s3_dpid

def _handle_PacketIn (event):
	global s1_dpid, s2_dpid, s3_dpid
	global CT0_PORT, CT1_PORT, CT2_PORT, CT0, CT1, CT2, lsp_manager
	# print "PacketIn: ", dpidToStr(event.connection.dpid)
	packet = event.parsed
	ipp = packet.find("ipv4")
	tcpp = packet.find("tcp")
	#print "Possiveis metodeos",dir(tcpp)
	#print "Origem ", packet.src
	#print "destino ", packet.dst
	#print "porta cliente ", tcpp.srcport
	#print "porta servidor ", tcpp.dstport

	if event.connection.dpid==s1_dpid:
		msg = of.ofp_flow_mod()
		msg.priority =1
		msg.idle_timeout = IDLE_TIMEOUT
		msg.hard_timeout = HARD_TIMEOUT
		msg.match.dl_type = 0x0806
		msg.actions.append(of.ofp_action_output(port = of.OFPP_ALL))
		event.connection.send(msg)
		
		#t = FlowTable()
		#teste = of.ofp_match()
		#if teste:
		#	print dir(teste)
		#	print teste.get_nw_dst()
		#if t:
			#t.remove_matching_entries(of.ofp_match(), 0, False)
		
		if isinstance(ipp, ipv4):
			msg = of.ofp_flow_mod()
			msg.priority =100
			msg.idle_timeout = IDLE_TIMEOUT
			msg.hard_timeout = HARD_TIMEOUT
			msg.match.dl_type = 0x0800
			msg.match.nw_src = ipp.srcip
			msg.match.nw_dst = ipp.dstip
			msg.match.nw_proto = 6
			#msg.match.tp_src = tcpp.srcport
			msg.match.tp_dst = tcpp.dstport
			
			msg2 = of.ofp_flow_mod()
			msg2.priority =100
			msg2.idle_timeout = IDLE_TIMEOUT
			msg2.hard_timeout = HARD_TIMEOUT
			msg2.match.dl_type = 0x0800
			msg2.match.nw_src = ipp.srcip
			msg2.match.nw_dst = ipp.dstip
			msg2.match.nw_proto = 6
			msg2.match.tp_src = tcpp.dstport
			#msg2.match.tp_dst = tcpp.dstport
			
			
			queue = define_CT(ipp.srcip, ipp.dstip, tcpp.srcport,tcpp.dstport)
			
			if queue != None:
				if isinstance(queue, int):
					add_flow(msg, msg2, queue)
					reserve_bw()
				elif isinstance(queue, tuple):
					q, preempt_list = queue
					
					for each in preempt_list:
						remove_flow(each)
						
					add_flow(msg, msg2, q)	
					reserve_bw()
			else:
				print "dropando paconte do host ", ipp.srcip
				msg.hard_timeout = 180
				event.connection.send(msg)
				
				if tcpp.dstport in CT0_PORT:
					CT = CT0
				elif tcpp.dstport in CT1_PORT:
					CT = CT1
				elif tcpp.dstport in CT2_PORT:
					CT = CT2

				with open("RDM_drop.txt", "a") as f:
					f.write(str(ipp.srcip) + ", ")
					f.write(str(ipp.dstip) + ", ")
					f.write(str(tcpp.srcport) + ", ")
					f.write(str(tcpp.dstport) + ", ")
					f.write(str(CT) + "\n")
		
			
			if ipp.srcip == "10.0.0.1":
				msg = of.ofp_flow_mod()
				msg.priority =10
				msg.idle_timeout = IDLE_TIMEOUT
				msg.hard_timeout = HARD_TIMEOUT
				msg.match.dl_type = 0x0800
				msg.match.nw_dst = ipp.srcip
				msg.actions.append(of.ofp_action_output(port = 1))
				event.connection.send(msg)            

			if ipp.srcip == "10.0.0.2":
				msg = of.ofp_flow_mod()
				msg.priority =10
				msg.idle_timeout = IDLE_TIMEOUT
				msg.hard_timeout = HARD_TIMEOUT
				msg.match.dl_type = 0x0800
				msg.match.nw_dst = ipp.srcip
				msg.actions.append(of.ofp_action_output(port = 2))
				event.connection.send(msg)

			if ipp.srcip == "10.0.0.3":
				msg = of.ofp_flow_mod()
				msg.priority =10
				msg.idle_timeout = IDLE_TIMEOUT
				msg.hard_timeout = HARD_TIMEOUT
				msg.match.dl_type = 0x0800
				msg.match.nw_dst = ipp.srcip
				msg.actions.append(of.ofp_action_output(port = 3))
				event.connection.send(msg)
		
		"""msg = of.ofp_flow_mod()
		msg.priority =10
		msg.idle_timeout = IDLE_TIMEOUT
		msg.hard_timeout = HARD_TIMEOUT
		msg.match.dl_type = 0x0800
		msg.match.nw_dst = "10.0.0.4"
		msg.actions.append(of.ofp_action_output(port = 4))
		event.connection.send(msg)"""

	elif event.connection.dpid==s2_dpid:
		msg = of.ofp_flow_mod()
		msg.priority =1
		msg.idle_timeout = IDLE_TIMEOUT
		msg.hard_timeout = HARD_TIMEOUT
		msg.match.dl_type = 0x0806
		msg.actions.append(of.ofp_action_output(port = of.OFPP_ALL))
		event.connection.send(msg)
		
		
		msg = of.ofp_flow_mod()
		msg.priority =1
		msg.idle_timeout = IDLE_TIMEOUT
		msg.hard_timeout = HARD_TIMEOUT
		msg.match.in_port =1
		msg.actions.append(of.ofp_action_output(port = 3))
		event.connection.send(msg)

		msg = of.ofp_flow_mod()
		msg.priority =1
		msg.idle_timeout = IDLE_TIMEOUT
		msg.hard_timeout = HARD_TIMEOUT
		msg.match.in_port =3
		msg.actions.append(of.ofp_action_output(port = 1))
		event.connection.send(msg)   


		msg = of.ofp_flow_mod()
		msg.priority =10
		msg.idle_timeout = IDLE_TIMEOUT
		msg.hard_timeout = HARD_TIMEOUT
		msg.match.dl_type = 0x0800
		msg.match.nw_dst = "10.0.0.1"
		msg.actions.append(of.ofp_action_output(port = 1))
		event.connection.send(msg)

		msg = of.ofp_flow_mod()
		msg.priority =10
		msg.idle_timeout = IDLE_TIMEOUT
		msg.hard_timeout = HARD_TIMEOUT
		msg.match.dl_type = 0x0800
		msg.match.nw_dst = "10.0.0.2"
		msg.actions.append(of.ofp_action_output(port = 1))
		event.connection.send(msg)

		msg = of.ofp_flow_mod()
		msg.priority =10
		msg.idle_timeout = IDLE_TIMEOUT
		msg.hard_timeout = HARD_TIMEOUT
		msg.match.dl_type = 0x0800
		msg.match.nw_dst = "10.0.0.3"
		msg.actions.append(of.ofp_action_output(port = 1))
		event.connection.send(msg)


		msg = of.ofp_flow_mod()
		msg.priority =10
		msg.idle_timeout = IDLE_TIMEOUT
		msg.hard_timeout = HARD_TIMEOUT
		msg.match.dl_type = 0x0800
		msg.match.nw_dst = "10.0.0.5"
		msg.actions.append(of.ofp_action_output(port = 3))
		event.connection.send(msg)

		msg = of.ofp_flow_mod()
		msg.priority =10
		msg.idle_timeout = IDLE_TIMEOUT
		msg.hard_timeout = HARD_TIMEOUT
		msg.match.dl_type = 0x0800
		msg.match.nw_dst = "10.0.0.6"
		msg.actions.append(of.ofp_action_output(port = 3))
		event.connection.send(msg)

	if event.connection.dpid==s3_dpid:
		msg = of.ofp_flow_mod()
		msg.priority =1
		msg.idle_timeout = IDLE_TIMEOUT
		msg.hard_timeout = HARD_TIMEOUT
		msg.match.dl_type = 0x0806
		msg.actions.append(of.ofp_action_output(port = of.OFPP_ALL))
		event.connection.send(msg)

		msg = of.ofp_flow_mod()
		msg.priority =10
		msg.idle_timeout = IDLE_TIMEOUT
		msg.hard_timeout = HARD_TIMEOUT
		msg.match.dl_type = 0x0800
		msg.match.nw_dst = "10.0.0.5"
		msg.actions.append(of.ofp_action_output(port = 1))
		event.connection.send(msg)            

		msg = of.ofp_flow_mod()
		msg.priority =10
		msg.idle_timeout = IDLE_TIMEOUT
		msg.hard_timeout = HARD_TIMEOUT
		msg.match.dl_type = 0x0800
		msg.match.nw_dst = "10.0.0.6"
		msg.actions.append(of.ofp_action_output(port = 2))
		event.connection.send(msg)

		msg = of.ofp_flow_mod()
		msg.priority =10
		msg.idle_timeout = IDLE_TIMEOUT
		msg.hard_timeout = HARD_TIMEOUT
		msg.match.dl_type = 0x0800
		msg.match.nw_dst = "10.0.0.1"
		msg.actions.append(of.ofp_action_output(port = 3))
		event.connection.send(msg)
		
		msg = of.ofp_flow_mod()
		msg.priority =10
		msg.idle_timeout = IDLE_TIMEOUT
		msg.hard_timeout = HARD_TIMEOUT
		msg.match.dl_type = 0x0800
		msg.match.nw_dst = "10.0.0.2"
		msg.actions.append(of.ofp_action_output(port = 3))
		event.connection.send(msg)
		
		msg = of.ofp_flow_mod()
		msg.priority =10
		msg.idle_timeout = IDLE_TIMEOUT
		msg.hard_timeout = HARD_TIMEOUT
		msg.match.dl_type = 0x0800
		msg.match.nw_dst = "10.0.0.3"
		msg.actions.append(of.ofp_action_output(port = 3))
		event.connection.send(msg)
		
def add_flow(msg, msg2, queue):
	global s1_dpid, s2_dpid, s3_dpid  
	
	
	for connection in core.openflow._connections.values():
		if connection.dpid == s1_dpid:
			msg.actions.append(of.ofp_action_enqueue(port = 4, queue_id=queue))
			connection.send(msg)
			
			if msg.match.nw_src == "10.0.0.1":
				msg2.actions.append(of.ofp_action_output(port = 1))
			elif msg.match.nw_src == "10.0.0.2":
				msg2.actions.append(of.ofp_action_output(port = 2))
			elif msg.match.nw_src == "10.0.0.3":
				msg2.actions.append(of.ofp_action_output(port = 3))	
			
		elif connection.dpid == s2_dpid:
			msg.actions.append(of.ofp_action_output(port = 3))
			connection.send(msg)
			
			if msg.match.nw_src == "10.0.0.1" or msg.match.nw_src == "10.0.0.2" or  msg.match.nw_src == "10.0.0.3":
				msg2.actions.append(of.ofp_action_output(port = 1))
		
		elif connection.dpid == s3_dpid:
			msg.actions.append(of.ofp_action_output(port = 2))
			connection.send(msg)
			
			if msg.match.nw_src == "10.0.0.1" or msg.match.nw_src == "10.0.0.2" or  msg.match.nw_src == "10.0.0.3":
				msg2.actions.append(of.ofp_action_output(port = 3))

def remove_flow(match):	
	print "******Removendo fluxo******"
	msg = of.ofp_flow_mod()
	#msg.priority =100	
	msg.match.dl_type = 0x0800
	msg.match.nw_src = match.src_ip
	msg.match.nw_dst = match.dst_ip
	msg.match.nw_proto = 6
	msg.match.tp_dst = match.dst_port
	msg.command = of.OFPFC_DELETE
	
	msg2 = of.ofp_flow_mod()
	#msg2.priority =100	
	msg2.match.dl_type = 0x0800
	msg2.match.nw_src = match.dst_ip
	msg2.match.nw_dst = match.src_ip
	msg2.match.nw_proto = 6
	msg2.match.tp_src = match.dst_port
	msg2.command = of.OFPFC_DELETE
	
	for connection in core.openflow._connections.values():
		connection.send(msg)
		connection.send(msg2)
	

def launch ():
	core.openflow.addListenerByName("ConnectionUp", _handle_ConnectionUp)
	core.openflow.addListenerByName("PacketIn", _handle_PacketIn)
