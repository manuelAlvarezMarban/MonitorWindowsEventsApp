#-*- coding: iso-8859-1 -*-

import socket

"""
Class for UDP sending in syslog format to destination server.
"""

class Facility:
  "syslog facilities"
  KERN, USER, MAIL, DAEMON, AUTH, SYSLOG, \
  LPR, NEWS, UUCP, CRON, AUTHPRIV, FTP = range(12)

  LOCAL0, LOCAL1, LOCAL2, LOCAL3, \
  LOCAL4, LOCAL5, LOCAL6, LOCAL7 = range(16, 24)

class Level:
  "syslog levels"
  EMERG, ALERT, CRIT, ERR, \
  WARNING, NOTICE, INFO, DEBUG = range(8)

class Syslog:

     #syslog methods
    def __init__(self, hostip, port, servername, encode, facility=Facility.DAEMON):
        self.host = hostip
        self.port = int(port)
        self.facility = facility
        self.sourceserver = servername
        self.dataencode = encode
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def send(self, message, level):
        "Send a syslog message to remote host using UDP."
        data = "<%d>%s%s" % (level + self.facility*8, self.sourceserver+"_Json: ", message)
        self.socket.sendto(data.encode(self.dataencode), (self.host, self.port))

    def warn(self, message):
        "Send a syslog warning message."
        self.send(message, Level.WARNING)

    def notice(self, message):
        "Send a syslog notice message."
        self.send(message, Level.NOTICE)

    def error(self, message):
        "Send a syslog error message."
        self.send(message, Level.ERR)

    def inf(self, message):
        "Send a syslog info message."
        self.send(message, Level.INFO)

    def emer(self, message):
        "Send a syslog emergency message."
        self.send(message, Level.EMERG)