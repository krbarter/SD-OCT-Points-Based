import cv2
import statistics
import numpy as np
import matplotlib
import matplotlib.image as mpimg
from time import gmtime, strftime
from matplotlib import pyplot as plt
from matplotlib.pyplot import figure
figure(num=None, figsize=(10, 10.24), dpi=96, facecolor='w', edgecolor='k')

class HeatMap:
    def __init__(self, retinal_thickness, name, frame, heat):
        self.retinal_thickness = retinal_thickness
        self.name = name
        self.frame_title = "Frame " + str(frame[0]) + "-" + str(frame[-1])
        self.frame = frame
        self.retinal_array = []
        self.retinal_gradient = []
        self.color_key = []
        self.minR = 0
        self.maxR = 0
        self.pixel_width = 6 #standard = 4
        self.file_name = strftime("%Y-%m-%d %H-%M-%S", gmtime())
        self.image_saved = False
        self.heat = heat

    def getIsSaved(self):
        return self.image_saved

    def getfile_name(self):
        return self.file_name

    def getPixelWidth(self):
        return self.pixel_width

    # A gradient from white, red, yellow, green and blue.
    def gradient(self):
        self.minR = np.amin(self.retinal_thickness)
        self.maxR = np.amax(self.retinal_thickness)

        if self.heat == "A":
            new_min = np.amin(self.maxR)
        else:
            new_min = int(self.heat)

        print(), print("MINUMUM VALUE: ", new_min)
        
        for x in self.retinal_thickness[]:
            img = []
            for y in x:
                img.append(y - new_min)   # 155 OS 00014 = 113 for the minumin value for comparison // new_min
            self.retinal_array.append(img)

        color_gradient = [[0,100,250], [0,95,235], [0,90,255], [0,85,212], [0,80,199], [0,75,186],
                          [0,70,175],  [0,65,162], [0,60,151], [0,55,138], [0,50,125], #Blue

                        [9,255,0], [8,245,0], [8,235,0], [7,225,0], [7,215,0], [6,205,0],
                        [6,195,0], [5,185,0], [4,175,0], [4,165,0], [3,155,0], #Green

                        [255,255,0], [250,250,0], [245,245,0], [240,240,0], [235,235,0],
                        [230,230,0], [225,225,0], [220,220,0], [215,215,0], [210,210,0], [205,205,0], #Yellow

                        [255,119,0], [245,117,0], [235,110,0], [225,105,0], [215,100,0], [205,96,0],
                        [195,91,0], [185,86,0], [175,83,0], [165,78,0], [155,72,0], #Orange

                        [255,0,0], [240,0,0], [225,0,0], [210,0,0], [195,0,0], [180,0,0],
                        [165,0,0], [150,0,0], [135,0,0], [120,0,0], [105,0,0]] #Red

        self.color_key = [x for x in color_gradient for i in range(10)]

        #spplying the color values
        for line in self.retinal_array:
            line_in = []
            for x in line:
                if (x >= len(color_gradient)):
                    line_in.append([105,0,0])
                elif (x < 0):
                    line_in.append([0,100,250])
                else:
                    line_in.append(color_gradient[x])

            #adding four lines per measurement to extend the image
            for x in range(self.pixel_width):
                self.retinal_gradient.append(line_in)
            #image gradient key

   
    # Adding padding to the front and end of each image to keep the shape
    #cm = plt.get_cmap("gist_rainbow") 
    def center(self):
        total_padding = 1000 - len(self.retinal_thickness)
        color_pad = 1000 - len(self.color_key)   #should be placing more at the front of the array
        pad = [0,0,0]

        for x in self.retinal_gradient:
            while len(x) < 1000:
                x.insert(0, pad)
                if len(x) < 1000:
                    x.append(pad)

        blank_line = []
        for x in range(0,1000):
            blank_line.append(pad)

        while len(self.color_key) < 1000:
            self.color_key.insert(0, pad)
            if len(self.color_key) < 1000:
                self.color_key.append(pad)

        for x in range(45):
            self.retinal_gradient.insert(0, blank_line)
            self.retinal_gradient.append(blank_line)

        for x in range(7):
            self.retinal_gradient.append(self.color_key)

        for x in range(5):
            self.retinal_gradient.append(blank_line)

        #print("------------------")
        #print(len(self.retinal_gradient))
        #print(self.retinal_gradient[0])
        #print(len(self.retinal_gradient[0]))
            
    # create and save as a tiff file
    def createImg(self):
        
        height = len(self.retinal_gradient) #number of Images
        width = len(self.retinal_gradient[0]) #width of each images
        blank_image = np.zeros((height,width,3), np.uint8)

        #print("------------------") 
        # printing the image color values onto the image
        for x in range(0,height):
            #print(self.retinal_gradient[x])
            for y in range(0,width):
                #print(self.retinal_gradient[x][y])
                RGB = self.retinal_gradient[x][y]
                blank_image[x][y] = (RGB[2], RGB[1], RGB[0])
        font = cv2.FONT_HERSHEY_SIMPLEX
        position = 895 - (len(self.frame_title) - 10) * 10
        
        cv2.putText(blank_image, self.name,(5, 17), font, 0.5,(255,255,255),1,cv2.LINE_AA)
        cv2.putText(blank_image, self.frame_title,(position, 17), font, 0.5,(255,255,255),1,cv2.LINE_AA)
        
        cv2.putText(blank_image, "Min",(250, len(self.retinal_gradient) - 15), font, 1,(255,255,255),1,cv2.LINE_AA)
        cv2.putText(blank_image, "Max",(685, len(self.retinal_gradient) - 15), font, 1,(255,255,255),1,cv2.LINE_AA)

        cv2.imwrite(self.file_name + ".tiff", blank_image)
        print(self.file_name + ".tiff")
        self.image_saved = True #saves the image in the current directory
        cv2.imshow("Retinal Heatmap", blank_image)

    #creating the click line to show image of the measurement
    def clickbox(self):
        pass

    def sceduler(self):
        HeatMap.gradient(self)
        HeatMap.center(self)
        HeatMap.createImg(self)

if __name__ == "__main__":
    retinal_thickness = [[45, 23], [23, 12], [12]]
    retinalMap = HeatMap(retinal_thickness, "Some", [40, 40])
    retinalMap.sceduler()
