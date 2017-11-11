#!/usr/bin/env python3

import sys
import select
import socket
import queue

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setblocking(0)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)


server_address = ('localhost', 4869)
server.bind(server_address)

server.listen(20)

inputs = [server]
outputs = []
message_queues = {}


while inputs:

    try:
        readable, writable, exceptional = select.select(inputs, outputs, inputs)
    except KeyboardInterrupt:
        server.close()
        sys.exit(0)

    for s in readable:

        # a new connection established
        if s is server:
            connection, client_address = s.accept()
            print(f'connection established {client_address}')
            connection.setblocking(0)
            inputs.append(connection)
            message_queues[connection] = queue.Queue(maxsize=40)
        else:
            data = s.recv(1024)

            # new data coming
            if data:
                print(f'data received from {s.getpeername()}: {data}')

                # broadcast
                for connection, client_queue in message_queues.items():

                    if connection is s:
                        continue

                    client_queue.put(data)

                    if connection not in outputs:
                        outputs.append(connection)

            # connection closed, drop it
            else:
                if s in outputs:
                    outputs.remove(s)

                inputs.remove(s)
                s.close()

                del message_queues[s]

    # handle outputs
    for s in writable:
        try:
            next_msg = message_queues[s].get_nowait()
        except queue.Empty:
            outputs.remove(s)
        else:
            s.send(next_msg)

    # handle errors
    for s in exceptional:
        inputs.remove(s)

        if s in outputs:
            outputs.remove(s)

        s.close()

        del message_queues[s]
