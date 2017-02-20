'''
ECE428: Distributed System
Machine Problem 1 -- Checkpoint 2
Author: Rui Xia, Youjie Li
Date: Feb. 9. 2017
'''

import socket
import threading
import time
import thread


class Node(object):
    def __init__(self, host, port, port_failure, period):
        self.host = host
        self.port = port
        self.period= period
        self.port_failure=port_failure

    def wait_input(self):  # method for take input msg
        while True:
            cmd = raw_input("")
            if cmd == 'q':
                #self.basic_multicast("Dead" + ":" + socket.gethostname())
                print "wait_input exited"
                thread.interrupt_main()

            self.basic_multicast(cmd)

    def basic_multicast(self,cmd):
        for key, value in CONNECTION_LIST.iteritems():
            self.client(key, self.port, cmd)  # pack the msg as a client socket to send

    def client(self, host, port, cmd):  # method for client socket
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        name = CONNECTION_LIST[socket.gethostname()]  # find current machine name

        try:
            s.connect((host, port))  # connect to server
        except:
            # print host + ": Not Online" #debug
            s.close()
            return -1

        try:
            s.sendall(name + " : " + cmd)  # send message to sever
        except:
            s.close()
            return -1

        s.close()
        return 0

    def server(self):
        ss = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        ss.bind((self.host, self.port))
        ss.listen(5)
        while True:
            conn, addr = ss.accept()
            # print 'Connected by ', addr
            while True:
                data = conn.recv(1024)
                if not data:  # recv ending msg from client
                    break

                if data.split(":")[1] == ' Dead':
                    if data.split(":")[2] == socket.gethostname():  # self-dead
                        print "server exited"
                        conn.close()
                        ss.close()
                        return -1
                    else:  # other dead
                        CONNECTION_LIST.pop(data.split(":")[2])

                # conn.send("server received you message.")
                print data #delivered

            conn.close()  # close client socket

#----------------------------------Failure Detection----------------------------------------
    def multicast_0(self):  # method for multi-cast given msg
        #print "Multicast Hb Entered"
        # uni-cast the msg to every node in this group
        for key, value in CONNECTION_LIST.iteritems():
            if (socket.gethostname() != key):
                self.client_0(key, self.port_failure)  # pack the msg as a client socket to send


    def client_0(self, host, port):  # method for client socket
        #print "Clinet Hb Entered"
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            s.connect((host, port))  # connect to server
        except:
            #print host + ": Not Online" #debug
            s.close()
            return -1

        try:
            s.sendall(socket.gethostname())  # send message to sever
            #print "Hb sent to ",  host
        except:
            s.close()
            return -1

        s.close()
        return 0

    def heartbeating(self): # multicast heartbeat
        #print "entered heartbeating"
        prev_time = time.time()*1000
        while True:
            time.sleep((self.period/1000)/5)
            cur_time = time.time()*1000
            if(cur_time-prev_time>self.period):
                #print "Hb Period Entered"
                prev_time = cur_time
                self.multicast_0()

    def detector(self): # receive, check, Multicast Failure
        #print "entered detector"
        ss = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        ss.bind((self.host, self.port_failure))
        ss.listen(10)

        while True:
            conn, addr = ss.accept()
            while True:
                hbaddr = conn.recv(1024)
                #print "recv Hb from " + hbaddr # debug
                if not hbaddr:  # recv ending msg from client
                    break

                timestamp[hbaddr] = time.time()*1000
                if hbaddr not in timer_thread:
                    timer_thread[hbaddr] = threading.Thread(target=self.Timer, args=(hbaddr,), kwargs={})
                    timer_thread[hbaddr].start()

            conn.close()  # close client socket

    def Timer(self, host):
        while True:
            # Wait for 300 milliseconds
            time.sleep((self.period/1000)/5)
            if(time.time()*1000 > timestamp[host] + 2*self.period):
                print(host+" failed")
                #broadcast
                return -1

# --------------------------------Total Ordering--------------------------------------------

#----------------------------------Main Method----------------------------------------------

if __name__ == "__main__":
    print "ChatRoom Started ..."

    T = 3000 # ms, period
    user_port = 9999
    fail_detect_port = 8888
    host = socket.gethostbyname(socket.gethostname())  # get host machine IP address
    node = Node(host, user_port, fail_detect_port, T)  # create node object containing both client and server; def __init__(self, host, port,port_failure,period):

    # global dictionary
    CONNECTION_LIST = {'sp17-cs425-g07-01.cs.illinois.edu': "VM01",
                       'sp17-cs425-g07-02.cs.illinois.edu': "VM02",
                       'sp17-cs425-g07-03.cs.illinois.edu': "VM03",
                       'sp17-cs425-g07-04.cs.illinois.edu': "VM04",
                       'sp17-cs425-g07-05.cs.illinois.edu': "VM05"}

    timestamp={}
    timer_thread = {}

    t1 = threading.Thread(target=node.wait_input)  # thread for client (send msg)
    t2 = threading.Thread(target=node.server)  # thread for server (recv msg)
    t3 = threading.Thread(target=node.heartbeating)
    t4 = threading.Thread(target=node.detector)

    t1.daemon=True
    t2.daemon=True
    t3.daemon=True
    t4.daemon=True

    t2.start()
    t1.start()
    t4.start()
    t3.start()

    while True:
        pass




    # threads terminate when target function returns
    # main thread terminate normally

