# MonitorWindowsEventsApp
Multi-thread app for real-time monitoring Windows Events of N hosts and send info by Syslog protocol to any final server.

The app uses the PyWin modules for integrating Python and Windows in order to get Windows Events info of all established hosts, 
a Queue manager takes care of sending this info by Syslog protocol (RFC 5424) to any server or log collector you have for BI or data use. 
With sending interval for server health care and auto-adjust for data bursts, etc.

The data gathered of Windows Events is: EventDate, UserSid, ProcessSource, HostSource (defined in Config.ini), Category, ID, Type, 
EventTag (System, Application or Security), EventContent and AppTimestamp. -*JSON inside the UDP Syslog message*-

## Prerequisites:
- Python v3*
- Windows System (because of Windows API dependencies)
- Python path added to environment variables of Windows (automatic with Python last versions installation) 

## Installing - Run:
Only execute the startApp batch script. (Must be in the project folder)

## Configuration:
*Edit the Config.ini file under Config folder.*
Mainly configuration you have to do:
- Add as many Windows hosts as you want to get their events info (using IP or host name in MONITORWINDOWSHOSTS file section)
- Establish IP and Port for the destination of Syslogs messages (SYSTEMIP and SYSTEMPORT of RSYSLOG file section)

#### Other Configuration and App details:
In Config.ini we have a section to timming, sending Queue, etc:
- WFS is the sampling rate for events listening (seconds), incrementing this will probably get blocks of more events each time. However, 
no events will be lost because of increment.
- WFQ is the sending interval, so it´s the time that Queue will wait before send one event info message if it has someone.
With AUTOADJUST_WFQOUT = True (recommend!) this time will be dinamically changing depending on the number of data gathered, for instance 
sending fast if many messages events are waiting.
- MAXCONTRIES is the number of consecutive failed connection tries to any Windows host before consider it has died.

#### App Screenshot:

![Alt Text](https://i.imgur.com/JhWwLZ2.png)
