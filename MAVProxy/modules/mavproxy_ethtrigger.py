#!/usr/bin/env python

import os
import os.path
import sys
from pymavlink import mavutil
import errno
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
          ])
        self.add_command('ethtrigger', self.cmd_ethtrigger, "ethtrigger module", ['status','set'])

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
        else:
            print(self.usage())

    def status(self):
        '''returns information about module'''
        return("steps: " + str(self.ethtrigger_settings.steps))

    def mavlink_packet(self, m):
        '''handle mavlink packets'''
        if m.get_type() == 'CAMERA_FEEDBACK':
            if self.ethtrigger_settings.verbose:
                print("CAMERA_FEEDBACK")

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

def init(mpstate):
    '''initialise module'''
    return ethtrigger(mpstate)
