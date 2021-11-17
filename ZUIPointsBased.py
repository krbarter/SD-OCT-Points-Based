""" © 2019-2021 Kent Barter All Rights Reserved """
import os
import cv2
import xlwt
import xlsxwriter
import statistics
import numpy as np
import matplotlib.image as mpimg
from random import randint
from time import gmtime, strftime
from xlwt import Workbook
from matplotlib import pyplot as plt
from matplotlib.pyplot import figure
from matplotlib.pyplot import Axes
figure(num=None, figsize=(10, 10.24), dpi=96, facecolor='w', edgecolor='k')
from HeatMap import HeatMap

class Image:
    def __init__(self, img_List, s_image_number, e_image_number, white_value_threshold, minimum_gap_value, maximum_gap_value, min_gap_value, storage_type, heatmap_setting, smoothingline_setting, testing, start_height, end_height, start_width, end_width, dirname):
        self.img_List = img_List
        self.start    = s_image_number
        self.stop     = e_image_number
        self.name     = ""
        dir_path      = os.path.dirname(os.path.realpath("UIPointsBased.py"))
        
        #SETTINGS // THRESHOLDING VARIBLES
        self.white_value_threshold = white_value_threshold      #Standard Value -> 110  ==> [IF THE OTHER VALUE IS NOT USED]
        self.minimum_gap_value     = minimum_gap_value          #Standard Value -> -35
        self.maximum_gap_value     = maximum_gap_value          #Standard Value -> -150
        self.min_gap_value         = min_gap_value              #Standard Value -> 4
        self.storage_type          = storage_type
        self.heatmap_setting       = heatmap_setting
        self.smoothingline_setting = smoothingline_setting
        self.testing = testing
        self.start_height = int(start_height)
        self.end_height   = int(end_height)
        self.start_width  = int(start_width)
        self.end_width    = int(end_width)
        self.dirname      = dir_path + os.sep + dirname.split(os.sep)[-1]

        # makeing new directory
        if os.path.exists(self.dirname):
            self.dirname = self.dirname + " " + str(randint(0, 999999))
            os.makedirs(self.dirname)
        else:
            os.makedirs(self.dirname)
        
        #layers
        self.outer_distance_list = []
        self.white_top_list      = []
        self.mid_top_list        = []
        self.mid_bot_list        = []
        self.white_bot_list      = []
        self.inner_distance_list = []

        # New heatmap
        #self.outer_distance_gaps = np.full((100, 968), "B")

        self.outer_distance_gaps = []
        for x in range(0, 100):
            l = []
            for y in range(0, 950):
                l.append("B")
            self.outer_distance_gaps.append(l)


        # getting the number of points measured for each frame
        self.outer_distance_measurement_number = []
        self.white_top_measurement_number      = []
        self.mid_top_measurement_number        = []
        self.mid_bot_measurement_number        = []
        self.white_bot_measurement_number      = []
        self.inner_distance_measurement_number = []
        
        #thinkness
        self.retinal_thickness      = []
        self.retinal_thickness_gaps = []
        
        #start and stop / frame information
        self.number_of_images = self.stop - self.start
        self.frame_list = []

        #BOUNDS SETTINGS
        self.end_bound_list = []                         # list that contains the end bouds (4) // if length = 0 no bounds set
        self.white_value_threshold_list = [102, 99]      # first value -> main | second value -> secondary[end boundaries]

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

    def getRetinalThicknessGaps(self):
        return self.outer_distance_gaps

    #RETURING IMAGE DATA
    def getName(self):
        return self.animal_number

    def getFrameList(self):
        return self.frame_list

    def getHeat(self):
        return self.heatmap_setting

    def getdirname(self):
        return self.dirname

    def Scheduler(self):
        for x in range(self.start, self.stop):
            currentImage = self.img_List[x]
            self.animal_number = currentImage[-42:-5]
            img = Image.prepareImage(self, currentImage)

            if Image.TestImage(self, img) == True:
                self.frame_list.append(currentImage[-8:-5])
                # setting the end bound
                if len(self.end_bound_list) > 0:
                    if (x >= self.end_bound_list[0] and x <= self.end_bound_list[1]) or (x >= self.end_bound_list[2] and x <= self.end_bound_list[3]):
                        self.white_value_threshold = self.white_value_threshold_list[1]  # won't return to orginal value
                    else:
                        self.white_value_threshold = self.white_value_threshold_list[0]
                Image.medianDerterminant(self, img, self.smoothingline_setting, x)
            else:
                print("This Image has an error if type: ")

        #print(len(self.retinal_thickness))
        #print(len(self.retinal_thickness[0]))
        #print(self.retinal_thickness)
        
        """Data Storage"""
        if self.storage_type == "Classic":  Image.StoreDataClassic(self)
        if self.storage_type == "Modern":   Image.StoreDataModern(self)
        if self.storage_type == "CSV":      Image.StoreCommaSeperatedValues(self)
        cv2.destroyAllWindows()

    def TestImage(self, mat_img):
        histr = cv2.calcHist([mat_img],[0],None,[256],[0,256])
        hist_sum_Pixel = sum(histr[50:100])
        hist_sum_Blank = sum(histr[100:125])
        error = True

        #if hist_sum_Pixel < 800000:
            #error = False
            #print("Pixelation Error")

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

    #band detection to save on computing time
    def medianDerterminant(self, image, sl, currentImage):
        outer_distance     = []
        white_top_distance = []
        mid_top_distance   = []
        mid_bot_distance   = []
        white_bot          = []
        white_top          = []
        inner_distance     = []

        height, width, depth = image.shape
        smooth = image.copy()

        #setting the points for the heatmap image
        image_bot       = []
        image_white_top = []
        image_mid       = []
        image_white_bot = []
        image_top       = []
                

        for pointx in range(self.start_width, self.end_width): #1000
            midpath  = []
            midwhite = []
            top      = []
            bot      = []

            for y in range(self.start_height,self.end_height): #RESTRICTING THE BOTTOM RANGE 1024 total  #
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

                    #getting down to pixel higlighting to get perpixel measurements
                    # if (top[-1] - top[0] >= self.min_gap_value and bot[-1] - bot[0] >= self.min_gap_value and top[0] != 0 and self.last_top_value - (bot[-1] - top[0]) >= -10)
                    # preventing two coloured points being on the sale point min gap standard - 5  low gap = 3
                    if (top[-1] - top[0] >= self.min_gap_value and bot[-1] - bot[0] >= self.min_gap_value and top[0] != 0 and self.last_top_value - (bot[-1] - top[0]) >= -10):
                        #image[medianPoint + 205][pointx] = (0,0,255,-1) # red points
                        #image[medianPoint + 206][pointx] = (0,0,255,-1) # red points
                        if self.start_height > 0:
                            image[top[-1] + self.start_height][pointx] = (0,255,0,-1)     #top green
                            image[bot[0]  + self.start_height][pointx] = (0,255,0,-1)     #bot green
                            image[top[0]  + self.start_height][pointx] = (255,0,0,-1)     #top blue 
                            image[bot[-1] + self.start_height][pointx] = (255,0,0,-1)     #bot blue

                            if self.smoothingline_setting == "On":
                                smooth[medianPoint + self.start_height][pointx] = (0,0,255,-1) # red points
                                smooth[medianPoint + self.start_height][pointx] = (0,0,255,-1) # red points
                        else:
                            image[top[-1]][pointx] = (0,255,0,-1)    #top green
                            image[bot[0]][pointx]  = (0,255,0,-1)    #bot green
                            image[top[0]][pointx]  = (255,0,0,-1)    #top blue 
                            image[bot[-1]][pointx] = (255,0,0,-1)    #bot blue

                            if self.smoothingline_setting == "On":
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

            if self.testing == True:
                cv2.imshow("ImageK By: Kent Barter", image)
                cv2.waitKey(1)

        #saving the image to the image  (priting whne the image has been complete)
        image_scale = cv2.cvtColor(image,cv2.COLOR_RGB2BGR) # moving from cv2's BRG mode
        image_crop = image_scale[0:750, 0:1000]
        
        #path = "C:\\Users\\krbar\\Desktop\\Project\\Images"
        
        path = self.dirname + os.sep + "Images"
        if not os.path.exists(path):
            os.mkdir(path)
        
        #name = time_current = strftime("%Y-%m-%d %H-%M-%S", gmtime()) + ".tiff"
        name_start = self.animal_number.split(os.sep)[-1]
        name = name_start + " " + strftime("%Y-%m-%d %H-%M-%S", gmtime()) + ".tiff"
        mpimg.imsave(os.path.join(path , name), image_crop)

        if self.smoothingline_setting == "On":
            image_s = cv2.cvtColor(smooth,cv2.COLOR_RGB2BGR)
            path = self.dirname + os.sep + "SmoothingLine"
            if not os.path.exists(path):
                os.mkdir(path)
            name = name_start + " " + strftime("%Y-%m-%d %H-%M-%S", gmtime()) + ".tiff"
            mpimg.imsave(os.path.join(path , name), image_s)
                    
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
        outer_distance_volume    = sum(outer_distance)
        white_top_volume         = sum(white_top)
        mid_top_volume           = sum(mid_top_distance)
        mid_bot_volume           = sum(mid_bot_distance)
        white_bot_volume         = sum(white_bot)
        inner_distance_volume    = sum(inner_distance)

        # getting the number of meaurements of each average
        self.outer_distance_measurement_number.append(len(outer_distance))
        self.white_top_measurement_number.append(len(white_top))
        self.mid_top_measurement_number.append(len(mid_top_distance))
        self.mid_bot_measurement_number.append(len(mid_bot_distance))
        self.white_bot_measurement_number.append(len(white_bot))
        self.inner_distance_measurement_number.append(len(inner_distance))

        #collecting the avarage of each image
        self.outer_distance_list.append(outer_distance_avg)
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

        #print("Volume and Percentage")
        #print("Total Volume: ",      outer_distance_volume), print()
        #print("NFL to GLC Volume: ",      white_top_volume), print("NFL/GLC Volume Percentage: ",      self.white_top_per), print()
        #print("ONL to RPE Volume: ",     white_bot_volume), print("ONL to RPE Volume Percentage: ",     self.white_bot_per), print()
        #print("GLC to ONL Volume: ", inner_distance_volume), print("GLC to ONL Volume Percentage: ", self.inner_distance_per), print()
        print("Animal Number: ", self.animal_number)
        
        # at the end of the computation send the value of self.outer_distance_list to the heatmap
        
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
        sheet.write(0, 10, "IPL/INL (um)" , style)
        sheet.write(0, 11, "Number of Readings", style)
        sheet.write(0, 14, "OPL/ONL/IS/OS/RPE (um)" , style)
        sheet.write(0, 15, "Number of Readings", style)

        #volumes percentages
        sheet.write(0,  20, "Specimen", style)
        sheet.write(3,  20, "NFL/GLC Volume Percentage", style)
        sheet.write(6,  20, "IPL/INL Volume Percentage", style) 
        sheet.write(9,  20, "OPL/ONL/IS/OS/RPE Volume Percentage", style) 
        sheet.write(12, 20, "White Value Threshold", style)
        sheet.write(15, 20, "Minimum Gap Threshold", style)
        sheet.write(18, 20, "Maximum Gap Threshold", style)
        sheet.write(21, 20, "Mimimum Thickness Value", style)

        # width and height
        sheet.write(24, 20, "Starting Height", style)
        sheet.write(27, 20, "Ending Height", style)
        sheet.write(30, 20, "Starting Width", style)
        sheet.write(33, 20, "Ending Width", style)
        
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
        
        sheet.write(25, 20, self.start_height)
        sheet.write(28, 20, self.end_height)
        sheet.write(31, 20, self.start_width)
        sheet.write(34, 20, self.end_width)
        
        time_current = strftime("%Y-%m-%d %H-%M-%S", gmtime())
        name_start = self.animal_number.split(os.sep)[-1]
        wb.save(self.dirname + os.sep + name_start + " " + time_current + ".xls")
        
    def StoreDataModern(self): #xlsx format
        time_current = strftime("%Y-%m-%d %H-%M-%S", gmtime())
        name_start = self.animal_number.split(os.sep)[-1]
        workbook = xlsxwriter.Workbook(self.dirname + os.sep + (name_start + " " + time_current + ".xlsx"))
        sheet = workbook.add_worksheet()
        style = workbook.add_format({'bold': True})

        sheet.write(0, 0, "Frame Number", style)
        sheet.write(0, 2, "Retinal Thickness (um)" , style)
        sheet.write(0, 3, "Number of Readings", style)
        sheet.write(0, 6, "NFL/GLC (um)" , style)
        sheet.write(0, 7, "Number of Readings", style)
        sheet.write(0, 10, "IPL/INL (um)" , style)
        sheet.write(0, 11, "Number of Readings", style)
        sheet.write(0, 14, "OPL/ONL/IS/OS/RPE (um)" , style)
        sheet.write(0, 15, "Number of Readings", style)

        #volumes percentages
        sheet.write(0,  20, "Specimen", style)
        sheet.write(3,  20, "NFL/GLC Volume Percentage", style)
        sheet.write(6,  20, "IPL/INL Volume Percentage", style) 
        sheet.write(9,  20, "OPL/ONL/IS/OS/RPE Volume Percentage", style) 
        sheet.write(12, 20, "White Value Threshold", style)
        sheet.write(15, 20, "Minimum Gap Threshold", style)
        sheet.write(18, 20, "Maximum Gap Threshold", style)
        sheet.write(21, 20, "Mimimum Thickness Value", style)

        # width and height
        sheet.write(24, 20, "Starting Height", style)
        sheet.write(27, 20, "Ending Height", style)
        sheet.write(30, 20, "Starting Width", style)
        sheet.write(33, 20, "Ending Width", style)
        
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
        sheet.write(25, 20, self.start_height)
        sheet.write(28, 20, self.end_height)
        sheet.write(31, 20, self.start_width)
        sheet.write(34, 20, self.end_width)
        workbook.close()

    def StoreCommaSeperatedValues(self): #csv format
        time_current = strftime("%Y-%m-%d %H-%M-%S", gmtime())
        name_start = self.dirname + os.sep + self.animal_number.split(os.sep)[-1]
        listEnd = len(self.outer_distance_list)
        with open(name_start + " " + time_current + ".csv", "w") as file:
            file.write("Frame Number, ,Retinal Thickness,Number of Readings, , NFL/GLC (um),Number of Readings, , IPL/INL (um), Number of Readings, , OPL/ONL/IS/OS/RPE (um), Number of Readings,\n")
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
            file.write("Specimen, ,NFL/GLC Volume Percentage, ,IPL/INL Volume Percentage, ,OPL/ONL/IS/OS/RPE Volume Percentage\n")
            line = self.animal_number + ", ," + str(round(self.white_top_per, 1)) + ", ," + str(round(self.inner_distance_per, 1)) + ", ," + str(round(self.white_bot_per, 1)) + "\n"
            file.write(line)
            file.write("\n")
            file.write("White Value Threshold, , Minimum Gap Threshold, , Maximum Gap Threshold, , Mimimum Thickness Value, , Starting Height, , Ending Height, , Starting Width, , Ending Width\n")
            line2 = str(self.white_value_threshold) + ", ," + str(self.minimum_gap_value) + ", ," + str(self.maximum_gap_value) + ", ," + str(self.min_gap_value) + ", ," + str(self.start_height) + ", ," + str(self.end_height) + ", ," + str(self.start_width) + ", ," + str(self.end_width) + "\n"
            file.write(line2)
        file.close()
