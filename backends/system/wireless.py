#!/usr/bin/env python
# coding=UTF-8
#
# Samsung-Tools
# 
# Part of the 'Linux On My Samsung' project - <http://www.voria.org/forum>
#
# Copyleft (C) 2010 by
# Fortunato Ventre (voRia) - <vorione@gmail.com> - <http://www.voria.org>
#
# 'Samsung-Tools' is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU General Public License for more details.
# <http://www.gnu.org/licenses/gpl.txt>

import os
import subprocess
import dbus.service

from backends.globals import *
from backends.config import Config

class Wireless(dbus.service.Object):
	""" Control wireless """
	def __init__(self, conn = None, object_path = None, bus_name = None):
		dbus.service.Object.__init__(self, conn, object_path, bus_name)
		# Set wireless toggling method to use
		config = Config(SYSTEM_CONFIG_FILE)
		self.method = config.getWirelessMethod()
		self.device = config.getWirelessDevice()
		self.module = config.getWirelessModule()
	
	@dbus.service.method(SYSTEM_INTERFACE_NAME, in_signature = None, out_signature = 'b',
						sender_keyword = 'sender', connection_keyword = 'conn')
	def IsAvailable(self, sender = None, conn = None):
		""" Check if wireless is available. """
		""" Return 'True' if available, 'False' otherwise. """
		process = subprocess.Popen(['/usr/bin/lspci'], stdout = subprocess.PIPE, stderr = subprocess.PIPE)
		output = process.communicate()[0].split()
		if "Wireless" in output:
			# if method is to use easy-slow-down-manager, check if it's actually available
			if self.method == "esdm":
				if os.path.exists('/proc/easy_wifi_kill'):
					return True
				else:
					# Try to load easy-slow-down-manager module
					process = subprocess.Popen(['/sbin/modprobe', 'easy-slow-down-manager'],
											stdout = subprocess.PIPE, stderr = subprocess.PIPE)
					process.communicate()
					if process.returncode != 0:
						log_system.write("ERROR: 'Wireless.IsAvailable()' - COMMAND: 'modprobe easy-slow-down-manager'")
						return False
					else:
						return True
			return True				
		else:
			# no wireless card is available
			return False
	
	@dbus.service.method(SYSTEM_INTERFACE_NAME, in_signature = None, out_signature = 'b',
						sender_keyword = 'sender', connection_keyword = 'conn')
	def IsEnabled(self, sender = None, conn = None):
		""" Check if wireless is enabled. """
		""" Return 'True' if enabled, 'False' if disabled. """
		if not self.IsAvailable():
			return False
		if self.method == "iwconfig":
			process = subprocess.Popen(['/sbin/iwconfig', self.device],
									stdout = subprocess.PIPE, stderr = subprocess.PIPE)
			output = process.communicate()[0].split()
			if "Tx-Power=off" in output:
				return False
			else:
				return True
		if self.method == "module":
			process = subprocess.Popen(['/sbin/lsmod'],
								stdout = subprocess.PIPE, stderr = subprocess.PIPE)
			output = process.communicate()[0].split()
			if self.module in output:
				return True
			else:
				return False
		if self.method == "esdm":
			process = subprocess.Popen(['/bin/cat', '/proc/easy_wifi_kill'],
									stdout = subprocess.PIPE, stderr = subprocess.PIPE)
			output = process.communicate()[0].strip()
			if output == "0":
				return False
			else:
				return True
		return False
	
	@dbus.service.method(SYSTEM_INTERFACE_NAME, in_signature = None, out_signature = 'b',
						sender_keyword = 'sender', connection_keyword = 'conn')
	def Enable(self, sender = None, conn = None):
		""" Enable wireless. """
		""" Return 'True' on success, 'False' otherwise. """
		if not self.IsAvailable():
			return False
		if self.IsEnabled():
			return True
		if self.method == "iwconfig":
			process = subprocess.Popen(['/sbin/iwconfig', self.device, 'txpower', 'auto'],
									stdout = subprocess.PIPE, stderr = subprocess.PIPE)
			process.communicate()
			if process.returncode != 0:
				log_system.write("ERROR: 'Wireless.Enable()' - COMMAND: 'iwconfig " + self.device + " txpower auto'")
				return False
			return True
		if self.method == "module":
			process = subprocess.Popen(['/sbin/modprobe', self.module],
								stdout = subprocess.PIPE, stderr = subprocess.PIPE)
			process.communicate()
			if process.returncode != 0:
				log_system.write("ERROR: 'Wireless.Enable()' - COMMAND: 'modprobe " + self.module + "'")
				return False
			return True
		if self.method == "esdm":
			try:
				with open('/proc/easy_wifi_kill', 'w') as file:
					file.write('1')
				return True
			except:
				return False
		return False
	
	@dbus.service.method(SYSTEM_INTERFACE_NAME, in_signature = None, out_signature = 'b',
						sender_keyword = 'sender', connection_keyword = 'conn')
	def Disable(self, sender = None, conn = None):
		""" Disable wireless. """
		""" Return 'True' on success, 'False' otherwise. """
		if not self.IsAvailable():
			return False
		if not self.IsEnabled():
			return True
		if self.method == "iwconfig":
			process = subprocess.Popen(['/sbin/iwconfig', self.device, 'txpower', 'off'],
									stdout = subprocess.PIPE, stderr = subprocess.PIPE)
			process.communicate()
			if process.returncode != 0:
				log_system.write("ERROR: 'Wireless.Disable()' - COMMAND: 'iwconfig " + self.device + " txpower off'")
				return False
			return True
		if self.method == "module":
			process = subprocess.Popen(['/sbin/modprobe', '-r', self.module],
								stdout = subprocess.PIPE, stderr = subprocess.PIPE)
			process.communicate()
			if process.returncode != 0:
				log_system.write("ERROR: 'Wireless.Disable()' - COMMAND: 'modprobe -r " + self.module + "'")
				return False
			return True
		if self.method == "esdm":
			try:
				with open('/proc/easy_wifi_kill', 'w') as file:
					file.write('0')
				return True
			except:
				return False
		return False
			
	@dbus.service.method(SYSTEM_INTERFACE_NAME, in_signature = None, out_signature = 'b',
						sender_keyword = 'sender', connection_keyword = 'conn')
	def Toggle(self, sender = None, conn = None):
		""" Toggle wireless. """
		""" Return 'True' on success, 'False' otherwise. """
		if not self.IsAvailable():
			return False
		if self.IsEnabled():
			return self.Disable()
		else:
			return self.Enable()
