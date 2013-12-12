import subprocess


config = subprocess.call(['python', 'config.py', '--size=720x350'])
if config is 0:
    download = subprocess.call(['python', 'binary.py', '--size=720x350'])
    if download is 0:
        print "ok"
        #end = subprocess.call(['python', 'end.py', '--size=720x350'])