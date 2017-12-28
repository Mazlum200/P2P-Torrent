import threading
from multiprocessing import Queue
import socket
import time
import sqlite3
from sqlite3 import Error
from uuid import getnode as get_mac
import glob, os

import sys

import mainwindow

logQueue = Queue()
interfaceQueue = Queue()
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

class connectionThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        global quitflag
        while True:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

            host = "0.0.0.0"
            port = 11121
            s.bind((host, port))
            s.listen(5)

            counter = 1

            # create_db("./users.db")

            while True:
                try:
                    threadQueue = Queue()
                    logQueue.put("Waiting for connections.")
                    c, addr = s.accept()
                    logQueue.put("Got connection from" + str(addr))
                    # writers[addr] = threadQueue
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
            print(unparsedmsg)
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
            uuid = msgList[0];
            self.uuid = uuid;
            self.tQueue.put("TIC");
        if cmd == "TOC":
            #timer eklenecek
            peers.setdefault(self.uuid, []).append(self.ip)
            peers.setdefault(self.uuid, []).append(self.port)
            #db'ye yaz
            #db'ye yaz
        if cmd == "TIC":
            self.tQueue.put("TOC " + str(get_mac()))
        if cmd == "SUCC":
            self.tQueue.put("LSQ")
        if cmd == "LSA":
            pList = msgList[0].split(":")
            for x in pList:
                pString = x.split(",")
                uuid = pString[0]
                if uuid:
                    ip = pString[1]
                    port = pString[2]
                    peers.setdefault(uuid, []).append(ip)
                    peers.setdefault(uuid, []).append(port)
                    print(peers)
        if cmd == "SEA":
            fname = msgList[0]
            ret = search_file(fname)
            if ret:
                self.tQueue.put("ASE " + ret)
        if cmd == "ASE":
            fString = msgList[0]
            print("Fstring = " + fString)
            interfaceQueue.put(fString)

def get_cList (ip, port):
    threadQueue = Queue()
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    host = ip
    s.connect_ex((host, port))
    print("Socket established with" + ip)
    rThread = readerThread(s, threadQueue, (ip, port))
    rThread.start()
    wThread = writeThread(s, threadQueue, (ip, port))
    wThread.start()
    threadQueue.put("USR " + str(get_mac()))
    #s.close()

def findFile(fname):
    for key, value in peers.items():
        print(key)
        print(get_mac())
        mac = get_mac()
        print(key!=mac) #bunu arastir
        if key != mac:
            threadQueue = Queue()
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            ip = value[0]
            host = ip
            port = 11121
            s.connect_ex((host, port))
            print("Socket established with" + ip)
            rThread = readerThread(s, threadQueue, (ip, port))
            rThread.start()
            wThread = writeThread(s, threadQueue, (ip, port))
            wThread.start()
            threadQueue.put("SEA " + fname)

def search_file(fname):
    os.chdir(sys.path[0] + "/shared")
    s = ""
    for file in glob.glob("*.txt"):
        print(file)
        s = s + file + ","
    if s:
        return s
    else:
        return 0


lThread = loggerThread("Logger", logQueue)
lThread.start()


counter = 1

#create_db("./users.db")