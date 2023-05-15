import socket
import json
import csv

class Agency_Behaviour:
    def __init__(self):
        self.Ambiguous = ""
        self.Cache_exist = ""
        self.Consistency = ""
        self.Preference = ""
        self.Multiple_host_headers = ""
        self.Space_preceded_host_as_first_header = ""
        self.Other_space_preceded_host_header = ""
        self.Space_succeeded_host_header = ""
        self.Schema_of_absolute_URI = ""

def send_request(IP_and_port, URI, headers):
    tcp_client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_client_socket.connect(IP_and_port)

    request_line = "GET " + URI + " HTTP/1.1\r\n"
    request_headers = headers
    request_blank = "\r\n"

    request_data = request_line
    for header in request_headers:
        request_data = request_data + header
    request_data = request_data + request_blank

    tcp_client_socket.send(request_data.encode())
    recv_data = tcp_client_socket.recv(4096).decode()
    return recv_data

def cloudfare_test(IP_and_port):
    base_headers = ["Connection: keep-alive\r\n",
                    "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36\r\n",
                    "Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9\r\n",
                    "Accept-Language: zh-CN,zh;q=0.9,en;q=0.8\r\n"]

    # step0: To record results
    Ambiguous = ""
    Cache_exist = ""
    Presence_host_header = ""
    Presence_absolute_URI = ""
    Consistency = ""
    Preference = ""
    Multiple_host_headers = ""
    Space_preceded_host_as_first_header = ""
    Other_space_preceded_host_header = ""
    Space_succeeded_host_header = ""
    Schema_of_absolute_URI = ""

    # step1: Cache exists
    headers = ["XNumber: 1\r\n",
               "host: waf1.cdnattack.shop\r\n"]
    headers.extend(base_headers)
    recv_data1 = send_request(IP_and_port, "http://waf1.cdnattack.shop/style.css", headers)
    recv_data1 = send_request(IP_and_port, "http://waf1.cdnattack.shop/style.css", headers)
    recv_data1 = send_request(IP_and_port, "http://waf1.cdnattack.shop/style.css", headers)
    headers = ["XNumber: 2\r\n",
               "host: waf1.cdnattack.shop\r\n"]
    recv_data2 = send_request(IP_and_port, "http://waf1.cdnattack.shop/style.css", headers)
    recv_data2 = send_request(IP_and_port, "http://waf1.cdnattack.shop/style.css", headers)
    recv_data2 = send_request(IP_and_port, "http://waf1.cdnattack.shop/style.css", headers)
    if recv_data2.splitlines()[-3].startswith("Ambiguous request: "):
        Ambiguous = recv_data2.splitlines()[-1][19:]
        print("Ambiguous: " + Ambiguous)
    else:
        recv_body2 = json.loads(recv_data2.splitlines()[-3])
        if recv_body2["number"] == "1":
            Cache_exist = "true"
            print("Cache exists")
        else:
            Cache_exist = "false"
            print("Cache doesn't exist")

    if Ambiguous == "":
        # step2: Presence of host
        # step2-1: Host header
        recv_data1 = send_request(IP_and_port, "http://waf1.cdnattack.shop/style.css", base_headers)
        recv_status1 = recv_data1.splitlines()[0].split(" ")[1]
        if recv_status1 == "400":
            Presence_host_header = "Must"
            print("Presence of host header: Must")
        elif recv_status1 == "200":
            Presence_host_header = "Optional"
            print("Presence of host header: Optional")
        else:
            print("Error: Presence of host header: Wrong status code")
        # step2-2: Absolute-URI
        headers = ["host: waf1.cdnattack.shop\r\n"]
        headers.extend(base_headers)
        recv_data1 = send_request(IP_and_port, "/style.css", headers)
        recv_status1 = recv_data1.splitlines()[0].split(" ")[1]
        if recv_status1 == "400":
            Presence_absolute_URI = "Must"
            print("Presence of absolute-URI: Must")
        elif recv_status1 == "200":
            Presence_absolute_URI = "Optional"
            print("Presence of absolute-URI: Optional")
        else:
            print("Error: Presence of absolute-URI: Wrong status code")

        # step3: Recognized absolute-URI vs. Recognized Host header
        headers = ["host: waf2.cdnattack.shop\r\n"]
        headers.extend(base_headers)
        recv_data1 = send_request(IP_and_port, "http://waf1.cdnattack.shop/style.css", headers)
        recv_status1 = recv_data1.splitlines()[0].split(" ")[1]
        recv_body1 = json.loads(recv_data1.splitlines()[-3])
        if recv_status1 == "400":
            Consistency = "Must"
            print("Consistency: Must")
        elif recv_status1 == "200":
            Consistency = "Optional"
            print("Consistency: Optional")
            if recv_body1["host"] == "waf1.cdnattack.shop":
                Preference = "Absolute-URI"
                print("Preference: Absolute-URI")
            elif recv_body1["host"] == "waf2.cdnattack.shop":
                Preference = "Host header"
                print("Preference: Host header")
            else:
                print("Error: Preference: Wrong host")
        else:
            print("Error: Consistency: Wrong status code")

        # step4: Multiple Host headers
        if Consistency == "Must":
            headers = ["host: waf1.cdnattack.shop\r\n",
                    "host: waf2.cdnattack.shop\r\n"]
            headers.extend(base_headers)
            recv_data1 = send_request(IP_and_port, "http://waf1.cdnattack.shop/style.css", headers)
            recv_status1 = recv_data1.splitlines()[0].split(" ")[1]
            if recv_status1 == "200":
                Multiple_host_headers = "Prefer first"
                print("Multiple Host headers: Prefer first")
            elif recv_status1 == "400":
                recv_data2 = send_request(IP_and_port, "http://waf2.cdnattack.shop/style.css", headers)
                recv_status2 = recv_data2.splitlines()[0].split(" ")[1]
                if recv_status2 == "200":
                    Multiple_host_headers = "Prefer last"
                    print("Multiple Host headers: Prefer last")
                elif recv_status2 == "400":
                    Multiple_host_headers = "Concatenate or Reject"
                    print("Multiple Host headers: Concatenate or Reject")
                else:
                    print("Error: Multiple Host headers: Wrong status code")
            else:
                print("Error: Multiple Host headers: Wrong status code")
        elif Presence_absolute_URI == "Must" and Preference == "Absolute-URI":
            print("Pass Multiple Host headers")
        else:
            headers = ["host: waf1.cdnattack.shop\r\n",
                    "host: waf2.cdnattack.shop\r\n"]
            headers.extend(base_headers)
            recv_data1 = send_request(IP_and_port, "http://waf1.cdnattack.shop/style.css", headers)
            recv_status1 = recv_data1.splitlines()[0].split(" ")[1]
            if recv_status1 == "400":
                Multiple_host_headers = "Concatenate or Reject"
                print("Multiple Host headers: Concatenate or Reject")
            elif recv_status1 == "200":
                recv_body1 = json.loads(recv_data1.splitlines()[-3])
                if recv_body1["host"] == "waf2.cdnattack.shop":
                    Multiple_host_headers = "Prefer last"
                    print("Multiple Host headers: Prefer last")
                elif recv_body1["host"] == "waf1.cdnattack.shop":
                    recv_data2 = send_request(IP_and_port, "http://waf2.cdnattack.shop/style.css", headers)
                    recv_status2 = recv_data2.splitlines()[0].split(" ")[1]
                    if recv_status2 == "200":
                        recv_body2 = json.loads(recv_data2.splitlines()[-3])
                        if recv_body2["host"] == "waf1.cdnattack.shop":
                            Multiple_host_headers = "Prefer first"
                            print("Multiple Host headers: Prefer first")
                        elif recv_body2["host"] == "waf2.cdnattack.shop":
                            Multiple_host_headers = "Use absolute-URI"
                            print("Multiple Host headers: Use absolute-URI")
                    else:
                        print("Error: Multiple Host headers: Wrong status code")
                else:
                    print("Error: Multiple Host headers: Unknown host")
            else:
                print("Error: Multiple Host headers: Wrong status code")

        # step5: Space-preceded Host as first header
        if Consistency == "Must":
            headers = [" host: waf1.cdnattack.shop\r\n"]
            headers.extend(base_headers)
            recv_data1 = send_request(IP_and_port, "http://waf1.cdnattack.shop/style.css", headers)
            recv_status1 = recv_data1.splitlines()[0].split(" ")[1]
            if recv_status1 == "200":
                Space_preceded_host_as_first_header = "Recognize"
                print("Space-preceded Host as first header: Recognize")
            elif recv_status1 == "400":
                headers = [" host: waf1.cdnattack.shop\r\n",
                        "host: waf2.cdnattack.shopr\n"]
                headers.extend(base_headers)
                recv_data2 = send_request(IP_and_port, "http://waf2.cdnattack.shop/style.css", headers)
                recv_status2 = recv_data2.splitlines()[0].split(" ")[1]
                if recv_status2 == "200":
                    Space_preceded_host_as_first_header = "Not recognize"
                    print("Space-preceded Host as first header: Not recognize")
                elif recv_status2 == "400":
                    Space_preceded_host_as_first_header = "Reject"
                    print("Space-preceded Host as first header: Reject")
                else:
                    print("Error: Space-preceded Host as first header: Wrong status code")
            else:
                print("Error: Space-preceded Host as first header: Wrong status code")
        elif Presence_absolute_URI == "Must" and Preference == "Absolute-URI":
            print("Pass Space-preceded Host as first header")
        else:
            if Presence_host_header == "Must":
                headers = [" host: waf1.cdnattack.shop\r\n"]
                headers.extend(base_headers)
                absolute_URI = "/style.css"
                if Presence_absolute_URI == "Must":
                    absolute_URI = "http://waf3.cdnattack.shop/style.css"
                recv_data1 = send_request(IP_and_port, absolute_URI, headers)
                recv_status1 = recv_data1.splitlines()[0].split(" ")[1]
                if recv_status1 == "200":
                    Space_preceded_host_as_first_header = "Recognize"
                    print("Space-preceded Host as first header: Recognize")
                elif recv_status1 == "400":
                    headers = [" host: waf1.cdnattack.shop\r\n",
                            "host: waf2.cdnattack.shop\r\n"]
                    recv_data2 = send_request(IP_and_port, absolute_URI, headers)
                    recv_status2 = recv_data2.splitlines()[0].split(" ")[1]
                    if recv_status2 == "400":
                        Space_preceded_host_as_first_header = "Reject"
                        print("Space-preceded Host as first header: Reject")
                    elif recv_status2 == "200":
                        Space_preceded_host_as_first_header = "Not recognize"
                        print("Space-preceded Host as first header: Not recognize")
                    else:
                        print("Error: Space-preceded Host as first header: Wrong status code")
                else:
                    print("Error: Space-preceded Host as first header: Wrong status code")
            else:
                headers = [" host: waf1.cdnattack.shop\r\n"]
                headers.extend(base_headers)
                recv_data1 = send_request(IP_and_port, "http://waf2.cdnattack.shop/style.css", headers)
                recv_status1 = recv_data1.splitlines()[0].split(" ")[1]
                if recv_status1 == "400":
                    Space_preceded_host_as_first_header = "Reject"
                    print("Space-preceded Host as first header: Reject")
                elif recv_status1 == "200":
                    recv_body1 = json.loads(recv_data1.splitlines()[-3])
                    if recv_body1["host"] == "waf1.cdnattack.shop":
                        Space_preceded_host_as_first_header = "Recognize"
                        print("Space-preceded Host as first header: Recognize")
                    elif recv_body1["host"] == "waf2.cdnattack.shop":
                        Space_preceded_host_as_first_header = "Not recognize"
                        print("Space-preceded Host as first header: Not recognize")
                    else:
                        print("Error: Space-preceded Host as first header: Unknown host")
                else:
                    print("Error: Space-preceded Host as first header: Wrong status code")

        # step6: Other space-preceded Host header
        if Consistency == "Must":
            headers = ["FH: firstheader\r\n",
                    " host: waf1.cdnattack.shop\r\n"]
            headers.extend(base_headers)
            recv_data1 = send_request(IP_and_port, "http://waf1.cdnattack.shop/style.css", headers)
            recv_status1 = recv_data1.splitlines()[0].split(" ")[1]
            if recv_status1 == "200":
                Other_space_preceded_host_header = "Recognize"
                print("Other space-preceded Host header: Recognize")
            elif recv_status1 == "400":
                headers = ["host: waf2.cdnattack.shop\r\n",
                        " host: waf1.cdnattack.shop\r\n"]
                headers.extend(base_headers)
                recv_data2 = send_request(IP_and_port, "http://waf2.cdnattack.shop/style.css", headers)
                recv_status2 = recv_data2.splitlines()[0].split(" ")[1]
                if recv_status2 == "200":
                    Other_space_preceded_host_header = "Not recognize"
                    print("Other space-preceded Host header: Not recognize")
                elif recv_status2 == "400":
                    Other_space_preceded_host_header = "Line folding or Reject"
                    print("Other space-preceded Host header: Line folding or Reject")
                else:
                    print("Error: Other space-preceded Host header: Wrong status code")
            else:
                print("Error: Other space-preceded Host header: Wrong status code")
        elif Presence_absolute_URI == "Must" and Preference == "Absolute-URI":
            print("Pass Other space-preceded Host header")
        else:
            if Presence_host_header == "Must":
                headers = ["FH: firstheader\r\n",
                        " host: waf1.cdnattack.shop\r\n"]
                headers.extend(base_headers)
                absolute_URI = "/style.css"
                if Presence_absolute_URI == "Must":
                    absolute_URI = "http://waf3.cdnattack.shop/style.css"
                recv_data1 = send_request(IP_and_port, absolute_URI, headers)
                recv_status1 = recv_data1.splitlines()[0].split(" ")[1]
                if recv_status1 == "200":
                    Other_space_preceded_host_header = "Recognize"
                    print("Other space-preceded Host header: Recognize")
                elif recv_status1 == "400":
                    headers = ["host: waf1.cdnattack.shop\r\n",
                            " host: waf2.cdnattack.shop\r\n"]
                    headers.extend(headers)
                    recv_data2 = send_request(IP_and_port, absolute_URI, headers)
                    recv_status2 = recv_data2.splitlines()[0].split(" ")[1]
                    if recv_status2 == "400":
                        Other_space_preceded_host_header = "Line folding or Reject"
                        print("Other space-preceded Host header: Line folding or Reject")
                    elif recv_status2 == "200":
                        recv_body2 = json.loads(recv_data2.splitlines()[-3])
                        if recv_body2["host"] == "waf1.cdnattack.shop":
                            Other_space_preceded_host_header = "Not recognize"
                            print("Other space-preceded Host header: Not recognize")
                        else:
                            print("Error: Other space-preceded Host header: Unknown host")
                    else:
                        print("Error: Other space-preceded Host header: Wrong status code")
                else:
                    print("Error: Other space-preceded Host header: Wrong status code")
            else:
                headers = ["FH: firstheader\r\n",
                        " host: waf1.cdnattack.shop\r\n"]
                headers.extend(base_headers)
                recv_data1 = send_request(IP_and_port, "http://waf2.cdnattack.shop/style.css", headers)
                recv_status1 = recv_data1.splitlines()[0].split(" ")[1]
                if recv_status1 == "400":
                    Other_space_preceded_host_header = "Line folding or Reject"
                    print("Other space-preceded Host header: Line folding or Reject")
                elif recv_status1 == "200":
                    recv_body1 = json.loads(recv_data1.splitlines()[-3])
                    if recv_body1["host"] == "waf1.cdnattack.shop":
                        Other_space_preceded_host_header = "Recognize"
                        print("Other space-preceded Host header: Recognize")
                    elif recv_body1["host"] == "waf2.cdnattack.shop":
                        headers = ["host: waf1.cdnattack.shop\r\n",
                                " host: waf2.cdnattack.shop\r\n"]
                        headers.extend(base_headers)
                        absolute_URI = "/style.css"
                        if Presence_absolute_URI == "Must":
                            absolute_URI = "http://waf3.cdnattack.shop/style.css"
                        recv_data2 = send_request(IP_and_port, absolute_URI, headers)
                        recv_body2 = json.loads(recv_data2.splitlines()[-3])
                        if recv_body2["host"] == "waf1.cdnattack.shop":
                            Other_space_preceded_host_header = "Not recognize"
                            print("Other space-preceded Host header: Not recognize")
                        else:
                            print("Error: Other space-preceded Host header: Unknown host")
                    else:
                        print("Error: Other space-preceded Host header: Unknown host")
                else:
                    print("Error: Other space-preceded Host header: Wrong status code")

        # step7: Space-succeeded Host header
        if Consistency == "Must":
            headers = ["host: waf1.cdnattack.shop \r\n"]
            headers.extend(base_headers)
            recv_data1 = send_request(IP_and_port, "http://waf1.cdnattack.shop/style.css", headers)
            recv_status1 = recv_data1.splitlines()[0].split(" ")[1]
            if recv_status1 == "200":
                Space_succeeded_host_header = "Recognize"
                print("Space-succeeded Host header: Recognize")
            elif recv_status1 == "400":
                headers = ["host: waf1.cdnattack.shop \r\n",
                        "host: waf2.cdnattack.shop\r\n"]
                headers.extend(base_headers)
                recv_data2 = send_request(IP_and_port, "http://waf2.cdnattack.shop/style.css", headers)
                recv_status2 = recv_data2.splitlines()[0].split(" ")[1]
                if recv_status2 == "200":
                    Space_succeeded_host_header = "Not recognize"
                    print("Space-succeeded Host header: Not recognize")
                elif recv_status2 == "400":
                    Space_succeeded_host_header = "Reject"
                    print("Space-succeeded Host header: Reject")
                else:
                    print("Error: Space-succeeded Host header: Wrong status code")
            else:
                print("Error: Space-succeeded Host header: Wrong status code")
        elif Presence_absolute_URI == "Must" and Preference == "Absolute-URI":
            print("Pass Space-succeeded Host header")
        else:
            if Presence_host_header == "Must":
                headers = ["host: waf1.cdnattack.shop \r\n"]
                headers.extend(base_headers)
                absolute_URI = "/style.css"
                if Presence_absolute_URI == "Must":
                    absolute_URI = "http://waf3.cdnattack.shop/style.css"
                recv_data1 = send_request(IP_and_port, absolute_URI, headers)
                recv_status1 = recv_data1.splitlines()[0].split(" ")[1]
                if recv_status1 == "200":
                    Space_succeeded_host_header = "Recognize"
                    print("Space-succeeded Host header: Recognize")
                elif recv_status1 == "400":
                    headers = ["host: waf1.cdnattack.shop \r\n",
                            "host: waf2.cdnattack.shop\r\n"]
                    recv_data2 = send_request(IP_and_port, absolute_URI, headers)
                    recv_status2 = recv_data2.splitlines()[0].split(" ")[1]
                    if recv_status2 == "400":
                        Space_succeeded_host_header = "Reject"
                        print("Space-succeeded Host header: Reject")
                    elif recv_status2 == "200":
                        Space_succeeded_host_header = "Not recognize"
                        print("Space-succeeded Host header: Not recognize")
                    else:
                        print("Error: Space-succeeded Host header: Wrong status code")
                else:
                    print("Error: Space-succeeded Host header: Wrong status code")
            else:
                headers = ["host: waf1.cdnattack.shop \r\n"]
                headers.extend(base_headers)
                recv_data1 = send_request(IP_and_port, "http://waf2.cdnattack.shop/style.css", headers)
                recv_status1 = recv_data1.splitlines()[0].split(" ")[1]
                if recv_status1 == "400":
                    Space_succeeded_host_header = "Reject"
                    print("Space-succeeded Host header: Reject")
                elif recv_status1 == "200":
                    recv_body1 = json.loads(recv_data1.splitlines()[-3])
                    if recv_body1["host"] == "waf1.cdnattack.shop":
                        Space_succeeded_host_header = "Recognize"
                        print("Space-succeeded Host header: Recognize")
                    elif recv_body1["host"] == "waf2.cdnattack.shop":
                        Space_succeeded_host_header = "Not recognize"
                        print("Space-succeeded Host header: Not recognize")
                    else:
                        print("Error: Space-succeeded Host header: Unknown host")
                else:
                    print("Error: Space-succeeded Host header: Wrong status code")

        # step8: Schema of absolute-URI
        if Consistency == "Must":
            headers = ["host: waf1.cdnattack.shop\r\n"]
            headers.extend(base_headers)
            recv_data1 = send_request(IP_and_port, "nonhttp://waf1.cdnattack.shop/style.css", headers)
            recv_status1 = recv_data1.splitlines()[0].split(" ")[1]
            if recv_status1 == "200":
                recv_data2 = send_request(IP_and_port, "nonhttp://waf2.cdnattack.shop/style.css", headers)
                recv_status2 = recv_data2.splitlines()[0].split(" ")[1]
                if recv_status2 == "400":
                    Schema_of_absolute_URI = "Recognize any"
                    print("Schema of absolute-URI: Recognize any")
                elif recv_status2 == "200":
                    recv_data3 = send_request(IP_and_port, "https://waf2.cdnattack.shop/style.css", headers)
                    recv_status3 = recv_data3.splitlines()[0].split(" ")[1]
                    if recv_status3 == "400":
                        Schema_of_absolute_URI = "Recognize HTTP/S, not others"
                        print("Schema of absolute-URI: Recognize HTTP/S, not others")
                    elif recv_status3 == "200":
                        recv_data4 = send_request(IP_and_port, "http://waf2.cdnattack.shop/style.css", headers)
                        recv_status4 = recv_data4.splitlines()[0].split(" ")[1]
                        if recv_status4 == "400":
                            print("Schema of absolute-URI: Recognize HTTP, not others")
                        else:
                            print("Error: Schema of absolute-URI: Wrong status code")
                    else:
                        print("Error: Schema of absolute-URI: Wrong status code")
                else:
                    print("Error: Schema of absolute-URI: Wrong status code")
            elif recv_status1 == "400":
                if Presence_absolute_URI == "Optional":
                    recv_data2 = send_request(IP_and_port, "https://waf1.cdnattack.shop/style.css", headers)
                    recv_status2 = recv_data2.splitlines()[0].split(" ")[1]
                    if recv_status2 == "200":
                        Schema_of_absolute_URI = "Recognize HTTP/S, reject others"
                        print("Schema of absolute-URI: Recognize HTTP/S, reject others")
                    elif recv_status2 == "400":
                        Schema_of_absolute_URI = "Recognize HTTP, reject others"
                        print("Schema of absolute-URI: Recognize HTTP, reject others")
                    else:
                        print("Error: Schema of absolute-URI: Wrong status code")
                else:
                    recv_data2 = send_request(IP_and_port, "https://waf1.cdnattack.shop/style.css", headers)
                    recv_status2 = recv_data2.splitlines()[0].split(" ")[1]
                    if recv_status2 == "200":
                        Schema_of_absolute_URI = "Recognize HTTP/S"
                        print("Schema of absolute-URI: Recognize HTTP/S")
                    elif recv_status2 == "400":
                        Schema_of_absolute_URI = "Recognize HTTP"
                        print("Schema of absolute-URI: Recognize HTTP")
                    else:
                        print("Error: Schema of absolute-URI: Wrong status code")
            else:
                print("Error: Schema of absolute-URI: Wrong status code")
        elif Presence_host_header == "Must" and Preference == "Host header":
            print("Pass Schema of absolute-URI")
        elif Presence_host_header == "Must" and Preference == "Absolute-URI":
            headers = ["host: waf2.cdnattack.shop\r\n"]
            headers.extend(base_headers)
            recv_data1 = send_request(IP_and_port, "https://waf1.cdnattack.shop/style.css", headers)
            recv_status1 = recv_data1.splitlines()[0].split(" ")[1]
            if recv_status1 == "400":
                Schema_of_absolute_URI = "Recognize HTTP, reject others"
            elif recv_status1 == "200":
                recv_body1 = json.loads(recv_data1.splitlines()[-3])
                if recv_body1["host"] == "waf2.cdnattack.shop":
                    Schema_of_absolute_URI = "Recognize HTTP/S, reject others"
                elif recv_body1["host"] == "waf1.cdnattack.shop":
                    recv_data2 = send_request(IP_and_port, "nonhttp://waf1.cdnattack.shop/style.css", headers)
                    recv_status2 = recv_data2.splitlines()[0].split(" ")[1]
                    if recv_status2 == "400":
                        Schema_of_absolute_URI = "Recognize HTTP/S, not others"
                    elif recv_status2 == "200":
                        recv_body2 = json.loads(recv_data2.splitlines()[-3])
                        if recv_body2["host"] == "waf2.cdnattack.shop":
                            Schema_of_absolute_URI = "Recognize HTTP/S, not others"
                        elif recv_body2["host"] == "waf1.cdnattack.shop":
                            Schema_of_absolute_URI = "Recognize any"
                        else:
                            print("Error: Schema of absolute-URI: Unknown host")
                    else:
                        print("Error: Schema of absolute-URI: Wrong status code")
                else:
                    print("Error: Schema of absolute-URI: Unknown host")
            else:
                print("Error: Schema of absolute-URI: Wrong status code")
        else:
            recv_data1 = send_request(IP_and_port, "https://waf1.cdnattack.shop/style.css", base_headers)
            recv_status1 = recv_data1.splitlines()[0].split(" ")[1]
            if recv_status1 == "400":
                headers = ["host: waf1.cdnattack.shop\r\n"]
                headers.extend(base_headers)
                recv_data2 = send_request(IP_and_port, "https://waf1.cdnattack.shop/style.css", headers)
                recv_status2 = recv_data2.splitlines()[0].split(" ")[1]
                if recv_status2 == "200":
                    Schema_of_absolute_URI = "Recognize HTTP, not others"
                    print("Schema of absolute-URI: Recognize HTTP, not others")
                elif recv_status2 == "400":
                    Schema_of_absolute_URI = "Recognize HTTP, reject others"
                    print("Schema of absolute-URI: Recognize HTTP, reject others")
                else:
                    print("Error: Schema of absolute-URI: Wrong status code")
            elif recv_status1 == "200":
                recv_data2 = send_request(IP_and_port, "nonhttp://waf1.cdnattack.shop/style.css", base_headers)
                recv_status2 = recv_data2.splitlines()[0].split(" ")[1]
                if recv_status2 == "200":
                    Schema_of_absolute_URI = "Recognize any"
                    print("Schema of absolute-URI: Recognize any")
                elif recv_status2 == "400":
                    headers = ["host: waf1.cdnattack.shop\r\n"]
                    headers.extend(base_headers)
                    recv_data3 = send_request(IP_and_port, "nonhttp://waf1.cdnattack.shop/style.css", headers)
                    recv_status3 = recv_data3.splitlines()[0].solit(" ")[1]
                    if recv_status3 == "200":
                        Schema_of_absolute_URI = "Recognize HTTP/S, not others"
                        print("Schema of absolute-URI: Recognize HTTP/S, not others")
                    elif recv_status3 == "400":
                        Schema_of_absolute_URI = "Recognize HTTP/S, reject others"
                        print("Schema of absolut-URI: Recognize HTTP/S, reject others")
                    else:
                        print("Error: Schema of absolute-URI: Wrong status code")
                else:
                    print("Error: Schema of absolute-URI: Wrong status code")
            else:
                print("Error: Schema of absolute-URI: Wrong status code")

    agency_behaviour = Agency_Behaviour()
    agency_behaviour.Ambiguous = Ambiguous
    agency_behaviour.Cache_exist = Cache_exist
    agency_behaviour.Consistency = Consistency
    agency_behaviour.Preference = Preference
    agency_behaviour.Multiple_host_headers = Multiple_host_headers
    agency_behaviour.Space_preceded_host_as_first_header = Space_preceded_host_as_first_header
    agency_behaviour.Other_space_preceded_host_header = Other_space_preceded_host_header
    agency_behaviour.Space_succeeded_host_header = Space_succeeded_host_header
    agency_behaviour.Schema_of_absolute_URI = Schema_of_absolute_URI

    return agency_behaviour

