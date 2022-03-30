#!/usr/bin/env python

import os
import os.path
import sys
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
              ('seeder_steps', int, 400),
              ('seeder_speed', int, 200),
              ('hoe_steps', int, 3200),
              ('hoe_speed', int, 400),
              ('hoe_outdistance', float, 0.01),   # hoe_outdistance m
              ('hoe_indistance', float, 0.18),    # hoe_indistance m
              ('hoe_firstdistance', float, 2.0),  # hoe_firstdistance m
              ('hoe_maxdistance', float, 2.25),   # hoe_maxdistance m
              ('mode', int, 0),                  # mode: 0=do nothing, 1=seed, 2=seed and collect data, 3=chop weeds
              ('seedfile', str, '/home/pi/data/webaro/seed.txt'),
          ])
        self.tool_settings.set_callback(self.set_callback)
        self.add_command('tool', self.cmd_tool, "tool module", ['status','set','seeder', 'hoe', 'read', 'write', 'reset', 'clear'])

        self.simstate = 0
        self.hoestatus = HOE.HOE_INIT
        self.seed_index = 1
        self.seed_index_log = 1
        self.seed_lat = 0.0
        self.seed_lng = 0.0
        self.passed = False

#        self.hoe_speed_read()
#        self.seed_speed_read()

    def usage(self):
        '''show help on command line options'''
        return "Usage: tool <status|set verbose|set steps|set stepshoe|set hoe_outdistance|set hoe_indistance|set hoe_firstdistance|set hoemaxdistance|set mode|set seedfile>"

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
        return("steps: " + str(self.tool_settings.seeder_steps))

    def set_callback(self, setting):
        if setting.name == "hoe_speed":
            self.hoe_speed(setting.value)
        if setting.name == 'seeder_speed':
            self.seed_speed(setting.value)

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

    def hoe_move(self):
        message = "yt" + str(self.tool_settings.hoe_steps) + "\r"
        self.send_seeder(message)

    def hoe_home(self):
        message = "yh\r"
        self.send_seeder(message)

    def hoe_speed(self, speed):
        message = "ys" + str(speed) + "\r"
        self.send_seeder(message)

    def hoe_speed_read(self):
        message = "ys\r"
        self.send_seeder(message)
        data = self.s.recv(96)
        num = int(data)
        if(num > 1):
            self.tool_settings.hoe_speed = num

    def hoe_start(self):
        self.hoestatus = HOE.HOE_INIT
        self.seedfile = open(self.tool_settings.seedfile)
        self.read_next_position()
        self.seed_index = 1
        self.tool_settings.mode = 3

    def hoe_stop(self):
        self.seedfile.close()
        self.seed_index = 1
        self.tool_settings.mode = 0

    def seed_move(self):
        message = "xt" + str(self.tool_settings.seeder_steps) + "\r"
        self.send_seeder(message)

    def seed_home(self):
        message = "xh\r"
        self.send_seeder(message)

    def seed_speed(self, speed):
        message = "xs" + str(speed) + "\r"
        self.send_seeder(message)

    def seed_speed_read(self):
        message = "xs\r"
        self.send_seeder(message)
        data = self.s.recv(96)
        num = int(data)
        if(num > 1):
            self.tool_settings.seeder_speed = num

    def seed_start(self):
        self.seedfile = open(self.tool_settings.seedfile, 'w')
        self.seed_index = 1
        self.tool_settings.mode = 2

    def seed_stop(self):
        self.seedfile.close()
        self.seed_index = 1
        self.tool_settings.mode = 0

    def reset_command(self, cmd):
        self.hoestatus = HOE.HOE_INIT
        self.seedfile.close()
        self.seed_index = 1

    def clear_command(self, cmd):
        self.hoestatus = HOE.HOE_INIT

    def hoe_command(self, cmd):
        if cmd[0] == 'home':
            self.hoe_home()
        if cmd[0] == 'move':
            self.hoe_move()
        if cmd[0] == 'start':
            self.hoe_start()
        if cmd[0] == 'stop':
            self.hoe_stop()
        if cmd[0] == 'read':
            self.hoe_speed_read()

    def seeder_command(self, cmd):
        if cmd[0] == 'home':
            self.seed_home()
        if cmd[0] == 'move':
            self.seed_move()
        if cmd[0] == 'read':
            self.seed_speed_read()
        if cmd[0] == 'start':
            self.seed_start()
        if cmd[0] == 'stop':
            self.seed_stop()

    def read_next_position(self):
        result = self.seedfile.readline().split()
        if len(result) == 0:
            return False
        self.seed_index = int(result[0])
        self.seed_time = int(result[1])
        self.seed_lat = float(result[2])
        self.seed_lng = float(result[3])
        self_seed_index_log = int(result[4])
        return True

    def mavlink_packet(self, m):
        '''handle mavlink packets'''
        # do nothing if mode = 0
        if self.tool_settings.mode == 0:
            return

        if m.get_type() == 'SIMSTATE':
            self.simstate = 1

        if self.tool_settings.mode == 3:
            if m.get_type() == 'GLOBAL_POSITION_INT':
                wgs84 = nv.FrameE(name='WGS84')
                positionA = wgs84.GeoPoint(latitude=(m.lat * 1e-7), longitude=(m.lon * 1e-7), degrees=True)
                positionB, azB = positionA.displace(1, (m.hdg / 100.0), degrees=True)
                positionC = wgs84.GeoPoint(latitude=self.seed_lat, longitude=self.seed_lng, degrees=True)
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
                    if distance < self.tool_settings.hoe_firstdistance:
                        self.hoestatus = HOE.HOE_OUT
                        if self.tool_settings.verbose:
                            print("(hoe) hoeinit: " + str(distance) + " m")
                        self.hoe_move()
                elif self.hoestatus == HOE.HOE_IN:
                    if distance > self.tool_settings.hoe_maxdistance:
                        # we missed the seed
                        self.hoestatus = HOE.HOE_ERROR
                    elif self.passed == False:
                        # we not passed the seed now
                        if self.tool_settings.hoe_outdistance < 0.0:
                            if distance < -self.tool_settings.hoe_outdistance:
                                # save seed end ?
                                if self.read_next_position() == True:
                                    self.hoestatus = HOE.HOE_OUT
                                    if self.tool_settings.verbose:
                                        print("(hoe) hoeout: " + str(-distance) + " m")
                                        print("Crosstrack " + str(s_xt[0]) + " m")
                                    self.hoe_move()
                                else:
                                    self.hoestatus = HOE.HOE_FINISH
                                    if self.tool_settings.verbose:
                                        print("hoefinish: " + str(distance) + " m")
                    elif distance > self.tool_settings.hoe_outdistance:
                        # save seed end ?
                        if self.read_next_position() == True:
                            self.hoestatus = HOE.HOE_OUT
                            if self.tool_settings.verbose:
                                print("(hoe) hoeout: " + str(distance) + " m")
                                print("Crosstrack " + str(s_xt[0]) + " m")
                            self.hoe_move()
                        else:
                            self.hoestatus = HOE.HOE_FINISH
                            if self.tool_settings.verbose:
                                print("hoefinish: " + str(distance) + " m")
                elif self.hoestatus == HOE.HOE_OUT:
                    if distance > self.tool_settings.hoe_maxdistance:
                        self.hoestatus = HOE.HOE_ERROR
                        if self.tool_settings.verbose:
                            print("ERROR hoein: " + str(distance) + " m")
                    # save seed !
                    elif distance < self.tool_settings.hoe_indistance:
                        self.hoestatus = HOE.HOE_IN
                        if self.tool_settings.verbose:
                            print("(save seed) hoein: " + str(distance) + " m")
                            print("Crosstrack " + str(s_xt[0]) + " m")
                        self.hoe_move()

        if m.get_type() == 'CAMERA_FEEDBACK':
            if self.tool_settings.mode < 3:
                if self.tool_settings.mode == 2:
                    time = m.time_usec
                    index = m.img_idx
                    lat = m.lat * 1e-7
                    lng = m.lng * 1e-7

                    if self.tool_settings.verbose:
                        print("Lat: " + str(lat) + "  Lon: " + str(lng) + "  Index: " + str(index))

                    try:
                        self.seedfile.write(str(self.seed_index) + " " + str(time) + " " + str(lat) + " " + str(lng) + " "+ str(index)+ "\r\n")
                        self.seedfile.flush()
                    except:
                        self.seed_stop()
                    self.seed_index = self.seed_index + 1

                # send only in none SITL
                if self.simstate == 0:
                    self.seed_move()

            if self.tool_settings.verbose:
                print("CAMERA_FEEDBACK")

def init(mpstate):
    '''initialise module'''
    return tool(mpstate)
