""" © 2019-2022 Kent Barter All Rights Reserved """
import os
import cv2
import xlwt
import xlsxwriter
import statistics
import numpy as np
import matplotlib.image as mpimg
from time import gmtime, strftime
from xlwt import Workbook
from matplotlib import pyplot as plt
from matplotlib.pyplot import figure
from matplotlib.pyplot import Axes
figure(num=None, figsize=(10, 10.24), dpi=96, facecolor='w', edgecolor='k')
from Project import Directory # file imports
from HeatMap import HeatMap
from HeatMapH import HeatMapH
from Settings import Settings

class Image:
    def __init__(self, img_List):
        self.img_List = img_List

        # retreving the setting from the settings file
        f = "settings.txt"
        s = Settings(f)
        self.s = s.retriveSettings()
        self.name = ""
        
        #layers
        self.outer_distance_list = []
        self.white_top_list      = []
        self.mid_top_list        = []
        self.mid_bot_list        = []
        self.white_bot_list      = []
        self.inner_distance_list = []

        # new heatmap
        self.outer_distance_gaps = []
        for x in range(0, 100):
            l = []
            for y in range(0, 1000):
                l.append("B")
            self.outer_distance_gaps.append(l)

        self.min_list = []
        self.max_list = []

        # getting the number of points measured for each frame
        self.outer_distance_measurement_number = []
        self.white_top_measurement_number      = []
        self.mid_top_measurement_number        = []
        self.mid_bot_measurement_number        = []
        self.white_bot_measurement_number      = []
        self.inner_distance_measurement_number = []
        
        #thinkness
        self.retinal_thickness   = []

        #getting the image points for heatmap2 (move heatmap points to set methods / each point should be unique)
        self.top_points = []
        self.top_white  = []
        self.mid_points = []
        self.bot_white  = []
        self.bot_points = []
        
        #start and stop / frame information
        self.start = int(self.s[0])
        self.stop  = int(self.s[1])
        self.number_of_images = self.stop - self.start
        self.frame_list = []

        #BOUNDS SETTINGS
        self.end_bound_list = []                         # list that contains the end bouds (4) // if length = 0 no bounds set
        self.white_value_threshold_list = [102, 99]      # first value -> main | second value -> secondary[end boundaries]

        #SETTINGS // THRESHOLDING VARIBLES
        self.image_set_number      = int(self.s[2])
        self.white_value_threshold = int(self.s[3])       #Standard Value -> 110  ==> [IF THE OTHER VALUE IS NOT USED]
        self.minimum_gap_value     = int(self.s[4])       #Standard Value -> -35
        self.maximum_gap_value     = int(self.s[5])       #Standard Value -> -150
        self.min_gap_value         = int(self.s[6])       #Standard Value -> 4

        # ALL MEASUREMENT ARE IN MICROMETERS (1 pixel * 1.62) // set to one for measurment in pixels
        self.newton_meter_conversion = 1.62      
        self.white_value_threshold_string = ""
        for x in range(0, len(self.white_value_threshold_list)):
            self.white_value_threshold_string  = self.white_value_threshold_string + str(self.white_value_threshold_list[x]) + " "
        self.end_bound_string = ""
        for x in range(0, len(self.end_bound_list)):
            self.end_bound_string = self.end_bound_string + str(self.end_bound_list[x]) + " "

        # Set by the program on its first run // AUTOMATIC SETTING
        self.last_top_value     = 0
        self.white_top_per      = 0
        self.mid_top_per        = 0
        self.mid_bot_per        = 0
        self.white_bot_per      = 0
        self.inner_distance_per = 0

        #Novel characteristics of the cultured Lumpfish Cyclopterus lumpus eye during post-hatch larval and juvenile developmental stages
        #Retinal Thickness - nfl to post
        #top white         - nfl to glc
        #bot white         - onl to post
        #inner distance    - glc to only
        #Focusing on the center of the eye, Images 30-70
        #Two Types of errors can be detected
    
    def getNumberOfImages(self):
        return self.number_of_images
        
    def getImageList(self):
        return self.img_List

    def getRetinalThickness(self):
        return self.retinal_thickness

    #RETURING IMAGE DATA
    def getTopPoints(self):
        return self.top_points

    def getTopWhite(self):
        return self.top_white

    def getMidPoints(self):
        return self.mid_points

    def getRetinalThicknessGaps(self):
        return self.outer_distance_gaps

    def getBotWhite(self):
        return self.bot_white

    def getBotPoints(self):
        return self.bot_points

    def getName(self):
        return self.name

    def getFrameList(self):
        return self.frame_list

    def getHeat(self):
        return self.s[8]

    def Scheduler(self):
        for x in range(self.start, self.stop):
            currentImage = self.img_List[self.image_set_number][x]
            self.animal_number = currentImage[5:-10]
            print(currentImage)
            img = Image.prepareImage(self, currentImage)

            if Image.TestImage(self, img) == True:
                self.frame_list.append(currentImage[-8:-5])
                # setting the end bound
                if len(self.end_bound_list) > 0:
                    if (x >= self.end_bound_list[0] and x <= self.end_bound_list[1]) or (x >= self.end_bound_list[2] and x <= self.end_bound_list[3]):
                        self.white_value_threshold = self.white_value_threshold_list[1]  # won't return to orginal value
                    else:
                        self.white_value_threshold = self.white_value_threshold_list[0]
                Image.medianDerterminant(self, img, self.s[9], x)
            else:
                print("This Image has an error if type: ")

        #print(len(self.retinal_thickness))
        #print(len(self.retinal_thickness[0]))
        #print(self.retinal_thickness)
        
        """Data Storage"""
        if int(self.s[7]) == 1:  Image.StoreDataClassic(self)
        if int(self.s[7]) == 2:  Image.StoreDataModern(self)
        if int(self.s[7]) == 3:  Image.StoreCommaSeperatedValues(self)
        cv2.destroyAllWindows()

    def TestImage(self, mat_img):
        histr = cv2.calcHist([mat_img],[0],None,[256],[0,256])
        hist_sum_Pixel = sum(histr[50:100])
        hist_sum_Blank = sum(histr[100:125])
        error = True

        if hist_sum_Pixel < 800000:
            error = False
            print("Pixelation Error")

        if hist_sum_Blank < 9000:
            print("Blank Error")
            error = False

        return error
    
    def prepareImage(self, currentImg):
        # denoise folled by smoothing filters
        mat_img = mpimg.imread(currentImg, 0) #loading as greyscale image
        mat_img = cv2.fastNlMeansDenoising(mat_img, None, 12, 13, 21) #((mat_img, None, 9, 13, 21))
        mat_img = cv2.GaussianBlur(mat_img,(5,5),0)
        mat_img = cv2.medianBlur(mat_img,5)  # stsandard value - 5
        ret,mat_img = cv2.threshold(mat_img,127,255,cv2.THRESH_TRUNC)
        return mat_img
        
    def intDisplay(self, image):
        #Display matplot can when (Pillow is a requirement)
        plt.subplot(121),plt.imshow(image,cmap = 'gray')
        plt.title('Image'), plt.xticks([]), plt.yticks([])
        plt.subplot(122),plt.hist(image.ravel(),256,[0,256])
        plt.title('Histogram'), plt.xticks([]), plt.yticks([])
        plt.show(), plt.close(fig = None)
        
    def pointDetector(self, img):
        """finding critical points, to be mapped"""
        #finding as mant points as possible
        feature_points = []
        edges = cv2.Canny(img,12,200, 20) #image,min,max,apeture
        plt.imshow(edges,cmap = 'gray'), plt.show()
        
        #indeces and points
        indices = np.where(edges != [0])
        coordinates = zip(indices[0], indices[1])
        for x in coordinates:
            feature_points.append(x)
        print("Number of Points: ", len(feature_points))
        return feature_points

    #band detection to save on computing time
    def medianDerterminant(self, image, sl, currentImage):
        outer_distance     = []
        white_top_distance = []
        mid_top_distance   = []
        mid_bot_distance   = []
        white_bot          = []
        white_top          = []
        inner_distance     = []

        smooth = image.copy()

        #setting the points for the heatmap image
        image_bot       = []
        image_white_top = []
        image_mid       = []
        image_white_bot = []
        image_top       = []

        for pointx in range(0, 1000):
            midpath  = []
            midwhite = []
            top      = []
            bot      = []

            for y in range(0,500): #RESTRICTING THE BOTTOM RANGE 1024 total
                 color = image[y, pointx]
                 midpath.append([y, color[0]])
                 
            #setting this value based on a function (histogram) (setting based on number of pixals of each value
            #print(np.percentile(midpath, 55))
            
            for x in midpath:
                if midpath[midpath.index(x)][1] >= self.white_value_threshold: #110 is the standerd value // lower the value to allow more to be considred apart of the line // increase to tighten
                    midwhite.append(midpath.index(x))

            #should be getting the largest gap // manipluatio of the gap value can change which part of the retina will be detected by adjusting the minimum and maximum diatances
            value_to_print = 0
            for x in range(1, len(midwhite) - 1, 1):
                if midwhite[x] - midwhite[x + 1] <= self.minimum_gap_value and midwhite[x] - midwhite[x + 1] >= self.maximum_gap_value:   #-35 and -150 are the standard values
                    top = midwhite[:x+1]
                    bot = midwhite[x+1:]
                    medianPoint = top[-1] - round((top[-1] - bot[0]) / 2)
                    value_to_print += 1

                    if self.last_top_value == 0:
                        self.last_top_value = bot[-1] - top[0]

                    #getting down to pixel higlighting to get perpixel measurements
                    # if (top[-1] - top[0] >= self.min_gap_value and bot[-1] - bot[0] >= self.min_gap_value and top[0] != 0 and self.last_top_value - (bot[-1] - top[0]) >= -10)
                    # preventing two coloured points being on the sale point min gap standard - 5  low gap = 3
                    if (top[-1] - top[0] >= self.min_gap_value and bot[-1] - bot[0] >= self.min_gap_value and top[0] != 0 and self.last_top_value - (bot[-1] - top[0]) >= -10):
                        #image[medianPoint + 205][pointx] = (0,0,255,-1) # red points
                        #image[medianPoint + 206][pointx] = (0,0,255,-1) # red points
                        image[top[-1]][pointx] = (0,255,0,-1)    #top green
                        image[bot[0]][pointx] = (0,255,0,-1)     #bot green
                        image[top[0]][pointx] = (255,0,0,-1)     #top blue 
                        image[bot[-1]][pointx] = (255,0,0,-1)    #bot blue

                        if sl == "s":
                            smooth[medianPoint][pointx] = (0,0,255,-1) # red points
                            smooth[medianPoint][pointx] = (0,0,255,-1) # red points


                    #geting heatmap points
                    image_top.append(top[0])
                    image_white_top.append(top[-1])
                    image_mid.append(medianPoint)
                    image_white_bot.append(bot[0])
                    image_bot.append(bot[-1])

                    #ax = Axes3D(fig)
                    #ax.scatter(x, top[0], value_to_print)
                    
                    #total width of the retina
                    total_width = bot[-1] - top[0]
                    if total_width >= self.min_gap_value and top[0] != 0:
                        outer_distance.append(total_width)
                        self.outer_distance_gaps[currentImage][pointx] = total_width   # image number

                    #top white area of the retina
                    top_white_width = top[-1] - top[0]
                    if top_white_width >= self.min_gap_value and top[0] != 0:
                        white_top.append(top_white_width)

                    #top mid area of the retina
                    top_mid_width =  medianPoint - top[-1]
                    if top_mid_width >= self.min_gap_value and top[0] != 0:
                        mid_top_distance.append(top_mid_width)

                    #bot mid area of the retina
                    bot_mid_width =  bot[0] - medianPoint
                    if bot_mid_width >= self.min_gap_value and top[0] != 0:
                        mid_bot_distance.append(bot_mid_width)

                    #bottom white area of the retina
                    bot_white_width = bot[-1] - bot[0]
                    if bot_white_width >= self.min_gap_value and top[0] != 0:
                        white_bot.append(bot_white_width)

                    #inner area of the retina (between both white sections)
                    inner_point = bot[0] - top[-1]
                    if inner_point >= self.min_gap_value and top[0] != 0:
                        inner_distance.append(inner_point)

                    # shows the image  // turn off to speed up processing
                    self.last_top_value = bot[-1] - top[0]
                    #cv2.imshow("ImageK By: Kent Barter", image)

        #saving the image to the image  (priting whne the image has been complete)
        image_scale = cv2.cvtColor(image,cv2.COLOR_RGB2BGR) # moving from cv2's BRG mode
        image_crop = image_scale[0:750, 0:1000]
        #path = "C:\\Users\\krbar\\Desktop\\Project\\Images"
        path = "Images"
        #name = time_current = strftime("%Y-%m-%d %H-%M-%S", gmtime()) + ".tiff"
        self.name = self.animal_number.split(os.sep)[-1]
        name = self.name + " " + strftime("%Y-%m-%d %H-%M-%S", gmtime()) + ".tiff"
        mpimg.imsave(os.path.join(path , name), image_crop)

        if sl == "s":
            image_s = cv2.cvtColor(smooth,cv2.COLOR_RGB2BGR)
            path = "SmoothingLine"
            name = self.animal_number.split(os.sep)[-1] + "  " + str(self.frame_list[-1]) + " " + strftime("%Y-%m-%d %H-%M-%S", gmtime()) + ".tiff"
            mpimg.imsave(os.path.join(path , name), image_s)

        #getting the heatmap points for each image
        self.top_points.append(image_top)
        self.top_white.append(image_white_top)
        self.mid_points.append(image_mid)
        self.bot_white.append(image_white_bot)
        self.bot_points.append(image_bot)
                    
        #the avarge values of thickness of each layery
        if len(outer_distance) > 1: outer_distance_avg = statistics.mean(outer_distance)
        else: outer_distance_avg = 0
        
        if len(white_top) > 1: white_top_avg = statistics.mean(white_top)
        else: white_top_avg = 0

        if len(mid_top_distance) > 1 : mid_top_avg = statistics.mean(mid_top_distance)
        else: mid_top_avg = 0

        if len(mid_bot_distance) > 1: mid_bot_avg = statistics.mean(mid_bot_distance)
        else: mid_bot_avg = 0

        if len(white_bot) > 1: white_bot_avg = statistics.mean(white_bot)
        else: white_bot_avg = 0

        if len(inner_distance) > 1: inner_distance_avg = statistics.mean(inner_distance)
        else: inner_distance_avg = 0

        #getting the volume of each layer (to get the (percentage of each layer)
        outer_distance_volume = sum(outer_distance)
        white_top_volume = sum(white_top)
        mid_top_volume = sum(mid_top_distance)
        mid_bot_volume = sum(mid_bot_distance)
        white_bot_volume = sum(white_bot)
        inner_distance_volume = sum(inner_distance)

        # getting the number of meaurements of each average
        self.outer_distance_measurement_number.append(len(outer_distance))
        self.white_top_measurement_number.append(len(white_top))
        self.mid_top_measurement_number.append(len(mid_top_distance))
        self.mid_bot_measurement_number.append(len(mid_bot_distance))
        self.white_bot_measurement_number.append(len(white_bot))
        self.inner_distance_measurement_number.append(len(inner_distance))

        #collecting the avarage of each image
        self.outer_distance_list.append(outer_distance_avg)

        #getting the min and max for the use in the heatmap
        self.min_list.append(min(outer_distance_avg))
        self.max_list.append(max(outer_distance_avg))

        self.white_top_list.append(white_top_avg)
        self.mid_top_list.append(mid_top_avg)
        self.mid_bot_list.append(mid_bot_avg)
        self.white_bot_list.append(white_bot_avg)
        self.inner_distance_list.append(inner_distance_avg)

        #collecting the outer distance
        self.retinal_thickness.append(outer_distance)
        
        #volume percentage (of each layer compared to the total volume of the retina)
        if outer_distance_volume != 0:
            self.white_top_per = (white_top_volume / outer_distance_volume) *100
            self.mid_top_per = (mid_top_volume / outer_distance_volume) *100
            self.mid_bot_per = (mid_bot_volume / outer_distance_volume) *100
            self.white_bot_per = (white_bot_volume / outer_distance_volume) *100
            self.inner_distance_per = (inner_distance_volume / outer_distance_volume) *100
        
        #formating printout
        print("Number of points: ", len(outer_distance))
        #print("Retinal Thicness: ", outer_distance),  print("Retinal Thicness Avarage: ",        outer_distance_avg), print()
        #print("GLC to ONL: ", inner_distance),        print("GLC to ONL Avarage: ",              inner_distance_avg), print()
        #print("NFL to GLC: ", white_top),             print( "NFL to GLC  Distance Avarage: ",   white_top_avg),      print()
        #print("ONL to Post: ", white_bot),            print( "ONL to Post Distance Avarage: ",   white_bot_avg),      print()

        print("Volume and Percentage")
        print("Total Volume: ",      outer_distance_volume), print()
        print("NFL to GLC Volume: ",      white_top_volume), print("NFL/GLC Volume Percentage: ",      self.white_top_per), print()
        print("ONL to RPE Volume: ",     white_bot_volume), print("ONL to RPE Volume Percentage: ",     self.white_bot_per), print()
        print("GLC to ONL Volume: ", inner_distance_volume), print("GLC to ONL Volume Percentage: ", self.inner_distance_per), print()
        #print("Animal Number: ", self.animal_number), print(self.frame_list)
        
        # at the end of the computation send the value of self.outer_distance_list to the heatmap
        cv2.waitKey(1)
        
    """Data Storage methods"""
    def StoreDataClassic(self): #xls format
        wb = xlwt.Workbook(encoding="utf-8")
        sheet = wb.add_sheet('SD-OST')
        style = xlwt.easyxf('font: bold 1') 

        sheet.write(0, 0, "Frame Number", style)
        sheet.write(0, 2, "Retinal Thickness (um)" , style)
        sheet.write(0, 3, "Number of Readings", style)
        sheet.write(0, 6, "NFL/GLC (um)" , style)
        sheet.write(0, 7, "Number of Readings", style)
        sheet.write(0, 10, "IPL/INL/OPL/ONL/IS (um)" , style)
        sheet.write(0, 11, "Number of Readings", style)
        sheet.write(0, 14, "OS/RPE (um)" , style)
        sheet.write(0, 15, "Number of Readings", style)

        #volumes percentages
        sheet.write(0,  20, "Specimen", style)
        sheet.write(3,  20, "NFL/GLC Volume Percentage", style)
        sheet.write(6,  20, "IPL/INL/OPL/ONL/IS Volume Percentage", style) 
        sheet.write(9,  20, "OS/RPE Volume Percentage", style) 
        sheet.write(12, 20, "White Value Threshold", style)
        sheet.write(15, 20, "Minimum Gap Threshold", style)
        sheet.write(18, 20, "Maximum Gap Threshold", style)
        sheet.write(21, 20, "Mimimum Thickness Value", style)
        
        listEnd = len(self.outer_distance_list)
        for x in range(0, listEnd):
            outdist = round(self.outer_distance_list[x] * self.newton_meter_conversion, 1)
            wtop    = round(self.white_top_list[x]* self.newton_meter_conversion, 1)  
            indist  = round(self.inner_distance_list[x]* self.newton_meter_conversion, 1)
            wbot    = round(self.white_bot_list[x]* self.newton_meter_conversion, 1)
            sheet.write(x + 1, 0,  self.frame_list[x])                         # Frame Number                Messurments:
            sheet.write(x + 1, 2,  outdist)               # Retinal Thicness
            sheet.write(x + 1, 3,  self.outer_distance_measurement_number[x])  # Number of Measurements
            sheet.write(x + 1, 6,  wtop)                     # NFL to GLC
            sheet.write(x + 1, 7,  self.white_top_measurement_number[x])       # Number of Measurements
            sheet.write(x + 1, 10, indist)                # GLC to Coroi
            sheet.write(x + 1, 11, self.inner_distance_measurement_number[x])  # Number of Measurements
            sheet.write(x + 1, 14, wbot)                     # ONL to Post
            sheet.write(x + 1, 15, self.white_bot_measurement_number[x])       # Number of Measurements
        #end values
        sheet.write(1,  20, self.animal_number)
        sheet.write(4,  20, round(self.white_top_per, 1))
        sheet.write(7,  20, round(self.inner_distance_per, 1))
        sheet.write(10, 20, round(self.white_bot_per, 1))
        #settings varibles
        sheet.write(13, 20, self.white_value_threshold)
        sheet.write(16, 20, self.minimum_gap_value)
        sheet.write(19, 20, self.maximum_gap_value)
        sheet.write(22, 20, self.min_gap_value)
        
        time_current = strftime("%Y-%m-%d %H-%M-%S", gmtime())
        name_start = self.animal_number.split(os.sep)[-1]
        wb.save(name_start + " " + time_current + ".xls")
        
    def StoreDataModern(self): #xlsx format
        time_current = strftime("%Y-%m-%d %H-%M-%S", gmtime())
        name_start = self.animal_number.split(os.sep)[-1]
        workbook = xlsxwriter.Workbook((name_start + " " + time_current + ".xlsx"))
        sheet = workbook.add_worksheet()
        style = workbook.add_format({'bold': True})

        sheet.write(0, 0, "Frame Number", style)
        sheet.write(0, 2, "Retinal Thickness (um)" , style)
        sheet.write(0, 3, "Number of Readings", style)
        sheet.write(0, 6, "NFL/GLC (um)" , style)
        sheet.write(0, 7, "Number of Readings", style)
        sheet.write(0, 10, "IPL/INL/OPL/ONL/IS (um)" , style)
        sheet.write(0, 11, "Number of Readings", style)
        sheet.write(0, 14, "OS/RPE (um)" , style)
        sheet.write(0, 15, "Number of Readings", style)

        #volumes percentages
        sheet.write(0,  20, "Specimen", style)
        sheet.write(3,  20, "NFL/GLC Volume Percentage", style)
        sheet.write(6,  20, "IPL/INL/OPL/ONL/IS Volume Percentage", style) 
        sheet.write(9,  20, "OS/RPE Volume Percentage", style) 
        sheet.write(12, 20, "White Value Threshold", style)
        sheet.write(15, 20, "Minimum Gap Threshold", style)
        sheet.write(18, 20, "Maximum Gap Threshold", style)
        sheet.write(21, 20, "Mimimum Thickness Value", style)
        
        listEnd = len(self.outer_distance_list)
        for x in range(0, listEnd):
            outdist = round(self.outer_distance_list[x] * self.newton_meter_conversion, 1)
            wtop    = round(self.white_top_list[x]* self.newton_meter_conversion, 1)  
            indist  = round(self.inner_distance_list[x]* self.newton_meter_conversion, 1)
            wbot    = round(self.white_bot_list[x]* self.newton_meter_conversion, 1)
            sheet.write(x + 1, 0,  self.frame_list[x])                         # Frame Number                Messurments:
            sheet.write(x + 1, 2,  outdist)               # Retinal Thicness
            sheet.write(x + 1, 3,  self.outer_distance_measurement_number[x])  # Number of Measurements
            sheet.write(x + 1, 6,  wtop)                     # NFL to GLC
            sheet.write(x + 1, 7,  self.white_top_measurement_number[x])       # Number of Measurements
            sheet.write(x + 1, 10, indist)                # GLC to Coroi
            sheet.write(x + 1, 11, self.inner_distance_measurement_number[x])  # Number of Measurements
            sheet.write(x + 1, 14, wbot)                     # ONL to Post
            sheet.write(x + 1, 15, self.white_bot_measurement_number[x])       # Number of Measurements
        
        #end values
        sheet.write(1,  20, self.animal_number)
        sheet.write(4,  20, round(self.white_top_per, 1))
        sheet.write(7,  20, round(self.inner_distance_per, 1))
        sheet.write(10, 20, round(self.white_bot_per, 1))
        #settings varibles
        sheet.write(13, 20, self.white_value_threshold)
        sheet.write(16, 20, self.minimum_gap_value)
        sheet.write(19, 20, self.maximum_gap_value)
        sheet.write(22, 20, self.min_gap_value)
        workbook.close()

    def StoreCommaSeperatedValues(self): #csv format
        time_current = strftime("%Y-%m-%d %H-%M-%S", gmtime())
        name_start = self.animal_number.split(os.sep)[-1]
        listEnd = len(self.outer_distance_list)
        with open(name_start + " " + time_current + ".csv", "w") as file:
            file.write("Frame Number, ,Retinal Thickness,Number of Readings, , NFL/GLC (um),Number of Readings, , IPL/INL/OPL/ONL/IS (um), Number of Readings, , OS/RPE (um), Number of Readings,\n")
            for x in range(0, listEnd, 1):
                outdist = round(self.outer_distance_list[x] * self.newton_meter_conversion, 1)
                wtop    = round(self.white_top_list[x]* self.newton_meter_conversion, 1)  
                indist  = round(self.inner_distance_list[x]* self.newton_meter_conversion, 1)
                wbot    = round(self.white_bot_list[x]* self.newton_meter_conversion, 1)
                frame_num       = str(self.frame_list[x])                            # Frame Number            Measurements:
                out_dist        = str(outdist)                  # Retinal Thicness
                out_dist_number = str(self.outer_distance_measurement_number[x])     # Number of Measurements
                wt_top          = str(wtop)                       # NFL to GLC
                wt_top_number   = str(self.white_top_measurement_number[x])          # Number of Measurements
                wt_bot          = str(wbot)                       # ONL to Post
                wt_bot_number   = str(self.white_bot_measurement_number[x])          # Number of Measurements
                in_dist         = str(indist)                  # GLC to ONL
                in_dist_number  = str(self.inner_distance_measurement_number[x])     # Number of Measurements
                seperator = ","
                blank = " "
                tojoin = [frame_num, blank, out_dist,  out_dist_number, blank, wt_top, wt_top_number, blank, in_dist, in_dist_number, blank, wt_bot, wt_bot_number]
                x = seperator.join(tojoin)
                file.write(x + "\n")
            file.write("\n")
            file.write("Specimen, ,NFL/GLC Volume Percentage, ,IPL/INL/OPL/ONL/IS Volume Percentage, ,OS/RPE Volume Percentage\n")
            line = self.animal_number + ", ," + str(round(self.white_top_per, 1)) + ", ," + str(round(self.inner_distance_per, 1)) + ", ," + str(round(self.white_bot_per, 1)) + "\n"
            file.write(line)
            file.write("\n")
            file.write("White Value Threshold, , Minimum Gap Threshold, , Maximum Gap Threshold, , Mimimum Thickness Value\n")
            line2 = str(self.white_value_threshold) + ", ," + str(self.minimum_gap_value) + ", ," + str(self.maximum_gap_value) + ", ," + str(self.min_gap_value) + "\n"
            file.write(line2)
        file.close()

