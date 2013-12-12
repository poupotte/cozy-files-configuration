from kivy.app import App
from kivy.uix.anchorlayout import AnchorLayout
from kivy.properties import *
from replication import recover_progression_binary
from kivy.clock import Clock
from threading import Thread
from multiprocessing import Process

import download_binary
import sys
import time

class Binary(AnchorLayout):
    '''
    Manage binaries download window
    '''
    progress = ObjectProperty()

    def init(self):
        '''
        Initialize class
        '''
        Clock.schedule_interval(self.progress_bar, 1/25)
        thread_configure = Thread(target=self.download)
        thread_configure.start()


    def download(self):
        '''
        Download binaries for all files
        '''
        self.download = Process(target = download_binary.main)
        self.download.start()
        pass

    def progress_bar(self, dt):
        '''
        Update progress bar
        '''
        progress = recover_progression_binary()
        print progress
        if progress == 1.0:
            self.progress.value = 100
            self.download.terminate()
            time.sleep(5)
            sys.exit(0)
            return False
        self.progress.value = 100*progress


class BinaryApp(App):
    def build(self):
        bin = Binary()
        bin.init()


if __name__ == '__main__':
    BinaryApp().run()