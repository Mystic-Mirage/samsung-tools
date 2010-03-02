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

try:
	import pynotify
except:
	pass

class Notification():
	def __init__(self, title = None, message = None, icon = None, urgency = "normal"):
		self.initialized = True
		try:
			if not pynotify.init("Samsung-Tools Notification System"):
				self.initialized = False
				return
		except:
			self.initialized = False
			return
		# Create a new notification
		self.notify = pynotify.Notification(" ")
		# Set initial values
		self.setTitle(title)
		self.setMessage(message)
		self.setIcon(icon)
		self.setUrgency(urgency)

	def setTitle(self, title):
		if not self.initialized:
			return
		self.title = title

	def setMessage(self, message):
		if not self.initialized:
			return
		self.message = message

	def setIcon(self, icon):
		if not self.initialized:
			return
		self.icon = icon

	def setUrgency(self, urgency):
		if not self.initialized:
			return
		if urgency == "low":
			self.urgency = pynotify.URGENCY_LOW
		elif urgency == "normal":
			self.urgency = pynotify.URGENCY_NORMAL
		elif urgency == "critical":
			self.urgency = pynotify.URGENCY_CRITICAL
		else:
			self.urgency = None
	
	def show(self):
		if not self.initialized:
			return
		if self.title == None or self.message == None:
			return
		self.notify.update(self.title, self.message, self.icon)
		if self.urgency != None:
			self.notify.set_urgency(self.urgency)
		self.notify.show()
		
