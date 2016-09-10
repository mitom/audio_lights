#!/usr/bin/python


import fcntl
import re
import os
import errno
import struct
import sys
import SocketServer
from threading import Thread
from time import sleep
import json
import socket
from Queue import *

DEBUGGING = False
current_command_id = 0
original = {}
q = Queue()

def json_encode(data):
    try:
        serialized = json.dumps(data)
    except (TypeError, ValueError), e:
        raise Exception('You can only send JSON-serializable data')

    return serialized + '\r\n'

def translate_rgb(r,g,b):
    return (int(r)*65536)+(int(g)*256)+int(b)

def debug(msg):
    if DEBUGGING:
        print msg

class MusicTCPHandler(SocketServer.BaseRequestHandler):
    def setup(self):
        c_color = None
        c_brightness = None
        command_id = 100
        client_ip = self.client_address[0]


        while True:
            cl = q.get()
            # Gracefully shut it down?
            if cl == False:
                break

            if cl == True:
                if c_color == True:
                    continue

                command_id += 1
                self.request.sendall(json_encode({
                    "id": command_id,
                    "method": "set_scene",
                    "params": ["ct", 3033, 100]
                }))
                c_color = True
                continue

            color = translate_rgb(cl['r'], cl['g'], cl['b'])
            brightness = cl['alpha']
            brightness = int(brightness/255.0*100)
            if c_color is color and c_brightness is brightness: continue

            command_id +=1
            #diff = 1
            #if c_color is not None:
            #    diff = abs(c_color - color)
            #print diff
            #print color, brightness
            self.request.sendall(json_encode({
                "id": command_id,
                "method": "set_rgb",
                "params": [color, "smooth", 20]
            }))
            sleep(0.05)
            self.request.sendall(json_encode({
                "id": command_id,
                "method": "set_bright",
                "params": [brightness, "smooth", 20]
            }))
            c_color = color
            c_brightness = brightness
            sleep(0.2)



