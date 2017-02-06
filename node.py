import socket, threading,sys

class Node1():
    def __init__(self, host, port):
        self.host = host
        self.port = port



    def wait_input(self):
        while True:
            cmd = raw_input("")
            if cmd=='q':
                sys.exit(1)
            self.broadcast_data(cmd)

    def client(self, host,port,cmd):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #while True:
        s.connect((host, port)) # connect to Node2
        name = CONNECTION_LIST[socket.gethostname()] # find current machine name
        s.send(name + ":" + cmd)  # send message to sever
        # print s.recv(1024) # print received messages
        s.close()


    def server(self):
        ss = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        ss.bind((self.host, self.port)) # wating for message to node1 port
        ss.listen(5)
        while True:
            conn, addr = ss.accept()
            # print 'Connected by ', addr

            while True:
                data = conn.recv(1024)
                if not data:
                    break
                # conn.send("server received you message.")
                print data

            conn.close()


    def broadcast_data(self,cmd):
        # Do not send the message to master socket and the client who has send us the message
        # for socket in CONNECTION_LIST:
        #     try:
        #         socket.send(message)
        #     except:
        for key,value in  CONNECTION_LIST.iteritems():
            self.client(key,self.port,cmd)
        # socket.close()
        # CONNECTION_LIST.remove(socket)


                            # def tcplink(self, sock, addr):
    #     while True:
    #         data = sock.recv(1024)
    #         sock.send("%s received" % data)
    #     sock.close()
    #     print "Connection closed."


if __name__ == "__main__":
	print "Chatroom Started ..."
	host=socket.gethostbyname(socket.gethostname())
	node1 = Node1(host, 9999)
	CONNECTION_LIST = {'sp17-cs425-g07-01.cs.illinois.edu':"VM01",
					   'sp17-cs425-g07-02.cs.illinois.edu':"VM02",
					   'sp17-cs425-g07-03.cs.illinois.edu':"VM03",
					   'sp17-cs425-g07-04.cs.illinois.edu':"VM04",
					   'sp17-cs425-g07-05.cs.illinois.edu':"VM05"
					   }
	t1 = threading.Thread(target=node1.wait_input)
	t2 = threading.Thread(target=node1.server)

	t2.start()
	t1.start()

