import socket
import json
import sys
import creator
import parser

SERVER_IP="172.20.10.4"
SERVER_PORT=8000
BUFFER_SIZE=5

with open("actividad_1/html_response.html", "r") as file:
    html = file.read()

server_response = {"HEAD":f"HTTP/1.1 403 Forbidden\r\nContent-Type: text/html; charset=UTF-8\r\nContent-Length: {len(html.encode("utf-8"))}","BODY":html}

def receive_full_head(socket, buffer_size):
    recv_message = socket.recv(buffer_size) 
    full_body = recv_message

    while full_body.decode().find("\r\n\r\n") == -1:
        recv_message = socket.recv(buffer_size)
        full_body += recv_message
    
    return parser.parse_HTTP_message(full_body) 

def receive_full_message(socket, buffer_size):
    recv_message = socket.recv(buffer_size)
    full_message = recv_message

    while len(recv_message) == buffer_size:
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

    json_name = "json_nombre.json"
    json_address = "actividad_1/"

    if len(sys.argv) == 2:
        json_name = sys.argv[1]
    elif len(sys.argv) == 3:
        json_name = sys.argv[1]
        json_address = sys.argv[2]
    elif len(sys.argv) > 3:
        print("Mas argumentos que lo esperado, usando valores por defecto")

    with open(json_address + json_name) as file:
        json = json.load(file)

    while True:
        new_socket, new_socket_address = server_socket.accept()
        block = False
        PROXY_PORT=80
        recv_message = receive_full_head(new_socket, buffer_size)
        
        print(f' -> Se ha recibido el siguiente mensaje: {recv_message["HEAD"]}')
        PROXY_HOST=""
        host_start = recv_message["HEAD"].find("Host: ") + 6
        current = host_start
    
        while recv_message["HEAD"][current] != "\r":
            PROXY_HOST += recv_message["HEAD"][current]
            current += 1
        
        route_start = recv_message["HEAD"].find("http://") + 7 + len(PROXY_HOST)
        if recv_message["HEAD"][route_start + 1] == " ":
            to_block = PROXY_HOST
        else:
            route = ""
            current_route = route_start
            while recv_message["HEAD"][current_route] != " ":
                route += recv_message["HEAD"][current_route]
                current_route += 1
                to_block = PROXY_HOST + route
        
        proxy_socket.connect((PROXY_HOST, PROXY_PORT))
        
        for blocked in json["blocked"]:
            if to_block == blocked:
                block = True

        print(block)
        
        if not block:
            proxy_socket.send(creator.create_HTTP_message(recv_message))
            parsed_proxy_message = receive_full_message(proxy_socket, BUFFER_SIZE)

            # ciclo que cambia las forbidden words
            for forbidden in json["forbidden_words"]:
                keys = forbidden.keys()
                for key in keys:
                    parsed_proxy_message["BODY"] = parsed_proxy_message["BODY"].replace(key, forbidden[key])
                    print(parsed_proxy_message["BODY"])
            proxy_response_message = creator.create_HTTP_message(parsed_proxy_message)
        else:
            proxy_response_message = creator.create_HTTP_message(server_response)

        # if response_message["HEAD"].find("\r\nX-ElQuePregunta") == -1:
        #     response_message["HEAD"] += f"\r\nX-ElQuePregunta: {name}"

        new_socket.send(proxy_response_message)
        new_socket.close()
        proxy_socket.close()
        print(f"conexión con {new_socket_address} ha sido cerrada")