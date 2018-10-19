# Copyright (c) 2018 Dario Pellegrini
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
                    "description": "The heigth of the Z axis.",
                    "unit": "mm",
                    "type": "float",
                    "default_value": 266
                },
                "E":
                {
                    "label": "Extrusion flow",
                    "description": "Calibrate the extrusion movement to obtain the proper flow. Increase to correct for underextrusion.",
                    "type": "float",
                    "default_value": 180
                },
                "YX":
                {
                    "label": "Rotate X and Y",
                    "description": "Cetus considers the plate movement as the X axis and the head movement as the Y axis. When enable the axis are rotated in order reproduce the UpStudio behaviour.",
                    "type": "bool",
                    "default_value": true
                },
                "Sound":
                {
                    "label": "Sound",
                    "description": "Play sounds when starting and ending the print job.",
                    "type": "bool",
                    "default_value": true
                },
                "Purge":
                {   
                    "label": "Purge line",
                    "description": "Prints a purge line at the beginning of the print job",
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
                    "default_value": 360,
                    "enabled": "Purge == 'manual'"
                },
                "PurgeStartX":
                {
                    "label": "   Start X",
                    "description": "Starting X coordinate of the purge line",
                    "type": "float",
                    "unit": "mm",
                    "default_value": 5,
                    "enabled": "Purge == 'manual'"
                },
                "PurgeStartY":
                {
                    "label": "   Start Y",
                    "description": "Starting Y coordinate of the purge line",
                    "type": "float",
                    "unit": "mm",
                    "default_value": 5,
                    "enabled": "Purge == 'manual'"
                },
                "PurgeEndX":
                {
                    "label": "   End X",
                    "description": "Ending X coordinate of the purge line",
                    "type": "float",
                    "unit": "mm",
                    "default_value": 55,
                    "enabled": "Purge == 'manual'"
                },
                "PurgeEndY":
                {
                    "label": "   End Y",
                    "description": "Ending Y coordinate of the purge line",
                    "type": "float",
                    "unit": "mm",
                    "default_value": 5,
                    "enabled": "Purge == 'manual'"
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
         print("Cura4Cetus INSERT", new)
         for i in range(len(d)):
             print("Cura4Cetus ", i, d[i])
             if containing in d[i]:
                 print ("Cura4Cetus REPLACING here")
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
                    if xi < x :
                        x = xi
                if my :
                    yi = float(my.group()[1:])
                    if yi < y :
                        y = yi
        return x,y

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
            E = 360
        if self.getSettingValueByKey("Purge") == "manual" :
            xi = self.getSettingValueByKey("PurgeStartX")
            yi = self.getSettingValueByKey("PurgeStartY")
            xf = self.getSettingValueByKey("PurgeEndX")
            yf = self.getSettingValueByKey("PurgeEndY")
            E = self.getSettingValueByKey("PurgeE")
        if not(self.check_low_bound(xi,yi) and self.check_up_bound(xf,yf)) :
            print("Cura4Cetus WARNING: purge line doesn't fit, skipping")
            purge_str = "; Purge line outside boundaries: skipped\n"
        else:
            if self.getSettingValueByKey("Purge") != "disabled" :
                purge_str += \
"""; BEGIN Purge Line
G1 X{} Y{} F5000     ; move to front left corner
G1 Z0.2 F1000        ; get nozzle close to bed
G92 E0               ; zero the extruded length
G1 X{} Y{} E{} F500  ; extrude a 5cm purge line
G92 E0               ; zero the extruded length
G1 E-12.5 Z10 F2700  ; retract a little
; END Purge Line
""".format(xi,yi,xf,yf,E)
        return purge_str

    def header(self,data):
        Z = self.getSettingValueByKey("Z")
        E = self.getSettingValueByKey("E")
        Sound = self.getSettingValueByKey("Sound")
        ## add beep before heating
        if Sound :
            self.insert(data, 1, ";Generated ", self.beep(300))
        ## create the new header string
        header_str = "; === Cura4Cetus HEADER ===\n"
        if Sound :
            header_str += self.beep(300)
        header_str += \
"""M206 Z-{}            ; Customized for the actual value
M206 X-180           ; offset X axis so the coordinates are 0..180, normally they are -180..0
M204 P800            ; set acceleration
""".format(Z) + self.makepurge(data) + \
"""M92 E{}              ; calibrate extrusion rate
; === Cura4Cetus END of HEADER ===
""".format(E)
        ## now fixing it
        self.insert(data, 1, "G1 ", header_str, replace=True)
        return data

    def footer(self,data):
        Z = self.getSettingValueByKey("Z")
        Sound = self.getSettingValueByKey("Sound")
        footer_str = \
"""
; === Cura4Cetus FOOTER ===
G92 E0   ; zero the extruded length
G1 E-30  ; retract a bit to avoid clogging
M109     ; switch off extruder
M191     ; switch off heated bed
G1 Z{} F5500   ; Safe place
G1 X3.0 Y3.0 ; Safe place
""".format(Z)
        if Sound :
            footer_str += self.beeps(100,300,3)
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
