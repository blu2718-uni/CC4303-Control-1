import socket
import json
import sys
import creator
import parser

SERVER_IP="arenarium"
SERVER_PORT=8000
BUFFER_SIZE=5

PROXY_HOST="example.com"
PROXY_PORT=80

with open("html_response.html", "r") as file:
    html = file.read()

server_response = {"HEAD":f"HTTP/1.1 200 OK\r\nContent-Type: text/html; charset=UTF-8\r\nContent-Length: {len(html.encode("utf-8"))}","BODY":html}

def receive_full_message(socket, buffer_size):
    recv_message = socket.recv(buffer_size) 
    full_message = recv_message

    while full_message.decode().find("\r\n\r\n") == -1:
        recv_message = socket.recv(buffer_size)
        full_message += recv_message
    
    return parser.parse_HTTP_message(full_message) 
    
if __name__ == "__main__":
    buffer_size = BUFFER_SIZE
    new_socket_address = (SERVER_IP, SERVER_PORT)

    print('Creando sockets')
    proxy_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(new_socket_address)
    server_socket.listen(3)

    # json_name = "json_nombre.json"
    # json_address = ""

    # if len(sys.argv) == 2:
    #     json_name = sys.argv[1]
    # elif len(sys.argv) == 3:
    #     json_name = sys.argv[1]
    #     json_address = sys.argv[2]
    # elif len(sys.argv) > 3:
    #     print("Mas argumentos que lo esperado, usando valores por defecto")

    # with open(json_address + json_name) as file:
        # name = json.load(file)["nombre"]

    while True:
        new_socket, new_socket_address = server_socket.accept()
        proxy_socket.connect((PROXY_HOST, PROXY_PORT))
        
        recv_message = receive_full_message(new_socket, buffer_size)
        
        print(f' -> Se ha recibido el siguiente mensaje: {recv_message["HEAD"]}')
        
        proxy_socket.send(creator.create_HTTP_message(recv_message))

        proxy_response_message = proxy_socket.recv(4092)
        # if response_message["HEAD"].find("\r\nX-ElQuePregunta") == -1:
        #     response_message["HEAD"] += f"\r\nX-ElQuePregunta: {name}"

        new_socket.send(proxy_response_message)
        new_socket.close()
        proxy_socket.close()
        print(f"conexión con {new_socket_address} ha sido cerrada")