if __name__ == "__main__":
    with open('CDNs.csv', 'a') as file:
        writer = csv.writer(file)
        writer.writerow(["IP",
                        "Cache_exist",
                        "Consistency",
                        "Preference",
                        "Multiple_host_headers",
                        "Space_preceded_host_as_first_header",
                        "Other_space_preceded_host_header",
                        "Space_succeeded_host_header",
                        "Schema_of_absolute_URI"])
    with open("CloudFlare_ipv4_2022-09-05.txt", "r", encoding = "utf-8") as src:
        lines = src.readlines()
        CF_low = 0
        CF_high = len(lines)
        for i in range(CF_low, CF_high):
            IP = lines[i]
            print("Testing number " + str(i) + " IP " + IP)
            try:
                agency_behaviour = cloudfare_test((IP, 80))            
                with open("CDNs.csv", "a") as file:
                    writer = csv.writer(file)
                    writer.writerow([IP, 
                                     agency_behaviour.Cache_exist,
                                     agency_behaviour.Consistency,
                                     agency_behaviour.Preference,
                                     agency_behaviour.Multiple_host_headers,
                                     agency_behaviour.Space_preceded_host_as_first_header,
                                     agency_behaviour.Other_space_preceded_host_header,
                                     agency_behaviour.Space_succeeded_host_header,
                                     agency_behaviour.Schema_of_absolute_URI])
                print("Finished testing number " + str(i) + " IP " + IP)
            except ConnectionResetError:
                with open("CDNs.csv", "a") as file:
                    writer = csv.writer(file)
                    writer.writerow([IP,
                                     "",
                                     "",
                                     "",
                                     "",
                                     "",
                                     "",
                                     "",
                                     ""])
                print("Failed testing number " + str(i) + " IP " + IP)

