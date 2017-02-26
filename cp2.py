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
    def __init__(self, host, port, port_failure, period,num_node_alive):
        self.host = host
        self.port = port
        self.period = period
        self.port_failure = port_failure
        self.pro_p = 0 # proposed priority
        self.num_node_alive= num_node_alive

    def wait_input(self):  # method for take input msg
        while True:
            cmd = raw_input("")
            if cmd == 'q':
                # self.basic_multicast("Left" + ":" + socket.gethostname())
                print "I am leaving"
                thread.interrupt_main()

            REC_PRO_COUNTER[cmd] =0
            AGR_P[cmd]=0
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
            s.sendall(name + ":" + cmd)  # send message to sever
        except:
            s.close()
            return -1

        s.close()
        return 0


    def server(self):
        ss = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        ss.bind((self.host, self.port))
        ss.listen(20)

        while True:
            conn, addr = ss.accept()
            # print 'Connected by ', addr

            while True:
                data = conn.recv(1024)
                if not data:  # recv ending msg from client
                    break

                if data.split(":")[1]=="0": #received proposed priority
                    print "Received Proposed Priority"
                    mse=data.split(":")[-1]
                    REC_PRO_COUNTER[mse] = REC_PRO_COUNTER[mse] + 1

                    if float(data.split(":")[2]) > AGR_P[mse]:
                        AGR_P[mse]= float(data.split(":")[2])

                    if REC_PRO_COUNTER[mse]==self.num_node_alive:
                        print "REC_PRO_COUNTER == 0"
                        broadcast_agr_p = threading.Thread(target=self.basic_multicast, args=("1"+":"+str(AGR_P[mse])+":"+data.split(":")[-2]+":"+mse,))
                                                                                        #self.name : 1 : agr_p : receive_name : message
                        broadcast_agr_p.start()


                elif data.split(":")[1]=="1": #received agreed priority
                    print "Received Agreed Priority"
                    #search agreed message
                    idx=[elem[2] for elem in queue].index(data.split(":")[-2]+":"+data.split(":")[-1])

                    # update agreed priority
                    queue[idx][1]=True
                    queue[idx][0]=float(data.split(":")[2])
                    self.pro_p=float(data.split(":")[2])

                    # reorder
                    queue.sort(key=lambda elem:elem[0])

                    # deliver
                    while(queue and queue[0][1]==True):
                        print (queue.pop(0)[2])


                elif data.split(":")[-1]=="failed" and Flag_Failed(data.split(":")[-2])==False:# received someone failed
                    failed_machine_num = data.split(":")[-2]
                    self.num_node_alive=self.num_node_alive-1
                    Flag_Failed[failed_machine_num]=True


                    failed_idx =[i for i,elem in enumerate(queue) if elem[-1].split(":")[0]==failed_machine_num]

                    if not failed_idx:
                        print failed_machine_num+"failed"

                    else:
                        for i in failed_idx:
                            if queue[failed_idx[i]][1]==False:
                                queue.pop(i)
                                failed_idx.remove(i)
                        if failed_idx:
                            queue.append([queue[failed_idx[-1]][0]+0.1,True, failed_machine_num+"failed"])
                            queue.sort(key=lambda elem: elem[0])
                        else:
                            print failed_machine_num+"failed"


                else: #received normal message
                    print "Received Normal Message"
                    self.pro_p = self.pro_p + 1

                    name=CONNECTION_LIST[socket.gethostname()]

                    p=float(name[-1])/10 +self.pro_p
                    queue.append([p,False,data])

                    #send propsed priority
                    send_pro_p = threading.Thread(target=self.client,args=(addr[0], self.port, "0" + ":" + str(p) + ":" +data,))
                                                                     #self.name : 0 : prop_p : receive_name : message
                    send_pro_p.start()




            conn.close()  # close client socket


#--------------------------------------Failure Detection-------------------------------------------

    def multicast_0(self):  # method for multi-cast given msg
        #print "Multicast Hb Entered"
        # uni-cast the msg to every node in this group
        for key, value in CONNECTION_LIST.iteritems():
            if (socket.gethostname() != key):
                self.client_0(key, self.port_failure)  # pack the msg as a client socket to send


    def client_0(self, host, port):  # method for client socket
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
        prev_time = time.time()*1000
        while True:
            time.sleep((self.period/1000)/5) #delay for checking
            cur_time = time.time()*1000
            if(cur_time-prev_time>self.period): #send heartbeating evry period
                prev_time = cur_time
                self.multicast_0()

    def detector(self): # receive, check, Multicast Failure
        ss = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        ss.bind((self.host, self.port_failure))
        ss.listen(10)
        while True:
            conn, addr = ss.accept()
            while True:
                hbaddr = conn.recv(1024)
                if not hbaddr:  # recv ending msg from client
                    break


                timestamp[hbaddr] = time.time()*1000
                if hbaddr not in timer_thread:
                    timer_thread[hbaddr] = threading.Thread(target=self.Timer, args=(hbaddr,), kwargs={})
                    timer_thread[hbaddr].start()

            conn.close()  # close client socket

    def Timer(self, host):
        while True:
            time.sleep((self.period/1000)/5)
            if(time.time()*1000 > timestamp[host] + 2*self.period):

                #CONNECTION_LIST.pop(host)
                #print(host+" failed")

                #broadcast

                self.basic_multicast(CONNECTION_LIST[host]+":"+"failed")


                return -1



#-----------------------------------Main Method----------------------------------------------
if __name__ == "__main__":
    print "ChatRoom Started ..."

    T = 3000 # ms, period
    user_port = 9999
    fail_detect_port = 8888
    host = socket.gethostbyname(socket.gethostname())  # get host machine IP address

    # global dictionary for machine #
    CONNECTION_LIST = {'sp17-cs425-g07-01.cs.illinois.edu': "VM01",
                       'sp17-cs425-g07-02.cs.illinois.edu': "VM02",
                       'sp17-cs425-g07-03.cs.illinois.edu': "VM03",
                       'sp17-cs425-g07-04.cs.illinois.edu': "VM04",
                       'sp17-cs425-g07-05.cs.illinois.edu': "VM05"}

    node = Node(host, user_port, fail_detect_port, T,len(CONNECTION_LIST))  # create node object containing both client and server; def __init__(self, host, port,port_failure,period):

    # global queue and priority for ISIS

    AGR_P={} #agreed priority
    REC_PRO_COUNTER={}
    # flag_deliverable=False
    queue=[]

    Flag_Failed ={"VM01": False,
                  "VM02": False,
                  "VM03": False,
                  "VM04": False,
                  "VM05": False}
    #timestamp for total ordering
    timestamp={}
    timer_thread = {}


    t1 = threading.Thread(target=node.wait_input)  # thread for client (send msg)
    t2 = threading.Thread(target=node.server)  # thread for server (recv msg)
    t3 = threading.Thread(target=node.heartbeating) # thread for sending heartbeating
    t4 = threading.Thread(target=node.detector) # thread for detector of heartbeating(receive heartbeat, detect failure)

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





