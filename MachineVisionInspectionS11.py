import json
import logging
import os
import socket
import subprocess
import time
import tkinter
import tkinter as tk
import urllib.request
from threading import Timer
from tkinter import *
from tkinter import messagebox

import customtkinter
import numpy as np
import cv2 as cv
from PIL import Image
from PIL import ImageTk
from tensorflow import keras
from tensorflow.keras.models import Sequential, load_model
import tensorflow as tf

"""if not os.path.isfile('CameraAttributeSettings.json'):
    subprocess.call([r'VisionCameraSettings.exe'])"""

def read_CameraAttributeSettings():
    BRIGHTNESS = []
    EXPOSURE = []
    CONTRAST = []
    SATURATION = []
    FOCUS = []
    SHARPNESS = []
    HUE = []
    GAIN = []
    ZOOM = []
    with open('CameraAttributeSettings.json', 'r') as json_file:
        CameraAttributeSettings = json.loads(json_file.read())
    for i in range(len(CameraAttributeSettings[0]["Cameraconfig"])):
        BRIGHTNESS.append(CameraAttributeSettings[0]["Cameraconfig"][i][0]["BRIGHTNESS"])
        EXPOSURE.append(CameraAttributeSettings[0]["Cameraconfig"][i][0]["EXPOSURE"])
        CONTRAST.append(CameraAttributeSettings[0]["Cameraconfig"][i][0]["CONTRAST"])
        SATURATION.append(CameraAttributeSettings[0]["Cameraconfig"][i][0]["SATURATION"])
        FOCUS.append(CameraAttributeSettings[0]["Cameraconfig"][i][0]["FOCUS"])
        SHARPNESS.append(CameraAttributeSettings[0]["Cameraconfig"][i][0]["SHARPNESS"])
        HUE.append(CameraAttributeSettings[0]["Cameraconfig"][i][0]["HUE"])
        GAIN.append(CameraAttributeSettings[0]["Cameraconfig"][i][0]["GAIN"])
        ZOOM.append(CameraAttributeSettings[0]["Cameraconfig"][i][0]["ZOOM"])
    return BRIGHTNESS, EXPOSURE, CONTRAST, SATURATION, FOCUS, SHARPNESS, HUE, GAIN, ZOOM

BRIGHTNESS, EXPOSURE, CONTRAST, SATURATION, FOCUS, SHARPNESS, HUE, GAIN, ZOOM = read_CameraAttributeSettings()

frame0 = cv.VideoCapture(1, cv.CAP_DSHOW)
frame0.set(cv.CAP_PROP_FRAME_WIDTH, 1366)
frame0.set(cv.CAP_PROP_FRAME_HEIGHT, 768)
frame0.set(cv.CAP_PROP_BRIGHTNESS, BRIGHTNESS[0])
frame0.set(cv.CAP_PROP_EXPOSURE, EXPOSURE[0])
frame0.set(cv.CAP_PROP_CONTRAST, CONTRAST[0])
frame0.set(cv.CAP_PROP_SATURATION, SATURATION[0])
frame0.set(cv.CAP_PROP_SHARPNESS, SHARPNESS[0])
frame0.set(cv.CAP_PROP_HUE, HUE[0])
frame0.set(cv.CAP_PROP_GAIN, GAIN[0])
frame0.set(cv.CAP_PROP_ZOOM, ZOOM[0])

frame1 = cv.VideoCapture(0, cv.CAP_DSHOW)
frame1.set(cv.CAP_PROP_FRAME_WIDTH, 1366)
frame1.set(cv.CAP_PROP_FRAME_HEIGHT, 768)
frame1.set(cv.CAP_PROP_BRIGHTNESS, BRIGHTNESS[1])
frame1.set(cv.CAP_PROP_EXPOSURE, EXPOSURE[1])
frame1.set(cv.CAP_PROP_CONTRAST, CONTRAST[1])
frame1.set(cv.CAP_PROP_SATURATION, SATURATION[1])
frame1.set(cv.CAP_PROP_SHARPNESS, SHARPNESS[1])
frame1.set(cv.CAP_PROP_HUE, HUE[1])
frame1.set(cv.CAP_PROP_GAIN, GAIN[1])
frame1.set(cv.CAP_PROP_ZOOM, ZOOM[1])

ROI = 15
font = "arial"

with open('Setting Paramiter.json', 'r') as json_file:
    Setting_Paramiter = json.loads(json_file.read())
Quantity_Cam = Setting_Paramiter[0]["Quantity_Cam"]
Board_Name = Setting_Paramiter[0]["Board_Name"]
Machine = Setting_Paramiter[0]["MachineName"]
Mode = Setting_Paramiter[0]["Mode"]
Port = Setting_Paramiter[0]["Port"]
IP = Setting_Paramiter[0]["IP"]

class GetEmp:
    @staticmethod
    def Information():
        dirName = 'Information'
        try:
            os.mkdir(dirName)
        except FileExistsError:
            pass
        try:
            with urllib.request.urlopen("http://192.168.1.48:89/RobotAPI/GetEmp") as response:
                json_Emp = json.loads(response.read())
            with open('Information/Operator.json', 'w') as Operator:
                json.dump(json_Emp, Operator, indent=6)
        except:
            pass

class GetAPI:
    @staticmethod
    def API():
        method = ["PartNumber", "BatchNumber", "PartName", "CustomerPartNumber", "PackingStd"]
        side = []
        data = []
        api_url = "https://api.bkf.co.th/APIGateway_DB_BKF/GetCurrentMachineStatus?machineNickName=" + Machine
        data_file = 'Planning Data.json'
        try:
            with urllib.request.urlopen(api_url, timeout=1) as response:
                json_api = json.loads(response.read())
            status = "Connected"
            with open(data_file, 'w') as f:
                json.dump(json_api, f, indent=6)
        except:
            with open(data_file, 'r') as f:
                json_api = json.loads(f.read())
            status = "Disconnected"

        for s in json_api:
            side.append(s)
            for key in method:
                data.append(json_api[s][key])

        return status, side, data


class Delete_Data:
    @staticmethod
    def Delete_Image():
        global flag_camera
        try:
            os.remove("Current.bmp")
        except FileNotFoundError:
            if Quantity_Cam >= 1:
                frame0.release()
                if Quantity_Cam >= 2:
                    frame0.release()
                    frame1.release()
            cv.destroyAllWindows()
            app.destroy()
            subprocess.call([r'TerminatedProcess.bat'])


class GetImage:
    def __init__(self):
        self.BKFImage = customtkinter.CTkImage(Image.open("BKF.png"), size=(140, 55))
        self.ExitImage = customtkinter.CTkImage(Image.open("Exit.PNG"), size=(140, 55))

class InfiniteTimer():
    def __init__(self, seconds, target):
        self._should_continue = False
        self.is_running = False
        self.seconds = seconds
        self.target = target
        self.thread = None

    def _handle_target(self):
        self.is_running = True
        self.target()
        self.is_running = False
        self._start_timer()

    def _start_timer(self):
        if self._should_continue:
            self.thread = Timer(self.seconds, self._handle_target)
            self.thread.start()

    def start(self):
        if not self._should_continue and not self.is_running:
            self._should_continue = True
            self._start_timer()
        else:
            pass

    def cancel(self):
        if self.thread is not None:
            self._should_continue = False
            self.thread.cancel()
        else:
            pass

class ReadFile:
    @staticmethod
    def ReadFile_Image(PartNumber):
        try:
            CouterPoint = 0
            dir_path = r"" + PartNumber + "\Master"
            for path in os.listdir(dir_path):
                if os.path.isfile(os.path.join(dir_path, path)):
                    if path.endswith('.bmp'):
                        CouterPoint += 1
            CouterPoint = int(CouterPoint / 2)
        except FileNotFoundError as ex:
            CouterPoint = 0
        return CouterPoint

    @staticmethod
    def ReadFile_Score(PartNumber, Couter_Point):
        Point_Left = []
        Point_Top = []
        Point_Right = []
        Point_Bottom = []
        Point_Score = []
        Point_Mode = []
        Point_Color = []
        Color = []
        if PartNumber != "":
            try:
                with open(PartNumber + '/' + PartNumber + '.json', 'r') as json_file:
                    Master = json.loads(json_file.read())
                if Couter_Point == len(Master):
                    if Couter_Point != 0:
                        for Point in range(Couter_Point):
                            FileFolder_Ok = 'Record/' + PartNumber + '/OK/Point' + str(Point + 1)
                            path = os.path.join(FileFolder_Ok)
                            try:
                                os.makedirs(path, exist_ok=True)
                            except OSError as error:
                                pass
                            FileFolder_NG = 'Record/' + PartNumber + '/NG/Point' + str(Point + 1)
                            path = os.path.join(FileFolder_NG)
                            try:
                                os.makedirs(path, exist_ok=True)
                            except OSError as error:
                                pass
                            Point_Mode.append(Master[Point]["Point" + str(Point + 1)][0]["Mode"])
                            Point_Left.append(Master[Point]["Point" + str(Point + 1)][0]["Left"])
                            Point_Top.append(Master[Point]["Point" + str(Point + 1)][0]["Top"])
                            Point_Right.append(Master[Point]["Point" + str(Point + 1)][0]["Right"])
                            Point_Bottom.append(Master[Point]["Point" + str(Point + 1)][0]["Bottom"])
                            Point_Score.append(Master[Point]["Point" + str(Point + 1)][0]["Score"])
                            Point_Color.append(Master[Point]["Point" + str(Point + 1)][0]["Color"])
                            Color.append("#A9A9A9")
                        return Point_Left, Point_Top, Point_Right, Point_Bottom, Point_Score, Point_Mode, Point_Color, Color
                else:
                    messagebox.showwarning("Warning", "MasterImage & MasterData Dont's Match")
            except:
                return Point_Left, Point_Top, Point_Right, Point_Bottom, Point_Score, Point_Mode, Point_Color, Color
        else:
            messagebox.showwarning("Warning", "Plan Down")
            return Point_Left, Point_Top, Point_Right, Point_Bottom, Point_Score, Point_Mode, Point_Color, Color


