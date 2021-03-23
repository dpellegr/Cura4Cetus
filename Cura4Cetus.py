# Copyright (c) 2018-2021 Dario Pellegrini < pellegrini.dario@gmail.com >
# The PostProcessingPlugin is released under the terms of the AGPLv3 or higher.
from ..Script import Script
import re

CETUS_SIZE = 180.0

class Cura4Cetus(Script):
    def __init__(self):
        super().__init__()

    def getSettingDataString(self):
        return """{
            "name":"Cura4Cetus",
            "key": "Cura4Cetus",
            "metadata": {},
            "version": 2,
            "settings":
            {
                "Z":
                {
                    "label": "Z axis height",
                    "description": "The heigth of the Z axis. Tune this value carefully within UpStudio with the bed levelling procedure, then copy it back here.",
                    "unit": "mm",
                    "type": "float",
                    "default_value": 266
                },
                "E":
                {
                    "label": "Extrusion flow",
                    "description": "Calibrate the rotation of the extruder motor to obtain the proper flow. Higher values compensate for underextrusion.",
                    "type": "float",
                    "default_value": 240
                },
                "YX":
                {
                    "label": "Rotate X and Y",
                    "description": "Cetus considers the bed rail as the X axis and the head rail as the Y axis. This is the opposite of what you may expect when slicing in Cura. Enable this setting to rotate the axes.",
                    "type": "bool",
                    "default_value": true
                },
                "Sound":
                {
                    "label": "Sound",
                    "description": "Play beeps when starting and ending the print job.",
                    "type": "bool",
                    "default_value": true
                },
                "Purge":
                {   
                    "label": "Purge line",
                    "description": "Prints a purge line at the beginning of the print job. Automatic will print a 5 cm line next to the part if space is available. Manual allows specifying the start and end point.",
                    "type": "enum",
                    "options": {"auto":"Automatic","manual":"Manual","disabled":"Disabled"},
                    "default_value": "auto"
                },
                "PurgeE":
                {
                    "label": "   Extrude",
                    "description": "Degrees of the extruder rotation for the purge line",
                    "type": "float",
                    "unit": "Deg",
                    "default_value": 180,
                    "enabled": "Purge != 'disabled'"
                },
                "PurgeStartX":
                {
                    "label": "   Start X",
                    "description": "Starting X coordinate of the purge line",
                    "type": "float",
                    "unit": "mm",
                    "default_value": 3,
                    "enabled": "Purge == 'manual'"
                },
                "PurgeStartY":
                {
                    "label": "   Start Y",
                    "description": "Starting Y coordinate of the purge line",
                    "type": "float",
                    "unit": "mm",
                    "default_value": 3,
                    "enabled": "Purge == 'manual'"
                },
                "PurgeEndX":
                {
                    "label": "   End X",
                    "description": "Ending X coordinate of the purge line",
                    "type": "float",
                    "unit": "mm",
                    "default_value": 53,
                    "enabled": "Purge == 'manual'"
                },
                "PurgeEndY":
                {
                    "label": "   End Y",
                    "description": "Ending Y coordinate of the purge line",
                    "type": "float",
                    "unit": "mm",
                    "default_value": 3,
                    "enabled": "Purge == 'manual'"
                },
                "HeadPos":
                {
                    "label": "Final head position",
                    "description": "Where to place the head once the print is over. Raise will raise the head 1 cm above the part. Raise and corner will also move the head to the top left corner. Top will raise the head to the top of the z axis.",
                    "type": "enum",
                    "options": {"r":"Raise","rc":"Raise and corner","t":"Top and corner"},
                    "default_value": "rc"
                },
                "CutPower":
                {   
                    "label": "Power off when finished",
                    "description": "Cut the power to the motors when the print is finished. If final head position is set to raise, a two minutes delay will be added for nozzle cooling. If you raise the head to the top, make sure to install a hook, otherwise the head will slam into the bed.",
                    "type": "bool",
                    "default_value": false,
                    "enabled": "HeadPos != 'rc'"
                }
            }
        }"""

    def beep(self,ms):
        return \
