import os
import socket
import sys
import time
from _thread import *

# The port that we're receiving connections on
port = 12345

# Thread count
thread_count = 0

# connection statuses
p1_connected = False
p2_connected = False


def init_move_list():
    global moves
    moves = []
    for i in range(43):
        moves.append('')

def threaded_client(connection):

    global p1_connected
    global p2_connected
    global moves

    # send the initial greeting
    connection.send("Welcome to the server!".encode("ascii"))
    while True:
        data = connection.recv(2048).decode("ascii")
        # print("Received message " + data)
        if not data:
            break

        # default reply
        reply = ''

        # If a player sends us an initial message while both players are
        # connected, it's likely that the game ended and they want to play
        # again.
        if (data == "p=1" or data == "p=2") and p1_connected and p2_connected:
            # clear the move list
            init_move_list()
            print("Someone is trying to start a game after one has already been started! Cleared move list.")
            p1_connected = False
            p2_connected = False

        if data == "p=1":
            p1_connected = True
            if p2_connected:
                reply = "start"
            else:
                reply = "wait"
        elif data == "p=2":
            p2_connected = True
            if p1_connected:
                reply = "start"
            else:
                reply = "wait"

        elif data == "waited":
            if p1_connected and p2_connected:
                reply = "start"
            else:
                reply = "wait"

        elif data == "gameover":
            # The game is over. Set the status of both players to disconnected,
            # and clear the movelist.
            p1_connected = False
            p2_connected = False
            init_move_list()
            reply == "affirm"

        elif data.startswith("turn"):
            # This is turn data. Very important.
            # Format of turn data: "turn x:y" where x=turn and y=column
            turn_num = int(data.split(' ')[1].split(':')[0])
            column = data.split(' ')[1].split(':')[1]
            moves[turn_num] = column
            print("Turn num: {}. Column: {}".format(turn_num, column))
            reply = "affirm"

        elif data.startswith("waiting"):
            turn_requested = int(data.split(' ')[1])
            if moves[turn_requested] == '':
                reply = "wait"
            else:
                reply = moves[turn_requested]

        connection.sendall(reply.encode("ascii"))

    connection.close()


# The list of moves! A list of strings, each containing a number 0-6.
# These, in order, represent all of the moves of the game so far.
moves = []
init_move_list()

# create a socket object
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:

    # bind to port
    server_socket.bind(('', port))

    # queue up to 5 requests
    print("Waiting for a connection...")
    server_socket.listen(5)

    while True:
        # establish connection
        client_socket, addr = server_socket.accept()
        print("Connected to {}:{}".format(addr[0], addr[1]), end=', ')
        start_new_thread(threaded_client, (client_socket, ))
        thread_count += 1
        print("Thread number: {}.".format(thread_count))

except KeyboardInterrupt:
    print("Keyboard interrupt received. Closing.")
    server_socket.close()
    sys.exit()

except Exception as e:
    print("Met an exception. Closing server.")
    print(e)
    server_socket.close()
