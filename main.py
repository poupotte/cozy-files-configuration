from kivy.app import App
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.progressbar import ProgressBar
from kivy.properties import *
from requests import post
from replication import replicate_to_local
from replication import recover_progression
from couchdb import Database, Server
from kivy.clock import Clock

try:
    import simplejson as json
except ImportError:
    import json # Python 2.6

database = 'cozy-files'

class Configuration(AnchorLayout):
    progress = ObjectProperty()
    url = ObjectProperty()
    pwd = ObjectProperty()
    name = ObjectProperty()
    error = ObjectProperty()

    def install(self):
        url = self.url.text
        pwd = self.pwd.text
        name = self.name.text
        if name is "" or pwd is "" or url is "":            
            self.error.text = 'Tous les champs doivent etre remplis'
            pass
        try:  
            data = {'login': name}
            r = post(url + '/device/', data=data, auth=('owner', pwd))                 
            if r.status_code == 401:
                self.error.text = "L'url et le mot de passe de votre cozy \n           ne correspondent pas"
                self.error.texture_update()
                self.error.anchors
                pass
            elif r.status_code == 400:
                self.error.text = 'Ce nom est deja utilise par un autre device'
                self.error.texture_update()
                self.error.anchors
                pass
            else:
                self.progress.value = 10
                self.error.text = ""
                self.error.texture_update()
                self.error.anchors
                self._init_database()                
                self.progress.value = 15
                data = json.loads(r.content)
                replicate_to_local(url, name, data['password'], data['id']) 
                Clock.schedule_interval(self.progress_bar, 1/25)
        except Exception, e:
            print e
            self.error.text = "Verifiez l'url de votre cozy"
            self.error.texture_update()
            self.error.anchors
            pass

    def progress_bar(self, dt):
        progress = recover_progression()
        if progress > 0.494:
            return False
        self.progress.value = 15 + 75*progress

    def _init_database(self):
        server = Server('http://localhost:5984/')
        # Read file
        f = open('/etc/cozy/cozy-files/couchdb.login')
        lines = f.readlines()
        f.close()
        username = lines[0].strip()
        password = lines[1].strip()
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



class ConfigurationApp(App):
    def build(self):
        return Configuration()


if __name__ == '__main__':
    ConfigurationApp().run()