from kivy.app import App
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.progressbar import ProgressBar
from kivy.properties import *
from requests import post
from replication import replicate_to_local, recover_progression, init_database, init_device, replicate_from_local
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
        else:
            url = self._normalize_url(url)
            if not url:        
                self.error.text = "L'url de votre cozy n'est pas correcte"
                pass
            else:
                try:  
                    data = {'login': name}
                    r = post(url + '/device/', data=data, auth=('owner', pwd)) 
                except Exception, e:
                    print e
                    self.error.text = "Verifiez l'url de votre cozy"
                    self.error.texture_update()
                    self.error.anchors
                    pass            
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
                    init_database()                
                    self.progress.value = 15
                    data = json.loads(r.content)
                    replicate_to_local(url, name, data['password'], data['id'])  
                    err = init_device(url, data['password'], data['id'])
                    if err:
                        self.error.text = err
                        self.error.texture_update()
                        self.error.anchors
                        return False 
                    else:
                        replicate_from_local(url, name, data['password'], data['id'])
                        Clock.schedule_interval(self.progress_bar, 1/25)

        

    def progress_bar(self, dt):
        progress = recover_progression()
        if progress > 0.98:
            return False
        self.progress.value = 15 + 75*progress

    def _normalize_url(self, url):
        url_parts = url.split('/')
        for part in url_parts:
            if part.find('cozycloud.cc') is not -1:
                return 'https://%s' %part
        return False


class ConfigurationApp(App):
    def build(self):
        return Configuration()


if __name__ == '__main__':
    ConfigurationApp().run()