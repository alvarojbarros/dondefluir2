# -*- coding: utf-8 -*-

import sys
def getSettings():
    ''' settingsfile = sys.argv[1]
    setvar = {}
    exec('import %s as settings' % settingsfile,setvar)
    settings = setvar['settings'] '''
    import settings as settings
    return settings

def getUserClass():
    settings = getSettings()
    setvar = {}
    exec('from %s import User as UserClass' % settings.user_file,setvar)
    User = setvar['UserClass']
    return User

def getDbFolder():
    settings = getSettings()
    return settings.db_folder
