import socket

def parse_HTTP_message(message):
    decoded_message = message.decode()
    HEAD_end = decoded_messade.find("\r\n")
    
    

    parsed_message = {
            "HEAD":head,
            "BODY":body
    }