# directory.openDirectory() = img_list
def __main__():
    #directory_name = str(input("Enter the name of the working directory: "))
    directory = Directory("Data")
    image = Image(directory.openDirectory())
    image.Scheduler()

    #creating the retinal heatmap (and the location list)
    retinal_thickness = image.getRetinalThickness()
    name = image.getName()
    frame = image.getFrameList()
    heat = image.getHeat()
    gaps = image.getRetinalThicknessGaps()
    retinalMap = HeatMap(retinal_thickness, name, frame, heat, gaps)
    retinalMap.sceduler()

    #creating retinal heatmap2
    #top_points = image.getTopPoints()
    #top_white = image.getTopWhite()
    #mid_points = image.getMidPoints()
    #bot_white = image.getBotWhite()
    #bot_points = image.getBotPoints()
    #heatmap = HeatMapH(top_points, top_white, mid_points, bot_white, bot_points)
    #heatmap.sceduler()

    #showing the heatmap image  (Not using the image display section to complete the analysis)
    #if (retinalMap.getIsSaved() == True):
    #    image_location = ImageDisplay(directory.openDirectory(), retinalMap.getPixelWidth(), image.getNumberOfImages(), retinalMap.getfile_name())
    #    image_location.pixel_location()
    #    image_location.showImg()
__main__()
