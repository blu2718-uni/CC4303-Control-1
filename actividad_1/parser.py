def parse_HTTP_message(message):
    decoded_message = message.decode()
    HEAD_end = decoded_message.find("\r\n\r\n")
        
    if HEAD_end == -1:
        print("Mensaje HTTP incompleto y/o inválido")
        return
        
    parsed_message = {
            "HEAD":decoded_message[:HEAD_end],
            "BODY":decoded_message[HEAD_end + 4:]
    }

    return parsed_message