import socket
import json

def request_handler(new_client_socket):

    Consistency = 0
    Multiple_host_headers = 0
    Space_preceded_Host_as_first_header = 0
    Other_space_preceded_host_header = 0
    Space_succeeded_host_header = 0

    request_data = new_client_socket.recv(1024).decode()
    print(request_data)
    request_body = request_data.splitlines(True)[-1]

    request_line = request_data.splitlines(True)[0]
    request_headers = request_data.splitlines(True)[1:-2]
    first_header = request_headers[0]
    other_headers = request_headers[1:]

    host_headers = []
    absolute_URI = request_line.split(" ")[1]

    non_match = ""
    if first_header.startswith("If-None-Match: ") or first_header.startswith("if-none-match: "):
        non_match = first_header[15:-2]
    else:
        for other_header in other_headers:
            if other_header.startswith("If-None-Match: ") or other_header.startswith("if-none-match: "):
                non_match = other_header[15:-2]
                break
    
    if first_header.startswith(" "):
        Space_preceded_Host_as_first_header = 1
    for other_header in other_headers:
        if other_header.startswith(" "):
            Other_space_preceded_host_header = 1
            break

    if first_header.endswith(" \r\n"):
        Space_succeeded_host_header = 1
    else:
        for other_header in other_headers:
            if other_header.endswith(" \r\n"):
                Space_succeeded_host_header = 1
                break
    
    if first_header.startswith("host:"):
        host_headers.append(first_header)
    for other_header in other_headers:
        if other_header.startswith(" "):
            host_headers.append(other_header)
    if len(host_headers) > 1:
        Multiple_host_headers = 1
    
    header_host = host_headers[0][6:-2]
    header_URI = absolute_URI.split("/")[-1]
    if header_host != header_URI:
        Consistency = 1

    response_line = "HTTP/1.1 200 OK\r\n"

    response_headers = ["server: Apache Tomcat/5.0.12\r\n",
                        "content-type: text/css\r\n",
                        "cache-control: public, max-age=1000\r\n"]
    response_blank = "\r\n"
    response_body = {"host": host_headers[0][6:-2]}

    if non_match != "" and non_match == host_headers[0][6:-2]:
        response_line = "HTTP/1.1 304 Not Modified\r\n"
        response_body = ""
    else:
        if Consistency:
            response_body = "Ambiguous request: consistency"
        elif Multiple_host_headers:
            response_body = "Ambiguous request: multiple host headers"
        elif Space_preceded_Host_as_first_header:
            response_body = "Ambiguous request: space-preceded host as first header"
        elif Other_space_preceded_host_header:
            response_body = "Ambiguous request: other space-preceded host header"
        elif Space_succeeded_host_header:
            response_body = "Ambiguous request: space-succeeded host header"
        else:
            try:
                request_dict = json.loads(json.loads(request_body))
                response_body["number"] = request_dict["number"]
                response_body = json.dumps(response_body)
            except:
                response_body = json.dumps(response_body)
        
        etag_header = "ETag: " + host_headers[0][6:-2] + "\r\n"
        response_headers.append(etag_header)

    response_data = response_line
    for header in response_headers:
        response_data = response_data + header
    response_data = response_data + response_blank
    response_data = response_data + response_body

    new_client_socket.send((response_data.encode()))
    new_client_socket.close()

tcp_server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tcp_server_socket.bind(("", 5555))
tcp_server_socket.listen(128)
while True:
    new_client_socket = tcp_server_socket.accept()[0]
    request_handler(new_client_socket)
