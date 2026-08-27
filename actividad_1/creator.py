def create_HTTP_message(message):
    head = message["HEAD"]
    body = message["BODY"]

    to_encode = head + "\r\n\r\n" + body
    encoded = to_encode.encode()

    return encoded