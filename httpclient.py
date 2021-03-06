#!/usr/bin/env python3
# coding: utf-8
#
# Copyright 2019 Alex Li
#
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

import sys
import socket
import re
# you may use urllib to encode data appropriately
import urllib.parse

def help():
    print("httpclient.py [GET/POST] [URL]\n")

class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body

class HTTPClient(object):
    #def get_host_port(self,url):

    def connect(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        return None

    def get_code(self, data):
        try:
            newline = data.index("\r\n")
            status = data[:newline].split()
            return int(status[1])
        except:
            return None

    def get_headers(self,data):
        try:
            section = data.split("\r\n\r\n")
            return section[0]
        except:
            return None

    def get_body(self, data):
        try:
            section = data.split("\r\n\r\n")
            return section[1]
        except:
            return None

    def sendall(self, data):
        self.socket.sendall(data.encode('utf-8'))

    def close(self):
        self.socket.close()

    # read everything from the socket
    def recvall(self, sock):
        # try:
        buffer = bytearray()
        done = False
        while not done:
            # sock.settimeout(1.0)
            part = sock.recv(1024)
            if (part):
                buffer.extend(part)
            else:
                done = not part
        return buffer.decode("utf-8")
        # except socket.timeout:
            # return buffer.decode("utf-8")

    def GET(self, url, args=None):
        url = urllib.parse.urlparse(url)
        host, port = url.hostname, url.port

        # create request
        query = ""
        if args:
            query = "?" + urllib.parse.urlencode(args)
        mediaTypes = "*/*"
        headers = [
            "GET" + " " + "/" + url.path + query + " HTTP/1.1",
            "Host: " + host,
            "Accept: " + mediaTypes,
            "Connection: close"
        ]
        request = "\r\n".join(headers) + "\r\n\r\n"

        # send request
        if not port:
            if url.scheme == 'http':
                port = 80
            elif url.scheme == 'https':
                port = 443
            else:
                port = 8080
        self.connect(host,port)
        self.sendall(request)

        # get response
        data = self.recvall(self.socket)
        self.close()
        code = self.get_code(data)
        headers = self.get_headers(data)
        body = self.get_body(data)
        print(headers + "\n\n" + body)
        print("---------------------\n")
        return HTTPResponse(code, body)

    def POST(self, url, args=None):
        url = urllib.parse.urlparse(url)
        host, port = url.hostname, url.port

        # create request
        content=""
        if args:
            content = urllib.parse.urlencode(args)
        mediaTypes = "*/*"
        contentType = "application/x-www-form-urlencoded"
        headers = [
            "POST" + " " + "/" + url.path + " HTTP/1.1",
            "Host: " + host,
            "Accept: " + mediaTypes,
            "Content-Type: " + contentType,
            "Content-Length: " + str(len(content)),
        ]
        headers = "\r\n".join(headers) + "\r\n\r\n"
        request = headers + content + "\r\n\r\n"

        # send request
        if not port:
            if url.scheme == 'http':
                port = 80
            elif url.scheme == 'https':
                port = 443
            else:
                port = 8080
        self.connect(host,port)
        self.sendall(request)
        data = self.recvall(self.socket)
        self.close()
        code = self.get_code(data)
        headers = self.get_headers(data)
        body = self.get_body(data)
        print(headers + "\n\n" + body)
        print("---------------------\n")
        return HTTPResponse(code, body)

    def command(self, url, command="GET", args=None):
        if (command == "POST"):
            return self.POST( url, args )
        else:
            return self.GET( url, args )

if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"
    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)
    elif (len(sys.argv) == 3):
        print(client.command( sys.argv[2], sys.argv[1] ))
    else:
        print(client.command( sys.argv[1] ))
