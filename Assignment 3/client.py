# Import socket module.
import socket

# Create a socket object and bind to port.
s = socket.socket()
port = 3125
s.connect(('localhost', port))

# Loop for sending messages from a single client.
while True:
	x = input("Send A Message? (Y/N)\n")
	if x == 'Y' or x == 'y':
		z = input("Please Enter Your Message:\n")
		# Send message to the server.
		s.sendall(z.encode('utf-8'))
	else:
		# Print final acknowledgement.
		print("Thanks For Using Our Chat Client!")
		break

# Close the connection.
s.close()