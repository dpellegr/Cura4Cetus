# Cura4Cetus

### Cura + Cetus = 🤕
### Cura + Cetus + Cura4Cetus = 😊

Cura4Cetus is intended to ease and improve the usability of the Tiertime Cetus3D printer with the Ultimaker Cura slicer. Experienced makers might prefer the latter to the original Tiertime UpStudio software due to its extra fine control of the slicing process. 

Cura4Cetus operates as a post processing script modifying the G-code produced by Cura. By doing so it introduces some of the functionalities implemented in UpStudio (such as beeping and purge line) and more. A GUI allows selecting them with just a click and carries online documentation.

## Screenshot
![Screenshot](https://raw.githubusercontent.com/dpellegr/Cura4Cetus/master/Screenshot.png)

## Features
* Centralised G-code manipulation, no need for custom G-code sections.
* Dialog windows adds the following entries:
  * Setting the Z axis length.
  * Calibration of the extrusion flow.
  * Rotation of the X and Y axis to a more intuitive positioning.
  * Reproducing sounds at the start of the job, when the hotend heating completes, and at the end of the job.
  * Printing of a purge line.
  * Controlling the position of the head after the print.
  * Possibility to switch off the motors.

## Installation
Download the script `Cura4Cetus.py` to the folder `YOUR_CURA_INSTALL_PATH/cura/plugins/PostProcessingPlugins/scripts/` (please find the full path according to your platform).

If you attempted to load some Start/End G-code before finding this script, make sure to remove it from `preferences -> printers -> Machine Settings`.

## Usage
Click on `Extensions > Post processing > Modify G-Code` then select Cetus4Cura from `Add a script`. Hovering your mouse over the various field will bring up their descriptions allowing for easy configuration.

## Notes
 * In order to produce G-code that succesfully prints on the Cetus, you still have to implement printer profiles for the various nozzles and layer thicknesses that you intend to use. I may try to collect a few in a database, contributions are welcomed.
 * An installation of UpStudio will still be required to send the G-code to the printer.


## Enjoy!
