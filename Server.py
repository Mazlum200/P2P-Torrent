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

###################
def create_db(db_file):
    """ create a database connection to a SQLite database """
    try:
        conn = sqlite3.connect(db_file)
        print(sqlite3.version)

    except Error as e:
        print(e)
    finally:
        conn.close()

def create_table(db_file):
    """ create a database connection to a SQLite database """
    try:
        conn = sqlite3.connect(db_file)
        print(sqlite3.version)
        with con:
            cur = con.cursor()
            print("calıstım")
            cur.execute("CREATE TABLE [peers] ([peer_id] INTEGER  PRIMARY KEY NULL,[uuid] INTEGER NULL,[ip] TEXT  NULL,[port] INTEGER  NULL")
            control=False
    except Error as e:
        print(e)
    finally:
        conn.close()

###veri tabanına peer eklemek için
def insert_peers(self,uuid,ip,port):
        self.cur.execute("""INSERT INTO peers VALUES(NULL,?,?,?)""", (uuid,ip,port))
        self.con.commit()
        return "Suc"


#########veri tabını boş mu dolu mu???
def control():
        conn = sqlite3.connect(db_file)
        cur = con.cursor()

        cur.execute("SELECT  *from peers ")

        data = cur.fetchall()
        return len(data)
        if len(data)>=1:
            return True
        else:
            return False

#########veri tabında daha önce eklenme varsa bunları peers dict yazacak server açılıp kapanınca peer listesi unutulmaın diye
def egaliser_db(db_file):
    conn = sqlite3.connect(db_file)
    cur = con.cursor()

    cur.execute("SELECT  *from peers  ")
    data = cur.fetchall()
    # print("len data", len(data))
    size = len(data)
    for i in range(size):
        peers.setdefault(data[i][1], []).append(data[i][2])
        peers.setdefault(data[i][1], []).append(data[i][3])


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

        s=""

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
            '''''
            self.uuid = uuid
            if searchlist__(uuid):
                self.cSocket.send("TICVAR".encode())
                #self.tQueue.put("TIC")
            else:
                self.tQueue.put("TIC")
            '''''
            ###ya da
            if self.uuid not in peers.keys():
                self.tQueue.put("TIC")

        if cmd == "TOC":
            #timer eklenecek
            uuid = msgList[0]
            if uuid == self.uuid:
                peers.setdefault(self.uuid, []).append(self.ip)
                peers.setdefault(self.uuid, []).append(self.port)
                #########veri tabanı ve peers listesi eşitlemeye çalışıyoruz
                insert_peers(self.uuid,self.ip,self.port)
                self.cpl.append([self.uid,self.ip,self.port])
                print(self.cpl)
                print(peers)
            self.tQueue.put("SUCC")
        if cmd == "LSQ":

            for key, value in list(peers.items()):
                s = self.s + str(key) + "," + str(value[0]) + "," + str(value[1]) + ":"
                print(s)
            self.tQueue.put("LSA " + self.s)

        ###lsq alternatif  cpl ile
        if cmd == "PEERLİST":
            ###katyıtlı olmayanlara listeyi vermiyoruz.
            mylist=""
            if(self.searchlist(uuid)):
                for item in self.cpl:
                    mylist += str(item[0]) + ":" + str(item[1]) + ":" + str(item[2]) +"\n"
            self.cSocket.send(("NLISTB\n" + mylist + "NLISTE").encode())

            self.tQueue.put("liste gönderiliyor")

            return


    ###listede olup olmadığın bakılıyor cpl alternatif
    def searchlist(uuid):
            #self.cplLock.acquire()
            global flag
            for i in range(0, len(self.cpl)):
               if (self.cpl[i][0] == self.uuid and self.cpl[i][1] == self.ip and self.cpl[i][2] == self.port):
                    self.cpl[i][3] = time.ctime()
                    #self.cSocket.send(("TICOK " + str(self.cpl[i][3])).encode())
                    print("Listede var")
                    flag=True
               else:
                    flag=False
            return flag
            # self.cplLock.release()
    ###dictionary modeli
    #######
    ########3
    ##sadece uid ile arama yaparsak
    ####if key not in self.fihrist.keys():  functionuda iş görüyor
    def searchlist__(uuid):
            #self.cplLock.acquire()
            global flag1
            for key, value in list(peers.items()):
               if (key == self.uuid and value[0] == self.ip and value[1] == self.port):
                    #item[2] = time.ctime()
                    #self.cSocket.send(("TICOK " + item[2]).encode())
                    print("Listede var")
                    flag1=True
               else:
                    flag1=False
            return flag1
            # self.cplLock.release()

class TimeThread(threading.Thread):
    def __init__(self, name, cplLock, ip, port):
        threading.Thread.__init__(self)
        self.name = name
        #self.cplLock = cplLock
        self.ip = ip
        self.port = port

    def run(self):
        print("Starting " + self.name)
        while True:
            time.sleep(20)  # 20s just to test
            delQueue = queue.Queue()


            for key, value in list(peers.items()):
                if (str(value[0]) != self.ip or int(value[1])!= self.port):
                    try:
                        testSocket = socket.socket()
                        testSocket.settimeout(5)
                        testSocket.connect((str(value[0]),int(value[1])))
                        testSocket.send("TIC".encode())
                        data = testSocket.recv(1024).decode()
                        if data[0:5] == "TOC":
                            pass
                        else:
                            delQueue.put((value[0], value[1]))
                        testSocket.send("BYBY".encode())

                    except:
                        delQueue.put(value[0], value[1])
            while not delQueue.empty():
                delIndex = delQueue.get()
                for key, value in list(peers.items()):
                    if (delIndex[0] == value[0] and int(delIndex[1]) == value[1]):
                        print("siliyorum ",peers[key])
                        del peers[key]
                        break


lThread = loggerThread("Logger", logQueue)
lThread.start()

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

host = "0.0.0.0"
port = 11120
s.bind((host, port))
s.listen(5)
cpl=[]
counter = 1



db_file = "./users.db"
if control()==False:
   create_table(db_file)


while True:
    try:
        threadQueue = Queue()
        logQueue.put("Waiting for connections.")
        c, addr = s.accept()
        logQueue.put("Got connection from" + str(addr))
        #writers[addr] = threadQueue
        time=TimeThread("TimeThread-",+ str(counter),host,port)
        time.start()
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