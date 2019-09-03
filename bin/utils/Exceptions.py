#-*- coding: iso-8859-1 -*-

'''
Own exceptions
'''

class ConfigNumSections(Exception):
    def __init__(self):
        self.message = 'More or less sections than expected in Config file!'
    def __str__(self):
        return self.message

class ConfigOptionMustBeInt(Exception):
    def __init__(self, option):
        self.message = 'The param '+option+' must be an Int!'
    def __str__(self):
        return self.message

class NoWindowsHosts(Exception):
    def __init__(self):
        self.message = 'No Windows host/s in Config file!'
    def __str__(self):
        return self.message