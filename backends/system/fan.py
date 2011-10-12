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

from __future__ import with_statement

import os
import subprocess
import dbus.service

from backends.globals import *

class Fan(dbus.service.Object):
	""" Control CPU Fan through the samsung-laptop interface """
	def __init__(self, conn = None, object_path = None, bus_name = None):
		dbus.service.Object.__init__(self, conn, object_path, bus_name)
	
	def __save_last_status(self, status):
		""" Save fan last status. """
		try:
			if status == "normal":
				if os.path.exists(LAST_DEVICE_STATUS_CPUFAN):
					os.remove(LAST_DEVICE_STATUS_CPUFAN)
			else:
				file = open(LAST_DEVICE_STATUS_CPUFAN, "w")
				file.write(status)
				file.close()
		except:
			systemlog.write("WARNING: 'Fan.__save_last_status()' - Cannot save last status.")
	
	@dbus.service.method(SYSTEM_INTERFACE_NAME, in_signature = None, out_signature = 'b',
						sender_keyword = 'sender', connection_keyword = 'conn')
	def IsAvailable(self, sender = None, conn = None):
		""" Check if the fan control is available. """
		""" Return 'True' if available, 'False' otherwise. """
		if os.path.exists(SL_PATH_PERFORMANCE):
			return True # already loaded
		command = COMMAND_MODPROBE + " " + SL_MODULE
		try:
			process = subprocess.Popen(command.split(), stdout = subprocess.PIPE, stderr = subprocess.PIPE)
			process.communicate()
			if process.returncode != 0:
				systemlog.write("ERROR: 'Fan.IsAvailable()' - COMMAND: '" + command + "' FAILED.")
				return False
			else:
				return True
		except:
			systemlog.write("ERROR: 'Fan.IsAvailable()' - COMMAND: '" + command + "' - Exception thrown.")
			return False
			
	@dbus.service.method(SYSTEM_INTERFACE_NAME, in_signature = None, out_signature = 'b',
						sender_keyword = 'sender', connection_keyword = 'conn')		
	def LastStatus(self, sender = None, conn = None):
		""" Return last status. """
		if not os.path.exists(LAST_DEVICE_STATUS_CPUFAN):
			return "normal"
		else:
			with open(LAST_DEVICE_STATUS_CPUFAN, "r") as file:
				return file.readline()
	
	@dbus.service.method(SYSTEM_INTERFACE_NAME, in_signature = None, out_signature = None,
						sender_keyword = 'sender', connection_keyword = 'conn')
	def RestoreLastStatus(self, sender = None, conn = None):
		""" Restore last status for CPU fan. """
		laststatus = self.LastStatus()
		if laststatus == "normal":
			self.SetNormal()
		elif laststatus == "silent":
			self.SetSilent()
		else:
			self.SetOverclock()
		
	@dbus.service.method(SYSTEM_INTERFACE_NAME, in_signature = None, out_signature = 'i',
						sender_keyword = 'sender', connection_keyword = 'conn')
	def Status(self, sender = None, conn = None):
		""" Get current fan mode. """
		"""Return 0 if 'normal', 1 if 'silent', 2 if 'overclock'. """
		""" Return 3 if any error. """
		if not self.IsAvailable():
			return 3
		try:
			with open(SL_PATH_PERFORMANCE, 'r') as file:
				status = file.read()[0:-1]
				self.__save_last_status(status)
				if status == "normal":
					return 0
				elif status == "silent":
					return 1
				else:
					return 2
		except:
			systemlog.write("ERROR: 'Fan.Status()' - cannot read from '" + SL_PATH_PERFORMANCE + "'.")
			return 3
	
	@dbus.service.method(SYSTEM_INTERFACE_NAME, in_signature = None, out_signature = 'b',
						sender_keyword = 'sender', connection_keyword = 'conn')
	def SetNormal(self, sender = None, conn = None):
		""" Set fan to 'normal' mode. """
		""" Return 'True' on success, 'False' otherwise. """
		if not self.IsAvailable():
			return False
		try:
			with open(SL_PATH_PERFORMANCE, 'w') as file:
				file.write("normal")
			self.__save_last_status("normal")
			return True
		except:
			systemlog.write("ERROR: 'Fan.SetNormal()' - cannot write to '" + SL_PATH_PERFORMANCE + "'.")
			return False
	
	@dbus.service.method(SYSTEM_INTERFACE_NAME, in_signature = None, out_signature = 'b',
						sender_keyword = 'sender', connection_keyword = 'conn')
	def SetSilent(self, sender = None, conn = None):
		""" Set fan to 'silent' mode. """
		""" Return 'True' on success, 'False' otherwise. """
		if not self.IsAvailable():
			return False
		try:
			with open(SL_PATH_PERFORMANCE, 'w') as file:
				file.write("silent")
			self.__save_last_status("silent")
			return True
		except:
			systemlog.write("ERROR: 'Fan.SetSilent()' - cannot write to '" + SL_PATH_PERFORMANCE + "'.")
			return False
	
	@dbus.service.method(SYSTEM_INTERFACE_NAME, in_signature = None, out_signature = 'b',
						sender_keyword = 'sender', connection_keyword = 'conn')
	def SetOverclock(self, sender = None, conn = None):
		""" Set fan to 'overclock' mode. """
		""" Return 'True' on success, 'False' otherwise. """
		if not self.IsAvailable():
			return False
		try:
			with open(SL_PATH_PERFORMANCE, 'w') as file:
				file.write("overclock")
			self.__save_last_status("overclock")
			return True
		except:
			systemlog.write("ERROR: 'Fan.SetOverclock()' - cannot write to '" + SL_PATH_PERFORMANCE + "'.")
			return False
	
	@dbus.service.method(SYSTEM_INTERFACE_NAME, in_signature = None, out_signature = 'b',
						sender_keyword = 'sender', connection_keyword = 'conn')
	def Cycle(self, sender = None, conn = None):
		""" Set the next fan mode in a cyclic way. """
		""" Return 'True' on success, 'False' otherwise. """
		if not self.IsAvailable():
			return False
		current = self.Status()
		if current == 0:
			return self.SetSilent()
		if current == 1:
			return self.SetOverclock()
		if current == 2:
			return self.SetNormal()
		return False
