# Cura4Cetus
This cura post-processing script is intended to ease and improve the usability of the Cetus3D printer with Cura. By rearranging the GCode it introduces some functionalities implemented in UpStudio selectable with just a click.

## Screenshot
![Screenshot](https://raw.githubusercontent.com/dpellegr/Cura4Cetus/master/Screenshot.png)

## Features
* Centralised GCode manipulation, no need for custom begin and end GCode sections.
* Dialog windows to adjust several settings:
  * Z axis length setting.
  * Calibration of the extrusion flow.
  * Rotation of the X and Y axis to a more intuitive positioning.
  * Reproducing sounds at the start of the job, after the heating and at the end of the job.
  * Printing of a purge line.

## Installation
Download Cura4Cetus to the folder `/cura/plugins/PostProcessingPlugins/scripts/` (please find the full path according to your platform). You may want to remove the start and/or end GCode from the printer settings.

## Usage
Click on `Extensions > Post processing > Modify G-Code` then select Cetus4Cura from `Add a script` and configure it following the on screen documentation. Enjoy!

