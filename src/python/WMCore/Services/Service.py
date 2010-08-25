#!/usr/bin/env python
"""
_Service_

A Service talks to some http accessible service that provides information. It
has a cache path (defaults to /tmp), cache duration, an endpoint (the url the 
service exists on) a logger and an accept type (json, xml etc) and method 
(GET/POST). 

The Service satisfies two caching cases:

1. set a defined query, cache results, poll for new ones
2. use a changing query, cache results to a file depending on the query, poll
   for new ones

Data maybe passed to the remote service either via adding the query string to 
the URL (for GET's) or by passing a dictionary to either the service constructor
(case 1.) or by passing the data as a dictionary to the refreshCache, 
forceCache, clearCache calls. 

The service has a default timeout of 30 seconds. Over ride this by passing in a 
timeout via the configuration dict, set to None if you want to turn off the 
timeout.

If you just want to retrieve the data without caching use the Requests class
directly.
"""

__revision__ = "$Id: Service.py,v 1.18 2009/07/15 11:19:42 metson Exp $"
__version__ = "$Revision: 1.18 $"

import datetime
import os
import urllib
import time
import socket
from urlparse import urlparse
from WMCore.Services.Requests import Requests

class Service(Requests):
    def __init__(self, dict={}):
        #The following should read the configuration class
        for a in ['logger', 'endpoint']:
            assert a in dict.keys(), "Can't have a service without a %s" % a

        # Inherit from Resource
        # then split the endpoint into netloc and basepath
        endpoint = urlparse(dict['endpoint'])
        
        #Only works on python 2.5 or above
        self.setdefault("basepath", endpoint.path)
        Requests.__init__(self, endpoint.netloc)
        
         #set up defaults
        self.setdefault("inputdata", {})
        self.setdefault("cachepath", '/tmp')
        self.setdefault("cacheduration", 0.5)
        self.setdefault("accept_type", 'text/xml')
        self.setdefault("method", 'GET')
        
        #Set a timeout for the socket
        self.setdefault("timeout", 30)
        
        # then update with the incoming dict
        self.update(dict)
        
        self['logger'].debug("""Service initialised (%s):
\t host: %s, basepath: %s (%s)\n\t cache: %s (duration %s hours)""" %
                  (self, self["host"], self["basepath"], self["accept_type"], self["cachepath"], 
                   self["cacheduration"]))

    def cacheFileName(self, cachefile, inputdata={}):
        hash = 0
        for i in self['inputdata'].items():
            hash += i[0].__hash__() + i[1].__hash__()
        for i in inputdata.items():
            hash += i[0].__hash__() + i[1].__hash__()
        cachefile = "%s/%s_%s" % (self["cachepath"], hash, cachefile)
        return cachefile
    
    def refreshCache(self, cachefile, url, inputdata={}):
        t = datetime.datetime.now() - datetime.timedelta(hours=self['cacheduration'])
        cachefile = self.cacheFileName(cachefile, inputdata)
        if not os.path.exists(cachefile) or os.path.getmtime(cachefile) < time.mktime(t.timetuple()):
            self['logger'].debug("%s expired, refreshing cache" % cachefile)
            self.getData(cachefile, url)
        return open(cachefile, 'r')

    def forceRefresh(self, cachefile, url, inputdata={}):
        cachefile = self.cacheFileName(cachefile, inputdata)

        self['logger'].debug("Forcing cache refresh of %s" % cachefile)
        self.getData(cachefile, url)
        return open(cachefile, 'r')

    def clearCache(self, cachefile, inputdata={}):
        cachefile = self.cacheFileName(cachefile, inputdata)
        try:
            os.remove(cachefile)
        except OSError: # File doesn't exist
            return

    def getData(self, cachefile, url, inputdata={}):
        """
        Takes the already generated *full* path to cachefile and the url of the 
        resource. Don't need to call self.cacheFileName(cachefile, inputdata)
        here.
        """
        # Set the timeout
        deftimeout = socket.getdefaulttimeout()
        socket.setdefaulttimeout(self['timeout'])
        try:
            # Get the data
            url = self["basepath"] + url
            data, status, reason = self.makeRequest(uri=url, 
                                                    type=self["method"],
                                                    data=self['inputdata'])
            # Don't need to prepend the cachepath, the methods calling getData
            # have done that for us 
            f = open(cachefile, 'w')
            f.write(data)
            f.close()
        except Exception, e:
            self['logger'].exception(e)
            raise e
        # Reset the timeout to it's original value
        socket.setdefaulttimeout(deftimeout)