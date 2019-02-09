# Import socket module.
import socket

# Create a socket object and bind to port.
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
port = 3125
s.bind(('0.0.0.0', port))
print('Socket Binded To Port 3125')

# Wait for client connection.
s.listen(3)
print('Socket Is Listening')

# Establish connection with client.
c, addr = s.accept()
print('Got A Connection From ', addr)

# Loop for long-running server.
while True:
	# Check for data.
	data = c.recv(1024)
	if not data:
		# Refresh connection if data is not received.
		c.close()
		c, addr = s.accept()
		# Print the acknowledgement for the new connection.
		print('Got A Connection From ', addr)
		continue
	else:
		# Print the received data
		print(data.decode('utf-8'))