# Copyright (C) 2008, Red Hat, Inc.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

import gtk
import dbus
import os
import signal
import sys

from sugar import session
from sugar import env

_session_manager = None

class SessionManager(session.SessionManager):
    MODE_LOGOUT = 0
    MODE_SHUTDOWN = 1
    MODE_REBOOT = 2

    def __init__(self):
        session.SessionManager.__init__(self)
        self._logout_mode = None

    def logout(self):
        self._logout_mode = self.MODE_LOGOUT
        self.initiate_shutdown()

    def shutdown(self):
        self._logout_mode = self.MODE_SHUTDOWN
        self.initiate_shutdown()

    def reboot(self):
        self._logout_mode = self.MODE_REBOOT
        self.initiate_shutdown()

    def shutdown_completed(self):
        session.SessionManager.shutdown_completed(self)

        bus = dbus.SystemBus()
        proxy = bus.get_object('org.freedesktop.Hal',
                               '/org/freedesktop/Hal/devices/computer')
        pm = dbus.Interface(proxy, \
                            'org.freedesktop.Hal.Device.SystemPowerManagement')

        if env.is_emulator():
            self._close_emulator()
        else:
            if self._logout_mode == self.MODE_SHUTDOWN:
                pm.Shutdown()
            elif self._logout_mode == self.MODE_REBOOT:
                pm.Reboot()

            gtk.main_quit()

    def _close_emulator(self):
        gtk.main_quit()

        if os.environ.has_key('SUGAR_EMULATOR_PID'):
            pid = int(os.environ['SUGAR_EMULATOR_PID'])
            os.kill(pid, signal.SIGTERM)

        # Need to call this ASAP so the atexit handlers get called before we get
        # killed by the X (dis)connection
        sys.exit()

def get_session_manager():
    global _session_manager

    if _session_manager == None:
        _session_manager = SessionManager()
    return _session_manager