"""M42 P4 S1 ; Beep ON
G4 P{} ; Pause for P ms
M42 P4 S0 ; Beep OFF
""".format(ms)

    def beeps(self,ms_on, ms_off, repeat):
        beeps_str = ""
        for i in range(repeat):
            beeps_str += self.beep(ms_on)
            if i != repeat-1 :
                beeps_str += "G4 P{} ; Pause for P ms\n".format(ms_off)
        return beeps_str

    def insert(self, data, index, containing, new, replace=False) :
         d = data[index].splitlines()
         done = False
         for i in range(len(d)):
             if containing in d[i]:
                 done = True
                 if replace :
                     d[i] = new
                 else :
                     d.insert(i+1, new)
                 break;
         if (not done):
              print("Cura4Cetus ERROR: string \"{}\" not found in data[{}], insert failed!!").format(containing,index)
         else:
             data[index] = '\n'.join(d)

    def transformYX(self,x,y):
        return CETUS_SIZE-y, x

    def minxy(self,data):
        x,y = CETUS_SIZE, CETUS_SIZE
        rex = re.compile(r"X[-+]?\d+\.?\d*")
        rey = re.compile(r"Y[-+]?\d+\.?\d*")
        for layer in data:
            for line in layer.splitlines():
                mx = rex.search(line)
                my = rey.search(line)
                if mx :
                    xi = float(mx.group()[1:])
                    if xi < x and xi > 0 :
                        x = xi
                if my :
                    yi = float(my.group()[1:])
                    if yi < y and yi > 0 :
                        y = yi
        return x,y

    def maxz(self,data):
        z = 0
        rez = re.compile(r"Z[-+]?\d+\.?\d*")
        for layer in data:
            for line in layer.splitlines():
                mz = rez.search(line)
                if mz :
                    zi = float(mz.group()[1:])
                    if zi > z :
                        z = zi
        return z

    def check_low_bound(self,x,y):
        return (x>0 and y>0)

    def check_up_bound(self,x,y):
        return (x<CETUS_SIZE and y<CETUS_SIZE)

    def makepurge(self,data):
        purge_str = ""
        if self.getSettingValueByKey("Purge") == "auto" :
            xi,yi = self.minxy(data)
            xi = min(xi, 130)
            yi -= 5
            xf = xi+50
            yf = yi
            E = self.getSettingValueByKey("PurgeE")
        if self.getSettingValueByKey("Purge") == "manual" :
            xi = self.getSettingValueByKey("PurgeStartX")
            yi = self.getSettingValueByKey("PurgeStartY")
            xf = self.getSettingValueByKey("PurgeEndX")
            yf = self.getSettingValueByKey("PurgeEndY")
            E = self.getSettingValueByKey("PurgeE")
        if not(self.check_low_bound(xi,yi) and self.check_up_bound(xf,yf)) :
            print("Cura4Cetus WARNING: purge line doesn't fit, skipping")
            purge_str = "; Skipped purge line outside boundaries ({},{}) ({},{})\n".format(xi,yi,xf,yf)
        else:
            if self.getSettingValueByKey("Purge") != "disabled" :
                purge_str += \
"""; BEGIN Purge Line
G1 X{} Y{} F5000     ; move to front left corner
G1 Z0.3 F1000        ; get nozzle close to bed
G92 E0               ; zero the extruded length
G1 X{} Y{} E{} F500  ; extrude a 5cm purge line
G92 E0               ; zero the extruded length
G1 E-45 F5000        ; retract a little
G1 Z5                ; head up a bit
G1 E-10              ; reverse retraction
; END Purge Line
""".format(xi,yi,xf,yf,E)
        return purge_str

    def header(self,data):
        header_title = "; === Cura4Cetus HEADER ===\n"
        Z = self.getSettingValueByKey("Z")
        E = self.getSettingValueByKey("E")
        Sound = self.getSettingValueByKey("Sound")
        ## Before Heating: axes calibration and positioning
        self.insert(data, 1, ";Generated", \
"""; === Cura4Cetus HEADER ===
M80                  ; ATX Power On
M206 Z-{}           ; Customized for the actual value
M206 X-180           ; offset X axis so the coordinates are 0..180, normally they are -180..0
M204 P800            ; set acceleration
""".format(Z) + (self.beep(300) if Sound else "") + \
""";G0 Z{} F5000         ; bring the head up to the top, to unclip the hook
G0 Z25                ; bring the head down before heating, to reduce oozing
""".format(Z))
        ## after heating: sound, print purge, calibrate extrusion rate
        self.insert(data, 1, "G92 ", (self.beeps(200,400,2) if Sound else "") + self.makepurge(data) + \
"""M92 E{}     ; adjust extruder flow rate
; === Cura4Cetus END of HEADER ===
""".format(E))
        return data

    def footer(self,data):
        Sound   = self.getSettingValueByKey("Sound")
        HeadPos = self.getSettingValueByKey("HeadPos")
        Z       = self.getSettingValueByKey("Z")
        Zpart   = min(Z, self.maxz(data)+10);
        footer_str = \
"""
; === Cura4Cetus FOOTER ===
G92 E0   ; zero the extruded length
G1 Z{} E-50  ; retract a bit to avoid clogging
M109     ; switch off extruder
M191     ; switch off heated bed
""".format(Zpart)
        if HeadPos == 't':
            footer_str += "G1 Z{} F5000 ; Raise the head to the top\n".format(Z)
        if HeadPos != 'r':
            footer_str += "G1 X0 Y0 ; Move the head to the corner\n"
        if Sound:
            footer_str += self.beeps(100,300,3)
        if HeadPos != 'rc' and self.getSettingValueByKey("CutPower") :
            if HeadPos == 'r': 
                footer_str += "G4 P120000 ; Pause for 2 min to allow for nozzle cooling\n"
            footer_str += "M81    ; ATX Power Off\n"
        footer_str += "M2   ; end of program\n; === Cura4Cetus END of Footer ===\n"
        data[-1] = footer_str
        return data

    def execute(self, data):
        ## Fix header
        data = self.header(data)
        
        ## Rotate coordinates
        if self.getSettingValueByKey("YX"):
            rex = re.compile(r"X[-+]?\d+\.?\d*")
            rey = re.compile(r"Y[-+]?\d+\.?\d*")
            for j in range(len(data)):
                layer = data[j].splitlines()
                for i in range(len(layer)):
                    mx = rex.search(layer[i])
                    my = rey.search(layer[i])
                    if ( mx and my ):
                        x = float(mx.group()[1:])
                        y = float(my.group()[1:])
                        x,y = self.transformYX(x,y)
                        layer[i] = rex.sub("X{}".format(x), layer[i])
                        layer[i] = rey.sub("Y{}".format(y), layer[i])
                data[j] = "\n".join(layer)
        
        ## Fix footer
        data = self.footer(data)

        return data
