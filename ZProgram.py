import wx
import os
import cv2
import wx.grid as grid
from HeatMap import HeatMap
from ZUIPointsBased import Image

class MyFrame(wx.Frame):
    def __init__(self, parent, title):
        super(MyFrame, self).__init__(parent, title= title, size = (700,735))
        self.panel = MyPanel(self)
        self.SetBackgroundColour("#2B4562")
        self.SetForegroundColour("#2B4562")
        ico = wx.Icon("icon.png", wx.BITMAP_TYPE_PNG)
        self.SetIcon(ico)


class MyPanel(wx.Panel):
    def __init__(self, parent):
        super(MyPanel, self).__init__(parent)
        # Path dialog
        self.path_btn = wx.Button(self, label = "Path", pos = (10, 10), size = (125, 30))
        self.path_btn.Bind(wx.EVT_BUTTON, self.getImageList)

        # Starting image number        - spin controller
        starting_image_number_label = wx.StaticText(self, label = "Starting Image Number", pos = (10, 45))
        starting_image_number_label.SetForegroundColour((255,255,255)) # set text color
        self.starting_image_number_spin = wx.SpinCtrl(self, id=-1,pos = (10,60))
        self.starting_image_number_spin.SetValue(4)
        self.starting_image_number_spin.Bind(wx.EVT_SPINCTRL, self.getStartingImage)
        
        # Ending image number          - spin controller
        ending_image_number_label = wx.StaticText(self, label = "Ending Image Number", pos = (10, 95))
        ending_image_number_label.SetForegroundColour((255,255,255)) # set text color
        self.ending_image_number_spin = wx.SpinCtrl(self, id=-1,pos = (10,110))
        self.ending_image_number_spin.SetValue(96)
        self.ending_image_number_spin.Bind(wx.EVT_SPINCTRL, self.getEndingImage)

        # White value threshold        - spin controller
        white_value_threshold_label = wx.StaticText(self, label = "White Value Threshold", pos = (10, 145))
        white_value_threshold_label.SetForegroundColour((255,255,255)) # set text color
        self.white_value_threshold_spin  = wx.SpinCtrl(self, id=-1,pos = (10,160))
        self.white_value_threshold_spin.SetRange(0, 300)
        self.white_value_threshold_spin.SetValue(100)
        self.white_value_threshold_spin.Bind(wx.EVT_SPINCTRL, self.getWhiteThreshold)

        # Minimum gap value (negative) - spin controller
        minimum_gap_value_label     = wx.StaticText(self, label = "Minumum Gap Value", pos = (10, 195))
        minimum_gap_value_label.SetForegroundColour((255,255,255)) # set text color
        self.minimum_gap_value_spin =  wx.SpinCtrl(self, id=-1,pos = (10,210))
        self.minimum_gap_value_spin.SetValue(35)
        self.minimum_gap_value_spin.Bind(wx.EVT_SPINCTRL, self.getMinimumGapValue)

        # Maximum gap value (negative) - spin controller
        maximum_gap_value_label      = wx.StaticText(self, label = "Maximum Gap Value", pos = (10, 245))
        maximum_gap_value_label.SetForegroundColour((255,255,255)) # set text color
        self.maximum_gap_value_spin  = wx.SpinCtrl(self, id=-1,pos = (10,260))
        self.maximum_gap_value_spin.SetRange(0, 350)
        self.maximum_gap_value_spin.SetValue(135)
        self.maximum_gap_value_spin.Bind(wx.EVT_SPINCTRL, self.getMaximumGapValue)

        # Minimum pixel gap value      - spin controller
        min_gap_value_label         = wx.StaticText(self, label = "Minimum Pixel Gap", pos = (10, 295))
        min_gap_value_label.SetForegroundColour((255,255,255)) # set text color
        self.min_gap_value_spin     = wx.SpinCtrl(self, id=-1,pos = (10,310))
        self.min_gap_value_spin.SetValue(2)
        self.min_gap_value_spin.Bind(wx.EVT_SPINCTRL, self.getMinValue)

        # Storage type (1 = xls, 2 = xlsx, 3 = csv) - radiobox
        storage_type_options = ["Classic", "Modern", "CSV"]
        self.storage_type_rbox  = wx.RadioBox(self, label = "Storage Type", pos = (10, 345), choices = storage_type_options, style= wx.RA_SPECIFY_ROWS)
        self.storage_type_rbox.SetForegroundColour((255,255,255)) # set text color
        self.storage_type_rbox.Bind(wx.EVT_RADIOBOX, self.getStorageType)

        # Heatmap setting (A for automatic else provide a number to compare sets of heatmaps) - radiobox
        heatmap_setting_label = wx.StaticText(self, label = "Heatmap Setting", pos = (10, 448))
        heatmap_setting_label.SetForegroundColour((255,255,255)) # set text color
        self.heatmap_setting_textcontrol = wx.TextCtrl(self, pos = (10, 463), size = (125, 30))
        self.heatmap_setting_textcontrol.SetValue("A")
        self.heatmap_setting_textcontrol.Bind(wx.EVT_TEXT, self.getHeatmapSetting)

        # Heatmap Slector
        heatmap_selector_label = wx.StaticText(self, label = "Heatmap Slector", pos = (10, 498))
        heatmap_selector_label.SetForegroundColour((255,255,255)) # set text color
        heatmap_options = ["Original", "Viridis", "Plasma", "Inferno", "Magma"]
        self.heatmap_selector_label_combobox = wx.ComboBox(self, pos=(10, 515),  size = (125, 30), choices=heatmap_options, style=wx.CB_READONLY)
        self.heatmap_selector_label_combobox.SetValue("Original")
        self.heatmap_selector_label_combobox.Bind(wx.EVT_COMBOBOX, self.getHeatmapOptions)
        
        # Smoothing line (S = smoothing line, N = turn off smoothing line) - radiobox
        smoothingline_setting = ["On", "Off"]
        self.smoothingline_setting_rbox = wx.RadioBox(self, label = "Smoothing Line", pos = (10, 543), choices = smoothingline_setting, style= wx.RA_SPECIFY_ROWS)
        self.smoothingline_setting_rbox.SetForegroundColour((255,255,255)) # set text color
        self.smoothingline_setting_rbox.Bind(wx.EVT_RADIOBOX, self.getSmoothingLineSetting)

        # Test Button
        self.test = wx.Button(self, label = "Test", pos = (10, 622), size = (125, 30))
        self.test.Bind(wx.EVT_BUTTON, self.getTest)

        # Start Button
        self.start = wx.Button(self, label = "Start", pos = (10, 657), size = (125, 30))
        self.start.Bind(wx.EVT_BUTTON, self.getStart)

        # -- Adjustment of the width and height of the image using the user inteface
        #start_height
        start_height_label = wx.StaticText(self, label = "Starting Height", pos = (160, 5))
        start_height_label.SetForegroundColour((255,255,255)) # set text color
        self.start_height_textcontrol = wx.TextCtrl(self, pos = (160, 20), size = (100, 20))
        self.start_height_textcontrol.SetValue("0")
        self.start_height_textcontrol.Bind(wx.EVT_TEXT, self.getStartHeight)

        #end_height
        end_height_label = wx.StaticText(self, label = "Ending Height", pos = (290, 5))
        end_height_label.SetForegroundColour((255,255,255)) # set text color
        self.end_height_textcontrol = wx.TextCtrl(self, pos = (290, 20), size = (100, 20))
        self.end_height_textcontrol.SetValue("500")
        self.end_height_textcontrol.Bind(wx.EVT_TEXT, self.getEndHeight)

        #start_width
        start_width_label = wx.StaticText(self, label = "Starting Width", pos = (420, 5))
        start_width_label.SetForegroundColour((255,255,255)) # set text color
        self.start_width_textcontrol = wx.TextCtrl(self, pos = (420, 20), size = (100, 20))
        self.start_width_textcontrol.SetValue("0")
        self.start_width_textcontrol.Bind(wx.EVT_TEXT, self.getStartWidth)

        #end_width
        end_width_label = wx.StaticText(self, label = "Ending Width", pos = (550, 5))
        end_width_label.SetForegroundColour((255,255,255)) # set text color
        self.end_width_textcontrol = wx.TextCtrl(self, pos = (550, 20), size = (100, 20))
        self.end_width_textcontrol.SetValue("1000")
        self.end_width_textcontrol.Bind(wx.EVT_TEXT, self.getEndWidth)

    def getImageList(self, event):
        dlg = wx.DirDialog(self, message="Choose a folder")
        self.imgs = []
        if dlg.ShowModal() == wx.ID_OK:
            self.dirname = dlg.GetPath()

            if os.path.isdir(self.dirname):
                for y in os.listdir(self.dirname):
                    if y.endswith(".TIFF"):
                        self.imgs.append(self.dirname + os.sep + y)

            if len(self.imgs) >= 2:
                toshow = round(len(self.imgs) / 2)
            else:
                toshow = 0
            
            png = wx.Image(self.imgs[toshow], wx.BITMAP_TYPE_ANY)
            self.W, self.H = png.GetSize()
            png = png.Scale(500, 500).ConvertToBitmap()
            self.bitmap = wx.StaticBitmap(self, -1, png, (160, 50), (png.GetWidth(), png.GetHeight()))
        dlg.Destroy()

    def getStartingImage(self, event):
        self.starting_image_number = self.starting_image_number_spin.GetValue()
        png = wx.Image(self.imgs[self.starting_image_number], wx.BITMAP_TYPE_ANY)
        png = png.Scale(500, 500).ConvertToBitmap()
        self.bitmap.SetBitmap(wx.Bitmap(png))

    def getEndingImage(self, event):
        self.ending_image_number   = self.ending_image_number_spin.GetValue()

    def getWhiteThreshold(self, event):
        self.white_value_threshold = self.white_value_threshold_spin.GetValue()

    def getMinimumGapValue(self, event):
        self.minimum_gap_value = -self.minimum_gap_value_spin.GetValue()

    def getMaximumGapValue(self, event):
        self.maximum_gap_value = -self.maximum_gap_value_spin.GetValue()

    def getMinValue(self, event):
        self.min_gap_value = self.min_gap_value_spin.GetValue()

    def getStorageType(self, event):
        self.storage_type = self.storage_type_rbox.GetStringSelection()

    def getHeatmapSetting(self, event):
        self.heatmap_setting = str(self.heatmap_setting_textcontrol.GetValue())
    
    def getHeatmapOptions(self, event):
        self.heatmap_options = event.GetString()
        self.heatmap_selector_label_combobox.SetLabel(self.heatmap_options)

    def getSmoothingLineSetting(self, event):
        self.smoothingline_setting = self.smoothingline_setting_rbox.GetStringSelection()

    # Height
    def getStartHeight(self, enent):
        self.start_height = self.start_height_textcontrol.GetValue()

    def getEndHeight(self, enent):
        self.end_height = self.end_height_textcontrol.GetValue()

    # Width
    def getStartWidth(self, event):
        self.start_width = self.start_width_textcontrol.GetValue()

    def getEndWidth(self, event):
        self.end_width = self.end_width_textcontrol.GetValue()

    def getTest(self, event):
        self.starting_image_number = self.starting_image_number_spin.GetValue()
        self.white_value_threshold = self.white_value_threshold_spin.GetValue()
        self.minimum_gap_value = -self.minimum_gap_value_spin.GetValue()
        self.maximum_gap_value = -self.maximum_gap_value_spin.GetValue()
        self.min_gap_value = self.min_gap_value_spin.GetValue()
        self.storage_type = self.storage_type_rbox.GetStringSelection()
        self.heatmap_setting = str(self.heatmap_setting_textcontrol.GetValue())
        self.smoothingline_setting = self.smoothingline_setting_rbox.GetStringSelection()
        testing = True

        # height and width
        self.start_height = self.start_height_textcontrol.GetValue()
        self.end_height   = self.end_height_textcontrol.GetValue()
        if int(self.end_height) > self.H:
            self.end_height = self.H
            self.end_height_textcontrol.SetValue(str(self.H))
        
        self.start_width  = self.start_width_textcontrol.GetValue()
        self.end_width    = self.end_width_textcontrol.GetValue()
        if int(self.end_width) > self.W:
            self.end_width = self.W
            self.end_width_textcontrol.SetValue(str(self.W))

        #Image
        image = Image(self.imgs, self.starting_image_number, self.starting_image_number + 1, self.white_value_threshold,  self.minimum_gap_value, self.maximum_gap_value, self.min_gap_value, self.storage_type, self.heatmap_setting, self.smoothingline_setting, testing, self.start_height, self.end_height, self.start_width, self.end_width, self.dirname)
        image.Scheduler()


    def getStart(self, event):
        self.starting_image_number = self.starting_image_number_spin.GetValue()

        self.ending_image_number   = self.ending_image_number_spin.GetValue()
        if self.ending_image_number > len(self.imgs):
            self.ending_image_number = len(self.imgs)
            self.ending_image_number_spin.SetValue(len(self.imgs))
        
        self.white_value_threshold = self.white_value_threshold_spin.GetValue()
        self.minimum_gap_value = -self.minimum_gap_value_spin.GetValue()
        self.maximum_gap_value = -self.maximum_gap_value_spin.GetValue()
        self.min_gap_value = self.min_gap_value_spin.GetValue()
        self.storage_type = self.storage_type_rbox.GetStringSelection()
        self.heatmap_setting = str(self.heatmap_setting_textcontrol.GetValue())
        self.smoothingline_setting = self.smoothingline_setting_rbox.GetStringSelection()
        testing = False
        
        # height and width
        self.start_height = self.start_height_textcontrol.GetValue()
        self.end_height   = self.end_height_textcontrol.GetValue()
        if int(self.end_height) > self.H:
            self.end_height = self.H
            self.end_height_textcontrol.SetValue(str(self.H))
        
        self.start_width  = self.start_width_textcontrol.GetValue()
        self.end_width    = self.end_width_textcontrol.GetValue()
        if int(self.end_width) > self.W:
            self.end_width = self.W
            self.end_width_textcontrol.SetValue(str(self.W))
        
        #Image
        image = Image(self.imgs, self.starting_image_number, self.ending_image_number, self.white_value_threshold,  self.minimum_gap_value, self.maximum_gap_value, self.min_gap_value, self.storage_type, self.heatmap_setting, self.smoothingline_setting, testing, self.start_height, self.end_height, self.start_width, self.end_width, self.dirname)
        image.Scheduler()

        #Heatmap
        retinal_thickness      = image.getRetinalThickness()
        retinal_thickness_gaps = image.getRetinalThicknessGaps()
        name  = image.getName()
        frame = image.getFrameList()
        heat  = image.getHeat()
        dirname = image.getdirname()
        image_list = image.getimagedict()
        max = image.getdisplaymax()
        min = image.getdisplaymin()

        # self.heatmap_options
        retinalMap = HeatMap(retinal_thickness, name, frame, heat, retinal_thickness_gaps, dirname, image_list, max, min, self.heatmap_options)
        retinalMap.sceduler()

class MyApp(wx.App):
    def OnInit(self):
        self.frame = MyFrame(parent = None, title = "Automated SD-OCT  By: Kent Barter")
        self.frame.Show()  # Show has to be capital letter
        return True        # C++ conventionl

app = MyApp()
app.MainLoop()
