#!/usr/bin/env python
""" 
_Fileset_t_

Unit tests for the WMBS Fileset class.
"""

__revision__ = "$Id: Fileset_t.py,v 1.16 2009/10/13 22:42:54 meloam Exp $"
__version__ = "$Revision: 1.16 $"

import unittest
import logging
import random
import os
import threading

from WMCore.WMBS.File import File
from WMCore.WMBS.Fileset import Fileset
from WMCore.WMBS.Workflow import Workflow
from WMCore.WMBS.Subscription import Subscription

from WMCore.DataStructs.Run import Run
from WMCore.DAOFactory import DAOFactory
from WMCore.WMFactory import WMFactory

from WMQuality.TestInit import TestInit

class FilesetTest(unittest.TestCase):
    _setup = False
    _teardown = False
      
    
    def setUp(self):
        """
        _setUp_
        
        Setup the database and logging connection.  Try to create all of the
        WMBS tables.
        """
        if self._setup:
            return
        
        self.testInit = TestInit(__file__, os.getenv("DIALECT"))
        self.testInit.setLogging()
        self.testInit.setDatabaseConnection()
        self.testInit.setSchema(customModules = ["WMCore.WMBS"],
                                useDefault = False)
        
        self._setup = True
        return
                                                                
    def tearDown(self):
        """
        _tearDown_
        
        Drop all the WMBS tables.
        """
        myThread = threading.currentThread()
        
        if self._teardown:
            return
        
        factory = WMFactory("WMBS", "WMCore.WMBS")
        destroy = factory.loadObject(myThread.dialect + ".Destroy")
        myThread.transaction.begin()
        destroyworked = destroy.execute(conn = myThread.transaction.conn)
        if not destroyworked:
            raise Exception("Could not complete WMBS tear down.")
        myThread.transaction.commit()
        
        self._teardown = True
        return                              
 
    def testCreateDeleteExists(self):
        """
        _testCreateDeleteExists_

        Create a delete a fileset object while also using the exists() method
        to determine the the create() and delete() methods succeeded.
        """
        testFileset = Fileset(name = "TestFileset")

        assert testFileset.exists() == False, \
               "ERROR: Fileset exists before it was created"

        testFileset.create()

        assert testFileset.exists() >= 0, \
               "ERROR: Fileset does not exist after it was created"

        testFileset.delete()

        assert testFileset.exists() == False, \
               "ERROR: Fileset exists after it was deleted"

        return

    def testCreateTransaction(self):
        """
        _testCreateTransaction_

        Create a Fileset and commit it to the database and then roll back the
        transaction.  Use the fileset's exists() method to verify that it
        doesn't exist in the database before create() is called, that is does
        exist after create() is called and that it does not exist after the
        transaction is rolled back.
        """
        myThread = threading.currentThread()
        myThread.transaction.begin()
        
        testFileset = Fileset(name = "TestFileset")

        assert testFileset.exists() == False, \
               "ERROR: Fileset exists before it was created"

        testFileset.create()

        assert testFileset.exists() >= 0, \
               "ERROR: Fileset does not exist after it was created"

        myThread.transaction.rollback()

        assert testFileset.exists() == False, \
               "ERROR: Fileset exists after transaction was rolled back."

        return    

    def testDeleteTransaction(self):
        """
        _testDeleteTransaction_

        Create a fileset and commit it to the database.  Delete the fileset
        and verify that it is no longer in the database using the exists()
        method.  Rollback the transaction and verify with the exists() method
        that the fileset is in the database.
        """
        testFileset = Fileset(name = "TestFileset")

        assert testFileset.exists() == False, \
               "ERROR: Fileset exists before it was created"

        testFileset.create()

        assert testFileset.exists() >= 0, \
               "ERROR: Fileset does not exist after it was created"

        myThread = threading.currentThread()
        myThread.transaction.begin()

        testFileset.delete()

        assert testFileset.exists() == False, \
               "ERROR: Fileset exists after it was deleted"

        myThread.transaction.rollback()

        assert testFileset.exists() >= 0, \
               "ERROR: Fileset doesn't exist after transaction was rolled back."

        return

    def testLoad(self):
        """
        _testLoad_

        Test retrieving fileset metadata via the id and the
        name.
        """
        testFilesetA = Fileset(name = "TestFileset")
        testFilesetA.create()

        testFilesetB = Fileset(name = testFilesetA.name)
        testFilesetB.load()        
        testFilesetC = Fileset(id = testFilesetA.id)
        testFilesetC.load()

        assert type(testFilesetB.id) == int, \
               "ERROR: Fileset id is not an int."

        assert type(testFilesetC.id) == int, \
               "ERROR: Fileset id is not an int."        

        assert testFilesetB.id == testFilesetA.id, \
               "ERROR: Load from name didn't load id"

        assert testFilesetC.name == testFilesetA.name, \
               "ERROR: Load from id didn't load name"

        testFilesetA.delete()
        return

    def testLoadData(self):
        """
        _testLoadData_

        Test saving and loading all fileset information.
        """
        testFileA = File(lfn = "/this/is/a/lfnA", size = 1024,
                         events = 20, cksum = 3)
        testFileA.addRun(Run( 1, *[45]))
        testFileB = File(lfn = "/this/is/a/lfnB", size = 1024,
                         events = 20, cksum = 3)
        testFileB.addRun(Run( 1, *[45]))
        testFileC = File(lfn = "/this/is/a/lfnC", size = 1024,
                         events = 20, cksum = 3)
        testFileC.addRun(Run( 1, *[45]))
        testFileA.create()
        testFileB.create()
        testFileC.create()

        testFilesetA = Fileset(name = "TestFileset")
        testFilesetA.create()

        testFilesetA.addFile(testFileA)
        testFilesetA.addFile(testFileB)
        testFilesetA.addFile(testFileC)
        testFilesetA.commit()

        testFilesetB = Fileset(name = testFilesetA.name)
        testFilesetB.loadData()        
        testFilesetC = Fileset(id = testFilesetA.id)
        testFilesetC.loadData()

        assert testFilesetB.id == testFilesetA.id, \
               "ERROR: Load from name didn't load id"

        assert testFilesetC.name == testFilesetA.name, \
               "ERROR: Load from id didn't load name"

        goldenFiles = [testFileA, testFileB, testFileC]
        for filesetFile in testFilesetB.files:
            assert filesetFile in goldenFiles, \
                   "ERROR: Unknown file in fileset"
            goldenFiles.remove(filesetFile)

        assert len(goldenFiles) == 0, \
               "ERROR: Fileset is missing files"

        goldenFiles = [testFileA, testFileB, testFileC]
        for filesetFile in testFilesetC.files:
            assert filesetFile in goldenFiles, \
                   "ERROR: Unknown file in fileset"
            goldenFiles.remove(filesetFile)

        assert len(goldenFiles) == 0, \
               "ERROR: Fileset is missing files"
        
        testFilesetA.delete()
        testFileA.delete()
        testFileB.delete()
        testFileC.delete()        
        
    def testGetFiles(self):
        """
        _testGetFiles_

        Create a fileset with three files and exercise the getFiles() method to
        make sure that all the results it returns are consistant.
        """
        testFileA = File(lfn = "/this/is/a/lfnA", size = 1024,
                         events = 20, cksum = 3)
        testFileA.addRun(Run( 1, *[45]))
        testFileB = File(lfn = "/this/is/a/lfnB", size = 1024,
                         events = 20, cksum = 3)
        testFileB.addRun(Run( 1, *[45]))
        testFileC = File(lfn = "/this/is/a/lfnC", size = 1024,
                         events = 20, cksum = 3)
        testFileC.addRun(Run( 1, *[45]))
        testFileA.create()
        testFileB.create()
        testFileC.create()

        testFilesetA = Fileset(name = "TestFileset")
        testFilesetA.create()
        
        testFilesetA.addFile(testFileA)
        testFilesetA.addFile(testFileB)
        testFilesetA.addFile(testFileC)
        testFilesetA.commit()

        filesetFiles = testFilesetA.getFiles(type = "list")

        goldenFiles = [testFileA, testFileB, testFileC]
        for filesetFile in filesetFiles:
            assert filesetFile in goldenFiles, \
                   "ERROR: Unknown file in fileset"
            goldenFiles.remove(filesetFile)

        assert len(goldenFiles) == 0, \
               "ERROR: Not all files in fileset"

        filesetFiles = testFilesetA.getFiles(type = "set")

        goldenFiles = [testFileA, testFileB, testFileC]
        for filesetFile in filesetFiles:
            assert filesetFile in goldenFiles, \
                   "ERROR: Unknown file in fileset"
            goldenFiles.remove(filesetFile)

        assert len(goldenFiles) == 0, \
               "ERROR: Not all files in fileset"

        filesetLFNs = testFilesetA.getFiles(type = "lfn")

        goldenLFNs = [testFileA["lfn"], testFileB["lfn"], testFileC["lfn"]]
        for filesetLFN in filesetLFNs:
            assert filesetLFN in goldenLFNs, \
                   "ERROR: Unknown lfn in fileset"
            goldenLFNs.remove(filesetLFN)

        assert len(goldenLFNs) == 0, \
               "ERROR: Not all lfns in fileset"

        filesetIDs = testFilesetA.getFiles(type = "id")

        goldenIDs = [testFileA["id"], testFileB["id"], testFileC["id"]]
        for filesetID in filesetIDs:
            assert filesetID in goldenIDs, \
                   "ERROR: Unknown id in fileset"
            goldenIDs.remove(filesetID)

        assert len(goldenIDs) == 0, \
               "ERROR: Not all ids in fileset"        

    def testFileCreate(self):
        """
        _testFileCreate_

        Create several files and add them to the fileset.  Test to make sure
        that the commit() fileset method will add the files to the database
        if they are not in the database.
        """
        testFileA = File(lfn = "/this/is/a/lfnA", size = 1024,
                         events = 20, cksum = 3)
        testFileA.addRun(Run( 1, *[45]))
        testFileB = File(lfn = "/this/is/a/lfnB", size = 1024,
                         events = 20, cksum = 3)
        testFileB.addRun(Run( 1, *[45]))
        testFileC = File(lfn = "/this/is/a/lfnC", size = 1024,
                         events = 20, cksum = 3)
        testFileC.addRun(Run( 1, *[45]))
        testFileC.create()

        testFilesetA = Fileset(name = "TestFileset")
        testFilesetA.create()

        testFilesetA.addFile(testFileA)
        testFilesetA.addFile(testFileB)
        testFilesetA.addFile(testFileC)
        testFilesetA.commit()

        testFilesetB = Fileset(name = testFilesetA.name)
        testFilesetB.loadData()        
        testFilesetC = Fileset(id = testFilesetA.id)
        testFilesetC.loadData()

        assert testFilesetB.id == testFilesetA.id, \
               "ERROR: Load from name didn't load id"

        assert testFilesetC.name == testFilesetA.name, \
               "ERROR: Load from id didn't load name"

        goldenFiles = [testFileA, testFileB, testFileC]
        for filesetFile in testFilesetB.files:
            assert filesetFile in goldenFiles, \
                   "ERROR: Unknown file in fileset"
            goldenFiles.remove(filesetFile)

        assert len(goldenFiles) == 0, \
               "ERROR: Fileset is missing files"

        goldenFiles = [testFileA, testFileB, testFileC]
        for filesetFile in testFilesetC.files:
            assert filesetFile in goldenFiles, \
                   "ERROR: Unknown file in fileset"
            goldenFiles.remove(filesetFile)

        assert len(goldenFiles) == 0, \
               "ERROR: Fileset is missing files"
        
        testFilesetA.delete()
        testFileA.delete()
        testFileB.delete()
        testFileC.delete()

    def testFileCreateTransaction(self):
        """
        _testFileCreateTransaction_

        Create several files and add them to a fileset.  Commit the fileset
        and the files to the database, verifying that they can loaded back
        from the database.  Rollback the transaction to the point after the
        fileset has been created buy before the files have been associated with
        the filset.  Load the filesets from the database again and verify that
        they do not have any files.
        """
        testFileA = File(lfn = "/this/is/a/lfnA", size = 1024,
                         events = 20, cksum = 3)
        testFileA.addRun(Run( 1, *[45]))
        testFileB = File(lfn = "/this/is/a/lfnB", size = 1024,
                         events = 20, cksum = 3)
        testFileB.addRun(Run( 1, *[45]))
        testFileC = File(lfn = "/this/is/a/lfnC", size = 1024,
                         events = 20, cksum = 3)
        testFileC.addRun(Run( 1, *[45]))
        testFileC.create()

        testFilesetA = Fileset(name = "TestFileset")
        testFilesetA.create()

        myThread = threading.currentThread()
        myThread.transaction.begin()

        testFilesetA.addFile(testFileA)
        testFilesetA.addFile(testFileB)
        testFilesetA.addFile(testFileC)
        testFilesetA.commit()

        testFilesetB = Fileset(name = testFilesetA.name)
        testFilesetB.loadData()
        testFilesetC = Fileset(id = testFilesetA.id)
        testFilesetC.loadData()

        assert testFilesetB.id == testFilesetA.id, \
               "ERROR: Load from name didn't load id"

        assert testFilesetC.name == testFilesetA.name, \
               "ERROR: Load from id didn't load name"

        goldenFiles = [testFileA, testFileB, testFileC]
        for filesetFile in testFilesetB.files:
            assert filesetFile in goldenFiles, \
                   "ERROR: Unknown file in fileset"
            goldenFiles.remove(filesetFile)

        assert len(goldenFiles) == 0, \
               "ERROR: Fileset is missing files"

        goldenFiles = [testFileA, testFileB, testFileC]
        for filesetFile in testFilesetC.files:
            assert filesetFile in goldenFiles, \
                   "ERROR: Unknown file in fileset"
            goldenFiles.remove(filesetFile)

        assert len(goldenFiles) == 0, \
               "ERROR: Fileset is missing files"

        myThread.transaction.rollback()

        testFilesetB.loadData()
        testFilesetC.loadData()

        assert len(testFilesetB.files) == 0, \
               "ERROR: Fileset B has too many files"

        assert len(testFilesetC.files) == 0, \
               "ERROR: Fileset C has too many files"        
        
        testFilesetA.delete()
        testFileA.delete()
        testFileB.delete()
        testFileC.delete()

    def testMarkOpen(self):
        """
        _testMarkOpen_

        Test that setting the openess of a fileset in the constructor works as
        well as changing it with the markOpen() method.
        """
        testFilesetA = Fileset(name = "TestFileset1", is_open = False)
        testFilesetA.create()
        testFilesetB = Fileset(name = "TestFileset2", is_open = True)
        testFilesetB.create()
        
        testFilesetC = Fileset(name = testFilesetA.name)
        testFilesetC.load()
        testFilesetD = Fileset(name = testFilesetB.name)
        testFilesetD.load()

        assert testFilesetC.open == False, \
               "ERROR: FilesetC should be closed."

        assert testFilesetD.open == True, \
               "ERROR: FilesetD should be open."

        testFilesetA.markOpen(True)
        testFilesetB.markOpen(False)

        testFilesetE = Fileset(name = testFilesetA.name)
        testFilesetE.load()
        testFilesetF = Fileset(name = testFilesetB.name)
        testFilesetF.load()

        assert testFilesetE.open == True, \
               "ERROR: FilesetE should be open."

        assert testFilesetF.open == False, \
               "ERROR: FilesetF should be closed."        

        myThread = threading.currentThread()
        daoFactory = DAOFactory(package="WMCore.WMBS", logger = myThread.logger,
                                dbinterface = myThread.dbi)
        openFilesetDAO = daoFactory(classname = "Fileset.ListOpen")
        openFilesetNames = openFilesetDAO.execute()        

        assert len(openFilesetNames) == 1, \
               "ERROR: Too many open filesets."

        assert "TestFileset1" in openFilesetNames, \
               "ERROR: Wrong fileset listed as open."
               
        return

    def testFilesetClosing(self):
        """
        _testFilesetClosing_

        Verify the proper operation of the closable fileset DAO object.  A
        fileset is closable if:
          - The subscription that feeds it has completed processing all files
            in it's input fileset
          - The fileset that feeds the subscription is closed
        """
        testOutputFileset1 = Fileset(name = "TestOutputFileset1")
        testOutputFileset1.create()
        testOutputFileset2 = Fileset(name = "TestOutputFileset2")
        testOutputFileset2.create()
        testOutputFileset3 = Fileset(name = "TestOutputFileset3")
        testOutputFileset3.create()
        testOutputFileset4 = Fileset(name = "TestOutputFileset4")
        testOutputFileset4.create()        
        
        testFilesetOpen = Fileset(name = "TestFilesetOpen", is_open = True)
        testFilesetOpen.create()
        testFileA = File(lfn = "/this/is/a/lfnA", size = 1024,
                         events = 20, cksum = 3)
        testFileB = File(lfn = "/this/is/a/lfnB", size = 1024,
                         events = 20, cksum = 3)        
        testFilesetOpen.addFile(testFileA)
        testFilesetOpen.addFile(testFileB)
        testFilesetOpen.commit()

        testFilesetClosed = Fileset(name = "TestFilesetClosed", is_open = False)
        testFilesetClosed.create()
        testFileC = File(lfn = "/this/is/a/lfnC", size = 1024,
                         events = 20, cksum = 3)
        testFileD = File(lfn = "/this/is/a/lfnD", size = 1024,
                         events = 20, cksum = 3)        
        testFilesetClosed.addFile(testFileC)
        testFilesetClosed.addFile(testFileD)
        testFilesetClosed.commit()

        testWorkflow1 = Workflow(spec = "spec1.xml", owner = "Steve",
                                 name = "wf001", task = "sometask")
        testWorkflow1.create()
        testWorkflow1.addOutput("out1", testOutputFileset1)
        testWorkflow1.addOutput("out2", testOutputFileset2)

        testWorkflow2 = Workflow(spec = "spec2.xml", owner = "Steve",
                                 name = "wf002", task = "sometask")
        testWorkflow2.create()
        testWorkflow2.addOutput("out3", testOutputFileset3)

        testWorkflow3 = Workflow(spec = "spec4.xml", owner = "Steve",
                                 name = "wf004", task = "sometask")
        testWorkflow3.create()
        testWorkflow3.addOutput("out4", testOutputFileset4)

        testSubscription1 = Subscription(fileset = testFilesetClosed,
                                         workflow = testWorkflow1)
        testSubscription1.create()
        testSubscription1.completeFiles([testFileC, testFileD])
        testSubscription2 = Subscription(fileset = testFilesetOpen,
                                         workflow = testWorkflow2)
        testSubscription2.create()
        testSubscription2.completeFiles([testFileA, testFileB])
        testSubscription3 = Subscription(fileset = testFilesetClosed,
                                         workflow = testWorkflow3)
        testSubscription3.create()        

        myThread = threading.currentThread()
        daoFactory = DAOFactory(package="WMCore.WMBS", logger = myThread.logger,
                                dbinterface = myThread.dbi)
        closableFilesetDAO = daoFactory(classname = "Fileset.ListClosable")
        closableFilesets = closableFilesetDAO.execute()

        goldenFilesets = ["TestOutputFileset1", "TestOutputFileset2"]

        for closableFileset in closableFilesets:
            newFileset = Fileset(id = closableFileset)
            newFileset.load()

            assert newFileset.name in goldenFilesets, \
                   "Error: Unknown closable fileset"

            goldenFilesets.remove(newFileset.name)

        assert len(goldenFilesets) == 0, \
               "Error: Filesets are missing"
        return
        
if __name__ == "__main__":
        unittest.main()
