import math
import matplotlib.pyplot


def frange(start, stop, step):
	i = start
	while i < stop:
		yield i
		i += step


class Source:
	next_id = 0

	def __init__(self, packet_size, bandwidth, duration):
		self.id = Source.next_id
		self.packet_size = packet_size
		self.transmission_delay = packet_size / bandwidth
		self.duration = duration
		self.timer = 0
		self.packets = []
		Source.next_id += 1

	def timer_reset(self):
		self.timer = 0

	def set_packet_rate(self, packet_rate):
		self.packet_rate = packet_rate

	def generate_packet(self, packet_id, packet_size, origin_time, inswitch_time, outswitch_time, end_time):
		self.packets.append([str(self.id) + '_' + str(packet_id), packet_size, origin_time, inswitch_time, outswitch_time, end_time])

	def generate_packets(self):
		counter = 0
		self.timer_reset()

		if self.packet_rate <= 0:
			print("Wrong packet production rate entered!! Aborting procedure!!")
			return

		for i in frange(0, self.duration, 1 / self.packet_rate):
			k = 0
			if self.timer > i:
				k = self.timer + self.transmission_delay
				self.generate_packet(counter, self.packet_size, i, k, None, None)
			else:
				k = i + self.transmission_delay
				self.generate_packet(counter, self.packet_size, i, k, None, None)
			self.timer = k
			counter += 1


class Switch:
	next_id = 0

	def __init__(self, delay, bandwidth):
		self.id = Switch.next_id
		self.delay = delay
		self.bandwidth = bandwidth
		self.timer = 0
		self.packets = []
		Switch.next_id += 1

	def timer_reset(self):
		self.timer = 0

	def join_queues(self, packet_queue):
		for x in packet_queue:
			self.packets.append(x)
		#print(packet_queue)

	def order_queues(self):
		self.packets.sort(key = lambda x: x[3])
		#print(self.packets)

	def process_packets(self):
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
			#print("Packet: ", x[0])
			#print("Timer: ", self.timer)
			#print("Origin: ", x[2])
			#print("Inswitch: ", x[3])
			#print("Outswitch: ", x[4])
			#print("Endtime: ", x[5])

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


space = []
scores = []
source = Source(100, 10, 10)

for k in frange(0.01, 0.5, 0.05):
	source.packets = []
	switch = Switch(0, 30)
	#print("Packet Rate: ", k)
	source.set_packet_rate(k)
	source.generate_packets()
	switch.join_queues(source.packets)
	switch.process_packets()
	switch.dequeue_packets()
	score = switch.average_delay()
	#print("Average Delay: ", score)
	space.append(k)
	scores.append(score)

matplotlib.pyplot.plot(space, scores, 'ro')
matplotlib.pyplot.xlabel('Packet Rate (per second)')
matplotlib.pyplot.ylabel('Average Delay (seconds)')
matplotlib.pyplot.title('Single Source Delay')
matplotlib.pyplot.savefig('../single_source_delay.png')
matplotlib.pyplot.gcf().clear()


space = []
scores = []
scores1 = []
scores2 = []
scores3 = []
source1 = Source(40, 100, 100)
source2 = Source(40, 1, 100)
source3 = Source(40, 10000, 100)

for k in frange(1.0, 100.0, 1.0):
	switch = Switch(0, 10)
	#print("Packet Rate: ", k)
	source1.packets = []
	source2.packets = []
	source3.packets = []
	source1.set_packet_rate(k)
	source1.generate_packets()
	source2.set_packet_rate(0.25)
	source2.generate_packets()
	source3.set_packet_rate(1000)
	source3.generate_packets()
	switch.join_queues(source1.packets)
	switch.join_queues(source2.packets)
	switch.join_queues(source3.packets)
	switch.order_queues()
	switch.process_packets()
	switch.dequeue_packets()
	score = switch.average_delay()
	score1 = switch.average_delay1(len(source1.packets))
	score2 = switch.average_delay2(len(source2.packets))
	score3 = switch.average_delay3(len(source3.packets))
	#print("Average Delay: ", score)
	space.append(k)
	scores.append(score)
	scores1.append(score1)
	scores2.append(score2)
	scores3.append(score3)

matplotlib.pyplot.plot(space, scores, 'ro')
matplotlib.pyplot.xlabel('Packet Rate (per second)')
matplotlib.pyplot.ylabel('Average Delay (seconds)')
matplotlib.pyplot.title('Multiple Source Delay')
matplotlib.pyplot.savefig('../multiple_source_delay.png')
matplotlib.pyplot.gcf().clear()

matplotlib.pyplot.plot(space, scores1, 'ro')
matplotlib.pyplot.xlabel('Packet Rate (per second)')
matplotlib.pyplot.ylabel('Average Delay (seconds)')
matplotlib.pyplot.title('Multiple Source Delay - Source 1')
matplotlib.pyplot.savefig('../multiple_source_delay1.png')
matplotlib.pyplot.gcf().clear()

matplotlib.pyplot.plot(space, scores2, 'ro')
matplotlib.pyplot.xlabel('Packet Rate (per second)')
matplotlib.pyplot.ylabel('Average Delay (seconds)')
matplotlib.pyplot.title('Multiple Source Delay - Source 2')
matplotlib.pyplot.savefig('../multiple_source_delay2.png')
matplotlib.pyplot.gcf().clear()

matplotlib.pyplot.plot(space, scores3, 'ro')
matplotlib.pyplot.xlabel('Packet Rate (per second)')
matplotlib.pyplot.ylabel('Average Delay (seconds)')
matplotlib.pyplot.title('Multiple Source Delay - Source 3')
matplotlib.pyplot.savefig('../multiple_source_delay3.png')
matplotlib.pyplot.gcf().clear()
