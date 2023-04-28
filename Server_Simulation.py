import socket
import re
import argparse
import json

# 0: Reject; 1: Prefer first; 2: Prefer last
multiple_host = 1

# 0: Not recognize; 1: Recognize; 2: Reject
space_preceded_host_first = 1

# 0: Line folding; 1: Not recognize
space_preceded_host_other = 0

# 0: Not Recognize; 1: Recognize
space_succeed_host = 1

# 0: Recognize HTTP, not others
# 1: Recognize HTTP/S, reject others
# 2: Recognize HTTP/S, not others
# 3: Recognize any schema
schema_of_absolute_URL = 0

# 0: Absolute-URL; 1: Host header
preference = 0

def request_handler(new_client_socket):

    request_data = new_client_socket.recv(1024).decode()
    print(request_data)
    request_body = request_data.splitlines(True)[-1]

    # host step0: collect potential headers
    request_line = request_data.splitlines(True)[0]
    request_headers = request_data.splitlines(True)[1:-2]
    first_header = request_headers[0]
    other_headers = request_headers[1:]

    status_code = 200
    
    recognized_headers = []
    host_headers = []
    host_header = ""
    host_URL = ""
    host = ""

    # host step1: recognize headers
    # host step1-1: first header
    if first_header[0] == " ":
        if space_preceded_host_first == 1:
            recognized_headers.append(first_header[1:])
        elif space_preceded_host_first == 2:
            status_code = 400
    elif first_header[-3] == " ":
        if space_succeed_host == 1:
            recognized_headers.append(first_header[:-3] + first_header[-2:])
    else:
        recognized_headers.append(first_header)
    # host step1-2: other headers
    if len(other_headers) > 0:
        for other_header in other_headers:
            if other_header[0] == " ":
                if space_preceded_host_other == 0:
                    recognized_headers[-1] = recognized_headers[-1][:-2] + other_header
            elif other_header[-3] == " ":
                if space_succeed_host == 1:
                    recognized_headers.append(first_header[:-3] + first_header[-2:])
            else:
                recognized_headers.append(other_header)    

    # host step2: choose a host header
    host_headers = [header for header in recognized_headers if header.startswith("Host:")]
    if len(host_headers) > 1:
        if multiple_host == 0:
            status_code = 400
        elif multiple_host == 1:
            host_header = host_headers[0]
        elif multiple_host == 2:
            host_header = host_header[-1]
    elif len(host_headers) == 1:
        host_header = host_headers[0]

    # host step3: get URL host
    absolute_URL = request_line.split(" ")[1]
    if absolute_URL != "/":
        absolute_host = re.sub("(.*): // ", "", absolute_URL)
    if absolute_URL.startswith("http://"):
        host_URL = absolute_host
    elif absolute_URL.startswith("https://"):
        if schema_of_absolute_URL != 0:
            host_URL = absolute_host
    else:
        if schema_of_absolute_URL == 1:
            status_code = 400
        elif schema_of_absolute_URL == 3:
            host_URL = absolute_host

    # host step3: choose between host header and absolute-URL
    if host_URL != "" and preference == 0:
        host = host_URL
    else:
        host = host_header    

    response_line = "HTTP/1.1 200 OK\r\n"
    if status_code == 400:
        response_line = "HTTP/1.1 400 Bad Request\r\n"
    
    response_headers = ["server: Apache Tomcat/5.0.12\r\n",
                        "content-type: text/css\r\n",
                        "cache-control: public, max-age=1000\r\n"]
    response_blank = "\r\n"
    response_body = ""
    print(request_body)    
    try:
        request_dict = json.loads(json.loads(request_body))
        response_body = request_dict["number"]
    except:
        response_body = ""
    if status_code == 400:
        response_body = ""

    response_data = response_line
    for header in response_headers:
        response_data = response_data + header
    response_data = response_data + response_blank
    response_data = response_data + response_body

    new_client_socket.send((response_data.encode()))
    new_client_socket.close()

Parser = argparse.ArgumentParser()
Parser.add_argument('-m', '--multiple_host', help = '多host头')
Parser.add_argument('-f', '--space_preceded_host_first', help = '首个头空格前缀')
Parser.add_argument('-o', '--space_preceded_host_other', help = '其余头空格前缀')
Parser.add_argument('-s', '--space_succeed_host', help = '头空格后缀')
Parser.add_argument('-a', '--schema_of_absolute_URL', help = '可接受的绝对URL格式')
Parser.add_argument('-p', '--preference', help = '同时存在host头和绝对URL时的选择')
Args = Parser.parse_args()
if Args.multiple_host:
    multiple_host = int(Args.multiple_host)
if Args.space_preceded_host_first:
    space_preceded_host_first = int(Args.space_preceded_host_first)
if Args.space_preceded_host_other:
    space_preceded_host_other = int(Args.space_preceded_host_other)
if Args.space_succeed_host:
    space_succeed_host = int(Args.space_succeed_host)
if Args.schema_of_absolute_URL:
    schema_of_absolute_URL = int(Args.schema_of_absolute_URL)
if Args.preference:
    preference = int(Args.preference)

tcp_server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tcp_server_socket.bind(("", 5555))
tcp_server_socket.listen(128)
while True:
    new_client_socket = tcp_server_socket.accept()[0]
    request_handler(new_client_socket)
