from pynput import keyboard
from threading import Thread

def OnPress(key):
    print(key)
def OnRelease(key):
    print(key)

class KeyAction(Thread):
    def __init__(self):
        pass