class Main:
    @staticmethod
    def Main(Partnumber, FileImage, Counter, Mode, Left, Top, Right, Bottom, Score_Set, Color_Data, Model):
            Color = []
            ImageSave = []
            ColorView = []
            Color_Save_Image = []
            Result = []
            Score = []
            ImageModel = []
            for x in range(Counter):
                ImageSave.append(cv.imread(FileImage))
                Template = r"" + Partnumber + "\Master""\\""Point" + str(x + 1) + "_Template.bmp"
                (template, top_left, scale, Score_Outline, bottom_right) = Shape.Process_Outline(FileImage, Template, Left[x], Top[x], Right[x], Bottom[x])
                Imageprocess = CropImage.Crop_find(FileImage, Left[x], Top[x], Right[x], Bottom[x], top_left, bottom_right, Score_Set[x], Score_Outline, Mode[x])
                ImageModel.append(Imageprocess)
                if Partnumber == "NHK0042RBK" or Partnumber == "NHK0043LBK" or Partnumber == "NHK0046RBK" or Partnumber == "NHK0047LBK":
                    Imageprocess = cv.cvtColor(Imageprocess, cv.COLOR_BGR2RGB)
                    resized_image = tf.image.resize(Imageprocess, (100, 100))
                    ytrin = Model.predict(np.expand_dims(resized_image / 255, 0))
                    Score_Area = ytrin[0][1] * 1000
                elif Partnumber == "TBA35C8RCO" or Partnumber == "TBA35C9LCO":
                    resize = tf.image.resize(Master_Image, (300, 300))
                    ytrin = Model.predict(np.expand_dims(resize / 255, 0))
                    Score_Area = ytrin[0][1] * 1000
                Score.append(Score_Area)
                if Score_Outline >= Score_Set[x] and Score_Area >= Score_Set[x]:
                    ColorView.append((0, 255, 0))
                    Color.append("#00B400")
                    Color_Save_Image.append((0, 255, 0))
                    Result.append(1)
                else:
                    ColorView.append((255, 0, 0))
                    Color.append("#B40000")
                    Result.append(0)
                    Color_Save_Image.append((0, 0, 255))
            return ImageSave, ColorView, Color_Save_Image, Result, Score, Color, top_left, ImageModel

    @staticmethod
    def ViewImage_Snap(Filename, Counter, Left, Top, Right, Bottom, Score_set ,Score, Color, top_left, new_scaling_float):
        image = cv.imread(Filename)
        image = cv.cvtColor(image, cv.COLOR_BGR2RGB)
        for s in range(Counter):
            if Score[s] >= Score_set[s]:
                cv.rectangle(image, (Left[s] + top_left[0] - ROI, Top[s] + top_left[1] - ROI), (Right[s] + top_left[0] - ROI, Bottom[s] + top_left[1] - ROI), Color[s], 2)
            else:
                cv.rectangle(image, (Left[s], Top[s]), (Right[s], Bottom[s]), Color[s], 2)
            cv.putText(image, str(s + 1), (Left[s] + top_left[0] - ROI, Top[s] + top_left[1] - ROI), cv.FONT_HERSHEY_SIMPLEX, 0.7, Color[s], 2)
        im = Image.fromarray(image)
        height = int(950 * new_scaling_float)
        weight = int(520 * new_scaling_float)
        im = im.resize((height, weight))
        image = ImageTk.PhotoImage(image=im)
        return image


class Shape:
    @staticmethod
    def Process_Area(Master, Template):
        Score_Ture = []
        Result_Score = 0
        swapped = False
        Couter = len(Master)
        for i in range(Couter):
            # print(Master[i], Template[i])
            if Master[i] < Template[i]:
                Score_Ture.append((Master[i] / Template[i]) * 1000)
            else:
                Score_Ture.append((Template[i] / Master[i]) * 1000)
        for n in range(len(Score_Ture) - 1, 0, -1):
            for i in range(n):
                if Score_Ture[i] > Score_Ture[i + 1]:
                    swapped = True
                    Score_Ture[i], Score_Ture[i + 1] = Score_Ture[i + 1], Score_Ture[i]
        for i in range(len(Score_Ture)):
            if i < 2:
                Result_Score += Score_Ture[i]
        Result_Score = int(Result_Score / 2)
        return Result_Score

    @staticmethod
    def Rule_Of_Thirds(ROT):
        total = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        mod = len(ROT) % 9
        if mod != 0:
            for i in range(mod):
                total[9] += sum(ROT[len(ROT) - mod + i])
        layout = int(len(ROT) / 9)
        for i in range(9):
            i = i + 1
            for j in range(layout * i):
                total[i - 1] += sum(ROT[j])
        point = [total[0]]
        for k in range(8):
            point.append(total[k + 1] - total[k])
        if mod != 0:
            point.append(total[9])
        return point

    @staticmethod
    def Process_Outline(image, Template, Left, Top, Right, Bottom):
        image = cv.imread(image, 0)
        Template = cv.imread(Template, 0)
        w, h = Template.shape[::-1]
        c = 0
        TemplateThreshold = 0.4
        #curMaxVal = 0
        curMaxTemplate = -1
        curMaxLoc = (0, 0)
        for meth in ['cv.TM_CCOEFF_NORMED']:
            method = eval(meth)
            image = image[(Top - ROI):(Bottom + ROI), (Left - ROI):(Right + ROI)]
            res = cv.matchTemplate(image, Template, method)
            min_val, max_val, min_loc, max_loc = cv.minMaxLoc(res)
            if max_val > TemplateThreshold and max_val > 0:
                top_left = max_loc
                curMaxTemplate = c
                curMaxLoc = max_loc
            c = c + 1
            try:
                if curMaxTemplate == -1:
                    return (0, (0, 0), 0, 0, (0, 0))
                else:
                    bottom_right = (top_left[0] + w, top_left[1] + h)
                    return (curMaxTemplate % 3, curMaxLoc, 1 - int(curMaxTemplate / 3) * 0.2, int(max_val*1000), bottom_right)
            except:
                return (0, (0, 0), 0, 0, (0, 0))


class CropImage:
    @staticmethod
    def Crop_Image(Imageframe, Left, Top, Right, Bottom, Mode):
        if Mode == "Color":
            image = cv.imread(Imageframe, cv.COLOR_BGR2RGB)
        elif Mode == "Shape":
            image = cv.imread(Imageframe, 0)
        crop_image = image[Top:Bottom, Left:Right]
        return crop_image

    @staticmethod
    def Crop_Image_Color(Imageframe, Left, Top, Right, Bottom):
        image = cv.imread(Imageframe, cv.COLOR_BGR2RGB)
        crop_image = image[Top:Bottom, Left:Right]
        return crop_image

    @staticmethod
    def Crop_find(image, Left, Top, Right, Bottom, top_left, bottom_right, score_set,score_outline, mode):
        image = cv.imread(image, 1)
        if score_outline >= score_set:
            image = image[(Top - ROI):(Bottom + ROI), (Left - ROI):(Right + ROI)]
            Left = top_left[0]
            Top = top_left[1]
            Right = bottom_right[0]
            Bottom = bottom_right[1]
            image = image[Top:Bottom, Left:Right]
        else:
            image = image[Top:Bottom, Left:Right]
        return image


class ColorProcessing:
    @staticmethod
    def ReadRBG(image):
        r_total = 0
        g_total = 0
        b_total = 0
        count = 0
        for i in range(len(image)):
            for j in range(len(image[i])):
                r_total += image[i][j][0]
                g_total += image[i][j][1]
                b_total += image[i][j][2]
                count += 1
        return int(r_total / count), int(g_total / count), int(b_total / count)

    @staticmethod
    def ColorScore(Data1, Data2):
        total = []
        for i in range(len(Data1)):
            if Data1[i] >= Data2[i]:
                total.append((Data2[i] / Data1[i]) * 1000)
            elif Data2[i] >= Data1[i]:
                total.append((Data1[i] / Data2[i]) * 1000)
        return int(min(total))


class Save_Data:
    @staticmethod
    def Save_Score(Partnumber, Batch, Machine, Couter, Score, Result):
        named_tuple = time.localtime()
        Time = time.strftime("%Y%m%d%H%M%S", named_tuple)
        parent_dir = 'Transaction/'
        path = os.path.join(parent_dir)
        try:
            os.makedirs(path, exist_ok=True)
        except OSError as error:
            pass
        Transition = [dict(PartNumber=Partnumber, BatchNumber=Batch, MachineName=Machine, Details=[])]
        for s in range(Couter):
            Transition[0]["Details"].append([dict(Score=int(Score[s]),
                                                  Result=Result[s], Point=s + 1)])
        with open('Transaction/' + Time + '.json', 'w') as json_file:
            json.dump(Transition, json_file, indent=6)

    @staticmethod
    def Save_Image(Partnumber, Counter, Image, Mode, Left, Top, Right, Bottom, Color, Score, Score_Set, Result, top_left):

        Time = time.strftime("%Y%m%d%H%M%S", time.localtime())
        for s in range(Counter):
            cv.rectangle(Image[s], (Left[s] + top_left[0] - ROI, Top[s] + top_left[1] - ROI), (Right[s] + top_left[0] - ROI, Bottom[s] + top_left[1] - ROI), Color[s], 2)
            cv.rectangle(Image[s], (Left[s] - ROI, Top[s] - ROI), (Right[s] + ROI, Bottom[s] + ROI), Color[s], 2)
            cv.putText(Image[s], "Mode : " + Mode[s], (10, 25), cv.FONT_HERSHEY_SIMPLEX, 1, Color[s], 2)
            cv.putText(Image[s], "Score : " + str(Score[s]) + " / " + str(Score_Set[s]), (10, 55), cv.FONT_HERSHEY_SIMPLEX, 1, Color[s], 2)
            cv.putText(Image[s], "Time : " + str(Time) + "", (10, 85), cv.FONT_HERSHEY_SIMPLEX, 1, Color[s], 2)
            if s <= 8:
                Point = "0"
            else:
                Point = ""
            if Result[s] == 1:
                cv.imwrite('Record/' + Partnumber + '/OK/Point' + str(s + 1) + '/' + Time + '_P' + Point + str(s + 1) + '.jpeg', Image[s])
            else:
                cv.imwrite('Record/' + Partnumber + '/NG/Point' + str(s + 1) + '/' + Time + '_P' + Point + str(s + 1) + '.jpeg', Image[s])

    @staticmethod
    def Master(Left, Top, Right, Bottom, Score, Point, Emp_ID, Mode, Partnumber):
        Score = int(Score)
        image = r'Current.bmp'
        Master_Image = CropImage.Crop_Image_Color(image, Left, Top, Right, Bottom)
        try:
            with open(Partnumber + '/' + Partnumber + '.json', 'r') as json_file:
                item = json.loads(json_file.read())
                for i in range(16):
                    str_ = str(i)
                    try:
                        if Point == "Point" + str_:
                            i = i - 1
                            item[i]["Point" + str_][0]["Mode"] = Mode
                            item[i]["Point" + str_][0]["Emp ID"] = Emp_ID
                            item[i]["Point" + str_][0]["Left"] = Left
                            item[i]["Point" + str_][0]["Top"] = Top
                            item[i]["Point" + str_][0]["Right"] = Right
                            item[i]["Point" + str_][0]["Bottom"] = Bottom
                            item[i]["Point" + str_][0]["Score"] = Score
                            item[i]["Point" + str_][0]["Color"] = ColorProcessing.ReadRBG(Master_Image)
                            with open(Partnumber + '/' + Partnumber + '.json', 'w') as json_file:
                                json.dump(item, json_file, indent=6)
                    except:
                        # item.append({''+Point+'': [{"Camera": "",'Left': "",'Top': "","Right": "","Bottom": "",'Score': ""}]}
                        with open(Partnumber + '/' + Partnumber + '.json', 'r') as json_file:
                            item = json.loads(json_file.read())
                        try:
                            logging.debug(item[i - 1])
                            item.append({'' + Point + '': [
                                {"Emp ID": Emp_ID, "Mode": Mode, 'Left': Left, 'Top': Top, "Right": Right, "Bottom": Bottom, 'Score': Score, 'Color': ColorProcessing.ReadRBG(Master_Image)}]})
                            with open(Partnumber + '/' + Partnumber + '.json', 'w') as json_file:
                                json.dump(item, json_file, indent=6)
                        except:
                            pass
        except FileNotFoundError as exc:
            if Point == "Point1":
                item = [
                    {'' + Point + '': [
                        {"Emp ID": Emp_ID, "Mode": Mode, 'Left': Left, 'Top': Top, "Right": Right, "Bottom": Bottom, 'Score': Score, 'Color': ColorProcessing.ReadRBG(Master_Image)}]}]
                with open(Partnumber + '/' + Partnumber + '.json', 'w') as json_file:
                    json.dump(item, json_file, indent=6)

    @staticmethod
    def Save_Image_Model(Partnumber, Result, Image):
        named_tuple = time.localtime()
        Time = time.strftime("%Y%m%d%H%M%S", named_tuple)
        for s in range(len(Result)):
            FileFolder_Ok = 'Model/' + Partnumber + '/OK/Point' + str(s + 1)
            path = os.path.join(FileFolder_Ok)
            try:
                os.makedirs(path, exist_ok=True)
            except OSError as error:
                pass
            FileFolder_NG = 'Model/' + Partnumber + '/NG/Point' + str(s + 1)
            path = os.path.join(FileFolder_NG)
            try:
                os.makedirs(path, exist_ok=True)
            except OSError as error:
                pass
            if s <= 8:
                Point = "0"
            else:
                Point = ""
            if Result[s] == 1:
                cv.imwrite('Model/' + Partnumber + '/OK/Point' + str(s + 1) + '/' + Time + '_P' + Point + str(s + 1) + '.png', Image[s])
            else:
                cv.imwrite('Model/' + Partnumber + '/NG/Point' + str(s + 1) + '/' + Time + '_P' + Point + str(s + 1) + '.png', Image[s])


