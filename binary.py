from kivy.app import App
from kivy.uix.anchorlayout import AnchorLayout
from kivy.properties import *
from replication import recover_progression_binary
from kivy.clock import Clock
from threading import Thread
from multiprocessing import Process


import download_binary
import sys

class Binary(AnchorLayout):
    progress = ObjectProperty()

    def init(self):
        print "build"
        Clock.schedule_interval(self.progress_bar, 1/25)
        thread_configure = Thread(target=self.download)
        thread_configure.start()


    def download(self):
        download = Process(target = download_binary.main)
        download.start()

    def progress_bar(self, dt):
        print "progress_bar"
        print self.progress.value
        progress = recover_progression_binary()
        print progress
        if progress is 1:
            sys.exit(0) 
            return False
        self.progress.value = 100*progress


class BinaryApp(App):
    def build(self):
        bin = Binary()
        bin.init()
        return bin


if __name__ == '__main__':
    BinaryApp().run()