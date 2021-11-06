#!/usr/bin/env python

import os
import os.path
import sys
import json
import socket

from pymavlink import mavutil

from MAVProxy.modules.lib import mp_module
from MAVProxy.modules.lib import mp_util
from MAVProxy.modules.lib import mp_settings

TCP_IP = '192.168.15.50'
TCP_PORT = 23

class HOE:
    HOE_IN = 1
    HOE_OUT = 2
    HOE_INIT = 3
    HOE_FINISH = 4
    HOE_ERROR = 5

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
              ('stepshoe', int, 400),
              ('hoeoutdistance', float, 0.1),    # hoeoutdistance m
              ('hoeindistance', float, 0.1),     # hoeindistance m
              ('hoefirstdistance', float, 1.0),  # hoefirstdistance m
              ('hoemaxdistance', float, 1.25),   # hoemaxdistance m
              ('mode', int, 2),                  # mode: 1=seed, 2=seed and collect data, 3=chop weeds
              ('seedfile', str, '/home/mirko/data/webaro/seed.txt'),
          ])
        self.add_command('ethtrigger', self.cmd_ethtrigger, "ethtrigger module", ['status','set','seed'])
        
        self.simstate = 0
        self.hoestatus = HOE.HOE_INIT
        self.seed_index = 1
        self.seed_position = None
        self.seeds = {}
        self.seeds['seeds'] = []

    def usage(self):
        '''show help on command line options'''
        return "Usage: ethtrigger <status|set verbose|set steps|set stepshoe|set hoeoutdistance|set hoeindistance|set hoefirstdistance|set hoemaxdistance|set mode|set seedfile>"

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

    def send_seeder(self, msg):
        # send only in none SITL
        if self.simstate == 0:
            MESSAGE = msg
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

    def move_hoe(self):
        message = "yt" + str(self.ethtrigger_settings.stepshoe) + "\r"
        self.send_seeder(message)

    def seed_command(self, cmd):
        if cmd[0] == 'clear':
            self.seeds = {}
        if cmd[0] == 'read':
            with open(self.ethtrigger_settings.seedfile) as json_file:
                self.seeds = json.load(json_file)
                self.seed_position = self.get_position(self.seed_index)
        if cmd[0] == 'write':
            with open(self.ethtrigger_settings.seedfile, 'w') as json_file:
                json.dump(self.seeds, json_file)
        if cmd[0] == 'dump':
            print(json.dumps(self.seeds, indent=4))
        if cmd[0] == 'reset':
            self.hoestatus = HOE.HOE_INIT
            self.seed_index = 1

        print("seed: " + cmd[0])

    def get_position(self, index):
        for dict in self.seeds['seeds']:
            if dict['index'] == index:
                return dict
        return None

    def mavlink_packet(self, m):
        '''handle mavlink packets'''
        if m.get_type() == "COMMAND_LONG":
            print ("Get Long")
            if m.command == mavutil.mavlink.MAV_CMD_DO_DIGICAM_CONFIGURE:
                print ("Got Message Digicam_configure")
            elif m.command == mavutil.mavlink.MAV_CMD_DO_DIGICAM_CONTROL:
                print ("Got Message Digicam_control")

        if m.get_type() == 'SIMSTATE':
            self.simstate = 1
        
        if self.ethtrigger_settings.mode == 3:
            if m.get_type() == 'AHRS2':
                distance = mp_util.gps_distance(self.seed_position['lat'], self.seed_position['lng'], m.lat * 1e-7, m.lng * 1e-7)
                if self.hoestatus == HOE.HOE_INIT:
                    if distance < self.ethtrigger_settings.hoefirstdistance:
                        self.hoestatus = HOE.HOE_OUT
                        print("hoeinit: " + str(distance) + " m")
                        self.move_hoe()
                        self.hoestatus = HOE.HOE_OUT
                elif self.hoestatus == HOE.HOE_IN:
                    if distance > self.ethtrigger_settings.hoemaxdistance:
                        self.hoestatus = HOE.HOE_ERROR
                    elif distance > self.ethtrigger_settings.hoeoutdistance:
                        if self.get_position(self.seed_index + 1) != None:
                            self.hoestatus = HOE.HOE_OUT
                            self.seed_index += 1
                            self.seed_position = self.get_position(self.seed_index)
                            print("hoeout: " + str(distance) + " m")
                            self.move_hoe()
                        else:
                            self.hoestatus = HOE.HOE_FINISH
                            print("hoefinish: " + str(distance) + " m")
                elif self.hoestatus == HOE.HOE_OUT:
                    if distance > self.ethtrigger_settings.hoemaxdistance:
                        self.hoestatus = HOE.HOE_ERROR
                        print("ERROR hoein: " + str(distance) + " m")
                    elif distance < self.ethtrigger_settings.hoeindistance:
                        self.hoestatus = HOE.HOE_IN
                        print("hoein: " + str(distance) + " m")
                        self.move_hoe()

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

                # send only in none SITL
                if self.simstate == 0:
                    message = "xt" + str(self.ethtrigger_settings.steps) + "\r"
                    self.send_seeder(message)

            if self.ethtrigger_settings.verbose:
                print("CAMERA_FEEDBACK")

def init(mpstate):
    '''initialise module'''
    return ethtrigger(mpstate)
