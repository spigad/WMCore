import os

def fakeRequest(requestType):
  requestName = 'Test' + requestType
  couchUrl = os.environ.get("COUCHURL", None)
  return {
  'ProdConfigCacheID' : 'f821abc0fd7ee5c5a7c34f3b96c995dc',
   # MC
  'ProdConfigCacheID' : '82c706f593ec15d7ddbd22f07b54b64f' ,
  'CouchURL' : couchUrl,
  'CouchUrl' : couchUrl,
  'CouchDBName' : "wmagent_config_cache",
  'RequestName' : requestName,
  'RequestType' : requestType,
  "Requestor" : "me",
  "Group" : "PeopleLikeMe",
  "RequestSizeEvents" : 100,
  "InputDatasets" : '/PRIM/PROC/TIER',
  "InputDataset" : '/PRIM/PROC/TIER',
  "PrimaryDataset" : '/PRIM/PROC/TIER',
  "PileupDatasets" : [],
  "CMSSWVersion" : 'CMSSW_3_5_8',
  "ProcessingVersion" : 'CMSSW_3_5_8',
  'FinalDestination' : 'somewhere',
  'GlobalTag' : 'V1::All',
  'LFNCategory' : '/store/data',
  'AcquisitionEra' : 'Now',
  'OutputTiers' : ['RECO', 'AOD'],
  'DBSURL' : 'www.theonion.com',
  'ScramArch' : 'slc5_ia32_gcc434',
  "SkimInput" : "output",
  "SkimConfig1"  : '36f2fd377a5ac1c4149f5dd535271a10',
  "CmsPath" : "/uscmst1/prod/sw/cms",
  "Emulator" : False
  }