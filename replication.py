from couchdb import Database, Document, ResourceNotFound, Server
from couchdb.client import Row, ViewResults

try:
    import simplejson as json
except ImportError:
    import json # Python 2.6

import requests
database = "cozy-files"
server = Server('http://localhost:5984/')


def replicate_to_local(url, device, pwdDevice, idDevice):
    (username, password) = _get_credentials()
    target = 'http://%s:%s@localhost:5984/%s' % (username, password, database)
    url = url.split('/')
    source = "https://%s:%s@%s/cozy" % (device, pwdDevice, url[2])
    server.replicate(source, target, continuous=True, filter="%s/filter" %idDevice)

def replicate_from_local(self):
    source = 'http://%s:%s@localhost:5984/%s' % (username, password, database)
    url = self.url.split('/')
    target = "https://%s:%s@%s/cozy" % (self.device, self.pwdDevice, url[2])
    self.rep = self.server.replicate(source, target, continuous=True, filter="%s/filter" %self.idDevice)

def recover_progression():
    url = 'http://localhost:5984/_active_tasks'
    r = requests.get(url)
    replications = json.loads(r.content)
    progress = 0
    for rep in replications:
        progress = progress + rep["progress"]
    return progress/200.


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
