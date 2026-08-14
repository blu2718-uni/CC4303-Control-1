import socket
import creator
import parser

def receive_full_message(socket, buffer_size):
    recv_message = socket.recv(buffer_size) 
    full_message = recv_message
    
    while full_message.decode().count("\r\n\r\n") < 2:
        recv_message = socket.recv(buffer_size)
        full_message += recv_message

    return parser.parse_HTTP_message(full_message) 
    
if __name__ == "__main__":
    buffer_size = 5
    new_socket_address = ("arenarium", 5000)

    print('Creando socket - Servidor')
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(new_socket_address)
    server_socket.listen(3)

    while True:
        # cuando llega una petición de conexión la aceptamos
        # y se crea un nuevo socket que se comunicará con el cliente
        new_socket, new_socket_address = server_socket.accept()

        # luego recibimos el mensaje usando la función que programamos
        # esta función entrega el mensaje en string (no en bytes) y sin el end_of_message
        recv_message = receive_full_message(new_socket, buffer_size)
        to_print = recv_message["BODY"]
        
        print(f' -> Se ha recibido el siguiente mensaje: {to_print}')

        # respondemos indicando que recibimos el mensaje
        response_message = f'Se ha sido recibido con éxito el mensaje: {to_print}'

        # el mensaje debe pasarse a bytes antes de ser enviado, para ello usamos encode
        new_socket.send(response_message.encode())

        # cerramos la conexión
        # notar que la dirección que se imprime indica un número de puerto distinto al 5000
        new_socket.close()
        print(f"conexión con {new_socket_address} ha sido cerrada")
