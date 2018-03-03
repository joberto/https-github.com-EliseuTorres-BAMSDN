# Copyright 2014 Eliseu Silva Torres
#
# This file is part of BAMSDN.
#
# MininetWeb is free software: you can redistribute it and/or modify
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


from queue_manager import QueueManager
import time

class LSP(object):    
	def __init__(self, src_ip, dst_ip, src_port, dst_port, class_queue):
		self.src_ip = src_ip
		self.dst_ip = dst_ip
		self.src_port = src_port
		self.dst_port = dst_port
		self.CT = class_queue
	def __eq__(self, r_value):
		if self.dst_ip == r_value.dst_ip and self.src_port == r_value.src_port and self.dst_port == r_value.dst_port and self.CT == r_value.CT:
			return True
		else:
			return False
			
class LSPMap(object):
	HARD_TIMEOUT = 600
	
	def __init__(self, lsp, bw, queue):
		self.lsp = lsp
		self.bw = bw
		self.queue = queue
		self._timeout = self.HARD_TIMEOUT
		self._time = int(time.time())
		
	def get_queue(self):
		return self.queue
		
	def update_timeout(self):
		self._timeout = self.HARD_TIMEOUT
		self._time = int(time.time())
		
	def get_timeout(self):
		self._update_time()
		return self._timeout
		
	def _update_time(self):
		current_time = int(time.time())
		aux = current_time - self._time
		self._timeout -= aux
		
		if self._timeout <= 0:
			self._timeout = 0

