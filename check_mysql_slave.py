#!/usr/bin/python
# Use at your own risk.
# Written mainly to get a handle on how to connect to MySQL via Python,
# as well as use command line args.

# The script can optionally change the color on a blink(1) device as a visual
# status alert if you want.  Possibly useful if you want to run the script
# in a loop in the background.
# blink(1) details here: http://thingm.com/products/blink-1.html



import MySQLdb as mdb
import sys
import argparse
from subprocess import call

# Set up available parameters.
parser = argparse.ArgumentParser()
parser.add_argument("-s","--server_ip",help="server ip of the mysql slave to check")
parser.add_argument("-u","--mysql_user",help="mysql user name for access")
parser.add_argument("-p","--mysql_passwd",help="mysql password")
parser.add_argument("-d","--mysql_db",
                    help="database name for connection.  default==test",default="test")
parser.add_argument("-P","--mysql_port",default=3306,type=int,
                    help="port mysql server is listening on.  default==3306")
parser.add_argument("-b","--blink", action="store_true",
                    help="also send outpout to blink(1).  green == ok, red == stopped, orange == delay")
args = parser.parse_args()
if args.server_ip == None:
    print "A server name or IP is mandatory."
    sys.exit()
if args.mysql_user == None:
    print "A mysql user must be specified."
    sys.exit()
if args.mysql_passwd == None:
    print "A mysql password must be specified."
    sys.exit()

server_ip = args.server_ip
mysql_user = args.mysql_user
mysql_passwd = args.mysql_passwd
mysql_db = args.mysql_db
mysql_port = args.mysql_port

con = None


try:

    con = mdb.connect(host=server_ip, user=mysql_user, 
        passwd=mysql_passwd, db=mysql_db, port=mysql_port);

    cur = con.cursor()
    cur.execute("SHOW SLAVE STATUS")

    data = cur.fetchone()
    
    # The Seconds_Behind_Master is field 32 (counting from zero), so we print that.
    if data[32] == 0:
        print "Server",server_ip,"is in sync with",data[32],"seconds of delay."
        if args.blink:
	    # blink setting: ./blink1-tool --rgb 11,255,53
	    call(["/usr/local/bin/blink1-tool","--rgb","11,255,53"])
    if data[32] == None:
        print "Server",server_ip,"has a replication problem: Seconds_Behind_Master is reporting NULL!"
        if args.blink: 
            # blink setting: ./blink1-tool --rgb 255,28,32
	    call(["/usr/local/bin/blink1-tool","--rgb", "255,28,32"])
    if data[32] > 0:
        print "Server",server_ip,"is experiencing replication delay.  It appears to be",data[32],"seconds behind."
        if args.blink:
            call(["/usr/local/bin/blink1-tool","--rgb","255,145,17"])

    
    
except mdb.Error, e:
  
    print "Error %d: %s" % (e.args[0],e.args[1])
    sys.exit(1)
    
finally:    
        
    if con:    
        con.close()
