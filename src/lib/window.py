from time import time

FRAME_TIMEOUT = 1  # in seconds
MAX_SEQUENCE_NUM = 10


class Frame:
    def __init__(self, data, seq_num):
        self.seq_num = seq_num
        self.data = data
        self.acknowledged = False
        self.time = None

    def start_timer(self):
        self.time = time()

    def check_timeout(self):
        """
        Check if frame has timed out
        :return: True if it has, false otherwise
        """
        return (time() - self.time) > FRAME_TIMEOUT


class Window:
    def __init__(self):
        self.size = int(MAX_SEQUENCE_NUM/2)
        self.buffer = []  # Used to buffer frames until they are all received
        self.window = [None] * (MAX_SEQUENCE_NUM)  # Used to store frames until they are added to the buffer


class ReceiverWindow(Window):
    def __init__(self):
        self.rcv_base = 0
        super(ReceiverWindow, self).__init__()

    def frame_received(self, frame):
        if frame.seq_num in self.valid_seq_num_range():
            self.window[frame.seq_num] = frame
            self.slide()

    def slide(self):
        """
        Check each frame, if a frame exist with the same seq_num as the recv_base, then it was received
        Hence the recv_base can increase
        :return:
        """
        seq_num = 0
        for frame in self.window:
            if frame is not None:
                if seq_num == self.rcv_base:
                    self.buffer.append(frame)
                    self.window[seq_num] = None
                    self.rcv_base = (self.rcv_base + 1) % (MAX_SEQUENCE_NUM)
            seq_num += 1

    def valid_seq_num_range(self):
        return [num % (MAX_SEQUENCE_NUM + 1) for num in range(self.rcv_base, self.rcv_base + self.size - 1)]

    def reconstruct(self):
        msg = ""
        for frame in self.buffer:
            if frame is not None:
                msg += frame.data.decode("utf-8")
        return msg


class SenderWindow(Window):
    def __init__(self):
        self.send_base = 0
        self.next_seq_num = 0
        super(SenderWindow, self).__init__()

    def ack_received(self, seq_num):
        frame = self.window[seq_num]
        if frame is not None:
            frame.acknowledged = True
            self.slide()
        else:
            print("Received ack for invalid packet")

    def slide(self):
        seq_num = 0
        for frame in self.window:
            if frame is not None:
                if frame.acknowledged and seq_num == self.send_base:
                    frame = None
                    self.send_base = (self.send_base + 1) % (MAX_SEQUENCE_NUM)
            seq_num += 1

    def add_part(self, part):
        if self.next_seq_num == self.get_max_sequence_num():
            return None
        else:
            seq_num = self.next_seq_num
            self.window.insert(self.next_seq_num, Frame(part, seq_num))
            self.next_seq_num = (self.next_seq_num + 1) % (MAX_SEQUENCE_NUM)
            return seq_num

    def get_window_frames(self):
        return [f for f in self.window if f is not None]

    def get_max_sequence_num(self):
        return [num % (MAX_SEQUENCE_NUM) for num in range(self.send_base, self.send_base + self.size - 1)][-1]