#!/usr/bin/env python
"""
_SplitFileBased_t_

Unit tests for the split file job splitting algorithm.
"""

__revision__ = "$Id: SplitFileBased_t.py,v 1.3 2009/10/13 22:42:57 meloam Exp $"
__version__ = "$Revision: 1.3 $"

from sets import Set
import unittest
import os
import threading

from WMCore.WMBS.File import File
from WMCore.WMBS.Fileset import Fileset
from WMCore.WMBS.Job import Job
from WMCore.WMBS.JobGroup import JobGroup
from WMCore.WMBS.Subscription import Subscription
from WMCore.WMBS.Workflow import Workflow

from WMCore.DataStructs.Run import Run

from WMCore.DAOFactory import DAOFactory
from WMCore.WMFactory import WMFactory
from WMCore.JobSplitting.SplitterFactory import SplitterFactory
from WMCore.Services.UUID import makeUUID
from WMQuality.TestInit import TestInit

class SplitFileBasedTest(unittest.TestCase):
    """
    _SplitFileBasedTest_

    Unit tests for the split file job splitting algorithm.
    """
    
    def setUp(self):
        """
        _setUp_

        Create database connection and load up the WMBS schema.
        """
        self.testInit = TestInit(__file__, os.getenv("DIALECT"))
        self.testInit.setLogging()
        self.testInit.setDatabaseConnection()
        self.testInit.setSchema(customModules = ["WMCore.WMBS"],
                                useDefault = False)
        
        return

    def tearDown(self):
        """
        _tearDown_

        Clear out WMBS.
        """
        myThread = threading.currentThread()

        if myThread.transaction == None:
            myThread.transaction = Transaction(self.dbi)
            
        myThread.transaction.begin()
            
        factory = WMFactory("WMBS", "WMCore.WMBS")
        destroy = factory.loadObject(myThread.dialect + ".Destroy")
        destroyworked = destroy.execute(conn = myThread.transaction.conn)
        
        if not destroyworked:
            raise Exception("Could not complete WMBS tear down.")
            
        myThread.transaction.commit()
        return

    def stuffWMBS(self):
        """
        _stuffWMBS_

        Insert some dummy jobs, jobgroups, filesets, files and subscriptions
        into WMBS to test job creation.  Three completed job groups each
        containing several files are injected.  Another incomplete job group is
        also injected.  Also files are added to the "Mergeable" subscription as
        well as to the output fileset for their jobgroups.
        """
        bunkFileset = Fileset(name = "bunkFileset")
        bunkFileset.create()

        bunkWorkflow = Workflow(name = "bunkWorkflow", spec = "bunk",
                                owner = "Steve")
        bunkWorkflow.create()
        
        bunkSubscription = Subscription(fileset = bunkFileset,
                                        workflow = bunkWorkflow)
        bunkSubscription.create()

        jobGroup1 = JobGroup(subscription = bunkSubscription)
        jobGroup1.create()
        newJob = Job()
        newJob.create(jobGroup1)
        newJob.changeStatus("COMPLETE")
        jobGroup2 = JobGroup(subscription = bunkSubscription)
        jobGroup2.create()
        newJob = Job()
        newJob.create(jobGroup2)
        newJob.changeStatus("COMPLETE")        
        jobGroup3 = JobGroup(subscription = bunkSubscription)
        jobGroup3.create()
        newJob = Job()
        newJob.create(jobGroup3)
        newJob.changeStatus("COMPLETE")
        jobGroup4 = JobGroup(subscription = bunkSubscription)
        jobGroup4.create()
        newJob = Job()
        newJob.create(jobGroup4)        

        file1 = File(lfn = "file1", size = 1024, events = 1024, first_event = 0)
        file1.addRun(Run(1, *[45]))
        file2 = File(lfn = "file2", size = 1024, events = 1024, first_event = 1024)
        file2.addRun(Run(1, *[45]))
        file3 = File(lfn = "file3", size = 1024, events = 1024, first_event = 2048)
        file3.addRun(Run(1, *[45]))
        file4 = File(lfn = "file4", size = 1024, events = 1024, first_event = 3072)        
        file4.addRun(Run(1, *[45]))

        fileA = File(lfn = "fileA", size = 1024, events = 1024, first_event = 0)
        fileA.addRun(Run(1, *[46]))
        fileB = File(lfn = "fileB", size = 1024, events = 1024, first_event = 1024)
        fileB.addRun(Run(1, *[46]))
        fileC = File(lfn = "fileC", size = 1024, events = 1024, first_event = 2048)
        fileC.addRun(Run(1, *[46]))

        fileI = File(lfn = "fileI", size = 1024, events = 1024, first_event = 0)
        fileI.addRun(Run(2, *[46]))
        fileII = File(lfn = "fileII", size = 1024, events = 1024, first_event = 1024)
        fileII.addRun(Run(2, *[46]))
        fileIII = File(lfn = "fileIII", size = 1024, events = 1024, first_event = 2048)
        fileIII.addRun(Run(2, *[46]))
        fileIV = File(lfn = "fileIV", size = 1024, events = 1024, first_event = 3072)        
        fileIV.addRun(Run(2, *[46]))        

        fileX = File(lfn = "badFileA", size = 1024, events = 1024, first_event = 0)
        fileX.addRun(Run(1, *[47]))
        fileY = File(lfn = "badFileB", size = 1024, events = 1024, first_event = 1024)
        fileY.addRun(Run(1, *[47]))
        fileZ = File(lfn = "badFileC", size = 1024, events = 1024, first_event = 2048)
        fileZ.addRun(Run(1, *[47]))

        jobGroup1.groupoutput.addFile(file1)
        jobGroup1.groupoutput.addFile(file2)
        jobGroup1.groupoutput.addFile(file3)
        jobGroup1.groupoutput.addFile(file4)        
        jobGroup1.groupoutput.commit()

        jobGroup2.groupoutput.addFile(fileA)
        jobGroup2.groupoutput.addFile(fileB)
        jobGroup2.groupoutput.addFile(fileC)
        jobGroup2.groupoutput.commit()

        jobGroup3.groupoutput.addFile(fileI)
        jobGroup3.groupoutput.addFile(fileII)
        jobGroup3.groupoutput.addFile(fileIII)
        jobGroup3.groupoutput.addFile(fileIV)        
        jobGroup3.groupoutput.commit()                

        jobGroup4.groupoutput.addFile(fileX)
        jobGroup4.groupoutput.addFile(fileY)
        jobGroup4.groupoutput.addFile(fileZ)
        jobGroup4.groupoutput.commit()

        self.mergeFileset = Fileset(name = "mergeFileset")
        self.mergeFileset.create()

        mergeWorkflow = Workflow(name = "mergeWorkflow", spec = "bunk2",
                                 owner = "Steve")
        mergeWorkflow.create()
        
        self.mergeSubscription = Subscription(fileset = self.mergeFileset,
                                              workflow = mergeWorkflow,
                                              split_algo = "SplitFileBased")
        self.mergeSubscription.create()
        
        self.mergeFileset.addFile(file1)
        self.mergeFileset.addFile(file2)
        self.mergeFileset.addFile(file3)
        self.mergeFileset.addFile(file4)
        self.mergeFileset.addFile(fileA)
        self.mergeFileset.addFile(fileB)
        self.mergeFileset.addFile(fileC)
        self.mergeFileset.addFile(fileI)
        self.mergeFileset.addFile(fileII)
        self.mergeFileset.addFile(fileIII)
        self.mergeFileset.addFile(fileIV)
        self.mergeFileset.addFile(fileX)
        self.mergeFileset.addFile(fileY)
        self.mergeFileset.addFile(fileZ)        
        self.mergeFileset.commit()

        return

    def testSplitAlgo(self):
        """
        _testSplitAlgo_

        Run the SplitFileBased splitting algorithm over the data created in
        the merge subscription.  This should produce three job groups each
        containing one job.  The files in the job should be ordered correctly.
        """
        self.stuffWMBS()

        splitter = SplitterFactory()
        jobFactory = splitter(package = "WMCore.WMBS",
                              subscription = self.mergeSubscription)

        result = jobFactory()

        assert len(result) == 3, \
               "ERROR: Wrong number of job groups returned."

        for jobGroup in result:
            assert len(jobGroup.jobs) == 1, \
                   "ERROR: One job should be in a job group."

        goldenFilesA = ["file1", "file2", "file3", "file4"]
        goldenFilesB = ["fileA", "fileB", "fileC"]
        goldenFilesC = ["fileI", "fileII", "fileIII", "fileIV"]

        for jobGroup in result:
            jobFiles = jobGroup.jobs.pop().getFiles()
            
            if jobFiles[0]["lfn"] in goldenFilesA:
                goldenFiles = goldenFilesA
            elif jobFiles[0]["lfn"] in goldenFilesB:
                goldenFiles = goldenFilesB
            else:
                goldenFiles = goldenFilesC

            currentRun = 0
            currentLumi = 0
            currentEvent = 0
            for file in jobFiles:
                file.loadData()
                assert file["lfn"] in goldenFiles, \
                       "ERROR: Unknown file in merge jobs."

                goldenFiles.remove(file["lfn"])

            fileRun = list(file["runs"])[0].run
            fileLumi = min(list(file["runs"])[0])
            fileEvent = file["first_event"]

            if currentRun == 0:
                currentRun = fileRun
                currentLumi = fileLumi
                currentEvent = fileEvent
                continue

            assert fileRun >= currentRun, \
                   "ERROR: Files not sorted by run."

            if fileRun == currentRun:
                assert fileLumi >= currentLumi, \
                       "ERROR: Files not ordered by lumi"

                if fileLumi == currentLumi:
                    assert fileEvent > currentEvent, \
                           "ERROR: Files not ordered by first event"

            currentRun = fileRun
            currentLumi = fileLumi
            currentEvent = fileEvent

        assert len(goldenFilesA) == 0 and len(goldenFilesB) == 0 and \
               len(goldenFilesC) == 0, \
               "ERROR: Files missing from merge jobs."

        return

if __name__ == '__main__':
    unittest.main()
