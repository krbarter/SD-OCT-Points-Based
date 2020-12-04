import cv2
import statistics
import numpy as np
import matplotlib
import matplotlib.image as mpimg
from time import gmtime, strftime
from matplotlib import pyplot as plt
from matplotlib.pyplot import figure
figure(num=None, figsize=(10, 10.24), dpi=96, facecolor='w', edgecolor='k')

class HeatMapH:
    def __init__(self, top_points, top_white, mid_points, bot_white, bot_points):
        self.top_points = top_points
        self.top_white = top_white
        self.mid_points = mid_points
        self.bot_white = bot_white
        self.bot_points = bot_points

        #IMAGE MAP
        self.H = 1024
        self.W = 1000
        self.blank_image = np.zeros((self.H,self.W,3), np.uint8)

        #GRADIENT
        self.min = 0

    def map(self):
        for x in self.top_points:
            while len(x) < self.W:
                x.insert(0, 0)
                if len(x) < self.W:
                    x.append(0)

        for x in self.top_white:
            while len(x) < self.W:
                x.insert(0, 0)
                if len(x) < self.W:
                    x.append(0)

        for x in self.mid_points:
            while len(x) < self.W:
                x.insert(0, 0)
                if len(x) < self.W:
                    x.append(0)

        for x in self.bot_white:
            while len(x) < self.W:
                x.insert(0, 0)
                if len(x) < self.W:
                    x.append(0)

        for x in self.bot_points:
            while len(x) < self.W:
                x.insert(0, 0)
                if len(x) < self.W:
                    x.append(0)

        #SETTING THE VALUES OF THE MAP PER LAYER

        #TOP WHITE
        min_value = 200
        for w in range(0, self.W - 1):
            for x in self.top_points:
                for y in self.bot_points:
                    for r in range(x[w], y[w]):
                        self.blank_image[r][w] = self.blank_image[r][w] + 1
        '''
        #TOP WHITE TO MID
        for w in range(0, self.W - 1):
            for x in self.top_white:
                for y in self.mid_points:
                    for r in range(x[w], y[w]):
                        if r > min_value:
                            self.blank_image[r][w] =  self.blank_image[r][w] + 1

        #MID TO BOT WHITE
        for w in range(0, self.W - 1):
            for x in self.mid_points:
                for y in self.bot_white:
                    for r in range(x[w], y[w]):
                        if r > min_value:
                            self.blank_image[r][w] =  self.blank_image[r][w] + 1

        #BOT WHITE TO BOT
        for w in range(0, self.W - 1):
            for x in self.bot_white:
                for y in self.bot_points:
                    for r in range(x[w], y[w]):
                        if r > min_value:
                            self.blank_image[r][w] =  self.blank_image[r][w] + 1
        '''

    def gradient(self):
        self.min = np.amin(self.blank_image[np.nonzero(self.blank_image)])
        print(self.min)
        
        # currently not using the colour methods leaving it black and white
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

        # APPLYING THE GRADIENT TO THE IMAGE
        """
        for x in self.blank_image:
            for y in x:
                for z in y:
                    print(z)
                    if int(z) == 0:
                        z = [0,0,0]
                    if int(z) > len(color_gradient):
                               z = [105,0,0]
                    z = color_gradient[z - self.min]
        

        for w in range(0, self.W - 1):
            for x in self.top_points:
                for y in self.bot_points:
                    for r in range(x[w], y[w]):
                            if self.blank_image[r][w][0] > len(color_gradient):
                                self.blank_image[r][w] = [105,0,0]
                            else:
                                self.blank_image[r][w] = color_gradient[self.blank_image[r][w][0]]
        pad = [0,0,0]
        while len(color_gradient) < 1000:
            color_gradient.insert(0, pad)
            if len(color_gradient) < 1000:
                color_gradient.append(pad)

        for x in range(0, 15):
            np.append(self.blank_image, color_gradient)

        font = cv2.FONT_HERSHEY_SIMPLEX
        cv2.putText(self.blank_image, "Min",(250, len(self.blank_image) - 15), font, 1,(255,255,255),1,cv2.LINE_AA)
        cv2.putText(self.blank_image, "Max",(685, len(self.blank_image) - 15), font, 1,(255,255,255),1,cv2.LINE_AA)
        """
        
    def createImg(self):
        #SAVING THE IMAGE
        time_current = strftime("%Y-%m-%d %H-%M-%S", gmtime())
        cv2.imshow("Retinal Heatmap2", self.blank_image)
        cv2.imwrite("HeatMap2" + time_current + ".tiff", self.blank_image)
        
    def sceduler(self):
        HeatMapH.map(self)
        HeatMapH.gradient(self)
        HeatMapH.createImg(self)


if __name__ == "__main__":
    inx = [[45], [23], [12]]
    iny = [[2]]
    retinalMap = HeatMapH(inx,inx,inx,inx,iny)
    retinalMap.sceduler()
