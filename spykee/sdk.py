import socket
import time
import threading

class Spykee:
    def __init__(self, IP, username, password):
        self.SN = None
        self.IP = IP
        self.username = username
        self.password = password
        self.sock = None
        self.docked = True ## TODO: use isDocked to actually set that
        self.listener = None

    def __repr__(self):
        return '<Spykee {} {}>'.format(self.IP, self.SN)

    def connect(self):
        self.sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.sock.connect((self.IP,9000))

        self.listener = threading.Thread(target=self.listener_thread, args=(self.sock,))
        self.listener.start()

        data = "PK\n\x00\x0c\x05{}\x05{}".format(self.username,self.password)
        self.sock.send(str.encode(data))

    def disconnect(self):
        self.sock.close()
        self.sock = None
        self.listener.join()
        self.listener = None

    def listener_thread(self, sock):
        while self.sock is not None:
            data = sock.recv(1024)
            if data[7:13].decode() == "SPYKEE":
                self.SN = data[7:23].decode()

    def sendCommand(self, command, data):
        print('command', command, data)
        lenstr = ""
        if len(data) <= 255:
            lenstr = "\x00%s" % chr(len(data))
        else:
            multiple = int(len(data) / 256)
            lenstr = "%s%s" % (multiple, len(data) % 256)
        data = str.encode(
            "PK{}{}{}".format(chr(command), lenstr, data)
        )
        self.sock.send(data)

    def motorStop(self):
        self.sendCommand(5, "\x00\x00")

    def motorCommand(self, leftMotor, rightMotor, t=0.2):
        self.sendCommand(5, "%s%s" % (chr(leftMotor), chr(rightMotor)))
        time.sleep(t)
        self.motorStop()

    def undock(self):
        self.sendCommand(16, "\x05")
        self.docked = False

    def dock(self):
        self.sendCommand(16, "\x06")
        self.docked = True

    def cancelDock(self):
        self.sendCommand(16, "\x07")
        self.docked = False

    def playSound(self, soundNumber):
        if soundNumber >= 0 and soundNumber < 256:
            self.sendCommand(7, chr(soundNumber))

    def motorForward(self, motorSpeed, time=0.2):
        if motorSpeed < 128 and motorSpeed >= 0:
            self.motorCommand(motorSpeed, motorSpeed, time)

    def motorBack(self, motorSpeed, time=0.2):
        if motorSpeed < 128 and motorSpeed >= 0:
            self.motorCommand(128 + motorSpeed, 128 + motorSpeed, time)

    def motorLeft(self, time=0.1):
        self.motorCommand(0x96, 0x64, time)

    def motorRight(self, time=0.1):
        self.motorCommand(0x64, 0x96, time)
