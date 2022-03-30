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

TCP_IP = '192.168.15.60'
TCP_PORT = 23

class lift(mp_module.MPModule):
    def __init__(self, mpstate):
        """Initialise module"""
        super(lift, self).__init__(mpstate, "lift", "")

        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.s.settimeout(1)
            self.s.connect((TCP_IP, TCP_PORT))
            self.s.settimeout(None)
        except:
            pass

        self.lift_settings = mp_settings.MPSettings(
            [ ('verbose', bool, False),
              ('time', int, 2000),
              ('speed', int, 200),
              ('mode', int, 2),                  # mode: 0=do nothing, 1=seed, 2=seed and collect data, 3=chop weeds
          ])
        self.lift_settings.set_callback(self.set_callback)
        self.add_command('lift', self.cmd_lift, "lift module", ['status','set','up', 'down'])
        self.simstate = 0

    def usage(self):
        '''show help on command line options'''
        return "Usage: lift <status|up|down|set verbose|set speed|set time>"

    def cmd_lift(self, args):
        '''control behaviour of the module'''
        if len(args) == 0:
            print(self.usage())
        elif args[0] == "status":
            print(self.status())
        elif args[0] == "set":
            self.lift_settings.command(args[1:])
        elif args[0] == "up":
            self.lift_up()
        elif args[0] == "down":
            self.lift_down()
        else:
            print(self.usage())

    def status(self):
        '''returns information about module'''
        return("steps: " + str(self.lift_settings.steps))

    def set_callback(self, setting):
        if setting.name == "speed":
            self.lift_speed(setting.value)

    def send_lift(self, msg):
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

    def lift_down(self):
        message = "1t-" + str(self.lift_settings.time) + "\r"
        self.send_lift(message)

    def lift_up(self):
        message = "1t" + str(self.lift_settings.time) + "\r"
        self.send_lift(message)

    def lift_home(self):
        message = "1h\r"
        self.send_lift(message)

    def lift_speed(self, speed):
        message = "1s" + str(speed) + "\r"
        self.send_lift(message)

    def mavlink_packet(self, m):
        '''handle mavlink packets'''
        if m.get_type() == "STATUSTEXT":
            if m.text == "lift up":
                print("lift up")
                self.lift_up()

            if m.text.startswith("lift down"):
                print("lift down")
                self.lift_down()

        # do nothing if mode = 0
        if self.lift_settings.mode == 0:
            return

        if m.get_type() == "COMMAND_LONG":
            print ("Get Long")
            if m.command == mavutil.mavlink.MAV_CMD_DO_DIGICAM_CONFIGURE:
                print ("Got Message Digicam_configure")
            elif m.command == mavutil.mavlink.MAV_CMD_DO_DIGICAM_CONTROL:
                print ("Got Message Digicam_control")

        if m.get_type() == 'SIMSTATE':
            self.simstate = 1

def init(mpstate):
    '''initialise module'''
    return lift(mpstate)