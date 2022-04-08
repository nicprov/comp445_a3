import socket
from enum import Enum
import ipaddress
from .packet import Packet, PacketType

BUFFER_SIZE = 1024


class TCPMode(Enum):
    SENDER = 1
    RECEIVER = 2


class TCP:
    def __init__(self, router_ip, router_port, timeout=300):
        self.router_ip = router_ip
        self.router_port = router_port

        self.timeout = timeout  # timeout in seconds
        self.connected = False

        self.conn = None
        self.ip = None
        self.s_port = None
        self.r_port = None

    def connect(self, s_port, r_port):
        """
        Establish connection with receiver
        :param s_port: Source port to bind to
        :param r_port: Receiver port
        :return:
        """
        self.s_port = s_port
        self.r_port = r_port

        self.ip = ipaddress.ip_address(socket.gethostbyname("localhost"))
        self.conn = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.conn.bind(("", self.s_port))
        self.conn.settimeout(self.timeout)

        try:
            # Send SYN packet
            self.conn.sendto(Packet(packet_type=PacketType.SYN,
                                    seq_num=1,
                                    peer_ip_addr=self.ip,
                                    peer_port=self.r_port,
                                    payload=b'').to_bytes(), (self.router_ip, self.router_port))

            # Receive SYN-ACK packet
            response, sender = self.conn.recvfrom(BUFFER_SIZE)
            p = Packet.from_bytes(response)
            if PacketType(p.packet_type) == PacketType.SYN_ACK:
                # Send ACK packet
                self.conn.sendto(Packet(packet_type=PacketType.ACK,
                                        seq_num=p.seq_num + 1,
                                        peer_ip_addr=self.ip,
                                        peer_port=self.r_port,
                                        payload=b'').to_bytes(), (self.router_ip, self.router_port))
                self.connected = True
                print("Connected to server")
            else:
                print("Error, unable to establish connection, server is misbehaving")
        except socket.timeout:
            print("No response from server, timed out")

    def listen(self, port):
        """
        Listen for incoming connection with sender
        :param port: Port to bind to
        :return:
        """
        self.ip = ipaddress.ip_address(socket.gethostbyname("localhost"))
        self.s_port = port
        self.conn = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.conn.bind(("", self.s_port))
        self.conn.settimeout(self.timeout)

        print("Listening on: %s" % self.s_port)

        try:
            # Receive SYN packet
            data, addr = self.conn.recvfrom(BUFFER_SIZE)

            p = Packet.from_bytes(data)
            print(p)
            self.r_port = p.peer_port
            if PacketType(p.packet_type) == PacketType.SYN:
                # Send SYN-ACK packet
                self.conn.sendto(Packet(packet_type=PacketType.SYN_ACK,
                                        seq_num=p.seq_num,
                                        peer_ip_addr=self.ip,
                                        peer_port=self.r_port,
                                        payload=b'').to_bytes(), (self.router_ip, self.router_port))

                # Wait for ACK packet
                data, _ = self.conn.recvfrom(BUFFER_SIZE)
                p = Packet.from_bytes(data)
                if PacketType(p.packet_type) == PacketType.ACK:
                    self.connected = True
                    print("Connected to client")
                else:
                    print("Unable to connect to client, invalid packet received")
            else:
                print("Unable to connect to client, invalid packet received")

        except socket.timeout:
            print("No response from client, timed out")

    def recv(self):
        """
        Mode must be receiver
        :return:
        """
        return self.conn.recvfrom(BUFFER_SIZE)

    def send(self):
        """
        Mode must be sender
        :return:
        """
        return 1
