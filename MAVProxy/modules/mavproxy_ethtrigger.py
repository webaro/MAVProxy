#!/usr/bin/env python

import os
import os.path
import sys
import json
import socket

from MAVProxy.modules.lib import mp_module
from MAVProxy.modules.lib import mp_util
from MAVProxy.modules.lib import mp_settings

TCP_IP = '192.168.15.50'
TCP_PORT = 23

class ethtrigger(mp_module.MPModule):
    def __init__(self, mpstate):
        """Initialise module"""
        super(ethtrigger, self).__init__(mpstate, "ethtrigger", "")

        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.s.settimeout(1)
            self.s.connect((TCP_IP, TCP_PORT))
            self.s.settimeout(None)
        except:
            pass

        self.ethtrigger_settings = mp_settings.MPSettings(
            [ ('verbose', bool, False),
              ('steps', int, 200),
              ('chopdistance', float, 0.1),  # chopdistance m
              ('mode', int, 2),              # mode: 1=seed, 2=seed and collect data, 3=chop weeds
          ])
        self.add_command('ethtrigger', self.cmd_ethtrigger, "ethtrigger module", ['status','set','seed'])
        
        self.simstate = 0
        self.seed_index = 1
        self.seeds = {}
        self.seeds['seeds'] = []

    def usage(self):
        '''show help on command line options'''
        return "Usage: ethtrigger <status|set verbose|set steps>"

    def cmd_ethtrigger(self, args):
        '''control behaviour of the module'''
        if len(args) == 0:
            print(self.usage())
        elif args[0] == "status":
            print(self.status())
        elif args[0] == "set":
            self.ethtrigger_settings.command(args[1:])
        elif args[0] == "seed":
            self.seed_command(args[1:])
        else:
            print(self.usage())

    def status(self):
        '''returns information about module'''
        return("steps: " + str(self.ethtrigger_settings.steps))

    def seed_command(self, cmd):
        if cmd[0] == 'clear':
            self.seeds = {}
        if cmd[0] == 'read':
            with open('/home/mirko/data/webaro/seed.txt') as json_file:
                self.seeds = json.load(json_file)
        if cmd[0] == 'write':
            with open('/home/mirko/data/webaro/seed.txt', 'w') as json_file:
                json.dump(self.seeds, json_file)
        if cmd[0] == 'dump':
            print(json.dumps(self.seeds, indent=4))

        print("seed: " + cmd[0])

    def mavlink_packet(self, m):
        '''handle mavlink packets'''
        if m.get_type() == 'SIMSTATE':
            self.simstate = 1
        
        if self.ethtrigger_settings.mode == 3:
            if m.get_type() == 'AHRS2':
                for dict in self.seeds['seeds']:
                    if dict['index'] == self.seed_index:
                        distance = mp_util.gps_distance(dict['lat'], dict['lng'], m.lat * 1e-7, m.lng * 1e-7)
                        if distance < self.ethtrigger_settings.chopdistance:
                            print("chop: " + str(distance) + " m")
                            self.seed_index += 1


        if m.get_type() == 'CAMERA_FEEDBACK':
            if self.ethtrigger_settings.mode < 3:
                if self.ethtrigger_settings.mode == 2:
                    time = m.time_usec
                    index = m.img_idx
                    lat = m.lat * 1e-7
                    lng = m.lng * 1e-7
                    
                    print("Lat: " + str(lat) + "  Lon: " + str(lng) + "  Index: " + str(index))

                    self.seeds['seeds'].append({
                        'time': time,
                        'index': index,
                        'lat': lat,
                        'lng': lng
                    })
                    #print(json.dumps(self.seeds, indent=4))

                # not send in SITL
                if self.simstate == 0:
                    MESSAGE = "xt" + str(self.ethtrigger_settings.steps) + "\r"
                    try:
                        self.s.send(MESSAGE.encode())
                    except:
                        # recreate the socket and reconnect
                        self.s.close()
                        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        self.s.settimeout(1)
                        self.s.connect((TCP_IP, TCP_PORT))
                        self.s.settimeout(None)
                        self.s.send(MESSAGE.encode())

            if self.ethtrigger_settings.verbose:
                print("CAMERA_FEEDBACK")

def init(mpstate):
    '''initialise module'''
    return ethtrigger(mpstate)
