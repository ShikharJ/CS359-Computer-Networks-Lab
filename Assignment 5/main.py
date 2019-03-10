import math
import random
import matplotlib.pyplot


def frange(start, stop, step):
	i = start
	while i < stop:
		yield i
		i += step


class Source:
	next_id = 1

	def __init__(self, packet_size, bandwidth, timeout = 10):
		self.id = Source.next_id
		self.packet_size = packet_size
		self.transmission_delay = packet_size / bandwidth
		self.clock = 0
		self.cwnd = 1
		self.RTT = timeout
		self.send_window = []
		Source.next_id += 1

	def set_RTT(self, RTT):
		self.RTT = RTT

	def set_cwnd(self, cwnd):
		self.cwnd = cwnd

	def clock_reset(self):
		self.clock = 0

	def generate_packet(self, packet_id, packet_size, origin_time, inswitch_time, outswitch_time, end_time, transmission_delay, ack_begin, ack_end):
		self.send_window.append([str(self.id) + '_' + str(packet_id), packet_size, origin_time, inswitch_time, outswitch_time, end_time, transmission_delay, ack_begin, ack_end])

	def generate_sender_window(self):
		counter = 0
		self.clock_reset()

		for i in range(self.cwnd):
			k = self.clock + self.transmission_delay
			self.generate_packet(counter, self.packet_size, self.clock, k, None, None, self.transmission_delay, None, None)
			self.clock = k
			counter += 1

	def validate(self, ack_queue):
		if len(ack_queue) == 0:
			return True

		if len(ack_queue) != self.cwnd:
			return False

		for i, x in enumerate(ack_queue):
			if x == self.send_window[i][0]:
				continue
			else:
				return False

		return True


class Switch:
	next_id = 0

	def __init__(self, delay, bandwidth, queue_size = None):
		self.id = Switch.next_id
		self.delay = delay
		self.bandwidth = bandwidth
		self.queue_size = queue_size
		self.timer = 0
		self.packets = []
		self.dropped = {}
		self.acks1 = []
		self.acks2 = []
		self.acks3 = []
		Switch.next_id += 1

	def timer_reset(self):
		self.timer = 0

	def join_queues(self, packet_queue):
		self.dropped[packet_queue[0][0][0]] = 0
		for x in packet_queue:
			self.packets.append(x)

	def order_queues(self):
		self.packets.sort(key = lambda x: x[3])

	def process_packets(self):
		if self.queue_size != None:
			self.timer_reset()
			for x in self.packets[:self.queue_size]:
				if self.timer > x[3]:
					x[4] = self.timer + self.delay
				else:
					x[4] = x[3] + self.delay

				self.timer = x[4]
		
			i = 0
			j = self.queue_size
			self.timer_reset()
			while j < len(self.packets):
				if self.timer > self.packets[i][4]:
					self.timer = self.timer + (self.packets[i][1] / self.bandwidth)
				else:
					self.timer = self.packets[i][4] + (self.packets[i][1] / self.bandwidth)

				while j < len(self.packets) and self.packets[j][3] < self.timer:
					self.dropped[self.packets[j][0][0]] += 1
					del self.packets[j]

				if j < len(self.packets):
					self.packets[j][4] =  self.packets[j][3] + self.delay

				j += 1
				i += 1
		else:
			self.timer_reset()
			for x in self.packets:
				if self.timer > x[3]:
					x[4] = self.timer + self.delay
				else:
					x[4] = x[3] + self.delay

				self.timer = x[4]

	def dequeue_packets(self):
		self.timer_reset()
		for x in self.packets:
			if self.timer > x[4]:
				x[5] = self.timer + (x[1] / self.bandwidth)
			else:
				x[5] = x[4] + (x[1] / self.bandwidth)

			x[7] = x[5] + (x[1] / self.bandwidth)
			x[8] = x[7] + (x[6])

			self.timer = x[5]

	def dispatch_acks(self):
		for x in self.packets:
			if x[0][0] == '1':
				self.acks1.append(x[0])
			elif x[0][0] == '2':
				self.acks2.append(x[0])
			elif x[0][0] == '3':
				self.acks3.append(x[0])
			else:
				print("Error")

source1 = Source(50, 10)
source2 = Source(50, 100)
source3 = Source(50, 50)

"""
Part One: TCP Reno
"""
space = []
scores1 = []
scores2 = []
scores3 = []

