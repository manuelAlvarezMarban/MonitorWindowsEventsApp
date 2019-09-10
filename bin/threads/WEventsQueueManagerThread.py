#-*- coding: iso-8859-1 -*-

from threading import Thread
from bin.syslog import SyslogSender
import time, traceback

'''Queue for gather events from threads and send them by RSyslog'''
class WEventsQueueManager(Thread):

    def __init__(self, log, appConfig, WindowsEventsQueue):

        self.myname = 'QueueManager'                                                        # Thread name
        self.log = log                                                                      # App logging
        self.wq = WindowsEventsQueue                                                        # Thread shared Queue
        self.appConfig = appConfig                                                          # App config
        self.finish = False                                                                 # Thread state
        self.fqout = float(self.appConfig.get('MONITORWINDOWS', 'WFQ'))                     # Sampling time
        self.syslog = SyslogSender.Syslog(appConfig.get('RSYSLOG', 'SYSTEMIP'),             # Syslog sender object
                                          appConfig.get('RSYSLOG', 'SYSTEMPORT'),
                                          'WindowsEventWE',
                                          appConfig.get('RSYSLOG', 'DATAENCODE'))
        self.autoadjust = True if self.appConfig.get('MONITORWINDOWS', 'AUTOADJUST_WFQOUT') == ('True' or 'true') else False
        self.fqoutstartwith = int(self.appConfig.get('MONITORWINDOWS', 'AUTOADJUST_WFQTHRESHOLDFORSTART'))
        self.autoadjustIncrement = True if  self.appConfig.get('MONITORWINDOWS', 'AUTOADJUST_WFQOUT_INCREMENT') == ('True' or 'true') else False
        self.incrementmax = float(self.appConfig.get('MONITORWINDOWS', 'AUTOADJUST_WFQOUT_INCREMENTMAX'))
        self.fqoutstartwithTwoThird = int(((self.fqoutstartwith * 2) / 3) + 1)              # Two third for decide decrement amount
        self.fqoutstartwithThird = int((self.fqoutstartwith / 3) + 1)                       # One third decide increment

        Thread.__init__(self)


    def run(self):


        def sendOneRow(self):
            '''
            Sending Function. Use Syslog object
            :param self:
            :return:
            '''

            # Extract one row of data from Queue to syslog sending to Graylog:
            msg = self.wq.get()
            print(msg)
            # We must associate each windows event type with Rsyslog level:
            if ('Type') in msg:
                if msg.get('Type').startswith('1') or msg.get('Type').startswith('2') or msg.get('Type').startswith('16'):
                    self.syslog.error(msg)
                    self.log.debug('---> Event (er) sent. ' + str(self.wq.qsize()) + ' in queue')

                if msg.get('Type').startswith('0') or msg.get('Type').startswith('4') or msg.get('Type').startswith('8'):
                    self.syslog.inf(msg)
                    self.log.debug('---> Event (inf) sent. ' + str(self.wq.qsize()) + ' in queue')

        #------------------------------------------------------------------------------------------------------------------

        self.log.info('QueueManager ok. Init with SenderRate: '+str(self.fqout)+' seconds.')

        while self.finish == False:

            time.sleep(self.fqout)

            try:

                currentQueueSize = self.wq.qsize()

                if (currentQueueSize == 0):
                    # -- queue is empty --
                    pass

                else:

                    # Extract one row of data from Queue to syslog sending to Graylog:
                    sendOneRow(self)


            except Exception as e:

                self.log.error('Error in Queue. ' + str(e))
                continue

            # ------------------------------------
            # --- AutoAdjust if it s activate: ---
            # ------------------------------------
            try:

                if self.autoadjust:

                    if currentQueueSize >= self.fqoutstartwith:                  #If size of queue bigger than threshold in Config, decrease fq in 5 sg else increase with different rates!

                        if self.fqout > 5.0:
                            self.fqout = self.fqout - 5.0
                            self.log.debug('AutoAdj - decrease FQ= ' + ("%0.2f" % self.fqout) + ' sc')
                        else:
                            if currentQueueSize <= self.fqoutstartwithTwoThird:
                                if self.fqout > 0.5:
                                    self.fqout = 0.5
                                    self.log.debug('AutoAdj - decrease FQ= ' + ("%0.2f" % self.fqout) + ' sc')
                            else:
                                if self.fqout > 0.05:                           #If Queue than two third of start, decrement to min
                                    self.fqout = 0.05
                                    self.log.debug('AutoAdj - decrease to min FQ= ' + ("%0.2f" % self.fqout) + ' sc')

                    else:
                        if self.autoadjustIncrement:
                            if currentQueueSize < self.fqoutstartwithThird:      #With less msgs in Queue than one third of start, FQ could be incremented

                                if currentQueueSize == 0:
                                    if self.fqout != self.incrementmax:
                                        self.fqout = self.fqout + 0.3
                                        if self.fqout >= self.incrementmax:      # <-- Max Threshold
                                            self.fqout = self.incrementmax
                                            self.log.debug('AutoAdj - incremented to Max= ' + ("%0.2f" % self.fqout) + ' sc')
                                        else:
                                            self.log.debug('AutoAdj - increase FQ= ' + ("%0.2f" % self.fqout) + ' sc')
                                else:
                                    if self.fqout != self.incrementmax:
                                        self.fqout = self.fqout + 0.1
                                        if self.fqout >= self.incrementmax:
                                            self.fqout = self.incrementmax
                                            self.log.debug('AutoAdj - incremented to Max= ' + ("%0.2f" % self.fqout) + ' sc')
                                        else:
                                            self.log.debug('AutoAdj - increase FQ= ' + ("%0.2f" % self.fqout) + ' sc')

            except Exception as e:

                self.log.error('Error in Autoadjust. ' + str(e))
                self.fqout = float( self.appConfig.get('MONITORWINDOWS', 'WFQ') )
                continue

        #***************** THREAD END
        # Send pending data to Graylog before thread ending:
        for i in range(0, self.wq.qsize()):
            sendOneRow(self)

        self.log.info('[WindowsEventsQueueManager] thread has been finished, managing pending data!')


    def setFinish(self,value):
        '''
        Finish thread method.
        :param value:
        :return:
        '''
        self.finish = value
