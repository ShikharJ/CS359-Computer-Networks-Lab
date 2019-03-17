import os
import random
import string

characters = string.digits + string.ascii_letters
for i in range(100):
    # Select a random file name and size.
    size = random.randint(7, 10)
    a = ""
    for i in range(size):
        a += random.choice(characters)
    a += '.txt'
    a = './files/' + a
    command = 'touch '+a
    print(command)
    os.system(command)