for k in frange(1.0, 25.0, 1.0):
	switch = Switch(0, 10, 100)
	source1.set_RTT(k)
	source2.set_RTT(k)
	source3.set_RTT(k)
	# Run Slow Start Phase
	while True:
		source1.send_window = []
		source2.send_window = []
		source3.send_window = []
		switch.packets = []
		switch.acks1 = []
		switch.acks2 = []
		switch.acks3 = []
		source1.generate_sender_window()
		source2.generate_sender_window()
		source3.generate_sender_window()
		switch.join_queues(source1.send_window)
		switch.join_queues(source2.send_window)
		switch.join_queues(source3.send_window)
		switch.order_queues()
		switch.process_packets()
		switch.dequeue_packets()
		switch.dispatch_acks()
		val1 = source1.validate(switch.acks1)
		if val1 == False:
			score1 = source1.cwnd
		else:
			source1.set_cwnd(source1.cwnd * 2)
		val2 = source2.validate(switch.acks2)
		if val2 == False:
			score2 = source2.cwnd
		else:
			source2.set_cwnd(source2.cwnd * 2)
		val3 = source3.validate(switch.acks3)
		if val3 == False:
			score3 = source3.cwnd
		else:
			source3.set_cwnd(source3.cwnd * 2)
		if val1 == False and (val2 == False and val3 == False):
			break
	source1.set_cwnd(int(score1 / 2))
	source2.set_cwnd(int(score2 / 2))
	source3.set_cwnd(int(score3 / 2))
	# Run AIMD Phase
	while True:
		source1.send_window = []
		source2.send_window = []
		source3.send_window = []
		switch.packets = []
		switch.acks1 = []
		switch.acks2 = []
		switch.acks3 = []
		source1.generate_sender_window()
		source2.generate_sender_window()
		source3.generate_sender_window()
		switch.join_queues(source1.send_window)
		switch.join_queues(source2.send_window)
		switch.join_queues(source3.send_window)
		switch.order_queues()
		switch.process_packets()
		switch.dequeue_packets()
		switch.dispatch_acks()
		val1 = source1.validate(switch.acks1)
		if val1 == False:
			score1 = source1.cwnd * 3 / 4
		else:
			source1.set_cwnd(source1.cwnd + 1)
		val2 = source2.validate(switch.acks2)
		if val2 == False:
			score2 = source2.cwnd * 3 / 4
		else:
			source2.set_cwnd(source2.cwnd + 1)
		val3 = source3.validate(switch.acks3)
		if val3 == False:
			score3 = source3.cwnd * 3 / 4
		else:
			source3.set_cwnd(source3.cwnd + 1)
		if val1 == False and (val2 == False and val3 == False):
			break

	space.append(k)
	scores1.append(score1)
	scores2.append(score2)
	scores3.append(score3)

matplotlib.pyplot.plot(space, scores1, 'ro')
matplotlib.pyplot.xlabel('RTT (in seconds)')
matplotlib.pyplot.ylabel('Throughput Rate')
matplotlib.pyplot.title('Throughput Rate - Source 1')
matplotlib.pyplot.savefig('../Throughput Rate - Source 1.png')
matplotlib.pyplot.gcf().clear()

matplotlib.pyplot.plot(space, scores2, 'ro')
matplotlib.pyplot.xlabel('RTT (in seconds)')
matplotlib.pyplot.ylabel('Throughput Rate')
matplotlib.pyplot.title('Throughput Rate - Source 2')
matplotlib.pyplot.savefig('../Throughput Rate - Source 2.png')
matplotlib.pyplot.gcf().clear()

matplotlib.pyplot.plot(space, scores3, 'ro')
matplotlib.pyplot.xlabel('RTT (in seconds)')
matplotlib.pyplot.ylabel('Throughput Rate')
matplotlib.pyplot.title('Throughput Rate - Source 2')
matplotlib.pyplot.savefig('../Throughput Rate - Source 3.png')
matplotlib.pyplot.gcf().clear()


"""
Part Two: TCP Cubic
"""
space = []
scores1 = []
scores2 = []
scores3 = []

