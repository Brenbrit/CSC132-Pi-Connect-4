import socket

PORT = 12345

# Create the socket object
# The arguments here aren't all too important. We can just leave them be.
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Bind the socket to PORT.
# We leave the hsot field as an empty string so that we can accept
# any connections coming our way.
s.bind('', PORT)

# Queue up to 5 requests.
s.listen(5)

while True:
    # Establish a connection.
    clientSocket, addr = s.accept()
    print("Got a connection from {}.".format(str(addr)))
    response = "Thanks for connecting. Goodbye!"

    # We've got to encode the message.
    response_enc = response.encode("ascii")
    clientSocket.send(response_enc)
    clientSocket.close()
