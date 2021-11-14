import os
import cv2
import statistics
import numpy as np
import matplotlib.image as mpimg
from time import gmtime, strftime
from matplotlib import pyplot as plt
from matplotlib.pyplot import figure
from mpl_toolkits import mplot3d
from matplotlib import cm
figure(num=None, figsize=(10, 10.24), dpi=96, facecolor='w', edgecolor='k')

class HeatMap:
    def __init__(self, retinal_thickness, name, frame, heat, retinal_thickness_gaps, dirname):
        self.retinal_thickness = retinal_thickness
        self.retinal_thickness_gaps = retinal_thickness_gaps
        self.name = name
        self.dirname = dirname
        
        if len(frame) > 2:
            self.frame_title = "Frame " + str(frame[0]) + "-" + str(frame[-1])
        else:
            self.frame_title = ""
        
        self.frame = frame
        self.retinal_array    = []
        self.retinal_array_3d = []
        self.retinal_gradient = []
        self.color_key        = []
        
        self.minR = 0
        self.maxR = 0
        self.pixel_width = 10 #standard = 4
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

        self.minR = 23
        self.maxR = 123

        if self.heat == "A" or self.heat == "a":
            self.new_min = np.amin(self.maxR)
        else:
            self.new_min = int(self.heat)

        print(), print("MINUMUM VALUE: ", self.new_min)
        
        for x in self.retinal_thickness_gaps:
            img    = []
            img_3d = []
            for y in x:
                if y  != "B":
                    img.append(int(y) - self.new_min)   # 155 OS 00014 = 113 for the minumin value for comparison // new_min
                    img_3d.append(int(y) - self.new_min) 
                else:
                    img.append(y)
            self.retinal_array.append(img)
            self.retinal_array_3d.append(img_3d)

        self.color_gradient = [[0,100,250], [0,95,235], [0,90,255], [0,85,212], [0,80,199], [0,75,186],
                          [0,70,175],  [0,65,162], [0,60,151], [0,55,138], [0,50,125],                       #Blue

                        [9,255,0], [8,245,0], [8,235,0], [7,225,0], [7,215,0], [6,205,0],
                        [6,195,0], [5,185,0], [4,175,0], [4,165,0], [3,155,0],                               #Green

                        [255,255,0], [250,250,0], [245,245,0], [240,240,0], [235,235,0],
                        [230,230,0], [225,225,0], [220,220,0], [215,215,0], [210,210,0], [205,205,0],        #Yellow

                        [255,119,0], [245,117,0], [235,110,0], [225,105,0], [215,100,0], [205,96,0],
                        [195,91,0], [185,86,0], [175,83,0], [165,78,0], [155,72,0],                          #Orange

                        [255,0,0], [240,0,0], [225,0,0], [210,0,0], [195,0,0], [180,0,0],
                        [165,0,0], [150,0,0], [135,0,0], [120,0,0], [105,0,0]]                               #Red

        self.color_key = [x for x in self.color_gradient for i in range(10)]

        #spplying the color values
        for line in self.retinal_array:
            line_in = []
            for x in line:
                if x == "B":
                    line_in.append([0,0,0])
                elif (x >= len(self.color_gradient)):
                    line_in.append([105,0,0])
                elif (x < 0):
                    line_in.append([0,100,250])
                else:
                    line_in.append(self.color_gradient[x])

            #adding four lines per measurement to extend the image
            for x in range(self.pixel_width):
                self.retinal_gradient.append(line_in)       
            #image gradient key

        for x in self.retinal_gradient:
            if np.all(x == x[0]):
                self.retinal_gradient.remove(x)


   
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

        min_line = str(round(self.minR * 1.62)) + "um"
        max_line = str(round(self.maxR * 1.62)) + "um"
        cv2.putText(blank_image, min_line,(230, len(self.retinal_gradient) - 20), font, 1,(255,255,255),1,cv2.LINE_AA)
        cv2.putText(blank_image, max_line,(660, len(self.retinal_gradient) - 20), font, 1,(255,255,255),1,cv2.LINE_AA)

        cv2.imwrite(self.dirname + os.sep + str(self.new_min) + " " + self.file_name + ".tiff", blank_image)
        print(self.file_name + ".tiff")
        self.image_saved = True #saves the image in the current directory
        #cv2.imshow("Retinal Heatmap", blank_image)

    # tring to plot the heatmap in 3d to show the retinal nerve in more context, points are not displaying properly, too mant points when loading the program
    def plot3d(self):
        points = []
        for x in range(0, len(self.retinal_array_3d)):
            for y in range(0, len(self.retinal_array_3d[x])):
                points.append([y, self.retinal_array_3d[x][y], x])

        x_p = []
        y_p = []
        z_p = []
        for x in range(0, len(points)):
            x_p.append(points[x][0])
            y_p.append(points[x][1])
            z_p.append(points[x][2])

        #print(points)
        #print(x_p)
        #print(len(y_p))
        #print(len(z_p))
        #ax.plot_trisurf(y_p, x_p, z_p, cmap=cm.coolwarm, linewidth=0, antialiased=False)

        # creating the 3d plot and displaying the points / one colour
        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')
        ax.scatter(y_p, x_p, z_p, alpha=1)
        plt.show()

    def sceduler(self):
        HeatMap.gradient(self)
        HeatMap.center(self)
        HeatMap.createImg(self)
        #HeatMap.plot3d(self)     # test feature

if __name__ == "__main__":
    retinal_thickness = [[45, 23], [23, 12], [12]]
    retinal_thickness_g = [[45, "B", 23], [23, 12], [12]]
    retinalMap = HeatMap(retinal_thickness, "Some", [40, 40], "A", retinal_thickness_g)
    retinalMap.sceduler()
