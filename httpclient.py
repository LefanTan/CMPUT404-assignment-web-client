#!/usr/bin/env python3
# coding: utf-8
# Copyright 2016 Abram Hindle, https://github.com/tywtyw2002, and https://github.com/treedust
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Do not use urllib's HTTP GET and POST mechanisms.
# Write your own HTTP GET and POST
# The point is to understand what you have to send and get experience with it

from email.policy import HTTP
import sys
import socket
import re
# you may use urllib to encode data appropriately
from urllib.parse import urlencode, urlparse

def help():
    print("httpclient.py [GET/POST] [URL]\n")

class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body

    def __str__(self) -> str:
        return f"{self.code}\r\n{self.body}"

class HTTPClient(object):
    def prep_url(self, url):
        if(not url.startswith("http")):
            url = "//" + url
        return url

    def connect(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((socket.gethostbyname(host), port))
        return None

    def get_code(self, data):
        if not data:
            return
            
        first_line = data.split("\n")[0]
        code = first_line.split()[1]
        return int(code)

    def get_headers(self,data):
        if not data:
            return

        split = data.split("\r\n\r\n")
        if(len(split) > 0):
            return split[0] 
        return split

    def get_body(self, data):
        if not data:
            return

        split = data.split("\r\n\r\n")
        if(len(split) > 1):
            return split[1] 
        return split
    
    def sendall(self, data):
        try:
            self.socket.sendall(data.encode('utf-8'))
        except Exception as e:
            print("Send payload fail:", e)
        
    def close(self):
        self.socket.close()

    # read everything from the socket
    def recvall(self, sock):
        buffer = bytearray()
        done = False
        try:
            while not done:
                part = sock.recv(1024)
                if (part):
                    buffer.extend(part)
                else:
                    done = not part
        except:
            print("Error receiving payload")
        return buffer.decode('utf-8')

    def GET(self, url, args=None):
        code = 500
        body = ""
        
        url = self.prep_url(url)
        path = urlparse(url).path or "/"
        host = urlparse(url).hostname
        port = urlparse(url).port or 80

        self.connect(host, port)
        
        request_header = f"GET {path} HTTP/1.1\r\nHost: {host}\r\nUser-Agent: curl/7.64.0\r\nAccept: */*\r\nConnection: keep-alive\r\n\r\n"
        self.sendall(request_header)

        self.socket.shutdown(socket.SHUT_WR)
        response = self.recvall(self.socket)
        self.close()

        body = self.get_body(response)
        code = self.get_code(response)

        return HTTPResponse(code, body)

    def POST(self, url, args=None):
        code = 500
        body = ""

        url = self.prep_url(url)
        path = urlparse(url).path or "/"
        host = urlparse(url).hostname
        port = urlparse(url).port or 80

        parsed_args = ""
        if args:
            parsed_args = urlencode(args)

        self.connect(host, port)
        request_header = f"""POST {path} HTTP/1.1\r\nHost: {host}\r\nUser-Agent: Lefan's Web Client\r\nContent-Type: application/x-www-form-urlencoded\r\nContent-Length: {len(parsed_args)}\r\n\r\n"""
        self.sendall(request_header)
        self.sendall(parsed_args)
        
        self.socket.shutdown(socket.SHUT_WR)
        response = self.recvall(self.socket)
        self.close()

        body = self.get_body(response)
        code = self.get_code(response)

        return HTTPResponse(code, body)

    def command(self, url, command="GET", args=None):
        if (command == "POST"):
            return self.POST( url, args )
        else:
            return self.GET( url, args )
    
if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"

    print(client.POST("http://asdf.com", {"as": "LEfan", "a": "lma\ro"}))
    # if (len(sys.argv) <= 1):
    #     help()
    #     sys.exit(1)
    # elif (len(sys.argv) == 3):
    #     print(client.command( sys.argv[2], sys.argv[1] ))
    # else:
    #     print(client.command( sys.argv[1] ))
