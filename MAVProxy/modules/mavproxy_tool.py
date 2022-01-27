#!/usr/bin/env python

import os
import os.path
import sys
import json
import socket

import numpy as np
import nvector as nv

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

class tool(mp_module.MPModule):
    def __init__(self, mpstate):
        """Initialise module"""
        super(tool, self).__init__(mpstate, "tool", "")

        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.s.settimeout(1)
            self.s.connect((TCP_IP, TCP_PORT))
            self.s.settimeout(None)
        except:
            pass

        self.tool_settings = mp_settings.MPSettings(
            [ ('verbose', bool, False),
              ('seeder_steps', int, 200),
              ('hoe_steps', int, 400),
              ('hoe_outdistance', float, 0.01),   # hoeoutdistance m
              ('hoe_indistance', float, 0.18),    # hoeindistance m
              ('hoe_firstdistance', float, 2.0),  # hoefirstdistance m
              ('hoe_maxdistance', float, 2.25),   # hoemaxdistance m
              ('mode', int, 2),                  # mode: 0=do nothing, 1=seed, 2=seed and collect data, 3=chop weeds
              ('seedfile', str, '/home/pi/data/webaro/seed.txt'),
          ])
        self.add_command('tool', self.cmd_tool, "tool module", ['status','set','seeder', 'hoe', 'read', 'write', 'reset', 'clear'])

        self.simstate = 0
        self.hoestatus = HOE.HOE_INIT
        self.seed_index = 1
        self.seed_position = None
        self.seeds = {}
        self.seeds['seeds'] = []
        self.outindex = 0
        self.passed = False

    def usage(self):
        '''show help on command line options'''
        return "Usage: tool <status|set verbose|set steps|set stepshoe|set hoeoutdistance|set hoeindistance|set hoefirstdistance|set hoemaxdistance|set mode|set seedfile>"

    def cmd_tool(self, args):
        '''control behaviour of the module'''
        if len(args) == 0:
            print(self.usage())
        elif args[0] == "status":
            print(self.status())
        elif args[0] == "set":
            self.tool_settings.command(args[1:])
        elif args[0] == "hoe":
            self.hoe_command(args[1:])
        elif args[0] == "seeder":
            self.seeder_command(args[1:])
        elif args[0] == "read":
            self.read_command(args[1:])
        elif args[0] == "write":
            self.write_command(args[1:])
        elif args[0] == "reset":
            self.reset_command(args[1:])
        elif args[0] == "clear":
            self.clear_command(args[1:])
        else:
            print(self.usage())

    def status(self):
        '''returns information about module'''
        return("steps: " + str(self.tool_settings.steps))

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
        message = "yt" + str(self.tool_settings.stepshoe) + "\r"
        self.send_seeder(message)

    def home_hoe(self):
        message = "yh\r"
        self.send_seeder(message)

    def move_seed(self):
        message = "xt" + str(self.tool_settings.steps) + "\r"
        self.send_seeder(message)

    def home_seed(self):
        message = "xh\r"
        self.send_seeder(message)

    def read_command(self, cmd):
        with open(self.tool_settings.seedfile) as json_file:
            self.seeds = json.load(json_file)
            self.seed_position = self.get_position(self.seed_index)

    def write_command(self, cmd):
        with open(self.tool_settings.seedfile, 'w') as json_file:
            json.dump(self.seeds, json_file)

    def reset_command(self, cmd):
        self.hoestatus = HOE.HOE_INIT
        self.seed_index = 1
        self.seed_position = self.get_position(self.seed_index)

    def clear_command(self, cmd):
        self.hoestatus = HOE.HOE_INIT

    def hoe_command(self, cmd):
        if cmd[0] == 'home':
            self.home_hoe()
        if cmd[0] == 'move':
            self.move_hoe()

    def seeder_command(self, cmd):
        if cmd[0] == 'home':
            self.home_hoe()
        if cmd[0] == 'move':
            self.move_hoe()
        if cmd[0] == 'dump':
            print(json.dumps(self.seeds, indent=4))

        print("seed: " + cmd[0])

    def get_position(self, index):
        for dict in self.seeds['seeds']:
            if dict['index'] == index:
                return dict
        return None

    def mavlink_packet(self, m):
        '''handle mavlink packets'''
        # do nothing if mode = 0
        if self.tool_settings.mode == 0:
            return

        if m.get_type() == "COMMAND_LONG":
            print ("Get Long")
            if m.command == mavutil.mavlink.MAV_CMD_DO_DIGICAM_CONFIGURE:
                print ("Got Message Digicam_configure")
            elif m.command == mavutil.mavlink.MAV_CMD_DO_DIGICAM_CONTROL:
                print ("Got Message Digicam_control")

        if m.get_type() == 'SIMSTATE':
            self.simstate = 1

        if self.tool_settings.mode == 3:
            if m.get_type() == 'GLOBAL_POSITION_INT':
