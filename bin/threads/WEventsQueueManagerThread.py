#-*- coding: iso-8859-1 -*-

from threading import Thread
from bin.syslog import SyslogSender
import time, traceback

'''Queue for gather events from threads and send them by RSyslog'''
class WEventsQueueManager(Thread):

    def __init__(self, log, appConfig, WindowsEventsQueue):

        self.myname = 'QueueManager'
        self.log = log
        self.wq = WindowsEventsQueue
        self.appConfig = appConfig
        self.finish = False
        self.fqout = float(self.appConfig.get('MONITORWINDOWS', 'WFQ'))
        self.syslog = SyslogSender.Syslog(appConfig.get('RSYSLOG', 'SYSTEMIP'),
                                          appConfig.get('RSYSLOG', 'SYSTEMPORT'), 'WindowsEventWE',
                                          appConfig.get('RSYSLOG', 'DATAENCODE'))
        self.autoadjust = self.appConfig.get('MONITORWINDOWS', 'AUTOADJUST_WFQOUT')
        if self.autoadjust == 'True' or 'true':
            self.fqoutstartwith = int(self.appConfig.get('MONITORWINDOWS', 'AUTOADJUST_WFQTHRESHOLDFORSTART'))
            self.autoadjustIncrement = self.appConfig.get('MONITORWINDOWS', 'AUTOADJUST_WFQOUT_INCREMENT')
            self.incrementmax = float(self.appConfig.get('MONITORWINDOWS', 'AUTOADJUST_WFQOUT_INCREMENTMAX'))
        Thread.__init__(self)

    def run(self):

        '''
        Sending Function
        :return:
        '''
        def sendOneRow(self):

            # Extract one row of data from Queue to syslog sending to Graylog:
            msg = self.wq.get()

            # We must associate each windows event type with Rsyslog level:
            if ('Type') in msg:
                if msg.get('Type').startswith('1') or msg.get('Type').startswith('2') or msg.get('Type').startswith('16'):
                    self.syslog.error(msg)
                    self.log.debug('---> Traza (er) enviada. Queda/n ' + str(self.wq.qsize()) + ' en cola')

                if msg.get('Type').startswith('0') or msg.get('Type').startswith('4') or msg.get('Type').startswith('8'):
                    self.syslog.inf(msg)
                    self.log.debug('---> Traza (inf) enviada. Queda/n ' + str(self.wq.qsize()) + ' en cola')

        #------------------------------------------------------------------------------------------------------------------

        self.log.info('Thread for Sending Queue initiated. Sender rate: '+str(self.fqout)+' seconds.')
        while self.finish == False:

            time.sleep(float(self.fqout))

            try:

                if (self.wq.qsize() == 0):
                    self.log.debug('\t\t WQueue empty! waiting for data..')

                else:

                    # Extract one row of data from Queue to syslog sending to Graylog:
                    sendOneRow(self)


            except Exception as e:
                template = "An exception of type {0} occurred in QueueManagerThread. Arguments:\n{1!r}{2}"
                message = template.format(type(e).__name__, e.args, traceback.format_exc())
                self.log.error(message)
                continue

                # AutoAdjust if it s activate:
            try:

                if self.autoadjust == 'True' or 'true':
                    if self.wq.qsize() >= self.fqoutstartwith:  # If size of queue bigger than 5, decrease fq in 5 sg else increase
                        if self.fqout > 5.0:
                            self.fqout = self.fqout - 5.0
                            self.log.debug('AutoAdj - decrease FQ= ' + str(self.fqout) + ' sc')
                        else:
                            if self.wq.qsize() < 3:
                                if self.fqout != 2.0:
                                    self.fqout = 2.0
                                    self.log.debug('AutoAdj - decrease FQ= ' + str(self.fqout) + ' sc')
                            else:
                                if self.fqout != 1.0:
                                    self.fqout = 1.0
                                    self.log.debug('AutoAdj - decrease to min FQ= ' + str(self.fqout) + ' sc')
                    else:
                        if self.autoadjustIncrement == 'True' or 'true':
                            if self.wq.qsize() <= 2:
                                if self.wq.qsize() == 0:
                                    self.fqout = self.fqout + 5.0
                                    if self.fqout > self.incrementmax:  # <-- Max Threshold
                                        self.fqout = self.incrementmax
                                    else:
                                            self.log.debug('AutoAdj - increase FQ= ' + str(self.fqout) + ' sc')
                                else:
                                    self.fqout = self.fqout + 2.0
                                    if self.fqout > self.incrementmax:
                                        self.fqout = self.incrementmax
                                    else:
                                        self.log.debug('AutoAdj - increase FQ= ' + str(self.fqout) + ' sc')

            except Exception as e:
                template = "An exception of type {0} occurred in QueueManagerThread - AutoadjustFQ. Arguments:\n{1!r}{2}"
                message = template.format(type(e).__name__, e.args, traceback.format_exc())
                self.log.error(message)
                self.fqout = 30.0
                continue

        #***************** THREAD END
        # Send pending data to Graylog before thread ending:
        for i in range(0, self.wq.qsize()):
            sendOneRow(self)

        self.log.info('[WindowsEventsQueueManager] thread has been finished, managing pending data!')


    '''
    Finish thread method
    '''
    def setFinish(self,value):

        self.finish = value