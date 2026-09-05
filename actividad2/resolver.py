import socket
from dnslib import DNSRecord
from dnslib.dns import CLASS, QTYPE
import dnslib

import parser

SERVER_IP="100.117.46.88"
SERVER_PORT=8000
BUFF_SIZE = 8192

def resolver(mensaje_consulta, ip_addr="198.41.0.4"):

    server_address = (ip_addr, 53)
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    mensaje_parseado_para_debug = parser.parse_DNS_message(mensaje_consulta)
    quiero_saber = str(mensaje_parseado_para_debug.get_q().get_qname())[::-1]
    print(f"(debug) Consultando '{mensaje_parseado_para_debug.get_q().get_qname()}' a '.' con dirección IP '{ip_addr}'")

    try:
        sock.sendto(mensaje_consulta, server_address)
        data, _ = sock.recvfrom(BUFF_SIZE)

        d = parser.parse_DNS_message(data)

        for rr in d.rr:
            if QTYPE.get(rr.rtype) == "A":
                return data

        for rr in d.auth:
            print("wena")
            if isinstance(rr.rdata, dnslib.dns.NS):
                for addrr in d.ar:
                    if QTYPE.get(addrr.rtype) == "A":
                        print("Tipo addrr.rdata: ",type(addrr.rdata))
                        return resolver(mensaje_consulta, "{}".format(addrr.rdata))
                q = DNSRecord.question(rr.rdata)
                q = bytes(q.pack())
                newData = resolver(q)
                return resolver(mensaje_consulta, "{}".format(newData.get_a().rdata))              

    finally:
        sock.close()

    return data

if __name__ == "__main__":
    server_socket_address = (SERVER_IP, SERVER_PORT)

    print("="*60)
    print('Creando socket no orientado a conexión...')
    print("-"*60)

    # Socket no orientado a conexion
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind(server_socket_address)
    
    print("Socket creado")
    print("="*60)

    while True:
        message, address = server_socket.recvfrom(BUFF_SIZE)
        print(f'Se ha recibido el siguiente mensaje:\n{message}\nDe:\n{address}')
        print(f"Mensaje parseado:\n{parser.parse_DNS_message(message)}")
        print("-"*60)

        resolve = resolver(message)

        if resolve != None:
            server_socket.sendto(resolve, address)
            print(f'Se ha enviado el siguiente mensaje:\n{resolve}\nA:\n{address}')
            print(f"Mensaje parseado:\n{parser.parse_DNS_message(resolve)}")

        print("="*60)