class LSPManager(object):
	TOTAL_BANDWIDTH = 500000000
	avaliable_bandwidth = TOTAL_BANDWIDTH
	
	_BC0 = 5000000
	_BC1 = 10000000
	_BC2 = 20000000
	
	CT0 = "CT0"
	CT1 = "CT1"
	CT2 = "CT2"
	
	TOTAL_PER = 100
	
	_maped_list = []
	
	
	_bc0 = {"min_bw_per": 50, "max_bw_per": 100}
	_bc1 = {"min_bw_per": 30, "max_bw_per": 50}
	_bc2 = {"min_bw_per": 20, "max_bw_per": 20}
	
	#link = None
	
	def add_lsp(self, lsp):
		lsp_exist = False
		if self._maped_list == []:
			print "Adicionando a primeira lsp "
			print "ip origem ", lsp.src_ip
			print "ip destino ", lsp.dst_ip
			if lsp.CT == self.CT0:
				lsp_map = LSPMap(lsp, self._BC0, 0)
				print "entrou no if CT0 para adicionar a primeira lsp"
				self._maped_list.append(lsp_map)
				print "lsp_map em add lsp", lsp_map.queue
			elif lsp.CT == self.CT1:
				lsp_map = LSPMap(lsp, self._BC1, 0)
				self._maped_list.append(lsp_map)
				print "lsp_map em add lsp", lsp_map.queue
			elif lsp.CT == self.CT2:
				lsp_map = LSPMap(lsp, self._BC2, 0)
				self._maped_list.append(lsp_map)
				print "lsp_map em add lsp", lsp_map.queue
			
			#self._maped_list.append(lsp_map)
			#print "lsp_map em add lsp", lsp_map.queue
			return 0
		else:
			self.check_lsp_time()
			queue = 0
			for each in self._maped_list:
				if each != None:
					if lsp.src_ip == each.lsp.src_ip and lsp.dst_ip == each.lsp.dst_ip and lsp.dst_port == each.lsp.dst_port:
						print "As lsps sao iguais"
						queue = each.queue
						self._maped_list[queue].update_timeout()
						lsp_exist = True
						break
			

			if lsp_exist == False:
				print "Adicionando mais uma lsp "
				queue = self._reserve_bandwidth(lsp)
				return queue
			else:
				return queue

	def _reserve_bandwidth(self, lsp):
		queue = None
		if self.CT0 == lsp.CT:
			queue = self._avaliable_bandwidth(lsp, self._BC0, self.CT0, self._bc0)
		elif self.CT1 == lsp.CT:
			queue = self._avaliable_bandwidth(lsp, self._BC1, self.CT1, self._bc1)
		elif self.CT2 == lsp.CT:
			queue = self._avaliable_bandwidth(lsp, self._BC2, self.CT2, self._bc2)

		return queue

	def _avaliable_bandwidth(self,lsp, BC, CT, bc):
		
		list_queue = []
		list_bw = []
		preempt_list = []
		
		if CT == self.CT0:
			used_per = self.percent_used_BC(BC, CT)
			
			if used_per <= bc["min_bw_per"]:
				queue = self.insert_lsp(lsp, BC)
				return queue
			else:
				aux_per1 = self.percent_used_BC(self._BC1, self.CT1, False)
				aux_per2 = self.percent_used_BC(self._BC2, self.CT2, False)
				
				total_used_per = used_per + aux_per1 + aux_per2
				
				if total_used_per <= bc["max_bw_per"]:
					queue = self.insert_lsp(lsp, BC)
					return queue
				else:
					return None
		elif CT == self.CT1:
			used_per = self.percent_used_BC(BC, CT)
			aux_per0 = self.percent_used_BC(self._BC0, self.CT0, False)
			aux_per2 = self.percent_used_BC(self._BC2, self.CT2, False)
			total_used_per = used_per + aux_per0 + aux_per2
			print "percentual usado de CT1", used_per
			print "percentual usado de CT0", aux_per0
			print "percentual usado de CT2", aux_per2
			if used_per <= bc["min_bw_per"]:
				print "Entrou no if CT1 "
				queue = None
				if aux_per0 <= self._bc0["min_bw_per"] and aux_per2 <= self._bc2["min_bw_per"]:
					queue = self.insert_lsp(lsp, BC)
				elif aux_per0 > self._bc0["min_bw_per"] and aux_per2 <= self._bc2["min_bw_per"] and total_used_per < self.TOTAL_PER:
					queue = self.insert_lsp(lsp, BC)
				elif aux_per0 > self._bc0["min_bw_per"] and aux_per2 <= self._bc2["min_bw_per"] and total_used_per > self.TOTAL_PER:
					while aux_per0 > self._bc0["min_bw_per"]:
						print "preempt ct0"
						preempt_lsp = self._preempt_lsp(self.CT0)
						preempt_list.append(preempt_lsp)
						aux_per0 = self.percent_used_BC(self._BC0, self.CT0, False)
						total_used_per = used_per + aux_per0 + aux_per2
						if total_used_per <= self.TOTAL_PER:
							queue = self.insert_lsp(lsp, BC)
							return queue, preempt_list
				
				return queue
				
			else:
				if used_per <= bc["max_bw_per"] and total_used_per <= self.TOTAL_PER:
					queue = self.insert_lsp(lsp, BC)
					return queue
				
				elif aux_per0 > self._bc0["min_bw_per"] and aux_per2 <= self._bc2["min_bw_per"]:
					while aux_per0 > self._bc0["min_bw_per"]:
						print "preempt ct0"
						preempt_lsp = self._preempt_lsp(self.CT0)
						preempt_list.append(preempt_lsp)
						aux_per0 = self.percent_used_BC(self._BC0, self.CT0, False)
						total_used_per = used_per + aux_per0 + aux_per2
						if total_used_per <= self.TOTAL_PER:
							queue = self.insert_lsp(lsp, BC)
							return queue, preempt_list
				else:
					return None
					
		elif CT == self.CT2:
			used_per = self.percent_used_BC(BC, CT)
			aux_per0 = self.percent_used_BC(self._BC0, self.CT0, False)
			aux_per1 = self.percent_used_BC(self._BC1, self.CT1, False)
			total_used_per = used_per + aux_per0 + aux_per1
			
			if used_per <= bc["min_bw_per"]:
				
				if aux_per0 <= self._bc0["min_bw_per"] and aux_per1 <= self._bc1["min_bw_per"]:
					#print "Adicionou fluxo da classe CT2"
					queue = self.insert_lsp(lsp, BC)
					return queue
				elif total_used_per > self.TOTAL_PER:
					while aux_per0 > self._bc0["min_bw_per"]:
						preempt_lps = self._preempt_lsp(self.CT0)
						preempt_list.append(preempt_lps)
						aux_per0 = self.percent_used_BC(self._BC0, self.CT0, False)
						total_used_per = used_per + aux_per0 + aux_per1
						if total_used_per <= self.TOTAL_PER:
							queue = self.insert_lsp(lsp, BC)
							
							return queue, preempt_list
							
					while aux_per1 > self._bc1["min_bw_per"]:
						preempt_lsp = self._preempt_lsp(self.CT1)
						preempt_list.append(preempt_lsp)
						aux_per0 = self.percent_used_BC(self._BC1, self.CT1, False)
						total_used_per = used_per + aux_per0 + aux_per1
						if total_used_per <= self.TOTAL_PER:
							queue = self.insert_lsp(lsp, BC)
							
							return queue, preempt_list
				else:
					return None
			
	def percent_used_BC(self, BC, CT, flag=True):
		num_lsp = 0
		for each_lsp in self._maped_list:
			if each_lsp != None:
				if each_lsp.lsp.CT == CT:
					num_lsp += 1
					
		if flag == True:
			num_lsp += 1
			
		used_bw = num_lsp * BC
		print "used bw ", used_bw
		used_per = ((used_bw * 100) / self.TOTAL_BANDWIDTH)
		
		return used_per
		
	def check_lsp_time(self):
		for each in self._maped_list:
			if each != None:
				if each.get_timeout() < 1:
					print "removendo a fluxo da fila ", each.queue
					lsp = each.lsp
					with open("RDM_timeout.txt", "a") as f:
						f.write(str(lsp.src_ip) + ", ")
						f.write(str(lsp.dst_ip) + ", ")
						f.write(str(lsp.src_port) + ", ")
						f.write(str(lsp.dst_port) + ", ")
						f.write(str(lsp.CT) + "\n")
					self._maped_list[each.queue] = None
		
		if self._maped_list[-1] == None:
			self.remove_lsp()
				
	def remove_lsp(self):
		print "removendo LSP"
		for index in range(len(self._maped_list)):
			if self._maped_list[-1] == None:
				_ = self._maped_list.pop()
	
	def insert_lsp(self, lsp, BC):
		lsp_insert = False
		lsp_q = 0
		for each_lsp in self._maped_list:
			if each_lsp == None:
				lsp_map = LSPMap(lsp, BC, lsp_q)
				self._maped_list.pop(lsp_q)
				self._maped_list.insert(lsp_q, lsp_map)
				lsp_insert = True
				break
							
			lsp_q += 1
		
		if not lsp_insert:
			lsp_map = LSPMap(lsp, BC, lsp_q)
			self._maped_list.append(lsp_map)
					
			"""for each in self._maped_list:
				list_queue.append(each.queue)
				list_bw.append(each.bw)"""

			#self.link.set_list_queue(list_queue)
			#self.link.set_queue_bw(list_bw)
			#self.link.update_queue()				

		return lsp_map.queue
	
	def _preempt_lsp(self, CT):
		index = 0
		deleted_lsp = None
		print "preemptou "
		for each in self._maped_list:
			if each != None:
				if each.lsp.CT == CT:
					deleted_lsp = each.lsp
					with open("RDM_preemp_lsp.txt", "a") as f:
						f.write(str(deleted_lsp.src_ip) + ", ")
						f.write(str(deleted_lsp.dst_ip) + ", ")
						f.write(str(deleted_lsp.src_port) + ", ")
						f.write(str(deleted_lsp.dst_port) + ", ")
						f.write(str(deleted_lsp.CT) + "\n")
					self._maped_list[index] = None
					return deleted_lsp
			index += 1
