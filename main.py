from kivy.app import App
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.progressbar import ProgressBar
from kivy.properties import *
from requests import post
from replication import replicate_to_local, recover_progression, init_database, init_device, replicate_from_local
from replication import recover_progression
from couchdb import Database, Server
from kivy.clock import Clock
from threading import Thread

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

    max_prog = 0
    end = False

    def install(self):
        url = self.url.text
        pwd = self.pwd.text
        name = self.name.text
        self.progress.value = 0
        if name is "" or pwd is "" or url is "":            
            self._display_error('Tous les champs doivent etre remplis')
            return
        url = self._normalize_url(url)
        if not url:        
            self._display_error("L'url de votre cozy n'est pas correcte")
            return      
        try:  
            data = {'login': name}
            r = post(url + '/device/', data=data, auth=('owner', pwd)) 
            if r.status_code == 401:
                self._display_error("""L'url et le mot de passe de votre cozy 
                            ne correspondent pas""")
                return
            elif r.status_code == 400:
                self._display_error('Ce nom est deja utilise par un autre device')
                return
        except Exception, e:
            print e
            self._display_error("Verifiez l'url de votre cozy")
            return 

        thread = Thread(target=Clock.schedule_interval, args=(self.progress_bar, 1/25))
        thread.start()
        threadbis = Thread(target=self.configure, args=(url, pwd, name, r))
        threadbis.start()

    def configure(self, url, pwd, name, r):
        self.max_prog = 0.1
        self._display_error("")
        init_database() 
        self.max_prog = 0.15
        data = json.loads(r.content)
        self.max_prog = 0.98
        replicate_to_local(url, name, data['password'], data['id']) 
        err = init_device(url, data['password'], data['id'])
        if err:
            self._display_error(err)
            return             
        replicate_from_local(url, name, data['password'], data['id'])
        pass
      
    def progress_bar(self, dt):
        print "progress_bar"
        print self.max_prog
        print self.progress.value
        if self.max_prog < 0.16:
            self.progress.value = 100 * self.max_prog
        else:
            progress = recover_progression()
            print progress
            if progress > 0.98:
                return False
            self.progress.value = 15 + 85*progress

    def _normalize_url(self, url):
        url_parts = url.split('/')
        for part in url_parts:
            if part.find('cozycloud.cc') is not -1:
                return 'https://%s' %part
        return False

    def _display_error(self, error):
        self.error.text = error
        self.error.texture_update()
        self.error.anchors


class ConfigurationApp(App):
    def build(self):
        return Configuration()


if __name__ == '__main__':
    ConfigurationApp().run()