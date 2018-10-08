# file: rfcomm-client.py auth: Albert Huang <albert@csail.mit.edu> desc: simple demonstration of a client application that uses RFCOMM sockets
#       intended for use with rfcomm-server
#
# $Id: rfcomm-client.py 424 2006-08-24 03:35:54Z albert $

from bluetooth import *
import sys
import time

if sys.version < '3':
    input = raw_input

addr = None

if len(sys.argv) < 2:
    print("no device specified.  Searching all nearby bluetooth devices for")
    print("the SampleServer service")
else:
    addr = sys.argv[1]
    print("Searching for SampleServer on %s" % addr)

# search for the SampleServer service
#uuid = "94f39d29-7d6d-437d-973b-fba39e49d4ee"
service_matches = find_service( address = addr )

if len(service_matches) == 0:
    print("couldn't find the SampleServer service =(")
    sys.exit(0)

first_match = service_matches[0]
port = first_match["port"]
name = first_match["name"]
host = first_match["host"]

port = 6

print("connecting to \"%s\" on %s" % (name, host))

print port,name,host

def SendCommandAndGetResult( sock, cmd ):
    cmd += "\r\n"
    sock.send(cmd)
    rdata = ""
    try:
        while True:
            data = sock.recv(1024)
            rdata += data
            if data.find("\r\n") != -1:
                break
        print cmd[:2],"->",str(rdata.replace("\r\n",""))
    except btcommon.BluetoothError as x:
        print cmd[:2],"TIMEOUT"
        return False
    return True


def test(host,port):
    # Create the client socket
    sock=BluetoothSocket( RFCOMM )
    sock.connect((host, port))

    print("connected.")
    sock.settimeout(2)

    SendCommandAndGetResult( sock, "RS" )
    time.sleep(6)

    while True:
	for i1 in range(ord("A"),ord("Z")+1):
            for i2 in range(ord("A"),ord("Z")+1):
                cmd = chr(i1)+chr(i2)
          	if not SendCommandAndGetResult( sock, cmd ):
                    print "RESET!"
                    SendCommandAndGetResult( sock, "RS" )
                    time.sleep(6)
                    SendCommandAndGetResult( sock, "ID" )
		else:
                    SendCommandAndGetResult( sock, cmd )
                time.sleep(1)

    sock.close()


test( host, port )
