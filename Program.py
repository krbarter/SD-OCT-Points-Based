import wx
import os
import cv2
import wx.grid as grid
from HeatMap import HeatMap
from UIPointsBased import Image

class MyFrame(wx.Frame):
    def __init__(self, parent, title):
        super(MyFrame, self).__init__(parent, title= title, size = (700,680))
        self.panel = MyPanel(self)


class MyPanel(wx.Panel):
    def __init__(self, parent):
        super(MyPanel, self).__init__(parent)
        # Path dialog
        self.path_btn = wx.Button(self, label = "Path", pos = (10, 10), size = (125, 30))
        self.path_btn.Bind(wx.EVT_BUTTON, self.getImageList)

        # Starting image number        - spin controller
        starting_image_number_label = wx.StaticText(self, label = "Starting Image Number", pos = (10, 45))
        self.starting_image_number_spin = wx.SpinCtrl(self, id=-1,pos = (10,60))
        self.starting_image_number_spin.SetValue(4)
        self.starting_image_number_spin.Bind(wx.EVT_SPINCTRL, self.getStartingImage)
        
        # Ending image number          - spin controller
        ending_image_number_label = wx.StaticText(self, label = "Ending Image Number", pos = (10, 95))
        self.ending_image_number_spin = wx.SpinCtrl(self, id=-1,pos = (10,110))
        self.ending_image_number_spin.SetValue(96)
        self.ending_image_number_spin.Bind(wx.EVT_SPINCTRL, self.getEndingImage)

        # White value threshold        - spin controller
        white_value_threshold_label = wx.StaticText(self, label = "White Value Threshold", pos = (10, 145))
        self.white_value_threshold_spin  = wx.SpinCtrl(self, id=-1,pos = (10,160))
        self.white_value_threshold_spin.SetRange(0, 300)
        self.white_value_threshold_spin.SetValue(100)
        self.white_value_threshold_spin.Bind(wx.EVT_SPINCTRL, self.getWhiteThreshold)

        # Minimum gap value (negative) - spin controller
        minimum_gap_value_label     = wx.StaticText(self, label = "Minumum Gap Value", pos = (10, 195))
        self.minimum_gap_value_spin =  wx.SpinCtrl(self, id=-1,pos = (10,210))
        self.minimum_gap_value_spin.SetValue(35)
        self.minimum_gap_value_spin.Bind(wx.EVT_SPINCTRL, self.getMinimumGapValue)

        # Maximum gap value (negative) - spin controller
        maximum_gap_value_label      = wx.StaticText(self, label = "Maximum Gap Value", pos = (10, 245))
        self.maximum_gap_value_spin  = wx.SpinCtrl(self, id=-1,pos = (10,260))
        self.maximum_gap_value_spin.SetRange(0, 350)
        self.maximum_gap_value_spin.SetValue(135)
        self.maximum_gap_value_spin.Bind(wx.EVT_SPINCTRL, self.getMaximumGapValue)

        # Minimum pixel gap value      - spin controller
        min_gap_value_label         = wx.StaticText(self, label = "Maximum Gap Value", pos = (10, 295))
        self.min_gap_value_spin     = wx.SpinCtrl(self, id=-1,pos = (10,310))
        self.min_gap_value_spin.SetValue(2)
        self.min_gap_value_spin.Bind(wx.EVT_SPINCTRL, self.getMinValue)

        # Storage type (1 = xls, 2 = xlsx, 3 = csv) - radiobox
        storage_type_options = ["Classic", "Modern", "CSV"]
        self.storage_type_rbox  = wx.RadioBox(self, label = "Storage Type", pos = (10, 345), choices = storage_type_options, style= wx.RA_SPECIFY_ROWS)
        self.storage_type_rbox.Bind(wx.EVT_RADIOBOX, self.getStorageType)

        # Heatmap setting (A for automatic else provide a number to compare sets of heatmaps) - radiobox
        heatmap_setting_label = wx.StaticText(self, label = "Heatmap Setting", pos = (10, 445))
        self.heatmap_setting_textcontrol = wx.TextCtrl(self, pos = (10, 460), size = (125, 30))
        self.heatmap_setting_textcontrol.SetValue("A")
        self.heatmap_setting_textcontrol.Bind(wx.EVT_TEXT, self.getHeatmapSetting)
        
        # Smoothing line (S = smoothing line, N = turn off smoothing line) - radiobox
        smoothingline_setting = ["On", "Off"]
        self.smoothingline_setting_rbox = wx.RadioBox(self, label = "Smoothing Line", pos = (10, 495), choices = smoothingline_setting, style= wx.RA_SPECIFY_ROWS)
        self.smoothingline_setting_rbox.Bind(wx.EVT_RADIOBOX, self.getSmoothingLineSetting)

        # Test Button
        self.test = wx.Button(self, label = "Test", pos = (10, 572), size = (125, 30))
        self.test.Bind(wx.EVT_BUTTON, self.getTest)

        # Start Button
        self.start = wx.Button(self, label = "Start", pos = (10, 607), size = (125, 30))
        self.start.Bind(wx.EVT_BUTTON, self.getStart)

    def getImageList(self, event):
        dlg = wx.DirDialog(self, message="Choose a folder")
        self.imgs = []
        if dlg.ShowModal() == wx.ID_OK:
            dirname = dlg.GetPath()

            if os.path.isdir(dirname):
                for y in os.listdir(dirname):
                    if y.endswith(".TIFF"):
                        self.imgs.append(dirname + os.sep + y)

            if len(self.imgs) >= 2:
                toshow = round(len(self.imgs) / 2)
            else:
                toshow = 0
            
            png = wx.Image(self.imgs[toshow], wx.BITMAP_TYPE_ANY)
            png = png.Scale(500, 500).ConvertToBitmap()
            wx.StaticBitmap(self, -1, png, (160, 50), (png.GetWidth(), png.GetHeight()))
        dlg.Destroy()

    def getStartingImage(self, event):
        self.starting_image_number = self.starting_image_number_spin.GetValue()

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

    def getSmoothingLineSetting(self, event):
        self.smoothingline_setting = self.smoothingline_setting_rbox.GetStringSelection()

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

        #Image
        image = Image(self.imgs, self.starting_image_number, self.starting_image_number + 1, self.white_value_threshold,  self.minimum_gap_value, self.maximum_gap_value, self.min_gap_value, self.storage_type, self.heatmap_setting, self.smoothingline_setting, testing)
        image.Scheduler()


    def getStart(self, event):
        self.starting_image_number = self.starting_image_number_spin.GetValue()
        self.ending_image_number   = self.ending_image_number_spin.GetValue()
        self.white_value_threshold = self.white_value_threshold_spin.GetValue()
        self.minimum_gap_value = -self.minimum_gap_value_spin.GetValue()
        self.maximum_gap_value = -self.maximum_gap_value_spin.GetValue()
        self.min_gap_value = self.min_gap_value_spin.GetValue()
        self.storage_type = self.storage_type_rbox.GetStringSelection()
        self.heatmap_setting = str(self.heatmap_setting_textcontrol.GetValue())
        self.smoothingline_setting = self.smoothingline_setting_rbox.GetStringSelection()
        testing = False
        
        #Image
        image = Image(self.imgs, self.starting_image_number, self.ending_image_number, self.white_value_threshold,  self.minimum_gap_value, self.maximum_gap_value, self.min_gap_value, self.storage_type, self.heatmap_setting, self.smoothingline_setting, testing)
        image.Scheduler()

        #Heatmap
        retinal_thickness      = image.getRetinalThickness()
        retinal_thickness_gaps = image.getRetinalThicknessGaps()
        name = image.getName()
        frame = image.getFrameList()
        heat = image.getHeat()
        retinalMap = HeatMap(retinal_thickness, name, frame, heat, retinal_thickness_gaps)
        retinalMap.sceduler()

class MyApp(wx.App):
    def OnInit(self):
        self.frame = MyFrame(parent = None, title = "Automated SD-OCT  By: Kent Barter")
        self.frame.Show()  # Show has to be capital letter
        return True        # C++ conventionl

app = MyApp()
app.MainLoop()
