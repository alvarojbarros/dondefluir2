# -*- coding: utf-8 -*-
from tools.Tools import *
from flask import url_for
import os
import settings

def getImageLink(table,id,fieldname):
    fname = '%s/%s.%s' %(table,fieldname,id)
    print(fname)
    print("%s/%s/%s" % (settings.images_url,settings.images_folder,fname))
    f = os.path.isfile("%s/%s/%s" % (settings.images_url,settings.images_folder,fname))
    if not f:
        url = url_for('static',filename='images/user.jpg')
    else:
        fname = "%s/%s" %(settings.images_folder,fname)
        url = url_for('static',filename=fname)
    return url
