# -*- coding: utf-8 -*-
#
#  Copyright 2017 uberdaff
#  
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#  
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#  
#  
# Requirement: pyserial
#
# getValue() - Get the measured value as a float
# getValueString() - Get the measured value as a string with the unit
#

import time
import serial

class pt3430Instrument:
	isConnected = False
	dmm_com = None
	status={}
	
	def __init__(self, dmm_com):
		dmm_com.isOpen()
		self.dmm_com = dmm_com
		self.isConnected = True
	
	def close(self):
		self.dmm_com.close()
	
	def pt3430translate(self, string):
		self.status["RangeHex"]=hex(ord(string[0]))
		self.status["FuncHex"]=hex(ord(string[6]))
		functions = {0x30:{"Name":"Current A (auto)", "Desimal":[3],              "Units":["A"]},\
		0x36:{"Name":"Capacitance",                   "Desimal":[3,2,4,3,2,4,3,2],"Units":["nF","nF","uF","uF","uF","mF","mF","mF"]},\
		0x31:{"Name":"Diode",                         "Desimal":[4],              "Units":["V"]},\
		0x39:{"Name":"Current A (manual)",            "Desimal":[3],              "Units":["A"]},\
		0x32:{"Name":"Frequency / Duty",              "Desimal":[3,2,4,3,2,4,3,2],"Units":["Hz","Hz","kHz","kHz","kHz","MHz","MHz","MHz"]},\
		0x3B:{"Name":"Voltage",                       "Desimal":[4,3,2,1,2],      "Units":["V","V","V","V","mV"]},\
		0x33:{"Name":"Ohm",                           "Desimal":[2,4,3,2,4,3,2],  "Units":["Ohm","kOhm","kOhm","kOhm","MOhm","MOhm","MOhm"]},\
		0x3D:{"Name":"Auto uA current",               "Desimal":[2,1],            "Units":["uA","uA"]},\
		0x35:{"Name":"Continuity",                    "Desimal":[2],              "Units":["Ohm"]},\
		0x3F:{"Name":"Auto mA current",               "Desimal":[3,2],            "Units":["mA","mA"]}}
		#divisor = {0x30:
		
		# self.status bits from byte 7
		self.status["Judge"]=str((ord(string[7])&(1 << 3))!=0)
		self.status["Batt"]=str((ord(string[7])&(1 << 1))!=0)
		self.status["OL"]=str((ord(string[7])&(1 << 0))!=0)
		
		if (ord(string[7])&(1 << 2)):
			self.status["Sign"]="-"
		else:
			self.status["Sign"]=""
		
		# self.status bits from byte 8
		self.status["Max"]=str((ord(string[8])&(1 << 3))!=0)
		self.status["Min"]=str((ord(string[8])&(1 << 2))!=0)
		self.status["Rel"]=str((ord(string[8])&(1 << 1))!=0)
		
		# self.status bits from byte 9
		self.status["UL"]=str((ord(string[9])&(1 << 3))!=0)
		self.status["Pmax"]=str((ord(string[9])&(1 << 2))!=0)
		self.status["Pmin"]=str((ord(string[9])&(1 << 1))!=0)
		
		# self.status bits from byte 10
		self.status["DC"]=str((ord(string[10])&(1 << 3))!=0)
		self.status["AC"]=str((ord(string[10])&(1 << 2))!=0)
		self.status["Auto"]=str((ord(string[10])&(1 << 1))!=0)
		self.status["VAHz"]=str((ord(string[10])&(1 << 0))!=0)
		
		# self.status bits from byte 11
		self.status["VBAR"]=str((ord(string[11])&(1 << 1))!=0)
		self.status["Hold"]=str((ord(string[11])&(1 << 1))!=0)
		self.status["LPF"]=str((ord(string[11])&(1 << 0))!=0)
		
		if ord(string[6]) in functions:
			self.status["Function"]=functions[ord(string[6])]["Name"]
			rangeIndex = ord(string[0])-48
			try:
				unit = functions[ord(string[6])]["Units"][rangeIndex]
			except:
				unit = "?"
			
			try:
				decimal = functions[ord(string[6])]["Desimal"][rangeIndex]
			except:
				decimal = 0
			
			self.status["Decimal"]=decimal
			self.status["Unit"]=unit
		
			if self.status["Function"]=="Frequency / Duty":
				if self.status["Judge"] == "True":
					self.status["Function"]="Frequency"
				else:
					self.status["Function"]="Duty"
			
			self.status["Division"]=pow(10,decimal)
			self.status["RawNumbers"]=self.status["Sign"]+string[1:6]
			self.status["Digits"]=float(string[1:6])/pow(10,decimal)
			if self.status["Sign"] == "-":
				self.status["Digits"]*=-1
			self.status["Measurement"]=str(self.status["Digits"])+self.status["Unit"]
			
			if self.status["OL"] == "True":
				self.status["Measurement"]="OL"
		
	def getValue(self):
		self.pt3430translate(self.dmm_com.readline())
		return self.status["Digits"]
	
	def getValueString(self):
		self.pt3430translate(self.dmm_com.readline())
		return self.status["Measurement"]
