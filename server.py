import socket
import creator
import parser
import message

SERVER_IP="arenarium"
SERVER_PORT=8000
BUFFER_SIZE=5

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

    print('Creando socket - Servidor')
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(new_socket_address)
    server_socket.listen(3)

    while True:
        new_socket, new_socket_address = server_socket.accept()
        recv_message = receive_full_message(new_socket, buffer_size)
        
        print(f' -> Se ha recibido el siguiente mensaje: {recv_message["HEAD"]}')
        response_message = server_response
        response_message["HEAD"] += "\r\nX-ElQuePregunta: Julio"

        new_socket.send(creator.create_HTTP_message(response_message))

        new_socket.close()
        print(f"conexión con {new_socket_address} ha sido cerrada")
