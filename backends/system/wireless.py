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

class Wireless(dbus.service.Object):
	""" Control wireless """
	def __init__(self, conn = None, object_path = None, bus_name = None):
		dbus.service.Object.__init__(self, conn, object_path, bus_name)
		self.available = self.__is_available()
	
	def __is_available(self):
		""" Check if wireless is available. """
		""" Return 'True' if available, 'False' otherwise. """
		if self.__load_esdm_module() == True:
			return True
		# FIXME: Find a better way to check if wireless is available
		try:
			process = subprocess.Popen([COMMAND_LSPCI], stdout = subprocess.PIPE, stderr = subprocess.PIPE)
			output = process.communicate()[0].split()
			if process.returncode != 0:
				systemlog.write("ERROR: 'Wireless.IsAvailable()' - COMMAND: '" + COMMAND_LSPCI + "' FAILED.")
				return False			
			if not "Wireless" in output:
				return False
			else:
				return True
		except:
			systemlog.write("ERROR: 'Wireless.IsAvailable()' - COMMAND: '" + COMMAND_LSPCI + "' - Exception thrown.")
			return False
			
	def __load_esdm_module(self):
		""" Load the easy-slow-down-manager kernel module. """
		""" Return 'True' on success, 'False' otherwise. """
		if os.path.exists(ESDM_PATH_WIRELESS):
			return True # already loaded
		command = COMMAND_MODPROBE + " " + ESDM_MODULE
		try:
			process = subprocess.Popen(command.split(),
									stdout = subprocess.PIPE, stderr = subprocess.PIPE)
			process.communicate()
			if process.returncode != 0:
				systemlog.write("ERROR: 'Wireless.__load_esdm_module()' - COMMAND: '" + command + "' FAILED.")
				return False
			else:
				return True
		except:
			systemlog.write("ERROR: 'Wireless.__load_esdm_module()' - COMMAND: '" + command + "' - Exception thrown.")
			return False
	
	def __save_last_status(self, status):
		""" Save wireless last status. """
		try:
			if status == True:
				if os.path.exists(LAST_DEVICE_STATUS_WIRELESS):
					os.remove(LAST_DEVICE_STATUS_WIRELESS)
			else:
				file = open(LAST_DEVICE_STATUS_WIRELESS, "w")
				file.close()
		except:
			systemlog.write("WARNING: 'Wireless.__save_last_status()' - Cannot save last status.")
	
	@dbus.service.method(SYSTEM_INTERFACE_NAME, in_signature = None, out_signature = 'b',
						sender_keyword = 'sender', connection_keyword = 'conn')
	def IsAvailable(self, sender = None, conn = None):
		""" Return 'True' if wireless control is available, 'False' otherwise. """
		return self.available
	
	@dbus.service.method(SYSTEM_INTERFACE_NAME, in_signature = None, out_signature = 'b',
						sender_keyword = 'sender', connection_keyword = 'conn')
	def IsEnabled(self, sender = None, conn = None):
		""" Check if wireless is enabled. """
		""" Return 'True' if enabled, 'False' if disabled. """
		if not self.available:
			return False
		method = systemconfig.getWirelessToggleMethod()
		if method == "iwconfig":
			device = systemconfig.getWirelessDevice()
			command = COMMAND_IWCONFIG + " " + device 
			try:
				process = subprocess.Popen(command.split(),
										stdout = subprocess.PIPE, stderr = subprocess.PIPE)
				output = process.communicate()[0].split()
				if process.returncode != 0:
					systemlog.write("ERROR: 'Wireless.IsEnabled()' - COMMAND: '" + command + "' FAILED.")
					return False
				if "Tx-Power=off" in output:
					return False
				else:
					return True
			except:
				systemlog.write("ERROR: 'Wireless.IsEnabled()' - COMMAND: '" + command + "' - Exception thrown.")
				return False
		elif method == "module":
			module = systemconfig.getWirelessModule()
			try:
				process = subprocess.Popen([COMMAND_LSMOD],
										stdout = subprocess.PIPE, stderr = subprocess.PIPE)
				output = process.communicate()[0].split()
				if process.returncode != 0:
					systemlog.write("ERROR: 'Wireless.IsEnabled()' - COMMAND: '" + COMMAND_LSMOD + "' FAILED.")
					return False
				if module in output:
					return True
				else:
					return False
			except:
				systemlog.write("ERROR: 'Wireless.IsEnabled()' - COMMAND: '" + COMMAND_LSMOD + "' - Exception thrown.")
				return False
		else: # method == "esdm":
			try:
				with open(ESDM_PATH_WIRELESS, 'r') as file:
					result = int(file.read(1))
					if result == 0:
						return False
					else:
						return True
			except:
				systemlog.write("ERROR: 'Wireless.IsEnabled()' - cannot read from '" + ESDM_PATH_WIRELESS + "'.")
				return False
	
	@dbus.service.method(SYSTEM_INTERFACE_NAME, in_signature = None, out_signature = 'b',
						sender_keyword = 'sender', connection_keyword = 'conn')
	def Enable(self, sender = None, conn = None):
		""" Enable wireless. """
		""" Return 'True' on success, 'False' otherwise. """
		if not self.available:
			return False
		if self.IsEnabled():
			return True
		method = systemconfig.getWirelessToggleMethod()
		if method == "iwconfig":
			device = systemconfig.getWirelessDevice()
			command = COMMAND_IWCONFIG + " " + device + " txpower auto"
			try:
				process = subprocess.Popen(command.split(),
										stdout = subprocess.PIPE, stderr = subprocess.PIPE)
				process.communicate()
				if process.returncode != 0:
					systemlog.write("ERROR: 'Wireless.Enable()' - COMMAND: '" + command + "' FAILED.")
					return False
			except:
				systemlog.write("ERROR: 'Wireless.Enable()' - COMMAND: '" + command + "' - Exception thrown.")
				return False
		elif method == "module":
			try:
				module = systemconfig.getWirelessModule()
				command = COMMAND_MODPROBE + " " + module
				process = subprocess.Popen(command.split(),
										stdout = subprocess.PIPE, stderr = subprocess.PIPE)
				process.communicate()
				if process.returncode != 0:
					systemlog.write("ERROR: 'Wireless.Enable()' - COMMAND: '" + command + "' FAILED.")
					return False
			except:
				systemlog.write("ERROR: 'Wireless.Enable()' - COMMAND: '" + command + "' - Exception thrown.")
				return False
		else: # method == "esdm":
			try:
				with open(ESDM_PATH_WIRELESS, 'w') as file:
					file.write('1')
			except:
				systemlog.write("ERROR: 'Wireless.Enable()' - cannot write to '" + ESDM_PATH_WIRELESS + "'.")
				return False
		# Save wireless status
		self.__save_last_status(True)
		return True
	
	@dbus.service.method(SYSTEM_INTERFACE_NAME, in_signature = None, out_signature = 'b',
						sender_keyword = 'sender', connection_keyword = 'conn')
	def Disable(self, sender = None, conn = None):
		""" Disable wireless. """
		""" Return 'True' on success, 'False' otherwise. """
		if not self.available:
			return False
		if not self.IsEnabled():
			return True
		method = systemconfig.getWirelessToggleMethod()
		if method == "iwconfig":
			device = systemconfig.getWirelessDevice()
			command = COMMAND_IWCONFIG + " " + device + " txpower off"
			try:
				process = subprocess.Popen(command.split(),
										stdout = subprocess.PIPE, stderr = subprocess.PIPE)
				process.communicate()
				if process.returncode != 0:
					systemlog.write("ERROR: 'Wireless.Disable()' - COMMAND: '" + command + "' FAILED.")
					return False
			except:
				systemlog.write("ERROR: 'Wireless.Disable()' - COMMAND: '" + command + "' - Exception thrown.")
				return False
		elif method == "module":
			module = systemconfig.getWirelessModule()
			command = COMMAND_MODPROBE + " -r " + module
			try:
				process = subprocess.Popen(command.split(),
										stdout = subprocess.PIPE, stderr = subprocess.PIPE)
				process.communicate()
				if process.returncode != 0:
					systemlog.write("ERROR: 'Wireless.Disable()' - COMMAND: '" + command + "' FAILED.")
					return False
			except:
				systemlog.write("ERROR: 'Wireless.Disable()' - COMMAND: '" + command + "' - Exception thrown.")
				return False
		else: # method == "esdm":
			try:
				with open(ESDM_PATH_WIRELESS, 'w') as file:
					file.write('0')
			except:
				systemlog.write("ERROR: 'Wireless.Disable()' - cannot write to '" + ESDM_PATH_WIRELESS + "'.")
				return False
		# Save wireless status
		self.__save_last_status(False)
		return True
			
	@dbus.service.method(SYSTEM_INTERFACE_NAME, in_signature = None, out_signature = 'b',
						sender_keyword = 'sender', connection_keyword = 'conn')
	def Toggle(self, sender = None, conn = None):
		""" Toggle wireless. """
		""" Return 'True' on success, 'False' otherwise. """
		if not self.available:
			return False
		if self.IsEnabled():
			return self.Disable()
		else:
			return self.Enable()
