import socket
import sys
import ipaddress
from .packet import Packet, PacketType
from .window import ReceiverWindow, SenderWindow, Frame

BUFFER_SIZE = 1024
MAX_MSG_SIZE = 10
TIMEOUT = 1
INITIAL_TIMEOUT = 10
MAX_RETRIES = 3


class TCP:
    def __init__(self, router_ip, router_port, timeout=TIMEOUT):
        self.router_ip = router_ip
        self.router_port = router_port

        self.timeout = timeout  # timeout in seconds
        self.connected = False

        self.conn = None
        self.ip = None
        self.s_port = None
        self.r_port = None

        self.s_buffer = None
        self.r_buffer = None

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

        syn_p = Packet(packet_type=PacketType.SYN,
                       seq_num=1,
                       peer_ip_addr=self.ip,
                       peer_port=self.r_port,
                       payload=b'').to_bytes()
        syn_ack_received = False

        while not syn_ack_received:
            try:
                # Send SYN packet
                print("Sending SYN")
                self.conn.sendto(syn_p, (self.router_ip, self.router_port))

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
                    syn_ack_received = True
                    print("Connected to server")
                else:
                    print("Error, unable to establish connection, server is misbehaving")
                    sys.exit(1)
            except socket.timeout:
                print("No response from server, retrying...")

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
        self.conn.settimeout(INITIAL_TIMEOUT)

        print("Listening on: %s" % self.s_port)

        syn_received = False
        ack_received = False

        while not (syn_received and ack_received):
            try:
                # Receive SYN packet
                data, _ = self.conn.recvfrom(BUFFER_SIZE)

                p = Packet.from_bytes(data)
                self.r_port = p.peer_port
                if PacketType(p.packet_type) in [PacketType.SYN, PacketType.DATA]:
                    # Send SYN-ACK packet if SYN received or if client ACK got lost
                    self.conn.sendto(Packet(packet_type=PacketType.SYN_ACK,
                                            seq_num=p.seq_num,
                                            peer_ip_addr=self.ip,
                                            peer_port=self.r_port,
                                            payload=b'').to_bytes(), (self.router_ip, self.router_port))
                    syn_received = True

                elif PacketType(p.packet_type) == PacketType.ACK:
                    self.connected = True
                    ack_received = True
                    print("Connected to client")

                else:
                    print(p)
                    print("Unable to connect to client, invalid packet received")
                    sys.exit(1)

            except socket.timeout:
                print("Nothing received from client, waiting...")

    def recv(self):
        done = False
        window = ReceiverWindow()

        while not done:
            try:
                # Read incoming packets
                self.conn.settimeout(TIMEOUT)
                data, _ = self.conn.recvfrom(BUFFER_SIZE)
                p = Packet.from_bytes(data)
                print("Received packet: #%s" % p.seq_num)
                if PacketType(p.packet_type) == PacketType.DATA:
                    f = Frame(p.payload, p.seq_num)
                    window.frame_received(f)

                    # Send ack when data is received
                    self.conn.sendto(Packet(packet_type=PacketType.ACK,
                                            seq_num=p.seq_num,
                                            peer_ip_addr=self.ip,
                                            peer_port=self.r_port,
                                            payload=b'').to_bytes(), (self.router_ip, self.router_port))

                elif PacketType(p.packet_type) == PacketType.DONE:
                    # Send ack_done when received done packet
                    self.conn.sendto(Packet(packet_type=PacketType.ACK_DONE,
                                            seq_num=p.seq_num,
                                            peer_ip_addr=self.ip,
                                            peer_port=self.r_port,
                                            payload=b'').to_bytes(), (self.router_ip, self.router_port))
                    done = True
            except socket.timeout:
                print("Timed out...waiting for packet")

        # When "done" packet received, reconstruct message and deliver
        return window.reconstruct()

    def send(self, msg):
        """
        :param msg: Message to send
        :return:
        """
        # Break up message into 1013 bytes max
        parts = self.split_message(msg.encode("utf-8"))
        num_frames = len(parts)
        counter = 0
        window = SenderWindow()

        while (counter < num_frames) or len(window.get_window_frames()) > 0:
            if counter < num_frames:
                part = parts[counter]
                seq_num = window.add_part(parts[counter])
            else:
                seq_num = None

            if seq_num is not None:
                # Window is not full, so send packet
                print("Sending frame #%s" % seq_num)
                self.conn.sendto(Packet(packet_type=PacketType.DATA,
                                        seq_num=seq_num,
                                        peer_ip_addr=self.ip,
                                        peer_port=self.r_port,
                                        payload=part).to_bytes(), (self.router_ip, self.router_port))
                counter += 1
            else:
                try:
                    # Window is full, check for incoming acks
                    self.conn.settimeout(TIMEOUT)
                    data, _ = self.conn.recvfrom(BUFFER_SIZE)
                    p = Packet.from_bytes(data)
                    if PacketType(p.packet_type) == PacketType.ACK:
                        window.ack_received(p.seq_num)
                    elif PacketType(p.packet_type) == PacketType.SYN_ACK:
                        # Server resent SYN_ACK because previous ACK got lost, so resend ACK
                        self.conn.sendto(Packet(packet_type=PacketType.ACK,
                                                seq_num=p.seq_num,
                                                peer_ip_addr=self.ip,
                                                peer_port=self.r_port,
                                                payload=b'').to_bytes(), (self.router_ip, self.router_port))
                    else:
                        print("Invalid packet response from server")
                        sys.exit(1)


                    # Window is full, check for timed out packets,
                    expired_frames = window.get_expired_frames()
                    for frame in expired_frames:
                        print("Re-Sending expired frame #%s" % frame.seq_num)
                        self.conn.sendto(Packet(packet_type=PacketType.DATA,
                                                seq_num=frame.seq_num,
                                                peer_ip_addr=self.ip,
                                                peer_port=self.r_port,
                                                payload=frame.data).to_bytes(), (self.router_ip, self.router_port))
                    window.reset_timer()  # Reset timer on all frames

                except socket.timeout:
                    # Resend all the packets not acknowledged in the window
                    frames = window.get_window_frames()
                    for frame in frames:
                        print("Re-Sending frame #%s" % frame.seq_num)
                        self.conn.sendto(Packet(packet_type=PacketType.DATA,
                                                seq_num=frame.seq_num,
                                                peer_ip_addr=self.ip,
                                                peer_port=self.r_port,
                                                payload=frame.data).to_bytes(), (self.router_ip, self.router_port))

        done_ack_received = False

        retry_count = 0

        while not done_ack_received:
            # When done, send flag done
            self.conn.sendto(Packet(packet_type=PacketType.DONE,
                                    seq_num=0,
                                    peer_ip_addr=self.ip,
                                    peer_port=self.r_port,
                                    payload=b'').to_bytes(), (self.router_ip, self.router_port))

            try:
                data, _ = self.conn.recvfrom(BUFFER_SIZE)
                p = Packet.from_bytes(data)
                if PacketType(p.packet_type) == PacketType.ACK_DONE:
                    done_ack_received = True
                    print("Receiver successfully received entire message")
            except socket.timeout:
                print("Timed out, retrying...")
                if retry_count < MAX_RETRIES:
                    retry_count += 1
                    # When done, send flag done
                    self.conn.sendto(Packet(packet_type=PacketType.DONE,
                                            seq_num=0,
                                            peer_ip_addr=self.ip,
                                            peer_port=self.r_port,
                                            payload=b'').to_bytes(), (self.router_ip, self.router_port))
                else:
                    done_ack_received = True

    def split_message(self, msg, n=MAX_MSG_SIZE):
        return [msg[i:min(len(msg), i + n)] for i in range(0, len(msg), n)]
