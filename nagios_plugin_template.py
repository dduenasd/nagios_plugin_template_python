#!/usr/bin/env python
# -*- coding: utf-8 -*-

#############################################################
# I'm a Spanish speaker, my English is basic but I try to write everything in English.
# Many translations have been made with automatic translators.
# If something is not meant pray excuse me.
# ¡VAMOS A ELLO! (LET'S GO!)

#-------------------------------------------------------------------------------
# Name:        plugin_nagios_template.py
# Purpose:
# Plantilla para plugins de nagios en python
# Python nagios plugins template
#
# Author:      Daniel Dueñas
#
# This plugin conforms to the Nagios Plugin Development Guidelines
# https://nagios-plugins.org/doc/guidelines.html
#
# Created:     18/02/2014
# Copyright:   (c) Daniel Dueñas Domingo 2014
# Licence:
#   This program is free software; you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation; either version 2 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program; if not, write to the Free Software
#   Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
#-------------------------------------------------------------------------------
#

import argparse, sys

#variable definitions
version="0.1"   #Plugin version
status = { 'OK' : 0 , 'WARNING' : 1, 'CRITICAL' : 2 , 'UNKNOWN' : 3}
exit_status = 'UNKNOWN'     #default exit_status
output = ""                 #The output text of the plugin
longoutput = ""             #The longoutput text of the plugin
perfdata = ""
mensage = ""

# argparse object definition (no numbers permited in argument definition example:-2)
parser = argparse.ArgumentParser(description='Plugin for monitorize something')
parser.add_argument('-V','--version', action='version',
                    help="Show plugin version",
                    version='%(prog)s '+version)
parser.add_argument('-v', '--verbosity',action="count",
                    help='''increase output verbosity:
                    -v Single line, additional information (eg list processes that fail)\n
                    -vv Multi line, configuration debug output (eg ps command used)
                    -vvv Lots of detail for plugin problem diagnosis
                    ''')
parser.add_argument('-H', '--host',
                    help="Name or Ip host, localhost by default",
                    default="localhost")
parser.add_argument('-w', '--warning',
                    help='Warning level')
parser.add_argument('-c','--critical',
                    help="Critical level")
# Add arguments
#.....

#Correct the negative numbers in arguments parser
for i, arg in enumerate(sys.argv):
  if (arg[0] == '-') and arg[1].isdigit(): sys.argv[i] = ' ' + arg
# arguments parse
args = parser.parse_args()

#Functions
#Try if string is a float
def is_float_try(str):
    try:
        float(str)
        return True
    except ValueError:
        return False

#This function define the range of warning and critical values
#Return a range --> (min,max,True/False)
#if True, data must be in the range
#if False, data must be out of the range
def define_range(str):
    if is_float_try(str):
        range = (0,float(str),True)  # x -> in range(0,x)
    elif str.count(":")==1:
        splits = str.split(":")
        if is_float_try(splits[0]) and is_float_try(splits[1]):
            range=(float(splits[0]),float(splits[1]),True) # x:y  -> in range(x,y)
        elif is_float_try(splits[0]) and splits[1]=="":
            range=(float(splits[0]),float("inf"),True)  # x:  -> in range(x,infinite)
        elif splits[0]=="~" and is_float_try(splits[1]):
            range=(float("-inf"),float(splits[1]),True) # ~:x -> in range(-infinite,x)
        if splits[0][0]=="@" and is_float_try(splits[0].replace("@","")) and is_float_try(splits[1]):
            range=(float(splits[0].replace("@","")),float(splits[1]),False) # @x:y -> out of range(x,y)
    else:
        print "bad range definition in "+str
        sys.exit(1) #Error in range definition
    if range[0]<range[1]:
        return range   # OK
    else:
        print "Second value of range "+str+" is less than first value"
        exit(1)

#This function resolve the state of a numerical value (Ok, warning or critical)
def define_status(value,warning,critical):
    warning_range = define_range(warning)  #Define warning range
    critical_range = define_range(critical)#Define critical range
    val=float(value)                       #The value
    exit_status="UNKNOWN"                   #status by default
    if args.verbosity:
        print "Value for test: "+str(value)
        print "Warning range (min:%s max:%s in_range:%s)"%(str(warning_range[0]),str(warning_range[1]),str(warning_range[2]))
        print "Critical range (min:%s max:%s in_range:%s)"%(str(critical_range[0]),str(critical_range[1]),str(critical_range[2]))

    #value into the range range(x:y:True)
    if warning_range[2]==True and critical_range[2]==True:
        if (warning_range[1]>critical_range[1]) or (warning_range[0]<critical_range[0]):
            parser.print_usage()
            parser.exit(3,"ERRROR: critical range (%s) is greater than warning range(%s)\n" % (critical, warning))
        if value<warning_range[0] or value>warning_range[1]:
            exit_status="WARNING"
            if value<critical_range[0] or value>critical_range[1]:
                exit_status="CRITICAL"
        else:
            exit_status="OK"
    #value out of range range(x:y:False)
    elif warning_range[2]==False and critical_range[2]==False:
        if (warning_range[1]<critical_range[1]) or (warning_range[0]>critical_range[0]):
            parser.print_usage()
            parser.exit(3,"ERRROR: critical range (%s) is greater than warning range(%s)\n" % (critical, warning))
        if value>warning_range[0] and value<warning_range[1]:
            exit_status="WARNING"
            if value>critical_range[0] and value<critical_range[1]:
                exit_status="CRITICAL"
        else:
            exit_status="OK"
    #warning and critical ranges must be both in or out
    else:
        parser.print_usage()
        parser.exit(status[exit_status],'''
ERROR: Both critical and warning values must be in or out of the ranges:
       warning('''+warning+''') and critical ('''+critical+''')\n''')

    return exit_status

#Arguments logic:
#If no arguments
if sys.argv[1:] == []:
    parser.print_usage()
    parser.exit(status['UNKNOWN'],
                "ERROR: No arguments, write '"+parser.prog+" -h' for help\n")

if args.verbosity!=None:
    if args.verbosity>3:
        args.verbosity=3
    print "verbosity level = %i"%(args.verbosity)

#------------------------------------------------------------------------------
#plugin logic...
if args.verbosity>2:
    print "Plugin arguments:",args

#.....
#.....
#calculate value
#exit_status=define_status(value,args.warning,args.critical)
exit_status=define_status(5,args.warning,args.critical)
output = "The output of plugin"

mensage = exit_status + " " + output
if perfdata!="":
    mensage = mensage + '|' + perfdata
if longoutput!="":
    mensage = mensage + longoutput
print mensage
sys.exit(status[exit_status])


