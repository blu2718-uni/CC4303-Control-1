import sys
import socket
from dnslib import DNSRecord, DNSHeader, RR, A
from dnslib.dns import CLASS, QTYPE
import dnslib

import parser

SERVER_IP="100.117.46.88"
SERVER_PORT=8000
BUFF_SIZE = 8192

def gen_new_cache(last, debug_mode=False):
    top = []
    # Manually count frequency of each element
    freq = {}
    for query in last:
        freq[query[0]] = freq.get(query[0], 0) + 1

    # Sort the keys based on their frequency in descending order
    sorted_keys = sorted(freq.keys(), key=lambda x: freq[x], reverse=True)

    for often in sorted_keys[:3]:
        for query in last:
            if query[0] == often:
                top.append((often, query[1]))
                break
    

    if debug_mode: print("(debug) Se generó un caché")

    return dict(top)

def resolver(mensaje_consulta, ip_addr="198.41.0.4", cache={}, debug_mode=False):

    server_address = (ip_addr, 53)
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    mensaje_parseado_para_debug = parser.parse_DNS_message(mensaje_consulta)
    quiero_saber = str(mensaje_parseado_para_debug.get_q().get_qname())[::-1]
    if debug_mode: print(f"(debug) Consultando '{mensaje_parseado_para_debug.get_q().get_qname()}' a '.' con dirección IP '{ip_addr}'")
    
    if "{}".format(mensaje_parseado_para_debug.get_q().get_qname()) in cache:
        cached_response = DNSRecord(DNSHeader(qr=1,
                                              rd=1,
                                              ra=1,
                                              id=mensaje_parseado_para_debug.header.id),
                                    q=mensaje_parseado_para_debug.get_q(),
                                    a=RR("{}".format(mensaje_parseado_para_debug.get_q().get_qname()), 
                                         rdata=A(cache["{}".format(mensaje_parseado_para_debug.get_q().get_qname())]))                                  )
        if debug_mode: print("(debug) Se utilizó el caché")
        return cached_response.pack()
    try:
        sock.sendto(mensaje_consulta, server_address)
        data, _ = sock.recvfrom(BUFF_SIZE)

        d = parser.parse_DNS_message(data)

        for rr in d.rr:
            if QTYPE.get(rr.rtype) == "A":
                return data

        for rr in d.auth:
            if isinstance(rr.rdata, dnslib.dns.NS):
                for addrr in d.ar:
                    if QTYPE.get(addrr.rtype) == "A":
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
    debug = False
    if len(sys.argv) == 2:
        if sys.argv[1] in ["-d", "--debug"]:
            debug = True
        else:
            print("Flag inválido, se continuará con la ejecución normal")


    print("="*60)
    print('Creando socket no orientado a conexión...')

    # Socket no orientado a conexion
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind(server_socket_address)
    
    print("Socket creado")
    print("="*60)
    if debug:
        print("Se ha activado el modo debug")
        print("="*60)
    
    last_queries = []

    while True:
        message, address = server_socket.recvfrom(BUFF_SIZE)
        print(f'Se ha recibido el siguiente mensaje:\n{message}\nDe:\n{address}')
        print(f"Mensaje parseado:\n{parser.parse_DNS_message(message)}")
        print("-"*60)

        resolve = resolver(message, cache=gen_new_cache(last_queries, debug_mode=debug), debug_mode=debug)

        if resolve != None:
            server_socket.sendto(resolve, address)
            print(f'Se ha enviado el siguiente mensaje:\n{resolve}\nA:\n{address}')
            parseado = parser.parse_DNS_message(resolve)
            print(f"Mensaje parseado:\n{parseado}")
            if len(last_queries) < 20:
                if debug: print("(debug) Se actualizaron las últimas queries")
                last_queries = [("{}".format(parseado.get_a().get_rname()),
                                 "{}".format(parseado.get_a().rdata))] + last_queries
            else:
                if debug: print("(debug) Se actualizaron las últimas queries")
                last_queries = [("{}".format(parseado.get_a().get_rname()),
                                "{}".format(parseado.get_a().rdata))] + last_queries.pop()
                

        print("="*60)