#                distance = mp_util.gps_distance(self.seed_position['lat'], self.seed_position['lng'], m.lat * 1e-7, m.lon * 1e-7)

                wgs84 = nv.FrameE(name='WGS84')
                positionA = wgs84.GeoPoint(latitude=(m.lat * 1e-7), longitude=(m.lon * 1e-7), degrees=True)
                positionB, azB = positionA.displace(1, (m.hdg / 100.0), degrees=True)
                positionC = wgs84.GeoPoint(latitude=self.seed_position['lat'], longitude=self.seed_position['lng'], degrees=True)
                s_AB, _azia, _azib = positionA.distance_and_azimuth(positionB)

                n_EA1_E = nv.lat_lon2n_E(positionA.latitude, positionA.longitude)
                n_EA2_E = nv.lat_lon2n_E(positionB.latitude, positionB.longitude)
                n_EB_E = nv.lat_lon2n_E(positionC.latitude, positionC.longitude)
                path = (n_EA1_E, n_EA2_E)
                s_xt = nv.cross_track_distance(path, n_EB_E)
 #               print("Crosstrack " + str(s_xt[0]))

                n_EC_E = nv.closest_point_on_great_circle(path, n_EB_E)
                if abs((nv.deg(nv.n_EA_E_and_n_EB_E2azimuth(n_EA1_E, n_EC_E)-_azia))) > 10.0:
                    self.passed = True
                else:
                    self.passed = False
                distance = nv.great_circle_distance(n_EA1_E, n_EC_E)[0]
  #              print("Entfernung: " + str(distance))


                if self.hoestatus == HOE.HOE_INIT:
                    if distance < self.tool_settings.hoefirstdistance:
                        self.hoestatus = HOE.HOE_OUT
                        print("(hoe) hoeinit: " + str(distance) + " m")
                        self.move_hoe()
                elif self.hoestatus == HOE.HOE_IN:
                    if distance > self.tool_settings.hoemaxdistance:
                        # we missed the seed
                        self.hoestatus = HOE.HOE_ERROR
                    elif self.passed == False:
                        # we not passed the seed now
                        if self.tool_settings.hoeoutdistance < 0.0:
                            if distance < -self.tool_settings.hoeoutdistance:
                                # save seed end ?
                                if self.get_position(self.seed_index + 1) != None:
                                    self.hoestatus = HOE.HOE_OUT
                                    self.seed_index += 1
                                    self.seed_position = self.get_position(self.seed_index)
                                    print("(hoe) hoeout: " + str(-distance) + " m")
                                    print("Crosstrack " + str(s_xt[0]) + " m")
                                    self.move_hoe()
                                else:
                                    self.hoestatus = HOE.HOE_FINISH
                                    print("hoefinish: " + str(distance) + " m")
                    elif distance > self.tool_settings.hoeoutdistance:
                        # save seed end ?
                        if self.get_position(self.seed_index + 1) != None:
                            self.hoestatus = HOE.HOE_OUT
                            self.seed_index += 1
                            self.seed_position = self.get_position(self.seed_index)
                            print("(hoe) hoeout: " + str(distance) + " m")
                            print("Crosstrack " + str(s_xt[0]) + " m")
                            self.move_hoe()
                        else:
                            self.hoestatus = HOE.HOE_FINISH
                            print("hoefinish: " + str(distance) + " m")
                elif self.hoestatus == HOE.HOE_OUT:
                    if distance > self.tool_settings.hoemaxdistance:
                        self.hoestatus = HOE.HOE_ERROR
                        print("ERROR hoein: " + str(distance) + " m")
                    # save seed !
                    elif distance < self.tool_settings.hoeindistance:
                        self.hoestatus = HOE.HOE_IN
                        print("(save seed) hoein: " + str(distance) + " m")
                        print("Crosstrack " + str(s_xt[0]) + " m")
                        self.move_hoe()

        if m.get_type() == 'CAMERA_FEEDBACK':
            if self.tool_settings.mode < 3:
                if self.tool_settings.mode == 2:
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
                    self.move_seed()

            if self.tool_settings.verbose:
                print("CAMERA_FEEDBACK")

def init(mpstate):
    '''initialise module'''
    return tool(mpstate)
