# MonitorWindowsEventsApp
Multi-thread system for Windows Events real-time monitoring of N hosts and information sending by UDP and RSyslog protocol.

Uses the PyWin modules for integrating Python and Windows in order to get Windows Events logs, a Queue manager takes care of sending this information with UDP messages by RSyslog protocol (RFC 5424) to any final server or log collector. It uses sending intervals and auto-adjust to avoid data bursts problems, queue saturation, etc.

The data gathered of each Windows Event is: EventDate, UserSid, ProcessSource, HostSource (defined in Config.ini), Category, ID, Type, EventTag (System, Application or Security), EventContent and AppTimestamp. -*included with key-value dict inside the UDP RSyslog message content*-

## Prerequisites:
- Python v3*
- Windows (because of Windows API dependencies)
- Python path added to environment variables of Windows (automatic with Python latest versions installation) 

## Installing - Run:
Only execute the startApp.bat

## Configuration:
*Edit the Config.ini file under Config folder.*
Main necessary configuration:
- Add as many Windows hosts as you want to get their events info (using IP or host name in MONITORWINDOWSHOSTS file section). Example: 'windows01=127.0.0.1'
- Establish IP and Port for the destination server of RSyslog messages (SYSTEMIP and SYSTEMPORT of RSYSLOG file section)

#### Other Configurations and Queue details:
In Config.ini:
- WFS is the sample rate for events listening (seconds), incrementing this will probably get blocks of more events each time. However, no events will be lost because of this increment.
- WFQ is the sending interval, so it´s the time that Queue will wait before send one event message if it has someone.
With AUTOADJUST_WFQOUT = True (recommend!) this time will change dinamically depending on the number of events waiting.
- MAXCONTRIES is the number of consecutive failed connection tries to any Windows host before consider it has died and kill its thread.
- AUTOADJUST_WFQTHRESHOLDFORSTART is the main auto adjust parameter of the queue. ('int' related to the number of messages in queue) The lower, the greater will be the CPU consumption, because the queue output will be faster.

#### Running Screenshot:

![Alt Text](https://i.imgur.com/JhWwLZ2.png)
