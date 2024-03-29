# ls_eval
ArcGIS Toolbox/ArcPy Script

This toolbox runs an ArcPy script to assess the accuracy of automatically derived landslide inventories where reference landslide inventories are available.

# Description
This toolbox can be used to determine the accuracy of automatically derived inventories in regard to their recognition and extent. Accuracy metrics used are recall and precision. The tool performs a series of geoprocessing operations on two user provided shapefiles: (1) the automatically derived landslide inventory and (2) the reference landlside inventory. The Intersection Over Union (IoU) is determined for each individual landslide and those landslides above an apporpriate IoU threshold are counted as true positives. False positives and false negatives are then counted and used to caclulate recall and preicison.The outputs of the calculations are shown in the results window. 

# Installation

**Step 1: Connect to downloaded folder.**

![TEST](Step1.PNG)

![TEST](Step2.PNG)



**Step 2: Right click AccuracyAssesment script > properties > Source and set source to the location in which you saved the python script.**


![TEST](Step3.PNG)


**Step 3: Open AccuracyAssesment script and input data, run.**


![TEST](Step4.png)

