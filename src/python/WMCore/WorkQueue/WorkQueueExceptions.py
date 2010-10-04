#!/usr/bin/env python
"""WorkQueue Exceptions"""

class WorkQueueError(StandardError):
    """Standard error baseclass"""
    def __init__(self, error):
        StandardError.__init__(self, error)
        self.msg = WorkQueueError.__class__.__name__
        self.error = error

    def __str__(self):
        return "%s: %s" % (self.msg, self.error)

class WorkQueueWMSpecError(WorkQueueError):
    """Problem with the spec file"""
    def __init__(self, wmspec, error):
        WorkQueueError.__init__(self, error)
        self.wmspec = wmspec
        self.msg = "Invalid WMSpec: '%s'" % self.wmspec.name()

class WorkQueueNoWorkError(WorkQueueError):
    """No work for spec"""
    def __init__(self, wmspec, error):
        WorkQueueError.__init__(self, error)
        self.wmspec = wmspec
        self.msg = "No work in spec: '%s' Check inputs" % self.wmspec.name()