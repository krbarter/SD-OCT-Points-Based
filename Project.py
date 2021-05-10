"""Use attrib -h in cmd on a file to reveal and delete all hidden files in data input"""
import os

class Directory:
    imageGroups = []
    img_input = []
    
    def __init__(self, directory_name):
        self.directory_name = directory_name
    
    #creating the image sets to be processed
    def openDirectory(self):
        if os.path.isdir(self.directory_name) == True:
            for x in os.listdir(self.directory_name):
                self.imageGroups.append("Data/" + x)
        else:
            return "Input is not a valid drectory"

        for x in self.imageGroups:
            imgs = []
            if os.path.isdir(x) == True:
                for y in os.listdir(x):
                    if y.endswith(".TIFF"):
                        imgs.append(x + str(os.sep) + y)
            self.img_input.append(imgs)
        return self.img_input
