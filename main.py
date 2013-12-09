from kivy.app import App
from kivy.uix.anchorlayout import AnchorLayout
from kivy.properties import *


class Configuration(AnchorLayout):
    url = ObjectProperty()
    pwd = ObjectProperty()
    name = ObjectProperty()

    def install(self):
        print self.url.text
        print self.pwd.text
        print self.name.text
        pass


class ConfigurationApp(App):
    def build(self):
        return Configuration()


if __name__ == '__main__':
    ConfigurationApp().run()