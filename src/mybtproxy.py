#!/usr/bin/python

import argparse
from bluetooth import *
from thread import start_new_thread
import time

verbose = False


def run_server( client_sock, sock ):
	while True:
		# read message from client
		msg = ""
		while True:
			msg += client_sock.recv(1024)
			if msg.find("\r\n") != -1:
				break
		print "->", str(msg.replace("\r\n", ""))

		# and write it to server
		sock.send(msg)

		# read message from server
		msg = ""
		while True:
			msg += sock.recv(1024)
			if msg.find("\r\n") != -1:
				break
		print "<-", str(msg.replace("\r\n", ""))

		# and write it to client
		client_sock.send(msg)


def doTheProxy( source ):

	# find service to be proxied

	service_matches = find_service( address=source )

	if len(service_matches) == 0:
		print("couldn't find the SampleServer service =(")
		sys.exit(0)

	for first_match in service_matches:
		port = first_match["port"]
		name = first_match["name"]
		host = first_match["host"]
		#port = 6

		# we open up a mock listen channel like the source one
		server_sock = BluetoothSocket(RFCOMM)
		server_sock.bind(("", PORT_ANY))
		server_sock.listen(1)

		server_port = server_sock.getsockname()[1]

		advertise_service( server_sock, "SampleServer", description=first_match["description"],
		                   provider=first_match['provider'], protocols=[first_match['protocol']],
		                   port=first_match['port'], service_classes= first_match['service-classes'],
		                   profiles=first_match['profiles'], service_id=first_match['service-id'] )

		print("Waiting for connection on RFCOMM channel %d" % server_port)

		client_sock, client_info = server_sock.accept()
		print("Accepted connection from ", client_info)

		# Create the client socket
		print("connecting to \"%s\" on %s" % (name, host))
		sock = BluetoothSocket(RFCOMM)
		sock.connect((host, port))

		print("connected.")

		start_new_thread( run_server, ( client_sock, sock, ))

		time.sleep(6000)


parser = argparse.ArgumentParser(description='My Bluetooth Proxy')
parser.add_argument("-d", "--source", help="device to proxy")
parser.add_argument("-v", "--verbose", action="store_true", help="verbose output")

args = parser.parse_args()

if not args.source:
	print "Need to specify device to proxy!"
	sys.exit(1)

if args.verbose:
	verbose = True

doTheProxy( args.source )