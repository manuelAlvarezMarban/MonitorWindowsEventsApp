#-*- coding: iso-8859-1 -*-
from threading import Thread
import time
from time import localtime, strftime
import win32.win32evtlog as win32evtlog, win32.win32security as win32security, win32.win32event as win32event
import win32api

'''
Thread for monitoring of one Windows Host Events -> eventvwr.msc (Events Reg)
'''
class EventsListenerThread(Thread):

    def __init__(self, log, appConfig, windowshostname, windowshostaddress, wQueue):

        #****************                                                          # Define Host Events State at start.
        def getNumOfEvents(self, eventType):
            '''
            Get current event id/num.
            :param self:
            :param eventType:
            :return:
            '''

            log_handle = win32evtlog.OpenEventLog(self.waddress, eventType)
            total = win32evtlog.GetNumberOfEventLogRecords(log_handle)
            win32evtlog.CloseEventLog(log_handle)

            return total
        # ****************
        self.conTries = 0                                                                                                       # Remote host connection tries
        self.maxBurst = int(appConfig.get('MONITORWINDOWS', 'MAXBURSTEVENTS'))                                                  # Max sending burst
        self.maxConTries = int(appConfig.get('MONITORWINDOWS', 'MAXCONTRIES'))                                                  # Max Conn tries until consider host died
        self.log = log                                                                                                          # App logging
        self.appConfig = appConfig                                                                                              # App config
        self.wname = windowshostname                                                                                            # Windows host name for this thread
        self.waddress = windowshostaddress                                                                                      # Windows host dir for this thread
        self.queue = wQueue                                                                                                     # Thread shared Queue
        self.fs = float(appConfig.get('MONITORWINDOWS', 'WFS'))                                                                 # Events sampling time
        self.active = True                                                                                                      # Thread State
        self.listenSystem = True if appConfig.get('WINDOWSEVENTS', 'SYSTEM') == ('True' or 'true') else False                   # Listen Windows System Events
        self.listenApplication = True if appConfig.get('WINDOWSEVENTS', 'APPLICATION') == ('True' or 'true') else False         # Listen Windows App Events
        self.listenSecurity = True if appConfig.get('WINDOWSEVENTS', 'SECURITY') == ('True' or 'true') else False               # Listen Windows Security Events
        self.SystemN = 0
        self.ApplicationN = 0
        self.SecurityN = 0

        # -- Start thread:
        if self.listenSystem:
            try:
                self.SystemN = getNumOfEvents(self, 'System')
            except Exception as e:
                self.log.warning('Error: Couldnt access to System events in '+self.wname+'. Privileges?')

        if self.listenApplication:
            try:
                self.ApplicationN = getNumOfEvents(self, 'Application')
            except Exception as e:
                self.log.warning('Error: Couldnt access to Application events in '+self.wname+'. Privileges?')

        if self.listenSecurity:
            try:
                self.SecurityN = getNumOfEvents(self, 'Security')
            except Exception as e:
                self.log.warning('Error: Couldnt access to Security events in '+self.wname+'. Privileges?')

        if win32api.GetVersion() & 0x80000000:
            print ("App only runs on WindowsNT family.")
            self.active = False
            return

        Thread.__init__(self)


    def run(self):


        def updateCurrentNum(self, eventType, num):
            '''
            Update the events count.
            :param self:
            :param eventType:
            :param num:
            :return:
            '''

            if eventType == 'System':
                self.SystemN = num
                self.log.debug('Waiting next ' + eventType + 'Event: ' + str(self.SystemN + 1))
            elif eventType == 'Application':
                self.ApplicationN = num
                self.log.debug('Waiting next ' + eventType + 'Event: ' + str(self.ApplicationN + 1))
            elif eventType == 'Security':
                self.SecurityN = num
                self.log.debug('Waiting next ' + eventType + 'Event: ' + str(self.SecurityN + 1))


        def getNumOfEvents(self, eventType):
            '''
            Get num of events.
            :param self:
            :param eventType:
            :return:
            '''

            log_handle = win32evtlog.OpenEventLog(self.waddress, eventType)
            total = win32evtlog.GetNumberOfEventLogRecords(log_handle)
            win32evtlog.CloseEventLog(log_handle)

            return total


        def getEventOfNumber(self, eventType, pendingEvents):
            '''
            Get events info.
            :param self:
            :param eventType:
            :param pendingEvents:
            :return:
            '''

            def getNameOfType(type):

                switcherDict = {
                    0: 'Success',
                    1: 'Error',
                    2: 'Warning',
                    4: 'Information',
                    8: 'Audit Success',
                    16: 'Audit Failure'
                }
                return switcherDict.get(type, "NoDefinido")

            try:
                eventDictsList = []

                #------------ READ EVENTS OF LOG ----------------
                log_handle = win32evtlog.OpenEventLog(self.waddress, eventType)
                flags = win32evtlog.EVENTLOG_BACKWARDS_READ | win32evtlog.EVENTLOG_SEQUENTIAL_READ

                while 1:

                    events = win32evtlog.ReadEventLog(log_handle, flags, 0)

                    if not events:
                        break

                    #------------------------ Extract as many events as are pending ---------------------------:
                    for i in range (pendingEvents):

                        event = events[i]

                        #***************** Extract Event data:
                        eventDict = {}
                        pywintime = event.TimeGenerated
                        timewithformat = str(pywintime.year) + '-' + str(pywintime.month).rjust(2, '0') + '-' + str(
                                    pywintime.day).rjust(2, '0') + '_' + str(pywintime.hour).rjust(2, '0') + ':' + str(
                                    pywintime.minute).rjust(2, '0') + ':' + str(pywintime.second).rjust(2, '0')
                        eventDict['EventDate'] = timewithformat

                        if event.Sid is not None:
                            sidDesc = None
                            try:
                                domain, user, typ = win32security.LookupAccountSid(self.waddress, event.Sid)
                                sidDesc = "%s/%s" % (domain, user)
                            except win32security.error:
                                sidDesc = str(object.Sid)

                            eventDict['UserSid'] = sidDesc
                        else:
                            eventDict['UserSid'] = 'NotDefined'

                        eventDict['ProcessSource'] = event.SourceName

                        eventDict['HostSource'] = str(self.wname+'-'+self.waddress)

                        eventDict['Category'] = str(event.EventCategory)

                        eventDict['ID'] = str(event.EventID)

                        eventDict['Type'] = str(event.EventType) + ':' + getNameOfType(
                                    event.EventType)  # 0->Success, 1->Error, 2->Warning, 4->Information, 8->Audit Success, 16->Audit Failure

                        eventDict['EventTag'] = 'WindowsEvent ' + eventType

                        data = event.StringInserts
                        if data:
                            msgs = []
                            for msg in data:
                                msgs.append(msg)
                            eventDict['EventContent'] = msgs
                        else:
                            eventDict['EventContent'] = 'NotDefined'

                        mTime = strftime("%Y-%m-%d %H:%M:%S", localtime())
                        eventDict['AppTimestamp'] = mTime

                        eventDictsList.append(eventDict)
                        #-----------------------------END reading Events

                    win32evtlog.CloseEventLog(log_handle)

                    break               #Exit while and exit


            except Exception as e:
                try:
                    win32evtlog.CloseEventLog(log_handle)
                except:
                    pass
                self.log('Error with event info. ' + str(e))
                eventDictsList.clear()                        #Return empty list to add nothing to QueueManager

            finally:

                return eventDictsList


        def listenForNewEvent(self, eventType):
            '''
            Check if new event exists.
            :param self:
            :param eventType:
            :return:
            '''

            num = getNumOfEvents(self, eventType)
            self.conTries = 0                                   # After OK reset connection tries
            if eventType == 'System':
                currentNum = self.SystemN
            elif eventType == 'Application':
                currentNum = self.ApplicationN
            elif eventType == 'Security':
                currentNum = self.SecurityN


            if num > currentNum:

                if currentNum != 0:                             # Correct init care
                    pendingEvents = num - currentNum            # New event could be more than one since last sampling

                    if pendingEvents > self.maxBurst:
                        pendingEvents = 1
                        self.log.warning('Max Burst Reached! Only one will be sent.')

                    self.log.info('('+self.wname+'-'+self.waddress+') '+str(pendingEvents)+' New Event/s of type: '+eventType)

                    # -- Put events in Queue and update state:
                    eventDictList = getEventOfNumber(self, eventType, pendingEvents)
                    if not eventDictList:
                        self.log.warning(' ---- Event info empty or incorrect! (PyWin/Windows API error?) ----')
                    for eventDict in eventDictList:
                        self.log.debug(eventDict)
                        if bool(eventDict):
                            self.queue.put(eventDict)           #Queue to send Event
                    updateCurrentNum(self, eventType, num)

                else:
                    updateCurrentNum(self, eventType, num)
                    self.log.debug('Events count now correct, bad init.')


        # ***************************************************************
        # ********************* Thread Start ****************************
        # ***************************************************************
        self.log.info('Initiated thread for Windows: '+self.wname+' ('+self.waddress+'). |sampling rate '+str(float(self.fs)*1000)+' msg| - Burst: '+str(self.maxBurst))

        while self.active:

            #Start Events Monitoring
            try:

                time.sleep(self.fs)

                if self.listenSystem:
                    listenForNewEvent(self, 'System')
                if self.listenApplication:
                    listenForNewEvent(self, 'Application')
                if self.listenSecurity:
                    listenForNewEvent(self, 'Security')

            except Exception as e:

                self.conTries += 1
                self.log.warn('Error RPC connecting to Windows, ¿died? - tries (' + str(self.conTries) + '). Max: ' + str(self.maxConTries))

                # -- Send Rsyslog with error too:
                eventDict = {}
                eventDict['EventDate'] = 'NO'
                eventDict['UserSid'] = 'NO'
                eventDict['ProcessSource'] = 'LogGatherApp'
                eventDict['HostSource'] = str(self.wname+'-'+self.waddress)
                eventDict['Category'] = 'NO'
                eventDict['ID'] = 'NO'
                eventDict['Type'] = str(1) + ':' + 'Error'
                eventDict['EventTag'] = 'WindowsEvent Error'
                eventDict['EventContent'] = ['Error:' + str(e) + ', Tries: '+str(self.conTries)]
                mTime = strftime("%Y-%m-%d %H:%M:%S", localtime())
                eventDict['AppTimestamp'] = mTime

                if self.conTries == self.maxConTries:
                    self.log.warn('Max tries reached, '+self.waddress+' host will be considered died !')
                    eventDict['EventContent'] = ['Max connection tries with Windows reached, '+str(self.wname+'-'+self.waddress)+' will be considered died !']
                    self.active = False                   #Close this thread, windows system died...

                if bool(eventDict):
                    self.queue.put(eventDict)
                    time.sleep(30)                        #Wait to let Windows system recover after get events exception


        self.log.warn('Events thread of '+self.wname+ ' has finished !')


    def finishThread(self):
        '''
        End Thread.
        :return:
        '''

        self.active = False