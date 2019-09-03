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

    if len(Config.sections()) != 4:
        raise myExceptions.ConfigNumSections

    # Must be int:
    list_check_ifint = [
        ('RSYSLOG', 'SYSTEMPORT'),
        ('MONITORWINDOWS', 'AUTOADJUST_WFQTHRESHOLDFORSTART'),
        ('MONITORWINDOWS', 'MAXCONTRIES'),
        ('MONITORWINDOWS', 'MAXBURSTEVENTS')
    ]

    def intCheck(sectionname, optionname):
        '''
        int checker.
        :param sectionname:
        :param optionname:
        :return:
        '''

        try:
            int(Config.get(sectionname, optionname))
        except:
            raise myExceptions.ConfigOptionMustBeInt(optionname)

    [intCheck(i[0], i[1]) for i in list_check_ifint]  # Verification with list comprehension

    #Check windows hosts for events monitoring:
    if len(Config.options('MONITORWINDOWSHOSTS')) == 0:
        raise myExceptions.NoWindowsHosts

    return Config
