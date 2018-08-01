#-*- coding: iso-8859-1 -*-
from threading import Thread
import time, traceback, sys
from time import localtime, strftime
import win32.win32evtlog as win32evtlog, win32.win32security as win32security, win32.win32event as win32event

'''
Thread for monitoring of one Windows Host Events -> eventvwr.msc (Events Reg)
'''
class EventsListenerThread(Thread):

    def __init__(self, log, appConfig, windowshostname, windowshostaddress, wQueue):

        #****************
        def getNumOfEvents(self, eventType):
            log_handle = win32evtlog.OpenEventLog(self.waddress, eventType)
            total = win32evtlog.GetNumberOfEventLogRecords(log_handle)
            win32evtlog.CloseEventLog(log_handle)

            return total
        # ****************
        self.conTries = 0
        self.handleInvalidCount = 0                                                 #Error tath occurs some times count
        self.maxInvalidCount = 50
        self.maxBurst = int(appConfig.get('MONITORWINDOWS', 'MAXBURSTEVENTS'))
        self.maxConTries = int(appConfig.get('MONITORWINDOWS', 'MAXCONTRIES'))
        self.log = log
        self.appConfig = appConfig
        self.wname = windowshostname
        self.waddress = windowshostaddress
        self.queue = wQueue
        self.fs = appConfig.get('MONITORWINDOWS', 'WFS')
        self.active = True
        self.listenSystem = appConfig.get('WINDOWSEVENTS', 'SYSTEM')
        self.listenApplication = appConfig.get('WINDOWSEVENTS', 'APPLICATION')
        self.listenSecurity = appConfig.get('WINDOWSEVENTS', 'SECURITY')
        self.SystemN = 0
        self.ApplicationN = 0
        self.SecurityN = 0
        if self.listenSystem == ('True' or 'true'):
            try:
                self.SystemN = getNumOfEvents(self, 'System')
            except Exception as e:
                self.log.warn('Error: Couldnt access to System events in '+self.wname+'. Privileges?')

        self.listenApplication = appConfig.get('WINDOWSEVENTS', 'APPLICATION')
        if self.listenApplication == ('True' or 'true'):
            try:
                self.ApplicationN = getNumOfEvents(self, 'Application')
            except Exception as e:
                self.log.warn('Error: Couldnt access to Application events in '+self.wname+'. Privileges?')

        self.listenSecurity = appConfig.get('WINDOWSEVENTS', 'SECURITY')
        if self.listenSecurity == ('True' or 'true'):
            try:
                self.SecurityN = getNumOfEvents(self, 'Security')
            except Exception as e:
                self.log.warn('Error: Couldnt access to Security events in '+self.wname+'. Privileges?')

        Thread.__init__(self)

    def run(self):

        '''
        Update the events count
        '''
        def updateCurrentNum(self, eventType, num):

            if eventType == 'System':
                self.SystemN = num
                self.log.debug('Waiting next ' + eventType + 'Event: ' + str(self.SystemN + 1))
            elif eventType == 'Application':
                self.ApplicationN = num
                self.log.debug('Waiting next ' + eventType + 'Event: ' + str(self.ApplicationN + 1))
            elif eventType == 'Security':
                self.SecurityN = num
                self.log.debug('Waiting next ' + eventType + 'Event: ' + str(self.SecurityN + 1))

        '''
        Get num of events
        '''
        def getNumOfEvents(self, eventType):

            log_handle = win32evtlog.OpenEventLog(self.waddress, eventType)
            total = win32evtlog.GetNumberOfEventLogRecords(log_handle)
            win32evtlog.CloseEventLog(log_handle)
            self.handleInvalidCount = 0             #reset count

            return total

        '''
        Get events info
        '''
        def getEventOfNumber(self, eventType, pendingEvents):

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
                    #self.log.debug('Error al cerrar log tras excepcion! Controlador no valido ?')
                    pass
                template = "An exception of type {0} occurred in EventsListenerThread(getEventsData). Arguments:\n{1!r}{2}"
                message = template.format(type(e).__name__, e.args, traceback.format_exc())
                eventDictsList.clear()                        #Return empty list to add nothing to QueueManager

            finally:

                return eventDictsList

        def listenForNewEvent(self, eventType):

            num = getNumOfEvents(self, eventType)
            self.conTries = 0  # After OK reset connection tries (for consider or not Windows host died)
            if eventType == 'System':
                currentNum = self.SystemN
            elif eventType == 'Application':
                currentNum = self.ApplicationN
            elif eventType == 'Security':
                currentNum = self.SecurityN


            if num > currentNum:
                if currentNum != 0:                             # Correct init care
                    pendingEvents = num - currentNum            # Could be more than one new event since last sampling
                    if pendingEvents > self.maxBurst:           # In server some times return anormal Number for App Events or care log rotation
                        pendingEvents = 1
                    self.log.info('('+self.wname+'-'+self.waddress+') '+str(pendingEvents)+' New Event/s of type: '+eventType+'!')
                    eventDictList = getEventOfNumber(self, eventType, pendingEvents)
                    for eventDict in eventDictList:
                        self.log.debug(eventDict)
                        if bool(eventDict):
                            self.queue.put(eventDict)           #Queue to send Event
                    updateCurrentNum(self, eventType, num)
                else:
                    updateCurrentNum(self, eventType, num)
                    self.log.debug('Numero de eventos fijado correctamente, estaba mal iniciado.')

        self.log.info('Initiated thread for Windows: '+self.wname+' ('+self.waddress+'). |sampling rate '+str(float(self.fs)*1000)+' msg| - Burst: '+str(self.maxBurst))

        while self.active:

            #Start Events Monitoring
            try:

                time.sleep(float(self.fs))

                if self.listenSystem == ('True' or 'true'):
                    listenForNewEvent(self, 'System')
                if self.listenApplication == ('True' or 'true'):
                    listenForNewEvent(self, 'Application')
                if self.listenSecurity == ('True' or 'true'):
                    listenForNewEvent(self, 'Security')

            except Exception as e:
                template = "An exception of type {0} occurred in WindowsEventsListenerThread. Arguments:\n{1!r}{2}"
                message = template.format(type(e).__name__, e.args, traceback.format_exc())

                eventDict = {}

                self.conTries += 1
                self.log.warn('Error RPC connecting to Windows, ¿died? - tries ('+str(self.conTries)+'). Max: '+str(self.maxConTries))
                eventDict['EventDate'] = 'NO'
                eventDict['UserSid'] = 'NO'
                eventDict['ProcessSource'] = 'LogGatherApp'
                eventDict['HostSource'] = str(self.wname+'-'+self.waddress)
                eventDict['Category'] = 'NO'
                eventDict['ID'] = 'NO'
                eventDict['Type'] = str(1) + ':' + 'Error'
                eventDict['EventTag'] = 'WindowsEvent Error'
                eventDict['EventContent'] = ['Error al pedir eventos Windows, intento '+str(self.conTries)]
                mTime = strftime("%Y-%m-%d %H:%M:%S", localtime())
                eventDict['AppTimestamp'] = mTime

                if self.conTries == self.maxConTries:
                    self.log.warn('Max tries reached, '+self.waddress+' host will be considered died !')
                    eventDict['EventContent'] = ['Max connection tries with Windows reached, '+str(self.wname+'-'+self.waddress)+' will be considered died !']
                    self.active = False                   #Close this thread, windows system died

                if bool(eventDict):
                    self.queue.put(eventDict)
                    time.sleep(30)                        #Wait to let Windows system recover after get events exception

                else:
                    self.log.error(message)

        self.log.warn('Events thread of '+self.wname+ ' has finished !')

    def finishThread(self):

        self.active = False