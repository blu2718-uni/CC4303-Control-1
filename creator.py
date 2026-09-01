import socket

def create_HTTP_message(message):
    head = message["HEAD"]
    body = message["BODY"]
    separator = "\r\n\r\n"
    if isinstance(body, str):
        body = body.encode("utf-8")
    
    encoded = head.encode("utf-8") + separator.encode("utf-8") + body

    return encoded
