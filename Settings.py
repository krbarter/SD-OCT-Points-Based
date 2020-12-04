import os
class Settings:
    def __init__(self, file):
        self.filepath = file
    
    def retriveSettings(self):
        fileopen = open(self.filepath, "r")
        fileopen = fileopen.read().lower()
        settingsList = fileopen.split(" ")
        return settingsList