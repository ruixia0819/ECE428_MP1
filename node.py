'''
ECE428: Distributed System
Machine Problem 1 -- Checkpoint 1
Author: Rui Xia, Youjie Li
Date: Feb. 9. 2017
'''

import socket
import threading


class Node(object):
    def __init__(self, host, port):
        self.host = host
        self.port = port

    def wait_input(self): # method for take input msg
        while True:
            cmd = raw_input("")
            if cmd == 'q':
                self.basic_multicast("Dead"+":"+socket.gethostname())
                print "wait_input exited"
                return -1

            self.basic_multicast(cmd)

    def basic_multicast(self, cmd): # method for multi-cast given msg
        # uni-cast the msg to every node in this group
        for key, value in CONNECTION_LIST.iteritems():
            self.client(key, self.port, cmd)  # pack the msg as a client socket to send

    def client(self, host, port, cmd): # method for client socket
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        name = CONNECTION_LIST[socket.gethostname()]  # find current machine name

        try:
            s.connect((host, port)) # connect to server
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
                if not data: # recv ending msg from client
                    break

                if data.split(":")[1] == ' Dead':
                    if data.split(":")[2] == socket.gethostname(): # self-dead
                        print "server exited"
                        conn.close()
                        ss.close()
                        return -1
                    else: # other dead
                        CONNECTION_LIST.pop(data.split(":")[2])
                    
                # conn.send("server received you message.")
                print data

            conn.close() # close client socket


if __name__ == "__main__":
    print "ChatRoom Started ..."

    host = socket.gethostbyname(socket.gethostname()) # get host machine IP address
    node = Node(host, 9999) # create node object containing both client and server

    # global dictionary
    CONNECTION_LIST = {'sp17-cs425-g07-01.cs.illinois.edu': "VM01",
                       'sp17-cs425-g07-02.cs.illinois.edu': "VM02",
                       'sp17-cs425-g07-03.cs.illinois.edu': "VM03",
                       'sp17-cs425-g07-04.cs.illinois.edu': "VM04",
                       'sp17-cs425-g07-05.cs.illinois.edu': "VM05"}

    t1 = threading.Thread(target=node.wait_input) # thread for client (send msg)
    t2 = threading.Thread(target=node.server) # thread for server (recv msg)

    t2.start()
    t1.start()

    # threads terminate when target function returns
    # main thread terminate normally

