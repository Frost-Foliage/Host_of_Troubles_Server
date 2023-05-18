import socket
import json
import time

host_1 = "waf1.cdnattack.shop"
host_2 = "waf2.cdnattack.shop"
last_etag_1 = ""
last_etag_2 = ""

def request_handler(new_client_socket):

    Consistency = 0
    Multiple_host_headers = 0
    Space_preceded_Host_as_first_header = 0
    Other_space_preceded_host_header = 0
    Space_succeeded_host_header = 0

    request_data = new_client_socket.recv(1024).decode()
    print(request_data)

    request_line = request_data.splitlines(True)[0]
    request_headers = request_data.splitlines(True)[1:-1]
    first_header = request_headers[0]
    other_headers = request_headers[1:]

    host_headers = []
    absolute_URI = request_line.split(" ")[1]

    XNumber = ""
    if first_header.startswith("XNumber: "):
        XNumber = first_header[9:-2]
    else:
        for other_header in other_headers:
            if other_header.startswith("XNumber: "):
                XNumber = other_header[9:-2]
                break

    none_match = ""
    if first_header.startswith("If-None-Match: ") or first_header.startswith("if-none-match: "):
        none_match = first_header[15:-2]
    else:
        for other_header in other_headers:
            if other_header.startswith("If-None-Match: ") or other_header.startswith("if-none-match: "):
                none_match = other_header[15:-2]
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
    
    if first_header.startswith("Host:"):
        host_headers.append(first_header)
    for other_header in other_headers:
        if other_header.startswith("Host:"):
            host_headers.append(other_header)
    if len(host_headers) > 1:
        Multiple_host_headers = 1
    
    header_host = host_headers[0][5:-2]
    if host_headers[0].startswith("Host: "):
        header_host = host_headers[0][6:-2]
    header_URI = absolute_URI.split("/")[-2]
    if header_host.startswith("http://") and header_host != header_URI:
        Consistency = 1

    response_line = "HTTP/1.1 200 OK\r\n"

    response_headers = ["Server: Apache Tomcat/5.0.12\r\n",
                        "Content-Type: text/css\r\n",
                        "Cache-Control: public, max-age=7200\r\n",
                        "Expires: Thu, 30 May 2023 18:30:00 GMT\r\n",]
    response_blank = "\r\n"
    response_body = {"host": header_host}

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
        if none_match != "":
            if header_host == host_1:
                if none_match == last_etag_1:
                    response_line = "HTTP/1.1 304 Not Modified\r\n"
                    response_body = ""
                else:
                    etag_1 = header_host + "-" + str(time.localtime())
                    etag_header = "ETag: " + etag_1 + "\r\n"
                    response_headers.append(etag_header)
                    last_etag_1 = etag_1
                    response_body["number"] = XNumber
                    response_body = json.dumps(response_body)
            elif header_host == host_2:
                if none_match == last_etag_2:
                    response_line = "HTTP/1.1 304 Not Modified\r\n"
                    response_body = ""
                else:
                    etag_2 = header_host + "-" + str(time.localtime())
                    etag_header = "ETag: " + etag_2 + "\r\n"
                    response_headers.append(etag_header)
                    last_etag_2 = etag_2
                    response_body["number"] = XNumber
                    response_body = json.dumps(response_body)
            else:
                print("unknown host")
                print(header_host)
                response_body = ""
        else:
            if header_host == host_1:
                etag_1 = header_host + "-" + str(time.localtime())
                etag_header = "ETag: " + etag_1 + "\r\n"
                response_headers.append(etag_header)
                last_etag_1 = etag_1
                response_body["number"] = XNumber
                response_body = json.dumps(response_body)
            elif header_host == host_2:
                etag_2 = header_host + "-" + str(time.localtime())
                etag_header = "ETag: " + etag_2 + "\r\n"
                response_headers.append(etag_header)
                last_etag_2 = etag_2
                response_body["number"] = XNumber
                response_body = json.dumps(response_body)
            else:
                print("unknown host")
                print(header_host)
                response_body = ""
    
    response_data = response_line
    for header in response_headers:
        response_data = response_data + header
    response_data = response_data + response_blank
    response_data = response_data + response_body

    new_client_socket.send((response_data.encode()))
    new_client_socket.close()

    # if none_match != "" and none_match == header_host:
    #     response_line = "HTTP/1.1 304 Not Modified\r\n"
    #     response_body = ""
    # else:
    #     if Consistency:
    #         response_body = "Ambiguous request: consistency"
    #     elif Multiple_host_headers:
    #         response_body = "Ambiguous request: multiple host headers"
    #     elif Space_preceded_Host_as_first_header:
    #         response_body = "Ambiguous request: space-preceded host as first header"
    #     elif Other_space_preceded_host_header:
    #         response_body = "Ambiguous request: other space-preceded host header"
    #     elif Space_succeeded_host_header:
    #         response_body = "Ambiguous request: space-succeeded host header"
    #     else:
    #         response_body["number"] = XNumber
    #         response_body = json.dumps(response_body)
        
    #     etag_header = "ETag: " + header_host + "\r\n"
    #     response_headers.append(etag_header)

    # response_data = response_line
    # for header in response_headers:
    #     response_data = response_data + header
    # response_data = response_data + response_blank
    # response_data = response_data + response_body

    # new_client_socket.send((response_data.encode()))
    # new_client_socket.close()

tcp_server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tcp_server_socket.bind(("", 80))
tcp_server_socket.listen(128)
while True:
    new_client_socket = tcp_server_socket.accept()[0]
    request_handler(new_client_socket)
