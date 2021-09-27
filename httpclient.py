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
        re.findall('(?:HTTP\/\d\.\d\s)(\d{3})(?:.*)', data)
        return None

    def get_headers(self, data):
        return None

    def get_body(self, data):
        return None

    def sendall(self, data):
        self.socket.sendall(data.encode('utf-8'))

    def close(self):
        self.socket.close()

    # read everything from the socket
    def recvall(self, sock):
        buffer = bytearray()
        done = False
        while not done:
            part = sock.recv(1024)
            if (part):
                buffer.extend(part)
            else:
                done = not part
        return buffer.decode('utf-8')

    def GET(self, url, args=None):
        code = 500
        body = ""
        url_dict = self.interprate_url(url)
        self.connect(url_dict['host'], int(url_dict['port']))
        self.socket.sendall(b'GET / HTTP/1.1 \r\n')
        self.socket.sendall(
            ('Host: ' + url_dict['host'] + '\r\n').encode('utf-8'))
        self.socket.sendall(b'Connection: close\r\n')
        self.socket.sendall(b'\r\n')
        try:
            received_data = self.recvall(self.socket)
            code = received_data

        return HTTPResponse(code, body)

    def POST(self, url, args=None):
        code = 500
        body = ""
        return HTTPResponse(code, body)

    def command(self, url, command="GET", args=None):
        if (command == "POST"):
            return self.POST(url, args)
        else:
            return self.GET(url, args)

    def interprate_url(self, url):
        http_dict = {}
        if re.search('^http:\/\/.*$', url):
            http_dict['scheme'] = 'http://'
        if re.search('https?:\/\/[\w\.]+:\d+(\/[\w\.]+)?', url):
            http_dict['host'] = re.findall(
                '(?:https?:\/\/)([\w\.]+)(?::\d+(\/[\w\.]+)?)', url)[0][0]
            http_dict['port'] = re.findall(
                '(?:https?:\/\/[\w\.]+:)(\d+)(?:(\/[\w\.]+)?)', url)[0][0]

        if re.search('(?:https?:\/\/[\w\.]+:\d+)(\/).*', url):
            http_dict['path'] = re.findall(
                '(?:https?:\/\/[\w\.]+:\d+\/)([\w\.]+)', url)[0][0]
        return http_dict


if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"
    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)
    elif (len(sys.argv) == 3):
        request_method = sys.argv[1]
        url = sys.argv[2]
        print(client.interprate_url(url))

        http_response = client.command(sys.argv[2], sys.argv[1])
        print(http_response.code)
        print(http_response.body)
        buffer = client.recvall(client.socket)
        print(buffer)
    else:
        print(client.command(sys.argv[1]))
