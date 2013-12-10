from couchdb import Database, Document, ResourceNotFound, Server
from couchdb.client import Row, ViewResults

try:
    import simplejson as json
except ImportError:
    import json # Python 2.6
import requests
import os

database = "cozy-files"
server = Server('http://localhost:5984/')


def replicate_to_local(url, device, pwdDevice, idDevice):
    (username, password) = _get_credentials()
    target = 'http://%s:%s@localhost:5984/%s' % (username, password, database)
    url = url.split('/')
    source = "https://%s:%s@%s/cozy" % (device, pwdDevice, url[2])
    server.replicate(source, target, continuous=True, filter="%s/filter" %idDevice)

def replicate_from_local(url, device, pwdDevice, idDevice):
    (username, password) = _get_credentials()
    source = 'http://%s:%s@localhost:5984/%s' % (username, password, database)
    url = url.split('/')
    target = "https://%s:%s@%s/cozy" % (device, pwdDevice, url[2])
    server.replicate(source, target, continuous=True, filter="%s/filter" %idDevice)

def recover_progression():
    url = 'http://localhost:5984/_active_tasks'
    r = requests.get(url)
    replications = json.loads(r.content)
    progress = 0
    for rep in replications:
        progress = progress + rep["progress"]
    return progress/200.

def init_database():
    # Create database
    db = server.create(database)

    db["_design/device"] = {
        "views": {
            "all": {
                "map": """function (doc) {
                              if (doc.docType === \"Device\") {
                                  emit(doc.id, doc) 
                              }
                          }"""
                    },
            "byUrl": {
                "map": """function (doc) {
                              if (doc.docType === \"Device\") {
                                  emit(doc.url, doc) 
                              }
                          }"""
                    }
                }
            }

    db["_design/folder"] = {
        "views": {
            "all": {
                "map": """function (doc) {
                              if (doc.docType === \"Folder\") {
                                  emit(doc.id, doc) 
                              }
                           }"""
                    },
            "byFolder": {
                "map": """function (doc) {
                              if (doc.docType === \"Folder\") {
                                  emit(doc.path, doc) 
                              }
                          }"""
                    },
            "byFullPath": {
                "map": """function (doc) {
                              if (doc.docType === \"Folder\") {
                                  emit(doc.path + '/' + doc.name, doc) 
                              }
                          }"""
                    }
                }
            }

    db["_design/file"] = {
        "views": {
            "all": {
                "map": """function (doc) {
                              if (doc.docType === \"File\") {
                                  emit(doc.id, doc) 
                              }
                           }"""
                    },
            "byFolder": {
                "map": """function (doc) {
                              if (doc.docType === \"File\") {
                                  emit(doc.path, doc) 
                              }
                          }"""
                    },
            "byFullPath": {
                "map": """function (doc) {
                              if (doc.docType === \"File\") {
                                  emit(doc.path + '/' + doc.name, doc) 
                              }
                          }"""
                    }
                }
            }

    db["_design/binary"] = {
        "views": {
            "all": {
                "map": """function (doc) {
                              if (doc.docType === \"Binary\") {
                                  emit(doc.id, doc) 
                              }
                           }"""
                    }
                }
            }

def init_device(url, pwdDevice, idDevice):
    db = server[database]
    res = db.view("device/all")
    if not res:
        init_device(url, pwdDevice, idDevice)
    else:
        for device in res:
            device = device.value
            # Update device
            folder = "%s/cozy-files" % os.environ['HOME']
            device['password'] = pwdDevice
            device['change'] = 0
            device['url'] = url
            device['folder'] = folder
            db.save(device)
            # Generate filter
            filter = """function(doc, req) {
                    if(doc._deleted) {
                        return true; 
                    }
                    if ("""
            for docType in device["configuration"]:
                filter = filter + "(doc.docType && doc.docType === \"%s\") ||" %docType
            filter = filter[0:-3]
            filter = filter + """){
                        return true; 
                    } else { 
                        return false; 
                    }
                }"""
            doc = {
                "_id": "_design/%s" % idDevice,
                "views": {},
                "filters": {
                    "filter": filter
                    }
                }
            db.save(doc) 
            return False


def _get_credentials():
    '''
    Get credentials from config file.
    '''
    credentials_file = open('/etc/cozy/cozy-files/couchdb.login')
    lines = credentials_file.readlines()
    credentials_file.close()
    username = lines[0].strip()
    password = lines[1].strip()
    return (username, password)
