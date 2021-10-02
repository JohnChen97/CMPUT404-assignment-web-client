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

type_text = ['css', 'csv', 'html', 'javascript', 'plain', 'xml']
type_application = ['x-www-form-urlencoded', 'octet-stream']


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
        print(data)
        code = re.findall('(?:HTTP\/\d\.\d\s)(\d{3})(?:.*)', data)
        return int(code[0])

    def get_headers(self, data):
        #header = re.findall('\\r\\n\\r\\n', data)
        header = data[0:data.find('\r\n\r\n')]
        return header[0]

    def get_body(self, data):
        #body = re.findall('(?:\\r\\n\\r\\n)(.*)', data)
        body = data[data.find('\r\n\r\n'):]
        return body

    def sendall(self, data):
        self.socket.sendall(data.encode('utf-8'))

    def close(self):
        self.socket.close()

    # read everything from the socket
    def recvall(self, sock):
        try:
            buffer = bytearray()
            done = False
            while not done:
                part = sock.recv(1024)
                if (part):
                    buffer.extend(part)
                else:
                    done = not part
            return buffer.decode(encoding='UTF-8', errors='ignore')
        except UnicodeDecodeError:
            print('UnicodeDecodeError')

    def GET(self, url, args=None):
        code = 500
        body = ""
        url_dict = self.interprate_url(url)
        try:

            ip_address = socket.gethostbyname(url_dict['host'])
            if 'port' in url_dict.keys():
                self.connect(ip_address, int(url_dict['port']))
            else:
                self.connect(ip_address, 80)

            if 'path' in url_dict.keys():

                Get_line_1 = 'GET ' + '/' + str(
                    url_dict['path']) + ' HTTP/1.1 \r\n'

                #self.socket.sendall(('GET ' + '/' + str(url_dict['path']) +
                #' HTTP/1.1 \r\n').encode('utf-8'))
                self.socket.sendall(
                    ('GET ' + str(urllib.parse.urlparse(url).path) +
                     ' HTTP/1.1 \r\n').encode('utf-8'))

            else:

                self.socket.sendall(b'GET / HTTP/1.1 \r\n')
            #self.socket.sendall(
            #('Host: ' + url_dict['host'] + '\r\n').encode('utf-8'))
            self.socket.sendall(
                ('Host: ' + str(urllib.parse.urlparse(url).hostname) +
                 '\r\n').encode('utf-8'))
            Get_line_2 = 'Host: ' + url_dict['host'] + '\r\n'

            self.socket.sendall(b'Connection: close\r\n')
            self.socket.sendall(
                b'Accept: application/x-www-form-urlencoded, text/html\r\n')
            self.socket.sendall(b'\r\n')
            received_data = self.recvall(self.socket)

            code = self.get_code(received_data)
            body = self.get_body(received_data)
        except ConnectionRefusedError:
            #self.socket.send("HTTP/1.1 404 Not Found \r\n".encode('utf-8'))
            http_response = HTTPResponse(code=404, body="")
            return http_response
        return HTTPResponse(code=code, body=body)

    def POST(self, url, args=None):
        code = 200
        body = ""
        url_dict = self.interprate_url(url)
        content_type = "application/x-www-form-urlencoded"

        #host, file_location = self.interprate_post_address(url_dict['host'] +
        #url_dict['path'])
        '''
        if self.interprate_file_type(args):
            if self.interprate_file_type(args) in type_text:
                content_type = "text/" + self.interprate_file_type(args)
        '''

        if type(args) == dict:
            for key, item in args.items():
                body = body + key + '=' + item + '&'
            body = body[0:-1]

        try:

            #self.connect(url_dict['host'], int(url_dict['port']))
            ip_address = socket.gethostbyname(url_dict['host'])
            if 'port' in url_dict.keys():
                self.connect(ip_address, int(url_dict['port']))
            else:
                self.connect(url_dict['host'], 80)
            self.socket.sendall(('POST ' + '/' + url_dict['path'] +
                                 ' HTTP/1.1 \r\n').encode('utf-8'))
            self.socket.sendall(
                ('Host: ' + url_dict['host'] + '\r\n').encode('utf-8'))
            self.socket.sendall(
                ('Content-Type: ' + content_type + '\r\n').encode('utf-8'))
            self.socket.sendall(
                ('Content-Length: ' + str(len(body)) + '\r\n').encode('utf-8'))
            self.socket.sendall(b'Connection: close\r\n')
            self.socket.sendall(b'\r\n')
            self.socket.sendall(body.encode('utf-8'))
            self.socket.sendall(b'\r\n')
            received_data = self.recvall(self.socket)
            code = self.get_code(received_data)
            body = self.get_body(received_data)
            return HTTPResponse(code, body)
        except ConnectionRefusedError:
            #self.socket.send("HTTP/1.1 404 Not Found \r\n".encode('utf-8'))
            http_response = HTTPResponse(code=404, body="")
            return http_response
        return HTTPResponse(code=code, body=body)

    def command(self, url, command="GET", args=None):
        if (command == "POST"):
            return self.POST(url, args)
        else:
            return self.GET(url, args)

    def interprate_url(self, url):
        http_dict = {}
        try:
            if re.search('^http:\/\/.*$', url):
                http_dict['scheme'] = 'http://'
            if re.search('https?:\/\/[\w\.]+:\d+(\/[\w\.]+)?', url):
                http_dict['host'] = re.findall(
                    '(?:https?:\/\/)([\w\.]+)(?::\d+\/[\w\.]+)', url)[0]

                http_dict['port'] = re.findall(
                    '(?:https?:\/\/[\w\.]+:)(\d+)(?:\/[\w\.]+)', url)[0]

            elif re.search('https?:\/\/[\w\.\/\=\+\?]+', url):
                http_dict['host'] = re.findall(
                    '(?:https?:\/\/)([\w\.]+)(?:\/[\w\.]+)?', url)[0]
            if re.search('(?:https?:\/\/[\w\.]+(:\d+)?)(\/).*', url):
                if re.search('(?:https?:\/\/[\w\.]+)(?::\d+)?(?:\/)(.*)',
                             url) != None:
                    http_dict['path'] = re.findall(
                        '(?:https?:\/\/[\w\.]+)(?::\d+)?(?:\/)(.*)', url)[0]
                elif url[-1] == '/':
                    http_dict['host'] = http_dict['host']
            return http_dict
        except KeyError:
            sys.stdout.write('something wrong with the dict\n')

    def interprate_file_type(self, file_name):

        if re.search('\.', file_name):
            if re.search('(?:\w+\.)(\w{3,10})', file_name):
                return re.findall('(?:\w+\.)(\w{3,10})', file_name)[0]
        else:
            return None

    def interprate_post_address(self, address):
        print('The address in POST is: ' + address)
        http_deleted = re.findall('(?:https?:\/\/)(.*)', address)
        location_list = http_deleted[0].split('/')
        host = location_list[0]
        file_location = re.sub(host, '', http_deleted)
        return host, file_location


if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"
    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)
    elif (len(sys.argv) == 3):
        http_result = client.command(sys.argv[2], sys.argv[1])
        print(http_result.code)
        print(http_result.body)

    else:
        print(client.command(sys.argv[1]))