for k in frange(1.0, 25.0, 1.0):
	switch = Switch(0, 10, 100)
	source1.set_RTT(k)
	source2.set_RTT(k)
	source3.set_RTT(k)
	# Run Slow Start Phase
	while True:
		source1.send_window = []
		source2.send_window = []
		source3.send_window = []
		switch.packets = []
		switch.acks1 = []
		switch.acks2 = []
		switch.acks3 = []
		source1.generate_sender_window()
		source2.generate_sender_window()
		source3.generate_sender_window()
		switch.join_queues(source1.send_window)
		switch.join_queues(source2.send_window)
		switch.join_queues(source3.send_window)
		switch.order_queues()
		switch.process_packets()
		switch.dequeue_packets()
		switch.dispatch_acks()
		val1 = source1.validate(switch.acks1)
		if val1 == False:
			score1 = source1.cwnd * 3 / 4
		else:
			source1.set_cwnd(source1.cwnd * 2)
		val2 = source2.validate(switch.acks2)
		if val2 == False:
			score2 = source2.cwnd * 3 / 4
		else:
			source2.set_cwnd(source2.cwnd * 2)
		val3 = source3.validate(switch.acks3)
		if val3 == False:
			score3 = source3.cwnd * 3 / 4
		else:
			source3.set_cwnd(source3.cwnd * 2)
		if val1 == False and (val2 == False and val3 == False):
			break
	source1.set_cwnd(int(score1 / 2))
	source2.set_cwnd(int(score2 / 2))
	source3.set_cwnd(int(score3 / 2))
	# Run Cubic Phase
	t1 = 0
	t2 = 0
	t3 = 0
	while True:
		source1.send_window = []
		source2.send_window = []
		source3.send_window = []
		switch.packets = []
		switch.acks1 = []
		switch.acks2 = []
		switch.acks3 = []
		source1.generate_sender_window()
		source2.generate_sender_window()
		source3.generate_sender_window()
		switch.join_queues(source1.send_window)
		switch.join_queues(source2.send_window)
		switch.join_queues(source3.send_window)
		switch.order_queues()
		switch.process_packets()
		switch.dequeue_packets()
		switch.dispatch_acks()
		t1 += 1
		t2 += 1
		t3 += 1
		val1 = source1.validate(switch.acks1)
		if val1 == False:
			cube_root = (source1.cwnd / 2) ** (1. / 3)
			score1 = source1.cwnd + 2 * ((t1 - cube_root) ** 3)
		else:
			cube_root = (source1.cwnd / 2) ** (1. / 3)
			source1.set_cwnd(int(source1.cwnd + 2 * ((t1 - cube_root) ** 3)))
		val2 = source2.validate(switch.acks2)
		if val2 == False:
			cube_root = (source2.cwnd / 2) ** (1. / 3)
			score2 = source2.cwnd + 2 * ((t2 - cube_root) ** 3)
		else:
			cube_root = (source2.cwnd / 2) ** (1. / 3)
			source2.set_cwnd(int(source2.cwnd + 2 * ((t2 - cube_root) ** 3)))
		val3 = source3.validate(switch.acks3)
		if val3 == False:
			cube_root = (source3.cwnd / 2) ** (1. / 3)
			score3 = source3.cwnd + 2 * ((t3 - cube_root) ** 3)
		else:
			cube_root = (source3.cwnd / 2) ** (1. / 3)
			source3.set_cwnd(int(source3.cwnd + 2 * ((t3 - cube_root) ** 3)))
		if val1 == False and (val2 == False and val3 == False):
			break

	space.append(k)
	scores1.append(score1)
	scores2.append(score2)
	scores3.append(score3)

matplotlib.pyplot.plot(space, scores1, 'ro')
matplotlib.pyplot.xlabel('RTT (in seconds)')
matplotlib.pyplot.ylabel('Throughput Rate')
matplotlib.pyplot.title('Throughput Rate - Source 1 (Cubic)')
matplotlib.pyplot.savefig('../Throughput Rate - Source 1 (Cubic).png')
matplotlib.pyplot.gcf().clear()

matplotlib.pyplot.plot(space, scores2, 'ro')
matplotlib.pyplot.xlabel('RTT (in seconds)')
matplotlib.pyplot.ylabel('Throughput Rate')
matplotlib.pyplot.title('Throughput Rate - Source 2 (Cubic)')
matplotlib.pyplot.savefig('../Throughput Rate - Source 2 (Cubic).png')
matplotlib.pyplot.gcf().clear()

matplotlib.pyplot.plot(space, scores3, 'ro')
matplotlib.pyplot.xlabel('RTT (in seconds)')
matplotlib.pyplot.ylabel('Throughput Rate')
matplotlib.pyplot.title('Throughput Rate - Source 3 (Cubic)')
matplotlib.pyplot.savefig('../Throughput Rate - Source 3 (Cubic).png')
matplotlib.pyplot.gcf().clear()