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

	def __init__(self, packet_size, bandwidth, duration):
		self.id = Source.next_id
		self.packet_size = packet_size
		self.transmission_delay = packet_size / bandwidth
		self.duration = duration
		self.timer = 0
		self.clock = 0
		self.packets = []
		Source.next_id += 1

	def timer_reset(self):
		self.timer = 0

	def clock_reset(self):
		self.clock = 0

	def set_packet_rate(self, packet_rate):
		self.packet_rate = packet_rate

	def generate_packet(self, packet_id, packet_size, origin_time, inswitch_time, outswitch_time, end_time):
		self.packets.append([str(self.id) + '_' + str(packet_id), packet_size, origin_time, inswitch_time, outswitch_time, end_time])

	def generate_packets(self):
		counter = 0
		self.timer_reset()
		self.clock_reset()

		if self.packet_rate <= 0:
			print("Wrong packet production rate entered!! Aborting procedure!!")
			return

		if self.duration <= 0:
			print("Wrong duration entered!! Aborting procedure!!")
			return

		while self.clock < self.duration:
			k = 0
			if self.clock == 0:
				k = self.clock + self.transmission_delay
			else:
				if self.timer > self.clock:
					k = self.timer + self.transmission_delay
				else:
					k = self.clock + self.transmission_delay
					
			self.generate_packet(counter, self.packet_size, self.clock, k, None, None)
			self.timer = k
			counter += 1
			r = random.uniform(0, 1)
			self.clock -= math.log(r) / self.packet_rate


class Switch:
	next_id = 0

	def __init__(self, delay, bandwidth, queue_size=None):
		self.id = Switch.next_id
		self.delay = delay
		self.bandwidth = bandwidth
		self.queue_size = queue_size
		self.timer = 0
		self.packets = []
		self.dropped = {}
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

			self.timer = x[5]

	def average_delay(self):
		total = 0
		for x in self.packets:
			total += x[5] - x[2]
		return total / len(self.packets)

	def average_delay1(self, num_packets):
		total = 0
		for x in self.packets:
			if x[0][0] == '1':
				total += x[5] - x[2]
		return total / num_packets

	def average_delay2(self, num_packets):
		total = 0
		for x in self.packets:
			if x[0][0] == '2':
				total += x[5] - x[2]
		return total / num_packets

	def average_delay3(self, num_packets):
		total = 0
		for x in self.packets:
			if x[0][0] == '3':
				total += x[5] - x[2]
		return total / num_packets


source1 = Source(50, 10, 100)
source2 = Source(50, 1000, 100)
source3 = Source(50, 10000, 100)

"""
Part One: Same Rate
"""
space = []
scores1 = []
scores2 = []
scores3 = []

for k in frange(1.0, 100.0, 1.0):
	switch = Switch(0, 10)
	source1.packets = []
	source2.packets = []
	source3.packets = []
	source1.set_packet_rate(k)
	source1.generate_packets()
	source2.set_packet_rate(k)
	source2.generate_packets()
	source3.set_packet_rate(k)
	source3.generate_packets()
	switch.join_queues(source1.packets)
	switch.join_queues(source2.packets)
	switch.join_queues(source3.packets)
	switch.order_queues()
	switch.process_packets()
	switch.dequeue_packets()
	score1 = switch.average_delay1(len(source1.packets))
	score2 = switch.average_delay2(len(source2.packets))
	score3 = switch.average_delay3(len(source3.packets))
	space.append(k)
	scores1.append(score1)
	scores2.append(score2)
	scores3.append(score3)

matplotlib.pyplot.plot(space, scores1, 'ro')
matplotlib.pyplot.xlabel('Packet Rate (per second)')
matplotlib.pyplot.ylabel('Average Delay (seconds)')
matplotlib.pyplot.title('Same Rate - Source 1')
matplotlib.pyplot.savefig('../same_rate1.png')
matplotlib.pyplot.gcf().clear()

matplotlib.pyplot.plot(space, scores2, 'ro')
matplotlib.pyplot.xlabel('Packet Rate (per second)')
matplotlib.pyplot.ylabel('Average Delay (seconds)')
matplotlib.pyplot.title('Same Rate - Source 2')
matplotlib.pyplot.savefig('../same_rate2.png')
matplotlib.pyplot.gcf().clear()

