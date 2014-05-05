#!/usr/bin/python
#####################################################################
# Requisites:		Python 2, nginx compiled and configured with the HttpStubStatusModule module ( http://wiki.nginx.org/HttpStubStatusModule )
#####################################################################
# Author: 		Axel Amigo (contacto@amigoarnold.me)
# Created: 		31/08/2013
# Last Modification: 	31/08/2013
#####################################################################
# Description:		This script returns XML data for acting
#			like a Pandora FMS agent plugin.
#			More information at: http://wiki.pandorafms.com/index.php?title=Pandora:Documentation_en:Operations#Using_software_agent_plugins
#
# Returned modules:	Active connections: Number of active connections
#			Accepted connections: Number of accepted connections (Incremental)
#			Handled connections: Number of connections handled (Incremental)
#			Handled requests: Number of requests handled (Incremental)
#			Keep-alive connections: Number of keep-alive connections
#####################################################################
# CHANGELOG:
# Revision 1.0  31/08/2013 Axel Amigo
#   The script was created
#####################################################################

from HTMLParser import HTMLParser
import httplib
import sys
import string

def print_help():
	print "Usage example: %s 127.0.0.1" % (str(str(sys.argv[0])))

def print_module(module_name,data,is_incremental):
	print "<module>"
	print "<name><![CDATA["+module_name+"]]></name>"
	if is_incremental:
		print "<type><![CDATA[generic_data_inc]]></type>"
	else:
		print "<type><![CDATA[generic_data]]></type>";
	print "<data><![CDATA["+data+"]]></data>"
	print "</module>"


class MyHTMLParser(HTMLParser):
    def __init__(self):
    	HTMLParser.__init__(self)
	self.information=[]
    def handle_data(self, data):
	self.information=filter(None,[word.strip(string.punctuation)
                 for word in data.replace(';','; ').split()
                 ])

if len(sys.argv)==1:
	print "I need a parameter with the IP address of the nginx server"
	print_help()
	sys.exit()
elif len(sys.argv)>2:
	print "You passed me too much parameters"
	print_help()
	sys.exit()

nginx_ip=str(sys.argv[1])
try:
	conn = httplib.HTTPConnection(nginx_ip,timeout=2)
	conn.request("GET", "/nginx_status")
except:
	#Fail silently
	sys.exit()

r1 = conn.getresponse()

data = r1.read()

parser=MyHTMLParser()
parser.feed(data)

#Information will be something like ['Active', 'connections', '1', 'server', 'accepts', 'handled', 'requests', '29', '29', '27', 'Reading', '0', 'Writing', '1', 'Waiting', '0']
conn.close()
try:
	active_connections=parser.information[2]
	accepted_connections=parser.information[7]
	handled_connections=parser.information[8]
	handled_requests=parser.information[9]
	keep_alive_connections=parser.information[15]
	print_module("Active connections",active_connections,False)
	print_module("Accepted connections",accepted_connections,True)
	print_module("Handled connections",handled_connections,True)
	print_module("Handled requests",handled_requests,True)
	print_module("Keep-alive connections",keep_alive_connections,False)
except:
	#This exceptions means that they used this plugin in some strange URL like google or something like that
	#Fail silently.
	sys.exit()
