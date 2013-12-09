from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.gridlayout import GridLayout


class Configuration(GridLayout):
    pass


class ConfigurationApp(App):
    def build(self):
        return Configuration()


if __name__ == '__main__':
    ConfigurationApp().run()