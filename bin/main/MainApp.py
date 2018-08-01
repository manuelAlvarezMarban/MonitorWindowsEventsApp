#-*- coding: iso-8859-1 -*-

import traceback
import sys
import queue
import logging
from time import localtime, strftime, sleep
from bin.main.ConfigManager import initAppConfig
from bin.threads.WEventsQueueManagerThread import WEventsQueueManager
from bin.threads.EventsListenerThread import EventsListenerThread

'''
MonitorWindows multi-thread app Starter. Will monitor threads life.
Config.ini for setttings
'''

#*** VAR
#---------------------------------
InitDate = strftime("%Y-%m-%d_%H-%M", localtime())      #Application start timestamp
WeventsThreads = []                                     #Threads for Windows Hosts
WindowsNum = 0                                          #Num of Windows hosts whose events will be monitoring
ThreadsAlerted = []                                     #List of thread names that have ended and alert mail is already sent
AppThreadList = []                                      #Final list of all threads that app is running
#---------------------------------

#*** FUNCTIONS
#Main aux functions:  ------------

def initAppLogging(AppConfig, ModuleName, CurrentDate):
    """
    Initialization for app logging of own messages
    :param AppConfig: param from initAppConfig()
    :param ModuleName: must be __name__
    :param CurrentDate: app initialization timestamp
    :return: logger
    """

    #Level DEBUG or INFO for show debug messages or not:
    logginglevel = logging.DEBUG

    logging.basicConfig(
        format = '%(asctime)s - %(name)s - %(levelname)-8s %(message)s',
        level = logginglevel,
        datefmt = '%Y-%m-%d %H:%M:%S')

#----------------------------------

#***********************************************************************************
#********************************* Start config for app ****************************
#***********************************************************************************
try:

    if not ('WIN' in sys.platform.upper()) and (sys.platform.upper() != 'DARWIN'):
        print('App must run under Windows System !')
        sys.exit(-1)

    #AppConfig:
    Config = initAppConfig()

except Exception as e:
    template = "An exception of type {0} occurred in Main. Starting Config. Arguments:\n{1!r}{2}"
    message = template.format(type(e).__name__, e.args, traceback.format_exc())
    print(message)
    print('\n--- App cannot start ---')
    sys.exit(-1)

#Start logging for all app modules and get logger for current:
initAppLogging(Config, __name__, InitDate)
log = logging.getLogger(__name__)

log.info('..Config for app loaded Ok..')

#***********************************************************************************
#************************************ Threads prepare ******************************
#***********************************************************************************
log.info('..Starting app Threads..')

try:

    # - WindowsEventsThreads: (One for earch host) + One Queue Thread:
    wq = queue.Queue()                       #WindowsEvents Threads will share the Queue for Rsyslog sending
    wqManagerThread = WEventsQueueManager (log, Config, wq)
    wqManagerThread.setName('QueueManager')
    #--
    windowshostsName = Config.options('MONITORWINDOWSHOSTS')
    windowshostsAddress = []
    for windowshost in windowshostsName:
        waddress = Config.get('MONITORWINDOWSHOSTS', windowshost)
        windowshostsAddress.append(waddress)
        log.debug(windowshost+' to monitoring: '+waddress)
        weventsThread = EventsListenerThread (log, Config, windowshost, waddress, wq)
        weventsThread.setName(windowshost)
        WeventsThreads.append(weventsThread)

    WindowsNum = len(windowshostsAddress)
    log.info(str(WindowsNum)+' host/s Windows will be listened.')

    #************************************* Threads start ********************************
    # *********(and add all threads to total list...)*************************************

    #starts all wlistener threads and the wqmanagerthread:
    wqManagerThread.start()
    AppThreadList.append(wqManagerThread)
    for wthread in WeventsThreads:
        wthread.start()
        AppThreadList.append(wthread)

    #*************************************************************************************************************
    log.info(str(len(AppThreadList))+' threads will be used by the App.')

    log.info('**************************** App initiated. Monitoring Windows Systems. *****************************')
    sys.exit(0)
    #************* Monitoring that threads are alive during app execution: ****************
    # *************************************************************************************

    finish = False
    closeCauseError = False         #App could be closed if one windows thread die..
    while not finish:

        sleep(120)    #Check threads state with 2 minutes period..

        if closeCauseError:                #Close all Threads for finish app
            log.error('...Initiating app end cause some thread is died...')
            for wthread in WeventsThreads:
                wthread.finishThread()
            wqManagerThread.setFinish(True)
            closeCauseError = False

        #---------------------------------------------------
        # ****** Windows Events threads monitoring ******
        wcont = 0

        for thread in WeventsThreads:
            if not thread.is_alive():
                #closeCauseError = True             #Discomment for closing app if Windows Host thread die
                wcont += 1
                if not any(thread.getName() in s for s in ThreadsAlerted):
                    #--- (HERE some warning like mail sending could be done...)
                    ThreadsAlerted.append(thread.getName())
                    log.warn('[' + thread.getName() + '] Windows thread has died !')

        if not wqManagerThread.is_alive():
            closeCauseError = True                 #App will not send info if Queue die
            if not any(wqManagerThread.getName() in s for s in ThreadsAlerted):
                ThreadsAlerted.append(wqManagerThread.getName())
                log.warn('[' + thread.getName() + '] Queue thread has died !')

        #--------------------------------------------------------------------------------------------------
        if wcont == WindowsNum:           #If all threads have ended, close the app.
            log.warn('All threads has died. App will be closed.')
            finish = True

    log.warn('--- App has finished its execution!.---')

except Exception as e:
    template = "An exception of type {0} occurred in Main. Arguments:\n{1!r}{2}"
    message = template.format(type(e).__name__, e.args, traceback.format_exc())
    log.error(message)