class LightController:


    def __init__(self):
        self.running = False
        self.MCAST_GRP = '239.255.255.250'
        self.scan_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        fcntl.fcntl(self.scan_socket, fcntl.F_SETFL, os.O_NONBLOCK)
        self.listen_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.listen_socket.bind(("", 1982))
        fcntl.fcntl(self.listen_socket, fcntl.F_SETFL, os.O_NONBLOCK)
        self.mreq = struct.pack("4sl", socket.inet_aton(self.MCAST_GRP), socket.INADDR_ANY)
        self.listen_socket.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, self.mreq)
        self.detected_bulbs = {}
        self.bulb_idx2ip = {}
        self.thread = None
        self.next_cmd = 0

    def update(self, cl):
        while (not q.empty()):
            q.get()
        q.put(cl)

    def start(self):
        #http://stackoverflow.com/questions/166506/finding-local-ip-addresses-using-pythons-stdlib
        self.local_ip = ([l for l in (
        [ip for ip in socket.gethostbyname_ex(socket.gethostname())[2] if not ip.startswith("127.")][:1], [
            [(s.connect(('8.8.8.8', 53)), s.getsockname()[0], s.close()) for s in
             [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1]]) if l][0][0])
        self.music_server = SocketServer.ThreadingTCPServer((self.local_ip, 0), MusicTCPHandler)

        self.running = True
        self.music_server.allow_reuse_address = True
        mthread = Thread(target=self.music_server.serve_forever)
        mthread.setDaemon(True)
        mthread.start()

        self.thread = Thread(target=self.bulbs_detection_loop)
        self.thread.start()

    def stop(self):
        print "closing"
        self.music_server.socket.close()
        self.music_server.shutdown()
        self.set_default()
        self.running = False
        self.thread.join()

    def set_default(self):
        self.operate_on_bulb(1, 'set_scene', ['ct', 3033, 100])


    def send_search_broadcast(self):
        '''
        multicast search request to all hosts in LAN, do not wait for response
        '''
        multicase_address = (self.MCAST_GRP, 1982)
        debug("send search request")
        msg = "M-SEARCH * HTTP/1.1\r\n"
        msg = msg + "HOST: 239.255.255.250:1982\r\n"
        msg = msg + "MAN: \"ssdp:discover\"\r\n"
        msg = msg + "ST: wifi_bulb"
        self.scan_socket.sendto(msg, multicase_address)

    def bulbs_detection_loop(self):
        '''
        a standalone thread broadcasting search request and listening on all responses
        '''
        debug("bulbs_detection_loop running")
        search_interval = 30000
        read_interval = 100
        time_elapsed = 0

        while self.running:
            if time_elapsed % search_interval == 0:
                self.send_search_broadcast()

            # scanner
            while True:
                try:
                    data = self.scan_socket.recv(2048)
                except socket.error, e:
                    err = e.args[0]
                    if err == errno.EAGAIN or err == errno.EWOULDBLOCK:
                        break
                    else:
                        print e
                        sys.exit(1)
                self.handle_search_response(data)

            # passive listener
            while True:
                try:
                    data, addr = self.listen_socket.recvfrom(2048)
                except socket.error, e:
                    err = e.args[0]
                    if err == errno.EAGAIN or err == errno.EWOULDBLOCK:
                        break
                    else:
                        print e
                        sys.exit(1)
                self.handle_search_response(data)

            time_elapsed += read_interval
            sleep(read_interval / 1000.0)
        self.scan_socket.close()
        self.listen_socket.close()

    def get_param_value(self, data, param):
        '''
        match line of 'param = value'
        '''
        param_re = re.compile(param + ":\s*([ -~]*)")  # match all printable characters
        match = param_re.search(data)
        value = ""
        if match != None:
            value = match.group(1)
            return value


    def handle_search_response(self, data):
        '''
        Parse search response and extract all interested data.
        If new bulb is found, insert it into dictionary of managed bulbs.
        '''
        location_re = re.compile("Location.*yeelight[^0-9]*([0-9]{1,3}(\.[0-9]{1,3}){3}):([0-9]*)")
        match = location_re.search(data)
        if match == None:
            debug("invalid data received: " + data)
            return

        host_ip = match.group(1)
        new = False
        if self.detected_bulbs.has_key(host_ip):
            bulb_id = self.detected_bulbs[host_ip][0]
        else:
            bulb_id = len(self.detected_bulbs) + 1
            new = True
        host_port = match.group(3)
        model = self.get_param_value(data, "model")
        power = self.get_param_value(data, "power")
        bright = self.get_param_value(data, "bright")
        rgb = self.get_param_value(data, "rgb")
        # use two dictionaries to store index->ip and ip->bulb map
        self.detected_bulbs[host_ip] = [bulb_id, model, power, bright, rgb, host_port]
        self.bulb_idx2ip[bulb_id] = host_ip
        if new: self.new_bulb(bulb_id)

    def new_bulb(self, bulb_id):
        print "new bulb"
        self.operate_on_bulb(bulb_id, 'set_music', [1, self.local_ip, self.music_server.socket.getsockname()[1]])

    def display_bulb(self, idx):
        if not self.bulb_idx2ip.has_key(idx):
            print "error: invalid bulb idx"
            return
        bulb_ip = self.bulb_idx2ip[idx]
        model = self.detected_bulbs[bulb_ip][1]
        power = self.detected_bulbs[bulb_ip][2]
        bright = self.detected_bulbs[bulb_ip][3]
        rgb = self.detected_bulbs[bulb_ip][4]
        print str(idx) + ": ip=" \
              + bulb_ip + ",model=" + model \
              + ",power=" + power + ",bright=" \
              + bright + ",rgb=" + rgb


    def display_bulbs(self):
        print str(len(self.detected_bulbs)) + " managed bulbs"
        for i in range(1, len(self.detected_bulbs) + 1):
            self.display_bulb(i)

    def operate_on_bulb(self, idx, method, params):
        '''
        Operate on bulb; no gurantee of success.
        Input data 'params' must be a compiled into one string.
        E.g. params="1"; params="\"smooth\"", params="1,\"smooth\",80"
        '''
        if not self.bulb_idx2ip.has_key(idx):
            print "error: invalid bulb idx"
            return

        bulb_ip = self.bulb_idx2ip[idx]
        port = self.detected_bulbs[bulb_ip][5]
        try:
            self.next_cmd += 1
            tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            print "connect ", bulb_ip, port, "..."
            tcp_socket.connect((bulb_ip, int(port)))
            msg = {
                "id": str(self.next_cmd),
                "method" : method,
                "params": params
            }

            tcp_socket.send(json_encode(msg))
            tcp_socket.close()
        except Exception as e:
            print "Unexpected error:", e