class Packing:
    @staticmethod
    def Read_Priter(Partnumber):
        try:
            with open(Partnumber + '\Counter_Printer.json', 'r') as json_file:
                Data = json.loads(json_file.read())
            return Data["Counter"]
        except:
            return 0

    @staticmethod
    def Counter_Printer(Partnumber, Packing,side):
        file_path = Partnumber + '\Counter_Printer.json'
        try:
            with open(file_path, 'r') as json_file:
                data = json.load(json_file)
        except FileNotFoundError:
            data = {"Partnumber": Partnumber, "Counter": 0, "Packing": Packing}
        packing_counter = data["Counter"] + 1
        pack_part = data["Partnumber"]
        if pack_part != Partnumber:
            printer = {"Partnumber": Partnumber, "Counter": 1, "Packing": Packing}
        else:
            printer = {"Partnumber": Partnumber, "Counter": packing_counter, "Packing": Packing}
        if packing_counter >= Packing:
            printer = {"Partnumber": Partnumber, "Counter": 0, "Packing": Packing}
            with open('Printer'+side+'.txt', 'w') as f:
                f.write('Printer')
        with open(file_path, 'w') as json_file:
            json.dump(printer, json_file, indent=6)

        return packing_counter


class App(customtkinter.CTk):
    customtkinter.set_appearance_mode("Dark")
    customtkinter.set_default_color_theme("green")

    def __init__(self):
        GetEmp.Information()
        super().__init__()
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        self.title('MachineVisionInspectionS11')
        self.geometry("1920x1020+0+0")
        self.attributes('-fullscreen', True)
        self.MachineName = Machine

        self.Comfrim_left = 0
        self.Comfrim_rigth = 0
        self.Comfrim_single = 0

        self.Model_R = ""
        self.Model_L = ""


        self.CouterPoint_Single = 0
        self.CouterPoint_Left = 0
        self.CouterPoint_Right = 0
        self.CouterOK_Left = 0
        self.CouterNG_Left = 0
        self.CouterOK_Right = 0
        self.CouterNG_Right = 0
        self.CouterOK_Single = 0
        self.CouterNG_Single = 0
        self.new_scaling_float = 1.0
        self.PartNumber_R = self.BatchNumber_R = self.PartName_R = self.CustomerPartNumber_R = self.Packing_R = ""
        self.PartNumber_L = self.BatchNumber_L = self.PartName_L = self.CustomerPartNumber_L = self.Packing_L = ""
        self.PartNumber_S = self.BatchNumber_S = self.PartName_S = self.CustomerPartNumber_S = self.Packing_S = ""
        self.Login = None
        self.ViewImage = False
        self.View_Point_Clear()
        self.View()
        self.AddMaster()


        self.Image_logo = GetImage()
        Fullscreen_width = 1920
        Fullscreen_height = 1080
        self.new_scaling_float = screen_width / Fullscreen_width
        customtkinter.set_widget_scaling(self.new_scaling_float)
        self.height_camera = int(950 * self.new_scaling_float)
        self.weight_camera = int(520 * self.new_scaling_float)

        self.Keepdata = ""
        customtkinter.CTkLabel(master=self, text="Vision Inspection", text_color="#00B400", font=customtkinter.CTkFont(family="Microsoft PhagsPa", size=50, weight="bold"), corner_radius=10).place(x=140, y=10)
        self.Communication = customtkinter.CTkButton(master=self, text="Connect Robot", text_color="#00B400", font=customtkinter.CTkFont(family="Microsoft PhagsPa", size=40, weight="bold"), corner_radius=10, fg_color="#353535", hover_color="#B4F0B4", command=lambda: [self.connecting()])
        self.Communication.place(x=970, y=10)
        customtkinter.CTkLabel(master=self, text="v 1.0.0", text_color="#00B400", font=customtkinter.CTkFont(family="Microsoft PhagsPa", size=15, weight="bold"), corner_radius=10).place(x=490, y=10)
        self.image_logo = customtkinter.CTkButton(master=self, image=self.Image_logo.BKFImage, command=self.Destory, text="", fg_color="#353535", hover_color="#353535")
        self.image_logo.place(x=1755, y=10)

        self.image_logo.bind("<Enter>", self.on_enter)
        self.image_logo.bind("<Leave>", self.on_leave)
        self.Camera()
        #Camerarun = InfiniteTimer(0.01, self.Camera)
        #Camerarun.start()
        customtkinter.CTkButton(master=self, text="Reorder", text_color="#00B400", hover_color="#B4F0B4", font=customtkinter.CTkFont(family="Microsoft PhagsPa", size=40, weight="bold"), corner_radius=10, fg_color=("#353535"),
                                command=lambda: [self.forget(), self.View_Point_Clear(), self.View()]).place(x=1570, y=10)

    def connect(self):
        host = IP
        port = Port
        if Mode == 3:
            server_socket = socket.socket()
            server_socket.settimeout(60)
            try:
                try:
                    server_socket.bind((host, port))
                except:
                    messagebox.showwarning("Communication Error !!", "The address or port does not match. !!!")
                    self.Communication.configure(text="Connect Robot")
                    self.Communication.place(x=970)
                server_socket.listen(2)
                self.conn, address = server_socket.accept()
                self.Loop = InfiniteTimer(0.1, self.server_program)
                self.Loop.start()
                self.Communication.configure(text="Connected")
                self.Communication.place(x=1050)
            except socket.timeout:
                messagebox.showwarning("Communication Error !!", "The communication with Robot time out 60 seconds")
                self.Communication.configure(text="Connect Robot")
                self.Communication.place(x=970)
            finally:
                server_socket.close()
        elif Mode == 4:
            try:
                host = socket.gethostname()
                self.client_socket = socket.socket()
                self.client_socket.connect((host, Port))
                self.Ready = False
                self.Loop = InfiniteTimer(0.1, self.client_program)
                self.Loop.start()
            except:
                messagebox.showwarning("Communication Error !!", "The address or port does not match. !!!")

    def connecting(self):
        self.Communication.configure(text="Connecting...")
        self.Communication.place(x=1010)
        timer = Timer(0.5, self.connect,args=())
        timer.start()


    def View(self):
        self.API = GetAPI.API()
        if self.API[0] == "Connected":
            color = "#00B400"
        else:
            color = "#D8D874"
        customtkinter.CTkLabel(master=self, text=Machine, text_color=color, font=customtkinter.CTkFont(family="Microsoft PhagsPa", size=65, weight="bold")).place(x=10, y=0)
        self.Run_Left = self.Run_Right = self.Run_Single = False

        self.CouterPacking_Left = 0
        self.CouterPacking_Right = 0
        self.CouterPacking_Single = 0

        self.Point_Left_R = self.Point_Top_R = self.Point_Right_R = self.Point_Bottom_R = self.Point_Score_R = self.Point_Mode_R = self.Point_Color_R = self.Color_R = []
        self.Point_Left_L = self.Point_Top_L = self.Point_Right_L = self.Point_Bottom_L = self.Point_Score_L = self.Point_Mode_L = self.Point_Color_L = self.Color_L = []
        self.Point_Left_S = self.Point_Top_S = self.Point_Right_S = self.Point_Bottom_S = self.Point_Score_S = self.Point_Mode_S = self.Point_Color_S = self.Color_S = []

        if len(self.API[1]) == 2:
            self.ImageReal_Left = customtkinter.CTkLabel(master=self, text="")
            self.ImageReal_Right = customtkinter.CTkLabel(master=self, text="")
            self.ImageReal_Left.place(x=0, y=260)
            self.ImageReal_Right.place(x=960, y=260)
            self.PartNumber_R = self.API[2][0]

            if self.BatchNumber_R != self.API[2][1]:
                self.BatchNumber_R = self.API[2][1]
                self.CouterOK_Right = 0
                self.CouterNG_Right = 0

            self.PartName_R = self.API[2][2]
            self.CustomerPartNumber_R = self.API[2][3]
            self.Packing_R = self.API[2][4]
            self.PartNumber_L = self.API[2][5]

            if self.BatchNumber_L != self.API[2][6]:
                self.BatchNumber_L = self.API[2][6]
                self.CouterOK_Left = 0
                self.CouterNG_Left = 0

            self.PartName_L = self.API[2][7]
            self.CustomerPartNumber_L = self.API[2][8]
            self.Packing_L = self.API[2][9]

            self.PartNumber = "|" + self.PartNumber_R + "|" + self.PartNumber_L
            self.CouterPacking_Left = Packing.Read_Priter(self.PartNumber_L)
            self.CouterPacking_Right = Packing.Read_Priter(self.PartNumber_R)
            if self.PartNumber_R == "NHK0042RBK" or self.PartNumber_R == "NHK0046RBK" or self.PartNumber_R == "TBA35C8RCO":
                self.Model_R  = tf.keras.models.load_model("ImageClassification\Model/" + str(self.PartNumber_R) + ".model")
                #self.Model_R = keras.models.load_model("ImageClassification\Model/" + str(self.PartNumber_R) + ".model")
            if  self.PartNumber_L == "NHK0043LBK" or self.PartNumber_L == "NHK0047LBK" or self.PartNumber_L == "TBA35C9LCO":
                self.Model_L = tf.keras.models.load_model("ImageClassification\Model/" + str(self.PartNumber_L) + ".model")
                #self.Model_L = keras.models.load_model("ImageClassification\Model/" + str(self.PartNumber_L) + ".model")

            self.CouterPoint_Left = ReadFile.ReadFile_Image(self.PartNumber_L)
            self.Point_Left_L, self.Point_Top_L, self.Point_Right_L, self.Point_Bottom_L, self.Point_Score_L, self.Point_Mode_L, self.Point_Color_L, self.Color_L = ReadFile.ReadFile_Score(self.PartNumber_L, self.CouterPoint_Left)
            self.View_Point_Left(self.Color_L)
            self.CouterPoint_Right = ReadFile.ReadFile_Image(self.PartNumber_R)
            self.Point_Left_R, self.Point_Top_R, self.Point_Right_R, self.Point_Bottom_R, self.Point_Score_R, self.Point_Mode_R, self.Point_Color_R, self.Color_R = ReadFile.ReadFile_Score(self.PartNumber_R, self.CouterPoint_Right)
            self.View_Point_Right(self.Color_R)

            self.BKF_Part_L_Lable = customtkinter.CTkLabel(master=self, text="BKF Part :", text_color="#00B400", font=customtkinter.CTkFont(family="Microsoft PhagsPa", size=25, weight="bold"))
            self.BKF_Part_L_Lable.place(x=10, y=100)
            self.PartNumber_L_Data = customtkinter.CTkLabel(master=self, text=self.PartNumber_L, text_color="#FFFFFF", font=customtkinter.CTkFont(family="Microsoft PhagsPa", size=25, weight="bold"), fg_color=("#00B400"), corner_radius=10)
            self.PartNumber_L_Data.place(x=150, y=100)
            self.Customer_L_Lable = customtkinter.CTkLabel(master=self, text="Customer :", text_color="#00B400", font=customtkinter.CTkFont(family="Microsoft PhagsPa", size=25, weight="bold"))
            self.Customer_L_Lable.place(x=10, y=140)
            self.CustomerPartNumber_L_Data = customtkinter.CTkLabel(master=self, text=self.CustomerPartNumber_L, text_color="#FFFFFF", font=customtkinter.CTkFont(family="Microsoft PhagsPa", size=25, weight="bold"), fg_color=("#00B400"), corner_radius=10)
            self.CustomerPartNumber_L_Data.place(x=150, y=140)
            self.Batch_L_Lable = customtkinter.CTkLabel(master=self, text="Batch :", text_color="#00B400", font=customtkinter.CTkFont(family="Microsoft PhagsPa", size=25, weight="bold"))
            self.Batch_L_Lable.place(x=10, y=180)
            self.BatchNumber_L_Data = customtkinter.CTkLabel(master=self, text=self.BatchNumber_L, text_color="#FFFFFF", font=customtkinter.CTkFont(family="Microsoft PhagsPa", size=25, weight="bold"), fg_color=("#00B400"), corner_radius=10)
            self.BatchNumber_L_Data.place(x=150, y=180)
            self.PartName_L_Lable = customtkinter.CTkLabel(master=self, text="Part Name :", text_color="#00B400", font=customtkinter.CTkFont(family="Microsoft PhagsPa", size=25, weight="bold"))
            self.PartName_L_Lable.place(x=10, y=220)
            self.PartName_L_Data = customtkinter.CTkLabel(master=self, text=self.PartName_L[:30], text_color="#FFFFFF", font=customtkinter.CTkFont(family="Microsoft PhagsPa", size=25, weight="bold"), fg_color=("#00B400"), corner_radius=10)
            self.PartName_L_Data.place(x=150, y=220)
            self.NG_L = customtkinter.CTkButton(master=self, text="NG : " + str(self.CouterNG_Left), text_color="#FFFFFF", hover_color="#C80000", font=customtkinter.CTkFont(family="Microsoft PhagsPa", size=50, weight="bold"), corner_radius=10, fg_color=("#FF0000")
                                                )
            self.NG_L.place(x=620, y=180)
            self.OK_L = customtkinter.CTkLabel(master=self, text="OK : " + str(self.CouterOK_Left), text_color="#FFFFFF", font=customtkinter.CTkFont(family="Microsoft PhagsPa", size=52, weight="bold"), corner_radius=10, fg_color=("#00B400"))
            self.OK_L.place(x=620, y=100)
            self.Packing_L_Lable = customtkinter.CTkLabel(master=self, text="Packing :", text_color="#00B400", font=customtkinter.CTkFont(family="Microsoft PhagsPa", size=25, weight="bold"), corner_radius=10)
            self.Packing_L_Lable.place(x=400, y=100)
            self.Packing_L_Show = customtkinter.CTkLabel(master=self, text=str(self.CouterPacking_Left) + "/" + str(self.Packing_L), text_color="#FFFFFF", font=customtkinter.CTkFont(family="Microsoft PhagsPa", size=25, weight="bold"), corner_radius=10, fg_color=("#00B400"))
            self.Packing_L_Show.place(x=530, y=100)

            self.BKF_Part_R_Lable = customtkinter.CTkLabel(master=self, text="BKF Part :", text_color="#00B400", font=customtkinter.CTkFont(family="Microsoft PhagsPa", size=25, weight="bold"))
            self.BKF_Part_R_Lable.place(x=960, y=100)
            self.PartNumber_R_Data = customtkinter.CTkLabel(master=self, text=self.PartNumber_R, text_color="#FFFFFF", font=customtkinter.CTkFont(family="Microsoft PhagsPa", size=25, weight="bold"), fg_color=("#00B400"), corner_radius=10)
            self.PartNumber_R_Data.place(x=1100, y=100)
            self.Customer_R_Lable = customtkinter.CTkLabel(master=self, text="Customer :", text_color="#00B400", font=customtkinter.CTkFont(family="Microsoft PhagsPa", size=25, weight="bold"))
            self.Customer_R_Lable.place(x=960, y=140)
            self.CustomerPartNumber_R_Data = customtkinter.CTkLabel(master=self, text=self.CustomerPartNumber_R, text_color="#FFFFFF", font=customtkinter.CTkFont(family="Microsoft PhagsPa", size=25, weight="bold"), fg_color=("#00B400"), corner_radius=10)
            self.CustomerPartNumber_R_Data.place(x=1100, y=140)
            self.Batch_R_Lable = customtkinter.CTkLabel(master=self, text="Batch :", text_color="#00B400", font=customtkinter.CTkFont(family="Microsoft PhagsPa", size=25, weight="bold"))
            self.Batch_R_Lable.place(x=960, y=180)
            self.BatchNumber_R_Data = customtkinter.CTkLabel(master=self, text=self.BatchNumber_R, text_color="#FFFFFF", font=customtkinter.CTkFont(family="Microsoft PhagsPa", size=25, weight="bold"), fg_color=("#00B400"), corner_radius=10)
            self.BatchNumber_R_Data.place(x=1100, y=180)
            self.PartName_R_Lable = customtkinter.CTkLabel(master=self, text="Part Name :", text_color="#00B400", font=customtkinter.CTkFont(family="Microsoft PhagsPa", size=25, weight="bold"))
            self.PartName_R_Lable.place(x=960, y=220)
            self.PartName_R_Data = customtkinter.CTkLabel(master=self, text=self.PartName_R[:30], text_color="#FFFFFF", font=customtkinter.CTkFont(family="Microsoft PhagsPa", size=25, weight="bold"), fg_color=("#00B400"), corner_radius=10)
            self.PartName_R_Data.place(x=1100, y=220)
            self.NG_R = customtkinter.CTkButton(master=self, text="NG : " + str(self.CouterNG_Right), text_color="#FFFFFF", hover_color="#C80000", font=customtkinter.CTkFont(family="Microsoft PhagsPa", size=50, weight="bold"), corner_radius=10, fg_color=("#FF0000"),
                                                )
            self.NG_R.place(x=1590, y=180)
            self.OK_R = customtkinter.CTkLabel(master=self, text="OK : " + str(self.CouterOK_Right), text_color="#FFFFFF", font=customtkinter.CTkFont(family="Microsoft PhagsPa", size=52, weight="bold"), corner_radius=10, fg_color=("#00B400"))
            self.OK_R.place(x=1590, y=100)
            self.Packing_R_Lable = customtkinter.CTkLabel(master=self, text="Packing :", text_color="#00B400", font=customtkinter.CTkFont(family="Microsoft PhagsPa", size=25, weight="bold"), corner_radius=10)
            self.Packing_R_Lable.place(x=1360, y=100)
            self.Packing_R_Show = customtkinter.CTkLabel(master=self, text=str(self.CouterPacking_Right) + "/" + str(self.Packing_R), text_color="#FFFFFF", font=customtkinter.CTkFont(family="Microsoft PhagsPa", size=25, weight="bold"), corner_radius=10, fg_color=("#00B400"))
            self.Packing_R_Show.place(x=1490, y=100)


        elif len(self.API[1]) == 1:  #
            if self.API[1][0] == "Right":
                    self.ImageReal_Right = customtkinter.CTkLabel(master=self, text="")
                    #self.ImageReal_Right = tk.Button(self, bg="White", command=lambda: self.ViewImagePart(self.PartNumber_R))
                    self.ImageReal_Right.place(x=960, y=260)
                    self.PartNumber_R = self.API[2][0]

                    if self.BatchNumber_R != self.API[2][1]:
                        self.BatchNumber_R = self.API[2][1]
                        self.CouterOK_Right = 0
                        self.CouterNG_Right = 0

                    self.PartName_R = self.API[2][2]
                    self.CustomerPartNumber_R = self.API[2][3]
                    self.Packing_R = self.API[2][4]
                    self.CouterPacking_Right = Packing.Read_Priter(self.PartNumber_R)
                    self.PartNumber = "|" + self.PartNumber_R + "|"

                    self.CouterPoint_Right = ReadFile.ReadFile_Image(self.PartNumber_R)
                    self.Point_Left_R, self.Point_Top_R, self.Point_Right_R, self.Point_Bottom_R, self.Point_Score_R, self.Point_Mode_R, self.Point_Color_R, self.Color_R = ReadFile.ReadFile_Score(self.PartNumber_R, self.CouterPoint_Right)
                    self.View_Point_Right(self.Color_R)
                    self.BKF_Part_R_Lable = customtkinter.CTkLabel(master=self, text="BKF Part :", text_color="#00B400", font=customtkinter.CTkFont(family="Microsoft PhagsPa", size=25, weight="bold"))
                    self.BKF_Part_R_Lable.place(x=960, y=100)
                    self.PartNumber_R_Data = customtkinter.CTkLabel(master=self, text=self.PartNumber_R, text_color="#FFFFFF", font=customtkinter.CTkFont(family="Microsoft PhagsPa", size=25, weight="bold"), fg_color=("#00B400"), corner_radius=10)
                    self.PartNumber_R_Data.place(x=1100, y=100)
                    self.Customer_R_Lable = customtkinter.CTkLabel(master=self, text="Customer :", text_color="#00B400", font=customtkinter.CTkFont(family="Microsoft PhagsPa", size=25, weight="bold"))
                    self.Customer_R_Lable.place(x=960, y=140)
                    self.CustomerPartNumber_R_Data = customtkinter.CTkLabel(master=self, text=self.CustomerPartNumber_R, text_color="#FFFFFF", font=customtkinter.CTkFont(family="Microsoft PhagsPa", size=25, weight="bold"), fg_color=("#00B400"), corner_radius=10)
                    self.CustomerPartNumber_R_Data.place(x=1100, y=140)
                    self.Batch_R_Lable = customtkinter.CTkLabel(master=self, text="Batch :", text_color="#00B400", font=customtkinter.CTkFont(family="Microsoft PhagsPa", size=25, weight="bold"))
                    self.Batch_R_Lable.place(x=960, y=180)
                    self.BatchNumber_R_Data = customtkinter.CTkLabel(master=self, text=self.BatchNumber_R, text_color="#FFFFFF", font=customtkinter.CTkFont(family="Microsoft PhagsPa", size=25, weight="bold"), fg_color=("#00B400"), corner_radius=10)
                    self.BatchNumber_R_Data.place(x=1100, y=180)
                    self.PartName_R_Lable = customtkinter.CTkLabel(master=self, text="Part Name :", text_color="#00B400", font=customtkinter.CTkFont(family="Microsoft PhagsPa", size=25, weight="bold"))
                    self.PartName_R_Lable.place(x=960, y=220)
                    self.PartName_R_Data = customtkinter.CTkLabel(master=self, text=self.PartName_R[:30], text_color="#FFFFFF", font=customtkinter.CTkFont(family="Microsoft PhagsPa", size=25, weight="bold"), fg_color=("#00B400"), corner_radius=10)
                    self.PartName_R_Data.place(x=1100, y=220)
                    self.NG_R = customtkinter.CTkButton(master=self, text="NG : " + str(self.CouterNG_Right), text_color="#FFFFFF", hover_color="#C80000", font=customtkinter.CTkFont(family="Microsoft PhagsPa", size=50, weight="bold"), corner_radius=10, fg_color=("#FF0000"),)
                    self.NG_R.place(x=1590, y=180)
                    self.OK_R = customtkinter.CTkLabel(master=self, text="OK : " + str(self.CouterOK_Right), text_color="#FFFFFF", font=customtkinter.CTkFont(family="Microsoft PhagsPa", size=52, weight="bold"), corner_radius=10, fg_color=("#00B400"))
                    self.OK_R.place(x=1590, y=100)
                    self.Packing_R_Lable = customtkinter.CTkLabel(master=self, text="Packing :", text_color="#00B400", font=customtkinter.CTkFont(family="Microsoft PhagsPa", size=25, weight="bold"), corner_radius=10)
                    self.Packing_R_Lable.place(x=1360, y=100)
                    self.Packing_R_Show = customtkinter.CTkLabel(master=self, text=str(self.CouterPacking_Right) + "/" + str(self.Packing_R), text_color="#FFFFFF", font=customtkinter.CTkFont(family="Microsoft PhagsPa", size=25, weight="bold"), corner_radius=10, fg_color=("#00B400"))
                    self.Packing_R_Show.place(x=1490, y=100)

            elif self.API[1][0] == "Left":
                self.ImageReal_Left = customtkinter.CTkLabel(master=self, text="")
                # self.ImageReal_Left = tk.Button(self, bg="White", command=lambda: self.ViewImagePart(self.PartNumber_L))
                self.ImageReal_Left.place(x=0, y=260)
                self.PartNumber_L = self.API[2][0]

                if self.BatchNumber_L != self.API[2][1]:
                    self.BatchNumber_L = self.API[2][1]
                    self.CouterOK_Left = 0
                    self.CouterNG_Left = 0

                self.PartName_L = self.API[2][2]
                self.CustomerPartNumber_L = self.API[2][3]
                self.Packing_L = self.API[2][4]
                self.CouterPacking_Right = Packing.Read_Priter(self.PartNumber_L)
                self.PartNumber = "|" + "|" + self.PartNumber_L

                self.CouterPoint_Left = ReadFile.ReadFile_Image(self.PartNumber_L)
                self.Point_Left_L, self.Point_Top_L, self.Point_Right_L, self.Point_Bottom_L, self.Point_Score_L, self.Point_Mode_L, self.Point_Color_L, self.Color_L = ReadFile.ReadFile_Score(self.PartNumber_L, self.CouterPoint_Left)
                self.View_Point_Left(self.Color_L)
                self.BKF_Part_L_Lable = customtkinter.CTkLabel(master=self, text="BKF Part :", text_color="#00B400", font=customtkinter.CTkFont(family="Microsoft PhagsPa", size=25, weight="bold"))
                self.BKF_Part_L_Lable.place(x=10, y=100)
                self.PartNumber_L_Data = customtkinter.CTkLabel(master=self, text=self.PartNumber_L, text_color="#FFFFFF", font=customtkinter.CTkFont(family="Microsoft PhagsPa", size=25, weight="bold"), fg_color=("#00B400"), corner_radius=10)
                self.PartNumber_L_Data.place(x=150, y=100)
                self.Customer_L_Lable = customtkinter.CTkLabel(master=self, text="Customer :", text_color="#00B400", font=customtkinter.CTkFont(family="Microsoft PhagsPa", size=25, weight="bold"))
                self.Customer_L_Lable.place(x=10, y=140)
                self.CustomerPartNumber_L_Data = customtkinter.CTkLabel(master=self, text=self.CustomerPartNumber_L, text_color="#FFFFFF", font=customtkinter.CTkFont(family="Microsoft PhagsPa", size=25, weight="bold"), fg_color=("#00B400"), corner_radius=10)
                self.CustomerPartNumber_L_Data.place(x=150, y=140)
                self.Batch_L_Lable = customtkinter.CTkLabel(master=self, text="Batch :", text_color="#00B400", font=customtkinter.CTkFont(family="Microsoft PhagsPa", size=25, weight="bold"))
                self.Batch_L_Lable.place(x=10, y=180)
                self.BatchNumber_L_Data = customtkinter.CTkLabel(master=self, text=self.BatchNumber_L, text_color="#FFFFFF", font=customtkinter.CTkFont(family="Microsoft PhagsPa", size=25, weight="bold"), fg_color=("#00B400"), corner_radius=10)
                self.BatchNumber_L_Data.place(x=150, y=180)
                self.PartName_L_Lable = customtkinter.CTkLabel(master=self, text="Part Name :", text_color="#00B400", font=customtkinter.CTkFont(family="Microsoft PhagsPa", size=25, weight="bold"))
                self.PartName_L_Lable.place(x=10, y=220)
                self.PartName_L_Data = customtkinter.CTkLabel(master=self, text=self.PartName_L[:30], text_color="#FFFFFF", font=customtkinter.CTkFont(family="Microsoft PhagsPa", size=25, weight="bold"), fg_color=("#00B400"), corner_radius=10)
                self.PartName_L_Data.place(x=150, y=220)
                self.NG_L = customtkinter.CTkButton(master=self, text="NG : " + str(self.CouterNG_Left), text_color="#FFFFFF", hover_color="#C80000", font=customtkinter.CTkFont(family="Microsoft PhagsPa", size=50, weight="bold"), corner_radius=10, fg_color=("#FF0000"),
                                                    command=lambda: self.ViewNG("NG_Left", self.PartNumber_L))
                self.NG_L.place(x=620, y=180)
                self.OK_L = customtkinter.CTkLabel(master=self, text="OK : " + str(self.CouterOK_Left), text_color="#FFFFFF", font=customtkinter.CTkFont(family="Microsoft PhagsPa", size=52, weight="bold"), corner_radius=10, fg_color=("#00B400"))
                self.OK_L.place(x=620, y=100)
                self.Packing_L_Lable = customtkinter.CTkLabel(master=self, text="Packing :", text_color="#00B400", font=customtkinter.CTkFont(family="Microsoft PhagsPa", size=25, weight="bold"), corner_radius=10)
                self.Packing_L_Lable.place(x=400, y=100)
                self.Packing_L_Show = customtkinter.CTkLabel(master=self, text=str(self.CouterPacking_Left) + "/" + str(self.Packing_L), text_color="#FFFFFF", font=customtkinter.CTkFont(family="Microsoft PhagsPa", size=25, weight="bold"), corner_radius=10, fg_color=("#00B400"))
                self.Packing_L_Show.place(x=530, y=100)


            elif self.API[1][0] == "Single":
                self.PartNumber_S = self.API[2][0]

                if self.BatchNumber_S != self.API[2][1]:
                    self.BatchNumber_S = self.API[2][1]
                    self.CouterOK_Single = 0
                    self.CouterNG_Single = 0

                self.PartName_S = self.API[2][2]
                self.CustomerPartNumber_S = self.API[2][3]
                self.Packing_S = self.API[2][4]
                self.CouterPacking_Single = Packing.Read_Priter(self.PartNumber_S)
                self.PartNumber = self.PartNumber_S + "|" + "|"
                # self.ImageReal_Left = customtkinter.CTkLabel(master=self, text="")
                self.ImageReal_Single = customtkinter.CTkLabel(master=self, text="")
                # self.ImageReal_Single = tk.Button(self, bg="White", command=lambda: self.ViewImagePart(self.PartNumber_S))
                self.ImageReal_Single.place(x=450, y=280)
                self.CouterPoint_Single = ReadFile.ReadFile_Image(self.PartNumber_S)
                self.Point_Left_S, self.Point_Top_S, self.Point_Right_S, self.Point_Bottom_S, self.Point_Score_S, self.Point_Mode_S, self.Point_Color_S, self.Color_S = ReadFile.ReadFile_Score(self.PartNumber_S, self.CouterPoint_Single)
                self.View_Point_Single(self.Color_S)

                self.BKF_Part_S_Lable = customtkinter.CTkLabel(master=self, text="BKF Part :", text_color="#00B400", font=customtkinter.CTkFont(family="Microsoft PhagsPa", size=25, weight="bold"))
                self.BKF_Part_S_Lable.place(x=450, y=100)
                self.PartNumber_S_Data = customtkinter.CTkLabel(master=self, text=self.PartNumber_S, text_color="#FFFFFF", font=customtkinter.CTkFont(family="Microsoft PhagsPa", size=25, weight="bold"), fg_color=("#00B400"), corner_radius=10)
                self.PartNumber_S_Data.place(x=590, y=100)
                self.Customer_S_Lable = customtkinter.CTkLabel(master=self, text="Customer :", text_color="#00B400", font=customtkinter.CTkFont(family="Microsoft PhagsPa", size=25, weight="bold"))
                self.Customer_S_Lable.place(x=450, y=140)
                self.CustomerPartNumber_S_Data = customtkinter.CTkLabel(master=self, text=self.CustomerPartNumber_S, text_color="#FFFFFF", font=customtkinter.CTkFont(family="Microsoft PhagsPa", size=25, weight="bold"), fg_color=("#00B400"), corner_radius=10)
                self.CustomerPartNumber_S_Data.place(x=590, y=140)
                self.Batch_S_Lable = customtkinter.CTkLabel(master=self, text="Batch :", text_color="#00B400", font=customtkinter.CTkFont(family="Microsoft PhagsPa", size=25, weight="bold"))
                self.Batch_S_Lable.place(x=450, y=180)
                self.BatchNumber_S_Data = customtkinter.CTkLabel(master=self, text=self.BatchNumber_S, text_color="#FFFFFF", font=customtkinter.CTkFont(family="Microsoft PhagsPa", size=25, weight="bold"), fg_color=("#00B400"), corner_radius=10)
                self.BatchNumber_S_Data.place(x=590, y=180)
                self.PartName_S_Lable = customtkinter.CTkLabel(master=self, text="Part Name :", text_color="#00B400", font=customtkinter.CTkFont(family="Microsoft PhagsPa", size=25, weight="bold"))
                self.PartName_S_Lable.place(x=450, y=220)
                self.PartName_S_Data = customtkinter.CTkLabel(master=self, text=self.PartName_S[:30], text_color="#FFFFFF", font=customtkinter.CTkFont(family="Microsoft PhagsPa", size=25, weight="bold"), fg_color=("#00B400"), corner_radius=10)
                self.PartName_S_Data.place(x=590, y=220)
                self.NG_S = customtkinter.CTkButton(master=self, text="NG : " + str(self.CouterNG_Single), text_color="#FFFFFF", hover_color="#C80000", font=customtkinter.CTkFont(family="Microsoft PhagsPa", size=50, weight="bold"), corner_radius=10, fg_color=("#FF0000"),
                                                    command=lambda: self.ViewNG("NG_Single", self.PartNumber_S))
                self.NG_S.place(x=1080, y=180)
                self.OK_S = customtkinter.CTkLabel(master=self, text="OK : " + str(self.CouterOK_Single), text_color="#FFFFFF", font=customtkinter.CTkFont(family="Microsoft PhagsPa", size=52, weight="bold"), corner_radius=10, fg_color=("#00B400"))
                self.OK_S.place(x=1080, y=100)
                self.Packing_S_Lable = customtkinter.CTkLabel(master=self, text="Packing :", text_color="#00B400", font=customtkinter.CTkFont(family="Microsoft PhagsPa", size=25, weight="bold"), corner_radius=10)
                self.Packing_S_Lable.place(x=850, y=100)
                self.Packing_S_Show = customtkinter.CTkLabel(master=self, text=str(self.CouterPacking_Single) + "/" + str(self.Packing_S), text_color="#FFFFFF", font=customtkinter.CTkFont(family="Microsoft PhagsPa", size=25, weight="bold"), corner_radius=10, fg_color=("#00B400"))
                self.Packing_S_Show.place(x=980, y=100)

    def forget(self):
        try:
            self.BKF_Part_L_Lable.place_forget()
            self.PartNumber_L_Data.place_forget()
            self.Customer_L_Lable.place_forget()
            self.CustomerPartNumber_L_Data.place_forget()
            self.Batch_L_Lable.place_forget()
            self.BatchNumber_L_Data.place_forget()
            self.PartName_L_Lable.place_forget()
            self.PartName_L_Data.place_forget()
            self.NG_L.place_forget()
            self.OK_L.place_forget()
            self.Packing_L_Lable.place_forget()
            self.Packing_L_Show.place_forget()
        except:
            pass
        try:
            self.BKF_Part_R_Lable.place_forget()
            self.PartNumber_R_Data.place_forget()
            self.Customer_R_Lable.place_forget()
            self.CustomerPartNumber_R_Data.place_forget()
            self.Batch_R_Lable.place_forget()
            self.BatchNumber_R_Data.place_forget()
            self.PartName_R_Lable.place_forget()
            self.PartName_R_Data.place_forget()
            self.NG_R.place_forget()
            self.OK_R.place_forget()
            self.Packing_R_Lable.place_forget()
            self.Packing_R_Show.place_forget()
        except:
            pass
        try:
            self.BKF_Part_S_Lable.place_forget()
            self.PartNumber_S_Data.place_forget()
            self.Customer_S_Lable.place_forget()
            self.CustomerPartNumber_S_Data.place_forget()
            self.Batch_S_Lable.place_forget()
            self.BatchNumber_S_Data.place_forget()
            self.PartName_S_Lable.place_forget()
            self.PartName_S_Data.place_forget()
            self.NG_S.place_forget()
            self.OK_S.place_forget()
            self.Packing_S_Lable.place_forget()
            self.Packing_S_Show.place_forget()
        except:
            pass
        try:
            self.ImageReal_Left.place_forget()
        except:
            pass
        try:
            self.ImageReal_Right.place_forget()
        except:
            pass
        try:
            self.ImageReal_Single.place_forget()
        except:
            pass

    def ViewImagePart(self, Partnumber):
        if self.ViewImage is False:
            self.ViewImage = True
            View = r"Image_Partnumber/" + Partnumber + ".png"
            if os.path.isfile(View) is False:
                View = r"BKF.png"
            img = cv.imread(View, cv.COLOR_BGR2RGB)
            cv.imshow(Partnumber, img)
        self.ViewImage = False

    def View_Point_Clear(self):
        self.Frame_Point = customtkinter.CTkFrame(master=self, width=1980, height=270).place(x=0, y=810)

    def View_Point_Left(self, color):
        self.Point_Left_View = []
        customtkinter.CTkLabel(master=self.Frame_Point, text="POINT CHECK", text_color="#FFFFFF", font=customtkinter.CTkFont(family="Microsoft PhagsPa", size=20, weight="bold"), corner_radius=10).place(x=0, y=810)
        if self.PartNumber_L != "":
            for Point_Left in range(self.CouterPoint_Left):
                if Point_Left <= 4:
                    self.Point_Left_View.append(customtkinter.CTkLabel(master=self.Frame_Point, text=str(Point_Left + 1), text_color="#FFFFFF", font=customtkinter.CTkFont(family="Microsoft PhagsPa", size=35, weight="bold"), corner_radius=10, fg_color=(color[Point_Left]), width=170, height=50))
                    self.Point_Left_View[Point_Left].place(x=190 * (Point_Left), y=850)
                elif Point_Left <= 9:
                    self.Point_Left_View.append(customtkinter.CTkLabel(master=self.Frame_Point, text=str(Point_Left + 1), text_color="#FFFFFF", font=customtkinter.CTkFont(family="Microsoft PhagsPa", size=35, weight="bold"), corner_radius=10, fg_color=(color[Point_Left]), width=170, height=50))
                    self.Point_Left_View[Point_Left].place(x=190 * (Point_Left - 5),y=930)
                elif Point_Left <= 15:
                    self.Point_Left_View.append(customtkinter.CTkLabel(master=self.Frame_Point, text=str(Point_Left + 1), text_color="#FFFFFF", font=customtkinter.CTkFont(family="Microsoft PhagsPa", size=35, weight="bold"), corner_radius=10, fg_color=(color[Point_Left]), width=170, height=50))
                    self.Point_Left_View[Point_Left].place(x=190 * (Point_Left - 10),y=1010)

    def View_Point_Right(self, color):
        self.Point_Rigth_View = []
        customtkinter.CTkLabel(master=self.Frame_Point, text="POINT CHECK", text_color="#FFFFFF", font=customtkinter.CTkFont(family="Microsoft PhagsPa", size=20, weight="bold"), corner_radius=10).place(x=960, y=810)
        if self.PartNumber_R != "":
            for Point_Right in range(self.CouterPoint_Right):
                if Point_Right <= 4:
                    self.Point_Rigth_View.append(customtkinter.CTkLabel(master=self.Frame_Point, text=str(Point_Right + 1), text_color="#FFFFFF", font=customtkinter.CTkFont(family="Microsoft PhagsPa", size=35, weight="bold"), corner_radius=10, fg_color=(color[Point_Right]), width=170, height=50))
                    self.Point_Rigth_View[Point_Right].place(x=960 + (Point_Right * 190), y=850)
                elif Point_Right <= 9:
                    self.Point_Rigth_View.append(customtkinter.CTkLabel(master=self.Frame_Point, text=str(Point_Right + 1), text_color="#FFFFFF", font=customtkinter.CTkFont(family="Microsoft PhagsPa", size=35, weight="bold"), corner_radius=10, fg_color=(color[Point_Right]), width=170, height=50))
                    self.Point_Rigth_View[Point_Right].place(x=960 + ((Point_Right - 5) * 190), y=930)
                elif Point_Right <= 15:
                    self.Point_Rigth_View.append(customtkinter.CTkLabel(master=self.Frame_Point, text=str(Point_Right + 1), text_color="#FFFFFF", font=customtkinter.CTkFont(family="Microsoft PhagsPa", size=35, weight="bold"), corner_radius=10, fg_color=(color[Point_Right]), width=170, height=50))
                    self.Point_Rigth_View[Point_Right].place(x=960 + ((Point_Right - 10) * 190), y=1010)

    def View_Point_Single(self, color):
        self.Point_Single_View = []
        customtkinter.CTkLabel(master=self.Frame_Point, text="POINT CHECK", text_color="#FFFFFF", font=customtkinter.CTkFont(family="Microsoft PhagsPa", size=20, weight="bold"), corner_radius=10).place(x=450, y=810)
        if self.PartNumber_S != "":
            for Point_Single in range(self.CouterPoint_Single):
                if Point_Single <= 4:
                    self.Point_Single_View.append(customtkinter.CTkLabel(master=self.Frame_Point, text=str(Point_Single + 1), text_color="#FFFFFF", font=customtkinter.CTkFont(family="Microsoft PhagsPa", size=35, weight="bold"), corner_radius=10, fg_color=(color[Point_Single]), width=170, height=50))
                    self.Point_Single_View[Point_Single].place(x=450 + (Point_Single * 190), y=850)
                elif Point_Single <= 9:
                    self.Point_Single_View.append(customtkinter.CTkLabel(master=self.Frame_Point, text=str(Point_Single + 1), text_color="#FFFFFF", font=customtkinter.CTkFont(family="Microsoft PhagsPa", size=35, weight="bold"), corner_radius=10, fg_color=(color[Point_Single]), width=170, height=50))
                    self.Point_Single_View[Point_Single].place(x=450 + ((Point_Single - 5) * 190), y=930)
                elif Point_Single <= 15:
                    self.Point_Single_View.append(customtkinter.CTkLabel(master=self.Frame_Point, text=str(Point_Single + 1), text_color="#FFFFFF", font=customtkinter.CTkFont(family="Microsoft PhagsPa", size=35, weight="bold"), corner_radius=10, fg_color=(color[Point_Single]), width=170, height=50))
                    self.Point_Single_View[Point_Single].place(x=450 + ((Point_Single - 10) * 190), y=1010)

    def Point_Left_Config(self,color):
        for Point_Left in range(self.CouterPoint_Left):
            if Point_Left <= 4:
                self.Point_Left_View[Point_Left].configure(fg_color=(color[Point_Left]))
            elif Point_Left <= 9:
                self.Point_Left_View[Point_Left].configure(fg_color=(color[Point_Left]))
            elif Point_Left <= 15:
                self.Point_Left_View[Point_Left].configure(fg_color=(color[Point_Left]))
    def Point_Right_Config(self,color):
        for Point_Right in range(self.CouterPoint_Right):
            if Point_Right <= 4:
                self.Point_Rigth_View[Point_Right].configure(fg_color=(color[Point_Right]))
            elif Point_Right <= 9:
                self.Point_Rigth_View[Point_Right].configure(fg_color=(color[Point_Right]))
            elif Point_Right <= 15:
                self.Point_Rigth_View[Point_Right].configure(fg_color=(color[Point_Right]))
    def Point_Single_Config(self,color):
        for Point_Single in range(self.CouterPoint_Single):
            if Point_Single <= 4:
                self.Point_Single_View[Point_Single].configure(fg_color=(color[Point_Single]))
            elif Point_Single <= 9:
                self.Point_Single_View[Point_Single].configure(fg_color=(color[Point_Single]))
            elif Point_Single <= 15:
                self.Point_Single_View[Point_Single].configure(fg_color=(color[Point_Single]))



    def Processing(self):
        if self.data == "Snap01":  # Single
            #if not os.path.isfile("PrinterS.txt"):
                if self.CouterPoint_Single != 0:
                    self.Run_Single = True
                    Filename = "Current.bmp"
                    cv.imwrite(Filename, frame0.read()[1])
                    ImageSave, ColorView, Color_Save_Image, Result, Score, Color_Point, top_left, ImageModel = Main.Main(self.PartNumber_S, Filename, self.CouterPoint_Single, self.Point_Mode_S, self.Point_Left_S, self.Point_Top_S, self.Point_Right_S, self.Point_Bottom_S, self.Point_Score_S, self.Point_Color_S)
                    Save_Data.Save_Image_Model(self.PartNumber_S, Result, ImageModel)
                    if sum(Result) == self.CouterPoint_Single:
                        self.message = "OK"
                        self.Comfrim_single = 0
                        self.CouterOK_Single += 1
                        self.OK_S.configure(text="OK : " + str(self.CouterOK_Single))
                        packing_counter = Packing.Counter_Printer(self.PartNumber_S, self.Packing_S,"S")
                        self.Packing_S_Show.configure(text=str(packing_counter) + "/" + str(self.Packing_S))
                    else:
                        self.message = "NG"
                        self.Comfrim_single += 1
                        if self.Comfrim_single >= 4:
                            self.CouterNG_Single = self.CouterNG_Single + 1
                            self.NG_S.configure(text="NG : " + str(self.CouterNG_Single))

                    image = Main.ViewImage_Snap(Filename, self.CouterPoint_Single, self.Point_Left_S, self.Point_Top_S, self.Point_Right_S, self.Point_Bottom_S,self.Point_Score_S, Score, ColorView, top_left, self.new_scaling_float)
                    Save_Data.Save_Image(self.PartNumber_S, self.CouterPoint_Single, ImageSave, self.Point_Mode_S, self.Point_Left_S, self.Point_Top_S, self.Point_Right_S, self.Point_Bottom_S, Color_Save_Image, Score, self.Point_Score_S, Result, top_left)
                    Save_Data.Save_Score(self.PartNumber_S, self.BatchNumber_S, self.MachineName, self.CouterPoint_Single, Score, Result)
                    self.ImageReal_Single.imgtk = image
                    self.ImageReal_Single.configure(image=image)
                    Point_Single_Config(Color_Point)
                    #self.View_Point_Single(Color_Point)
                    #os.system('cls')
                    #Delete_Data.Delete_Image()
                elif self.CouterPoint_Single == 0:
                    self.message = "NG"

        elif self.data == "Snap02":  # Right
            #if not os.path.isfile("PrinterR.txt"):
                if self.CouterPoint_Right != 0:
                    self.Run_Right = True
                    Filename = "Current.bmp"
                    cv.imwrite(Filename, frame1.read()[1])
                    ImageSave, ColorView, Color_Save_Image, Result, Score, Color_Point, top_left, ImageModel = Main.Main(self.PartNumber_R, Filename, self.CouterPoint_Right, self.Point_Mode_R, self.Point_Left_R, self.Point_Top_R, self.Point_Right_R, self.Point_Bottom_R, self.Point_Score_R, self.Point_Color_R, self.Model_R)
                    Save_Data.Save_Image_Model(self.PartNumber_R, Result, ImageModel)
                    if sum(Result) == self.CouterPoint_Right:
                        self.message = "OK"
                        self.Comfrim_rigth = 0
                        self.CouterOK_Right = self.CouterOK_Right + 1
                        self.OK_R.configure(text="OK : " + str(self.CouterOK_Right))
                        packing_counter = Packing.Counter_Printer(self.PartNumber_R, self.Packing_R,"R")
                        self.Packing_R_Show.configure(text=str(packing_counter) + "/" + str(self.Packing_R))
                    else:
                        self.message = "NG"
                        self.Comfrim_rigth += 1
                        if self.Comfrim_rigth >= 4:
                            self.CouterNG_Right = self.CouterNG_Right + 1
                            self.NG_R.configure(text="NG : " + str(self.CouterNG_Right))
                    image = Main.ViewImage_Snap(Filename, self.CouterPoint_Right, self.Point_Left_R, self.Point_Top_R, self.Point_Right_R, self.Point_Bottom_R, self.Point_Score_R, Score, ColorView, top_left, self.new_scaling_float)
                    Save_Data.Save_Image(self.PartNumber_R, self.CouterPoint_Right, ImageSave, self.Point_Mode_R, self.Point_Left_R, self.Point_Top_R, self.Point_Right_R, self.Point_Bottom_R, Color_Save_Image, Score, self.Point_Score_R, Result, top_left)
                    Save_Data.Save_Score(self.PartNumber_R, self.BatchNumber_R, self.MachineName, self.CouterPoint_Right, Score, Result)
                    self.ImageReal_Right.imgtk = image
                    self.ImageReal_Right.configure(image=image)
                    self.Point_Right_Config(Color_Point)
                    #self.View_Point_Right(Color_Point)
                    #os.system('cls')
                    #Delete_Data.Delete_Image()
                elif self.CouterPoint_Right == 0:
                    self.message = "NG"
            #else:
                #self.message = "NG"

        elif self.data == "Snap03":  # Left
            #if not os.path.isfile("PrinterL.txt"):
                if self.CouterPoint_Left != 0:
                    self.Run_Left = True
                    Filename = "Current.bmp"
                    cv.imwrite(Filename, frame0.read()[1])
                    ImageSave, ColorView, Color_Save_Image, Result, Score, Color_Point, top_left,ImageModel = Main.Main(self.PartNumber_L, Filename, self.CouterPoint_Left, self.Point_Mode_L, self.Point_Left_L, self.Point_Top_L, self.Point_Right_L, self.Point_Bottom_L, self.Point_Score_L, self.Point_Color_L,self.Model_L)
                    Save_Data.Save_Image_Model(self.PartNumber_L, Result, ImageModel)
                    if sum(Result) == self.CouterPoint_Right:
                        self.message = "OK"
                        self.Comfrim_left = 0
                        self.CouterOK_Left = self.CouterOK_Left + 1
                        self.OK_L.configure(text="OK : " + str(self.CouterOK_Left))
                        packing_counter = Packing.Counter_Printer(self.PartNumber_L, self.Packing_L,"L")
                        self.Packing_L_Show.configure(text=str(packing_counter) + "/" + str(self.Packing_L))
                    else:
                        self.message = "NG"
                        self.Comfrim_left += 1
                        if self.Comfrim_left >= 4:
                            self.CouterNG_Left = self.CouterNG_Left + 1
                            self.NG_L.configure(text="NG : " + str(self.CouterNG_Left))
                    image = Main.ViewImage_Snap(Filename, self.CouterPoint_Left, self.Point_Left_L, self.Point_Top_L, self.Point_Right_L, self.Point_Bottom_L, self.Point_Score_L, Score, ColorView, top_left, self.new_scaling_float)
                    Save_Data.Save_Image(self.PartNumber_L, self.CouterPoint_Left, ImageSave, self.Point_Mode_L, self.Point_Left_L, self.Point_Top_L, self.Point_Right_L, self.Point_Bottom_L, Color_Save_Image, Score, self.Point_Score_L, Result, top_left)
                    Save_Data.Save_Score(self.PartNumber_L, self.BatchNumber_L, self.MachineName, self.CouterPoint_Left, Score, Result)
                    self.ImageReal_Left.imgtk = image
                    self.ImageReal_Left.configure(image=image)
                    self.Point_Left_Config(Color_Point)
                    #self.View_Point_Left(Color_Point)
                    #os.system('cls')
                    #Delete_Data.Delete_Image()

                elif self.CouterPoint_Left == 0:
                    self.message = "NG"
            #else:
                #self.message = "NG"

    def server_program(self):
        self.data = self.conn.recv(128).decode()
        if self.data == "Vision":
            if self.API[0] == "Connected":
                # print(self.API[1])
                if len(self.API[1]) == 1:
                    if self.API[1][0] == "Right" and self.CouterPoint_Right != 0:
                        self.message = "Ready"
                    elif self.API[1][0] == "Left" and self.CouterPoint_Left != 0:
                        self.message = "Ready"
                    elif self.API[1][0] == "Single" and self.CouterPoint_Single != 0:
                        self.message = "Ready"
                    else:
                        self.message = "Setup"
                elif len(self.API[1]) == 2 and (self.CouterPoint_Right != 0 and self.CouterPoint_Left != 0):
                    self.message = "Ready"
                else:
                    self.message = "Setup"
            else:
                self.message = "Setup"
        elif self.data == "PartNumber":
            self.message = self.PartNumber
        elif self.data == "Snap01":  # Single
            self.Processing()
        elif self.data == "Snap02":  # Left
            self.Processing()
        elif self.data == "Snap03":  # Right
            self.Processing()
        self.Keepdata = self.data
        self.conn.send(self.message.encode())
        self.message = ""

    def on_enter(self, event):
        self.image_logo.configure(image=self.Image_logo.ExitImage)

    def on_leave(self, enter):
        self.image_logo.configure(image=self.Image_logo.BKFImage)

    def Destory(self):
        response = messagebox.askquestion("Close Programe", "Are you sure?", icon='warning')
        if response == "yes":
            if Quantity_Cam == 1:
                frame0.release()
            elif Quantity_Cam == 2:
                frame0.release()
                frame1.release()
            cv.destroyAllWindows()
            app.destroy()
            os.system('TASKKILL /F /IM MachineVisionInspectionS11.exe')
            #subprocess.call([r'TerminatedProcess.bat'])

    def Camera(self):
        self.Camera_1 = cv.cvtColor(frame0.read()[1], cv.COLOR_BGR2RGB)
        self.Camera_2 = cv.cvtColor(frame1.read()[1], cv.COLOR_BGR2RGB)
        if len(self.API[1]) == 2:
            if self.Run_Left == False:
                Camera_1 = Image.fromarray(self.Camera_1)
                Resize_1 = Camera_1.resize((self.height_camera, self.weight_camera))
                Commit_1 = ImageTk.PhotoImage(image=Resize_1)
                self.ImageReal_Left.imgtk = Commit_1
                self.ImageReal_Left.configure(image=Commit_1)
            if self.Run_Right == False:
                Camera_2 = Image.fromarray(self.Camera_2)
                Resize_2 = Camera_2.resize((self.height_camera, self.weight_camera))
                Commit_2 = ImageTk.PhotoImage(image=Resize_2)
                self.ImageReal_Right.imgtk = Commit_2
                self.ImageReal_Right.configure(image=Commit_2)
        if len(self.API[1]) == 1:
            if self.API[1][0] == "Single":
                if self.Run_Single == False:
                    Camera_1 = Image.fromarray(self.Camera_1)
                    Resize_1 = Camera_1.resize((self.height_camera, self.weight_camera))
                    Commit_1 = ImageTk.PhotoImage(image=Resize_1)
                    self.ImageReal_Single.imgtk = Commit_1
                    self.ImageReal_Single.configure(image=Commit_1)
            elif self.API[1][0] == "Right":
                if self.Run_Right == False:
                    Camera_2 = Image.fromarray(self.Camera_2)
                    Resize_2 = Camera_2.resize((self.height_camera, self.weight_camera))
                    Commit_2 = ImageTk.PhotoImage(image=Resize_2)
                    self.ImageReal_Right.imgtk = Commit_2
                    self.ImageReal_Right.configure(image=Commit_2)
            elif self.API[1][0] == "Left":
                if self.Run_Left == False:
                    Camera_1 = Image.fromarray(self.Camera_1)
                    Resize_1 = Camera_1.resize((self.height_camera, self.weight_camera))
                    Commit_1 = ImageTk.PhotoImage(image=Resize_1)
                    self.ImageReal_Left.imgtk = Commit_1
                    self.ImageReal_Left.configure(image=Commit_1)
        self.after(60, self.Camera)

    def AddMaster(self):
        customtkinter.CTkButton(master=self, text="Add-master", text_color="#00B400", hover_color="#B4F0B4", font=customtkinter.CTkFont(family="Microsoft PhagsPa", size=40, weight="bold"), corner_radius=10, fg_color=("#353535"), command=self.SaveMasterNewWindow).place(x=1300, y=10)

    def TCP(self):
        customtkinter.CTkLabel(master=self, text="Read : ", text_color="#00B400", font=customtkinter.CTkFont(family="Microsoft PhagsPa", size=25, weight="bold")).place(x=580, y=30)
        customtkinter.CTkLabel(master=self, text="TCP", text_color="#FFFFFF", font=customtkinter.CTkFont(family="Microsoft PhagsPa", size=25, weight="bold"), corner_radius=10, fg_color=("#00B400")).place(x=660, y=30)
        customtkinter.CTkLabel(master=self, text="Write : ", text_color="#00B400", font=customtkinter.CTkFont(family="Microsoft PhagsPa", size=25, weight="bold")).place(x=850, y=30)
        customtkinter.CTkLabel(master=self, text="TCP", text_color="#FFFFFF", font=customtkinter.CTkFont(family="Microsoft PhagsPa", size=25, weight="bold"), corner_radius=10, fg_color=("#00B400")).place(x=940, y=30)

    def Close_SaveMasterNewWindow(self):
        self.Login.destroy()
        self.Login = None

    def SaveMasterNewWindow(self):
        if not self.Login:
            self.Login = Toplevel(self)
            self.Login.protocol("WM_DELETE_WINDOW", self.Close_SaveMasterNewWindow)
            self.Login.title("Login")
            self.Login.wm_attributes("-topmost", 0)
            self.Login.configure(background='#232323')
            self.Login.geometry('220x140')
            self.Login.grab_set()
            self.Password = tk.StringVar()
            self.Password.trace("w", lambda *args: character_limit())

            def character_limit():
                try:
                    if len(self.Password.get()) > 0:
                        self.Password.set(self.Password.get()[6])
                except:
                    pass

            self.Error_passWord = customtkinter.CTkLabel(self.Login, text="", font=customtkinter.CTkFont(family="Microsoft PhagsPa", size=10, weight="bold"), text_color="red")
            self.Error_passWord.place(x=10, y=0)
            customtkinter.CTkEntry(self.Login, width=200, height=50, corner_radius=10, placeholder_text="Password", font=customtkinter.CTkFont(family="Microsoft PhagsPa", size=40, weight="bold"), show='*', textvariable=self.Password).place(x=10, y=20)

            def Loginform():
                with open('Information\Operator.json', 'r') as json_Part:
                    json_object = json.loads(json_Part.read())
                    id_Emp = []
                    for d in json_object:
                        id_Emp.append(d['id_Emp'])
                for i in range(len(id_Emp)):
                    if id_Emp[i] == self.Password.get():
                        return True
                self.Error_passWord.configure(text='Wrong password did not match')
                return False

        def Search():
            if Loginform():
                self.Login.destroy()
                self.Login = None
                # self.Login.protocol("WM_DELETE_WINDOW", self.Close_SaveMasterNewWindow)
                SaveMaster = Toplevel(self)
                SaveMaster.title("Save Master")
                SaveMaster.configure(background='#232323')
                SaveMaster.geometry('330x470')
                SaveMaster.grab_set()
                Score_Data_Area = tk.StringVar()
                Score_Data_Area.trace("w", lambda *args: score_limit(Score_Data_Area))
                Score_Data_Outline = tk.StringVar()
                Score_Data_Outline.trace("w", lambda *args: score_limit(Score_Data_Outline))

                def Save_Master():
                    Point = Point_value.get()
                    Emp_ID = self.Password.get()
                    Score = Score_value.get()
                    Mode = Mode_value.get()
                    if str.isdigit(Score) and int(Score) >= 500:
                        if Side.get() == 0:
                            Partnumber = self.PartNumber_S
                            Imagesave = Image.fromarray(self.Camera_1)
                        elif Side.get() == 1:
                            Partnumber = self.PartNumber_R
                            Imagesave = Image.fromarray(self.Camera_2)
                        elif Side.get() == 2:
                            Partnumber = self.PartNumber_L
                            Imagesave = Image.fromarray(self.Camera_1)
                        Imagesave.save("Current.bmp")
                        Create = Partnumber + '/Master'
                        if not os.path.exists(Create):
                            os.makedirs(Create)
                        else:
                            print("")
                        refPt = []
                        cropping = False

                        def click_and_crop(event, x, y, flags, param):
                            global refPt, cropping
                            image = clone.copy()

                            if event == cv.EVENT_LBUTTONDOWN:
                                refPt = [(x, y)]
                                # print(refPt)
                                cropping = True
                            elif event == cv.EVENT_LBUTTONUP:
                                refPt.append((x, y))
                                # print(refPt)
                                cropping = False
                                cv.rectangle(image, refPt[0], refPt[1], (85, 255, 51), 2)
                                cv.imshow(Point, image)
                                if len(refPt) == 2:
                                    roi = clone[refPt[0][1]:refPt[1][1], refPt[0][0]:refPt[1][0]]
                                    x = cv.cvtColor(roi, cv.COLOR_BGR2RGB)
                                    Left = refPt[0][0]
                                    Top = refPt[0][1]
                                    Right = refPt[1][0]
                                    Bottom = refPt[1][1]
                                    img = Image.fromarray(x)
                                    Showtext = cv.putText(image, Point, (10, 25),
                                                          cv.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                                    cv.imshow(Point, Showtext)
                                    img.save('' + Create + '/' + Point + '_Template.bmp')
                                    cv.imwrite('' + Create + '/' + Point + '_Master.bmp', image)
                                    if Left and Top and Right and Bottom != 0:
                                        Save_Data.Master(Left, Top, Right, Bottom, Score, Point, Emp_ID, Mode, Partnumber)

                        path = r'Current.bmp'
                        image = cv.imread(path)
                        clone = image.copy()
                        cv.namedWindow(Point)
                        cv.setMouseCallback(Point, click_and_crop)
                        cv.imshow(Point, image)
                    else:
                        messagebox.showwarning("Score", "Minumun Score 500")

                customtkinter.CTkLabel(SaveMaster, text="Point:", text_color="#00B400", font=customtkinter.CTkFont(family="Microsoft PhagsPa", size=25, weight="bold")).place(x=5, y=26)
                Point_value = customtkinter.StringVar()
                Point_value.set("Point1")
                Point = customtkinter.CTkComboBox(SaveMaster, variable=Point_value, values=['Point1', 'Point2', 'Point3', 'Point4', 'Point5', 'Point6', 'Point7', 'Point8', 'Point9', 'Point10', 'Point11', 'Point12', 'Point13', 'Point14', 'Point15'],
                                                  corner_radius=10, border_color="#C5C5C5", text_color="#00B400", border_width=5, width=200, height=50, font=customtkinter.CTkFont(family="Microsoft PhagsPa", size=25, weight="bold"), button_hover_color="#B4F0B4", button_color="#C5C5C5",
                                                  dropdown_hover_color="#B4F0B4", dropdown_text_color="#00B400", dropdown_font=("Microsoft PhagsPa", 20)).place(x=120, y=20)

                customtkinter.CTkLabel(SaveMaster, text="Mode:", text_color="#00B400", font=customtkinter.CTkFont(family="Microsoft PhagsPa", size=25, weight="bold")).place(x=5, y=102)
                Mode_value = customtkinter.StringVar()
                Mode_value.set("Shape")
                Mode = customtkinter.CTkComboBox(SaveMaster, variable=Mode_value, values=['Shape', 'Color'],
                                                 corner_radius=10, border_color="#C5C5C5", text_color="#00B400", border_width=5, width=200, height=50, font=customtkinter.CTkFont(family="Microsoft PhagsPa", size=25, weight="bold"), button_hover_color="#B4F0B4", button_color="#C5C5C5",
                                                 dropdown_hover_color="#B4F0B4", dropdown_text_color="#00B400", dropdown_font=("Microsoft PhagsPa", 20)).place(x=120, y=100)

                customtkinter.CTkLabel(SaveMaster, text="Side:", text_color="#00B400", font=customtkinter.CTkFont(family="Microsoft PhagsPa", size=25, weight="bold")).place(x=5, y=182)
                # Side_value = customtkinter.StringVar()
                # Side = customtkinter.CTkComboBox(SaveMaster, variable=Side_value, values=['Left', 'Right'],
                # corner_radius=10, border_color="#C5C5C5", text_color="#00B400", border_width=5, width=200, height=50, font=customtkinter.CTkFont(family="Microsoft PhagsPa", size=25, weight="bold"), button_hover_color="#B4F0B4", button_color="#C5C5C5",
                # dropdown_hover_color="#B4F0B4", dropdown_text_color="#00B400", dropdown_font=("Microsoft PhagsPa", 20)).place(x=120, y=180)

                if self.API[1][0] == "Single":
                    Side = tkinter.IntVar(value=0)
                    Side_Single = customtkinter.CTkRadioButton(SaveMaster, variable=Side, value=0, text="Single", font=customtkinter.CTkFont(family="Microsoft PhagsPa", size=30, weight="bold"), text_color="#00B400")
                    Side_Single.place(x=120, y=180)
                else:
                    Side = tkinter.IntVar(value=1)
                    Side_Left = customtkinter.CTkRadioButton(SaveMaster, variable=Side, value=2, text="Left ", font=customtkinter.CTkFont(family="Microsoft PhagsPa", size=30, weight="bold"), text_color="#00B400")
                    Side_Left.place(x=120, y=180)
                    Side_Right = customtkinter.CTkRadioButton(SaveMaster, variable=Side, value=1, text="Right", font=customtkinter.CTkFont(family="Microsoft PhagsPa", size=30, weight="bold"), text_color="#00B400")
                    Side_Right.place(x=120, y=220)

                customtkinter.CTkLabel(SaveMaster, text="Score:", text_color="#00B400", font=customtkinter.CTkFont(family="Microsoft PhagsPa", size=25, weight="bold")).place(x=5, y=290)
                Score_value = customtkinter.StringVar()
                Score_value.set("800")
                customtkinter.CTkEntry(SaveMaster, width=200, height=50, placeholder_text="Score", font=customtkinter.CTkFont(family="Microsoft PhagsPa", size=30, weight="bold"), textvariable=Score_value, text_color="#00B400").place(x=120, y=285)
                Save = customtkinter.CTkButton(SaveMaster, text="Save", text_color="#00B400", hover_color="#B4F0B4", font=customtkinter.CTkFont(family="Microsoft PhagsPa", size=60, weight="bold"), corner_radius=10, fg_color=("#353535"), command=Save_Master).place(x=90, y=350)

                def score_limit(*args):
                    s = Score_value.get()
                    if str.isdigit(s):
                        if len(s) > 3:
                            Score_value.set(s[:3])
                    else:
                        Score_value.set(s[:0])

                Score_value.trace("w", score_limit)
                SaveMaster.mainloop()

        customtkinter.CTkButton(self.Login, text="Login", text_color="#00B400", hover_color="#B4F0B4", font=customtkinter.CTkFont(family="Microsoft PhagsPa", size=30, weight="bold"), corner_radius=10, fg_color=("#353535"), command=Search).place(x=40, y=90)
        self.Login.deiconify()

app = App()
app.mainloop()
