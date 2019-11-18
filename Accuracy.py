

## =======================SETTING UP PARAMETERS=================================== ##

# Import necessary modules
from __future__ import division
import arcpy

#Allow output file to overwrite any existing file of the same name
arcpy.env.overwriteOutput = True

#Inputs (shapefiles of the automatically and manually derived inventories)
automatic = arcpy.GetParameter(0)
manual = arcpy.GetParameter(1)
arcpy.env.workspace = arcpy.GetParameter(2)

#Outputs (shapefiles created in process to determine accuracy)
intersect = "Intersection.shp"
merge = "Merge.shp"
dissolve = "Dissolve.shp"
spatialjoin = "Spatial_Join.shp"

#Sets spatial reference to that of the input shapefile.
dsc = arcpy.Describe(manual)
coord_sys = dsc.spatialReference


## ==========================ACCURACY ASSESMENT=================================== ##

#Intersect the Manual and Automatic Inventory Shapefiles
arcpy.Intersect_analysis(in_features=[automatic, manual],
                         out_feature_class=intersect,
                         join_attributes="ALL",
                         output_type="INPUT")

#Determine Area of Intersection (Create an 'Area Field')
arcpy.AddField_management (intersect, "Area_Int", "DOUBLE", "", "", "", "NULLABLE", "")
geometryField = arcpy.Describe(intersect).shapeFieldName 
cursor = arcpy.UpdateCursor(intersect)
for row in cursor:
    AreaValue = row.getValue(geometryField).area 
    row.setValue("Area_Int",AreaValue) 
    cursor.updateRow(row)
del row, cursor

#Merge the Manual Inventory and Automatic Inventory Shapefiles
arcpy.Merge_management(inputs=[automatic,manual],
                       output= merge)

#Dissolve the Merged Shapefile.
arcpy.Dissolve_management(in_features=merge,
                          out_feature_class= dissolve,
                          dissolve_field="",
                          statistics_fields="",
                          multi_part="SINGLE_PART",
                          unsplit_lines="UNSPLIT_LINES")

#Determine the Area of the Union (Create an 'Area Field')
arcpy.AddField_management (dissolve, "Area_Diss", "DOUBLE", "", "", "", "NULLABLE", "")
geometryField = arcpy.Describe(dissolve).shapeFieldName 
cursor = arcpy.UpdateCursor(dissolve)
for row in cursor:
    AreaValue = row.getValue(geometryField).area 
    row.setValue("Area_Diss",AreaValue) 
    cursor.updateRow(row)
del row, cursor #Clean up cursor objects



#Create a spatial join of the intersection and the dissolve.

fieldmappings = arcpy.FieldMappings()
fieldnamestosum = ["Area_Int"]
fieldmappings.addTable(dissolve)
fieldmappings.addTable(intersect)

keepers = ["Area_Diss", "Area_Int"]
for field in fieldmappings.fields:
    if field.name not in keepers:
        fieldmappings.removeFieldMap(fieldmappings.findFieldMapIndex(field.name))

for fieldName in fieldnamestosum:  
  
    
    fieldIndex = fieldmappings.findFieldMapIndex(fieldName)      
    fieldMap = fieldmappings.getFieldMap(fieldIndex)
    fieldMap.mergeRule = 'Sum'   
    fieldmappings.replaceFieldMap(fieldIndex, fieldMap)  

       
arcpy.SpatialJoin_analysis(target_features=dissolve,
                           join_features=intersect,
                           out_feature_class=spatialjoin,
                           join_operation="JOIN_ONE_TO_ONE",
                           join_type="KEEP_ALL",
                           field_mapping = fieldmappings,
                           match_option="CONTAINS",
                           )

#Create a new column in the spatially joined file.
arcpy.AddField_management (spatialjoin, "IoU", "DOUBLE", "", "", "", "NULLABLE", "")

#Calulate the IoU value. 
arcpy.CalculateField_management(in_table=spatialjoin,
                                field="IoU",
                                expression="[Area_Int] / [Area_Diss]",
                                expression_type="VB",
                                code_block="")

#Count how many landslides are above threshold IoU VALYE. 

fields = "IoU"
count = 0
with arcpy.da.SearchCursor(spatialjoin, fields) as cursor:
    for row in cursor:
        if row[0] > .20:
            count += 1

#Count True Positives       
TP = count
#Count how many landslides in Manual Inventory 
NL_MM = int(arcpy.GetCount_management(manual).getOutput(0))
#Count how many landslides are in Automatic Inventory. 
NL_AM = int(arcpy.GetCount_management(automatic).getOutput(0))
#Determine False Negatives(TP-NL_MM). 
FN = NL_MM - TP
#Determine False Positives.(TP-NL_AM). 
FP = NL_AM - TP
#Determine Recall. (TP/(TP+FN)*100)
Recall = (TP/(TP+FN))*100
#Determine Precision. (TP/(TP+FP)*100)
Precision = (TP/(TP+FP))*100

# Sum the area of manual inventory landslides. 
summed_total = 0
with arcpy.da.SearchCursor(manual, "Shape_Area") as cursor:
    for row in cursor:
        summed_total = summed_total + row[0]
        
Area_M = summed_total

# Sum the area of automatic inventory landslides. 
summed_total_A = 0
with arcpy.da.SearchCursor(automatic, "Shape_Area") as cursor:
    for row in cursor:
        summed_total_A = summed_total_A + row[0]
        
Area_A = summed_total_A


#Sum the area of true positves by summing areas in auto mapping above threholds.
field1 = "IoU"
field2 = "Area_Int"
summed_total2 = 0
with arcpy.da.SearchCursor(spatialjoin, [field1, field2]) as cursor:
    for row in cursor:
        if row[0] > .30:
            summed_total2 = summed_total2 + row[1]
        

Area_TP = summed_total2


#False Negatives. (Area_FN = Area_M - Area_TP)
Area_FN = Area_M - Area_TP
#False Positives. (Area_FP = Area_A - Area_TP)
Area_FP = Area_A - Area_TP
#Recall. (Area_TP/Area_TP + Area_FN)
Area_Recall = (Area_TP/(Area_TP + Area_FN))*100
#Precision. (Area_TP/Area_TP + Area_FP)
Area_Precision = (Area_TP/(Area_TP + Area_FP))*100



## ================PRINTS ACCURACY VALUES TO RESULTS WINDOW ================ ##

print arcpy.AddMessage('====RECOGNITION ACCURACY====')
print arcpy.AddMessage('Recall: ')
print arcpy.AddMessage(Recall)
print arcpy.AddMessage('Precision: ')
print arcpy.AddMessage(Precision)


print arcpy.AddMessage('====EXTENT ACCURACY====')
print arcpy.AddMessage('Recall: ')
print arcpy.AddMessage(Area_Recall)
print arcpy.AddMessage('Precision: ')
print arcpy.AddMessage(Area_Precision)



## =============================================================================== ##




