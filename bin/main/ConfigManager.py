#-*- coding: iso-8859-1 -*-
import os
import configparser
import bin.utils.Exceptions as myExceptions

def initAppConfig():
    """
    Start config from project .ini file.
    :return: returns Config data
    """
    cwd = os.getcwd()                                       #(first need to get local path with cwd)
    if '\\bin\\' in cwd:                                    #Depends on where the main.py is called
        cwd = cwd[0: cwd.index('\\bin\\')]
    configpath = os.path.join(cwd, "Config")
    configpath = os.path.join(configpath, "Config.ini")
    Config = configparser.ConfigParser()
    Config.read(configpath)

    #**************** Verifications:

    if len(Config.sections()) != 5:
        raise myExceptions.ConfigNumSections

    try:
        int(Config.get('MONITORWINDOWS', 'AUTOADJUST_WFQTHRESHOLDFORSTART'))
    except:
        raise myExceptions.ConfigOptionMustBeInt('AUTOADJUST_WFQTHRESHOLDFORSTART')
    try:
        int(Config.get('MONITORWINDOWS', 'MAXCONTRIES'))
    except:
        raise myExceptions.ConfigOptionMustBeInt('MAXCONTRIES')
    try:
        int(Config.get('MONITORWINDOWS', 'MAXBURSTEVENTS'))
    except:
        raise myExceptions.ConfigOptionMustBeInt('MAXBURSTEVENTS')

    #Check windows hosts for events monitoring:
    if len(Config.options('MONITORWINDOWSHOSTS')) == 0:
        raise myExceptions.NoWindowsHosts

    return Config