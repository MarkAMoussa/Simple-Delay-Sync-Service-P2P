import sys
import os
import threading
import socket
import time
import uuid
import struct
import datetime

# https://bluesock.org/~willkg/dev/ansi.html
ANSI_RESET = "\u001B[0m"
ANSI_RED = "\u001B[31m"
ANSI_GREEN = "\u001B[32m"
ANSI_YELLOW = "\u001B[33m"
ANSI_BLUE = "\u001B[34m"

_NODE_UUID = str(uuid.uuid4())[:8]


def print_yellow(msg):
    print(f"{ANSI_YELLOW}{msg}{ANSI_RESET}")


def print_blue(msg):
    print(f"{ANSI_BLUE}{msg}{ANSI_RESET}")


def print_red(msg):
    print(f"{ANSI_RED}{msg}{ANSI_RESET}")


def print_green(msg):
    print(f"{ANSI_GREEN}{msg}{ANSI_RESET}")


def get_broadcast_port():
    return 35498


def get_node_uuid():
    return _NODE_UUID


class NeighborInfo(object):
    def __init__(self, delay, last_timestamp, ip=None, tcp_port=None, broadcast_count=None):
        # Ip and port are optional, if you want to store them.
        self.delay = delay
        self.last_timestamp = last_timestamp
        self.ip = ip
        self.tcp_port = tcp_port
        self.broadcast_count = broadcast_count


############################################
#######  Y  O  U  R     C  O  D  E  ########
############################################


# Don't change any variable's name.
# Use this hashmap to store the information of your neighbor nodes.
neighbor_information = {}
# Leave the server socket as global variable.
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(("", 0))
server.listen()
# Leave broadcaster as a global variable.
broadcaster = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# Setup the UDP socket
broadcaster.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
broadcaster.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
broadcaster.bind(("", get_broadcast_port()))

# ba send crucial stuff uuid, port, address (ana mawgood ya gma3a)
broadcast_count = 0
# done


def send_broadcast_thread():
    node_uuid = get_node_uuid()
    while True:
        broadcaster.sendto((f"{node_uuid} ON {server.getsockname()[1]}".encode(
            "UTF-8")), ('255.255.255.255', get_broadcast_port()))
        global broadcast_count
        print(f"{node_uuid} ON {server.getsockname()[1]}")
        broadcast_count += 1
       # every 10 time it resets the list
        if broadcast_count % 10 == 0:
            print_green("list reset")
            neighbor_information.clear()
        time.sleep(1)   # Leave as is.


# recieve udp ba5od el crucial stuff we aft7 el tcp
def receive_broadcast_thread():
    """
    Receive broadcasts from other nodes,
    launches a thread to connect to new nodes
    and exchange timestamps.
    """
    while True:
        data, (ip, port) = broadcaster.recvfrom(4096)
        print_blue(f"RECV: {data} FROM: {ip}:{port}")
        data = data.decode("utf-8").split()
        node_id = data[0]
        node_port = data[2]

        # to put a condition for creating a thread not just mindlessly creating them
        if not node_id in neighbor_information.keys():
            print("new node spotted")
            timestamp_thread = daemon_thread_builder(exchange_timestamps_thread,
                                                     args=(node_id, ip, node_port,))
            timestamp_thread.start()


# done
def tcp_server_thread():
    """
    Accept connections from other nodes and send them
    this node's timestamp once they connect.
    """
    while True:
        temp_socket, _ = server.accept()
        time_now = datetime.datetime.utcnow().timestamp()
        print(time_now)
        time_now = struct.pack("!f", time_now)
        temp_socket.send(time_now)
        temp_socket.close()


def exchange_timestamps_thread(other_uuid: str, other_ip: str, other_tcp_port: int):
    """
    Open a connection to the other_ip, other_tcp_port
    and do the steps to exchange timestamps.
    Then update the neighbor_info map using other node's UUID.
    """
    print_yellow(f"ATTEMPTING TO CONNECT TO {other_uuid}")
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((other_ip, int(other_tcp_port)))
    other_time = sock.recv(4096)
    other_time = struct.unpack("!f", other_time)
    print("*" * 50)
    my_time = datetime.datetime.utcnow().timestamp()
    delay = my_time - other_time[0]
    neighbor = NeighborInfo(delay, my_time, other_ip,
                            other_tcp_port, broadcast_count)
    print_red(neighbor_information)
    #neighbor_information.update({other_uuid: neighbor})
    neighbor_information[other_uuid] = neighbor
    print_red(neighbor_information)


# leave as is
def daemon_thread_builder(target, args=()):
    """
    Use this function to make threads. Leave as is.
    """
    th = threading.Thread(target=target, args=args)
    th.setDaemon(True)
    return th


def entrypoint():
    # you can mindlessly create threads or control them for the number of neighbours in list
    print("heeeh ebtadena")
    # send broadcast
    send_thread = daemon_thread_builder(send_broadcast_thread, args=())
    send_thread.start()
    # recive broadcast
    recieve_thread = daemon_thread_builder(receive_broadcast_thread, args=())
    recieve_thread.start()
    # tcp server
    tcp_thread = daemon_thread_builder(tcp_server_thread, args=())
    tcp_thread.start()

    while True:
        continue


############################################
############################################


def main():
    """
    Leave as is.
    """
    print("*" * 50)
    print_red("To terminate this program use: CTRL+C")
    print_red("If the program blocks/throws, you have to terminate it manually.")
    print_green(f"NODE UUID: {get_node_uuid()}")
    print("*" * 50)
    time.sleep(2)   # Wait a little bit.
    entrypoint()


if __name__ == "__main__":
    main()
