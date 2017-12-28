import threading
from multiprocessing import Queue
import socket
import time
import sqlite3
from sqlite3 import Error

logQueue = Queue()
writers = {}
quitflag = 0
peers = {}

def create_db(db_file):
    """ create a database connection to a SQLite database """
    try:
        conn = sqlite3.connect(db_file)
        print(sqlite3.version)
    except Error as e:
        print(e)
    finally:
        conn.close()


class loggerThread (threading.Thread):

    def __init__(self, name, logQueue):
        threading.Thread.__init__(self)
        self.name = name
        self.lQueue = logQueue

    def run(self):
        print("Starting " + self.name)
        with open('logs.txt', 'a') as f:
            while True:
                msg = self.lQueue.get()
                if msg != "":
                    t = time.ctime()
                    msg = msg.strip()
                    log = str(t) + " : " + str(msg) + "\n"
                    f.write(log)
                    print(log)
                    if msg == "QUIT":
                        f.close()
                        break

class writeThread(threading.Thread):
    def __init__(self, sc, writerQueue, addr):
        threading.Thread.__init__(self)
        self.s = sc
        self.wQueue = writerQueue

    def run(self):
        global quitflag
        while True:
            unparsedmsg = self.wQueue.get()
            print(unparsedmsg)
            if(unparsedmsg == "QUIT"):
                logQueue.put("Exiting WriterThread - " + str(self.number))
                self.s.close()
                return True
            else:
                self.s.send(unparsedmsg.encode())

class readerThread(threading.Thread):
    def __init__(self, sc, threadQueue, addr):
        threading.Thread.__init__(self)
        self.s = sc
        self.uuid = ""
        self.tQueue = threadQueue
        self.ip = addr[0]
        self.port = addr[1]

    def run(self):
        while True:
            unparsedmsg = self.s.recv(1024).decode()
            parsedmsg = self.outgoingParser(unparsedmsg)
            if(parsedmsg == "QUI"):
                logQueue.put("Exiting ReaderThread - " + str(self.number))
                return True


    def outgoingParser(self, msg):
        global quitflag
        msgList = msg.split(" ")
        #print(msgList[0].strip())
        #print(len(msgList))
        cmd = msgList[0].strip()
        #print(cmd)
        msgList.pop(0)
        if cmd == "USR":
            uuid = msgList[0]
            self.uuid = uuid
            self.tQueue.put("TIC")
        if cmd == "TOC":
            #timer eklenecek
            uuid = msgList[0]
            if uuid == self.uuid:
                peers.setdefault(self.uuid, []).append(self.ip)
                peers.setdefault(self.uuid, []).append(self.port)
                print(peers)
            self.tQueue.put("SUCC")
        if cmd == "LSQ":
            s = ""
            for key, value in peers.items():
                s = str(key) + "," + str(value[0]) + "," + str(value[1]) + ":"
                print(s)
            self.tQueue.put("LSA " + s)





lThread = loggerThread("Logger", logQueue)
lThread.start()

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

host = "0.0.0.0"
port = 11119
s.bind((host, port))
s.listen(5)

counter = 1

#create_db("./users.db")

while True:
    try:
        threadQueue = Queue()
        logQueue.put("Waiting for connections.")
        c, addr = s.accept()
        logQueue.put("Got connection from" + str(addr))
        #writers[addr] = threadQueue
        logQueue.put("Starting ReaderThread - " + str(counter))
        rThread = readerThread(c, threadQueue, addr)
        rThread.start()
        logQueue.put("Starting WriterThread - " + str(counter))
        wThread = writeThread(c, threadQueue, addr)
        wThread.start()
        counter += 1
    except KeyboardInterrupt:
            s.close()
            logQueue.put('QUIT')
            break