matplotlib.pyplot.plot(space, scores3, 'ro')
matplotlib.pyplot.xlabel('Packet Rate (per second)')
matplotlib.pyplot.ylabel('Average Delay (seconds)')
matplotlib.pyplot.title('Same Rate - Source 3')
matplotlib.pyplot.savefig('../same_rate3.png')
matplotlib.pyplot.gcf().clear()

"""
Part Two: Different Rate
"""
space = []
scores1 = []
scores2 = []
scores3 = []

for k in frange(1.0, 100.0, 1.0):
	switch = Switch(0, 10)
	source1.packets = []
	source2.packets = []
	source3.packets = []
	source1.set_packet_rate(k)
	source1.generate_packets()
	source2.set_packet_rate(k * 0.5)
	source2.generate_packets()
	source3.set_packet_rate(k * 0.1)
	source3.generate_packets()
	switch.join_queues(source1.packets)
	switch.join_queues(source2.packets)
	switch.join_queues(source3.packets)
	switch.order_queues()
	switch.process_packets()
	switch.dequeue_packets()
	score1 = switch.average_delay1(len(source1.packets))
	score2 = switch.average_delay2(len(source2.packets))
	score3 = switch.average_delay3(len(source3.packets))
	space.append(k)
	scores1.append(score1)
	scores2.append(score2)
	scores3.append(score3)

matplotlib.pyplot.plot(space, scores1, 'ro')
matplotlib.pyplot.xlabel('Packet Rate (per second)')
matplotlib.pyplot.ylabel('Average Delay (seconds)')
matplotlib.pyplot.title('Different Rate - Source 1')
matplotlib.pyplot.savefig('../different_rate1.png')
matplotlib.pyplot.gcf().clear()

matplotlib.pyplot.plot(space, scores2, 'ro')
matplotlib.pyplot.xlabel('Packet Rate (per second)')
matplotlib.pyplot.ylabel('Average Delay (seconds)')
matplotlib.pyplot.title('Different Rate - Source 2')
matplotlib.pyplot.savefig('../different_rate2.png')
matplotlib.pyplot.gcf().clear()

matplotlib.pyplot.plot(space, scores3, 'ro')
matplotlib.pyplot.xlabel('Packet Rate (per second)')
matplotlib.pyplot.ylabel('Average Delay (seconds)')
matplotlib.pyplot.title('Different Rate - Source 3')
matplotlib.pyplot.savefig('../different_rate3.png')
matplotlib.pyplot.gcf().clear()


"""
Part Three: Package Loss Rate
"""
space = []
scores1 = []
scores2 = []
scores3 = []

for k in frange(1.0, 100.0, 1.0):
	switch = Switch(0, 10, 100)
	source1.packets = []
	source2.packets = []
	source3.packets = []
	source1.set_packet_rate(k)
	source1.generate_packets()
	source2.set_packet_rate(k * 0.5)
	source2.generate_packets()
	source3.set_packet_rate(k * 0.1)
	source3.generate_packets()
	switch.join_queues(source1.packets)
	switch.join_queues(source2.packets)
	switch.join_queues(source3.packets)
	switch.order_queues()
	switch.process_packets()
	switch.dequeue_packets()
	score1 = switch.dropped['1']
	score2 = switch.dropped['2']
	score3 = switch.dropped['3']
	space.append(k)
	scores1.append(score1)
	scores2.append(score2)
	scores3.append(score3)

matplotlib.pyplot.plot(space, scores1, 'ro')
matplotlib.pyplot.xlabel('Packet Rate (per second)')
matplotlib.pyplot.ylabel('Packet Loss Rate (seconds)')
matplotlib.pyplot.title('Packet Loss Rate - Source 1')
matplotlib.pyplot.savefig('../packet_loss_rate1.png')
matplotlib.pyplot.gcf().clear()

matplotlib.pyplot.plot(space, scores2, 'ro')
matplotlib.pyplot.xlabel('Packet Rate (per second)')
matplotlib.pyplot.ylabel('Packet Loss Rate (seconds)')
matplotlib.pyplot.title('Packet Loss Rate - Source 2')
matplotlib.pyplot.savefig('../packet_loss_rate2.png')
matplotlib.pyplot.gcf().clear()

matplotlib.pyplot.plot(space, scores3, 'ro')
matplotlib.pyplot.xlabel('Packet Rate (per second)')
matplotlib.pyplot.ylabel('Packet Loss Rate (seconds)')
matplotlib.pyplot.title('Packet Loss Rate - Source 3')
matplotlib.pyplot.savefig('../packet_loss_rate3.png')
matplotlib.pyplot.gcf().clear()
