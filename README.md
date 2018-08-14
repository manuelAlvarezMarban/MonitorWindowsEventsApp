# MonitorWindowsEventsApp
Multi-thread app for real-time monitoring Windows Events of N hosts and information sending by Syslog protocol to any final server.

The app uses the PyWin modules for integrating Python and Windows in order to get Windows Events logs of all established hosts, 
a Queue manager takes care of sending this information by Syslog protocol (RFC 5424) to any server or log collector you may have for BI or data exploitation. 
It uses sending intervals for server health caring and auto-adjust for avoid data bursts problems, queue saturation, etc.

The data gathered of Windows Events is: EventDate, UserSid, ProcessSource, HostSource (defined in Config.ini), Category, ID, Type, EventTag (System, Application or Security), EventContent and AppTimestamp. -*JSON inside the UDP Syslog message*-

## Prerequisites:
- Python v3*
- Windows System (because of Windows API dependencies)
- Python path added to environment variables of Windows (automatic with Python latest versions installation) 

## Installing - Run:
Only execute the startApp batch script. (Must be in the project folder)

## Configuration:
*Edit the Config.ini file under Config folder.*
Main configuration you have to do:
- Add as many Windows hosts as you want to get their events info (using IP or host name in MONITORWINDOWSHOSTS file section)
- Establish IP and Port for the destination server of Syslog messages (SYSTEMIP and SYSTEMPORT of RSYSLOG file section)

#### Other Configuration and App details:
In Config.ini we have a section to timing, sending Queue configuration, etc:
- WFS is the sample rate for events listening (seconds), incrementing this will probably get blocks of more events each time. However, no events will be lost because of this increment.
- WFQ is the sending interval, so it´s the time that Queue will wait before send one event info message if it has someone.
With AUTOADJUST_WFQOUT = True (recommend!) this time will be dinamically changing depending on the number of data gathered, for instance, sending fast if many messages events are waiting.
- MAXCONTRIES is the number of consecutive failed connection tries to any Windows host before consider it has died.
- AUTOADJUST_WFQTHRESHOLDFORSTART is the main auto adjust parameter for the queue. (Is an int related to the number of messages in queue) The lower, the greater will be the CPU consumption, cause the queue output will be faster. -Even so, depending on the queue size-.

#### App Screenshot:

![Alt Text](https://i.imgur.com/JhWwLZ2.png)
