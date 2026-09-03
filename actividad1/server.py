import socket
import json
import sys
import creator
import parser

SERVER_IP="arenarium"
SERVER_PORT=8000
BUFFER_SIZE=5

with open("html_response.html", "r") as file:
    html = file.read()

server_response = {"HEAD":f"HTTP/1.1 403 Forbidden\r\nContent-Type: text/html; charset=UTF-8\r\nContent-Length: {len(html.encode("utf-8"))}","BODY":html}

def gen_image_response(image):
    with open(image[1:], "rb") as file:
        picture = file.read()
    return {"HEAD":f"HTTP/1.1 403 Forbidden\r\nContent-Type: image/jpeg; charset=UTF-8\r\nContent-Length: {len(picture)}","BODY":picture}

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

    print("="*60)
    print('Creando sockets del servidor...')
    print("-"*60)

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(new_socket_address)
    server_socket.listen(3)
    
    print("Sockets del servidor creados")
    print("-"*60)
    
    json_name = "json_nombre.json"
    json_address = ""

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
        block = False
        image = [False, ""]
        new_socket, new_socket_address = server_socket.accept()
        recv_message = receive_full_head(new_socket, buffer_size)
        proxy_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        proxy_response_message = b''
        PROXY_HOST=""
        
        print(f'Se ha recibido el siguiente mensaje:\n{recv_message["HEAD"]}')
        print("-"*60)
        
        if "GET" in recv_message["HEAD"]:
            if "image/" in recv_message["HEAD"]:
                image[0] = True

            host_start = recv_message["HEAD"].find("http://") + 7
            current = host_start

            while recv_message["HEAD"][current] != "/":
                PROXY_HOST += recv_message["HEAD"][current]
                current += 1        
            
            new_proxy_address = (PROXY_HOST, 80) 
           
            print(f"Lo que se proxeará es: {new_proxy_address}")
            print("-"*60)
            
            if recv_message["HEAD"][current + 1] == " ":
                to_block = PROXY_HOST
            else:
                route = ""
                while recv_message["HEAD"][current] != " ":
                    route += recv_message["HEAD"][current]
                    current += 1
                to_block = PROXY_HOST + route
                if image[0]:
                    image[1] = route
            
            proxy_socket.connect(new_proxy_address)
            
            for forbidden in json["blocked"]:
                if to_block == forbidden:
                    block = True
            
            if not block:
                if recv_message["HEAD"].find("\r\nX-ElQuePregunta") == -1:
                    recv_message["HEAD"] += f"\r\nX-ElQuePregunta: {json["nombre"]}"
                
                proxy_socket.send(creator.create_HTTP_message(recv_message))
                parsed_proxy_message = receive_full_message(proxy_socket, BUFFER_SIZE)
                
                for forbidden in json["forbidden_words"]:
                    keys = forbidden.keys()
                    for key in keys:
                        parsed_proxy_message["BODY"] = parsed_proxy_message["BODY"].replace(key, forbidden[key])
                
                if not image[0]:
                    proxy_response_message = creator.create_HTTP_message(parsed_proxy_message)
                else:
                    proxy_response_message = creator.create_HTTP_message(gen_image_response(image[1]))
            else:
                proxy_response_message = creator.create_HTTP_message(server_response)

            proxy_socket.close()
            print(f"conexión con el socket de proxy {new_proxy_address} ha sido cerrada")    
        
        new_socket.send(proxy_response_message)
        new_socket.close()
        print(f"conexión con el socket de servidor {new_socket_address} ha sido cerrada")
        print("="*60)
