# -*- coding: utf-8 -*-
"""
Version: ArcGIS Pro 2.2.4
Author: Anam Khan
Date: 5/1/19
Description: Intelligent Dasymetric Mapping (IDM) disaggregates population 
counts enumerated by vector source units to the spatial resolution of a 
categorical ancillary raster containing classes that are indicative of the 
spatial distribution of population within the source units. This script is 
an updated version of the original EnviroAtlas IDM toolbox developed by 
Torrin Hultgren for ArcMap: https://www.epa.gov/enviroatlas/dasymetric-toolbox.
This version follows the publication by Mennis and Hultgren (2006) with the
exception that class densities for unsampled ancillary classes are calculated
using census polygons where the population estimated for sampled/preset 
ancillary classes did not exceed the census population. Other changes include
combining all geoprocessing and calculations into one step and using pandas
data frames for calculations.
"""

"""
Information from the original toolbox
Source Name:   DasymetricToolbox.pyt
Version:       ArcGIS Pro / 10.3
Author:        Torrin Hultgren, GISP
Description:   This toolbox contains a number of scripts that assist 
               preparing vector population and raster ancillary datasets 
               for intelligent dasymetric mapping, performs the dasymetric 
               calculations, and then generates a floating point output 
               raster of revised population density.  Please see the 
               documentation on the individual tools for more information.
"""

import arcpy, os, sys, traceback, json
import numpy as np
import pandas as pd


# Helper function for displaying messages
def AddPrintMessage(msg, severity = 0):
    print(msg)
    if severity == 0: arcpy.AddMessage(msg)
    elif severity == 1: arcpy.AddWarning(msg)
    elif severity == 2: arcpy.AddError(msg)               

# Helper function for setting suffix according to input directory
def setSuffixes(inputPath):
    fcSuffix, tblSuffix, rastSuffix = '' , '', ''
    if arcpy.Describe(inputPath).workspaceType == 'FileSystem':
        fcSuffix, tblSuffix, rastSuffix = '.shp', '.dbf', '.tif'
    return fcSuffix, tblSuffix, rastSuffix
    
class Toolbox(object):
    def __init__(self):
        """Define the toolbox (the name of the toolbox is the name of the
        .pyt file)."""
        self.label = "Intelligent Dasymetric Mapping Toolbox"
        self.alias = "IDM"
        # List of tool classes associated with this toolbox
        self.tools = [DasymetricPopulationMapping]

# Tool implementation code

class DasymetricPopulationMapping(object):
    """
        METHOD:
        __init__(): Define tool name and class info
        getParameterInfo(): Define parameter definitions in tool
        isLicensed(): Set whether tool is licensed to execute
        updateParameters():Modify the values and properties of parameters
                           before internal validation is performed
        updateMessages(): Modify the messages created by internal validation
                          for each tool parameter.
        execute(): Runtime script for the tool
    """
    def __init__(self):
        self.label = u'Dasymetric Population Mapping'
        self.description = "This tool assists in preparing vector population \
        and raster ancillary datasets for intelligent dasymetric mapping, \
        performs the dasymetric calculations, and then generates a floating \
        point output raster of revised population density. The tool uses a \
        config.json file to set preset class densities for the following\
        land cover classes from the National Land Cover Database: Open Water,\
        Perennial Ice/Snow, and Emergent Herbaceous Wetlands."
        self.canRunInBackground = False

    def getParameterInfo(self):
        # Population_Features
        param_1 = arcpy.Parameter()
        param_1.name = u'Population_Features'
        param_1.displayName = u'Population Features'
        param_1.parameterType = 'Required'
        param_1.direction = 'Input'
        param_1.datatype = u'Feature Class'

        # Population_Count_Field
        param_2 = arcpy.Parameter()
        param_2.name = u'Population_Count_Field'
        param_2.displayName = u'Population Count Field'
        param_2.parameterType = 'Required'
        param_2.direction = 'Input'
        param_2.datatype = u'Field'
        param_2.parameterDependencies = [param_1.name]

        # Population_Key_Field
        param_3 = arcpy.Parameter()
        param_3.name = u'Population_Key_Field'
        param_3.displayName = u'Population Key Field'
        param_3.parameterType = 'Required'
        param_3.direction = 'Input'
        param_3.datatype = u'Field'
        param_3.filter.list = ["OID", "Short", "Long", "Text", "Double"]
        param_3.parameterDependencies = [param_1.name]

        # Ancillary_Raster
        param_4 = arcpy.Parameter()
        param_4.name = u'Ancillary_Raster'
        param_4.displayName = u'Ancillary Raster'
        param_4.parameterType = 'Required'
        param_4.direction = 'Input'
        param_4.datatype = u'Raster Dataset'
        
        # Uninhabited_File
        param_5 = arcpy.Parameter()
        param_5.name = u'Uninhabited_File'
        param_5.displayName = u'Uninhabited File'
        param_5.parameterType = 'Optional'
        param_5.direction = 'Input'
        param_5.datatype = u'Feature Class'
   
        # Minimum_Sample
        param_6 = arcpy.Parameter()
        param_6.name = u'Minimum_Sample'
        param_6.displayName = u'Minimum Sample'
        param_6.parameterType = 'Required'
        param_6.direction = 'Input'
        param_6.datatype = u'Long'
        param_6.value = u'3'

        # Minimum_Sampling_Area
        param_7 = arcpy.Parameter()
        param_7.name = u'Minimum_Sampling_Area'
        param_7.displayName = u'Minimum Sampling Area'
        param_7.parameterType = 'Required'
        param_7.direction = 'Input'
        param_7.datatype = u'Long'
        param_7.value = u'1'

        # Percent
        param_8 = arcpy.Parameter()
        param_8.name = u'Percent'
        param_8.displayName = u'Percent'
        param_8.parameterType = 'Required'
        param_8.direction = 'Input'
        param_8.datatype = u'Double'
        param_8.value = u'0.95'

        # Output_Directory
        param_9 = arcpy.Parameter()
        param_9.name = u'Output_Directory'
        param_9.displayName = u'Output Directory'
        param_9.parameterType = 'Required'
        param_9.direction = 'Input'
        param_9.datatype = u'DEWorkspace'
        

        return [param_1, param_2, param_3, 
                param_4, param_5, param_6, 
                param_7, param_8, param_9]

    def isLicensed(self):
        """Allow the tool to execute, only if the Spatial Analyst extension 
        is available."""
        try:
            if arcpy.CheckExtension("spatial") != "Available":
                raise Exception
            if arcpy.CheckExtension("3D") != "Available":
                raise Exception
        except Exception:
            return False  # tool cannot be executed
        return True  # tool can be executed

    def updateParameters(self, parameters):
        validator = getattr(self, 'ToolValidator', None)
        if validator:
             return validator(parameters).updateParameters()

    def updateMessages(self, parameters):
        validator = getattr(self, 'ToolValidator', None)
        if validator:
             return validator(parameters).updateMessages()

    def execute(self, parameters, messages):
        try:
            AddPrintMessage("Beginning the population polygon to raster conversion...",0) 
            #Check out extensions
            arcpy.CheckOutExtension("3D")
            arcpy.CheckOutExtension("spatial")
            
            # Variables from parameters
            popFeatures = parameters[0].valueAsText  
            #The population polygon FeatureClass to be converted to a raster.
            popCountField = parameters[1].valueAsText 
            #The field in the population dataset that contains count data.
            popKeyField = parameters[2].valueAsText
            #The unique identifier field for population polygons (ex: OBJECTID) 
            ancRaster = parameters[3].valueAsText 
            #The ancillary raster dataset to be used to redistribute population.
            uninhab_user = parameters[4].valueAsText 
            #User provided uninhabited polygons
            sampleMin = parameters[5].valueAsText 
            #Minimum number of source units to ensure a representative sample 
            #- default = 3
            popAreaMin = parameters[6].valueAsText 
            #Minimum number of raster cells required for a source unit to be 
            #considered representative - default = 1
            percent = parameters[7].valueAsText 
            #Optional parameter - percent value for percent area method 
            #- default = 0.95
            out_dir = parameters[8].valueAsText 
            #The directory where all outputs from the tool will be saved
            
            #Set config.json file in the toolbox's directory to presetTable
            presetTable = os.path.join(sys.path[0], "config.json")
            
            AddPrintMessage('Populaton features path is ' + popFeatures)
            AddPrintMessage('Populaton count field is ' + popCountField)
            AddPrintMessage('Population key field is ' + popKeyField)
            AddPrintMessage('Ancillary raster path is ' + ancRaster)
            if uninhab_user:
                AddPrintMessage('Uninhabited features path is ' + uninhab_user)
            AddPrintMessage('The minimum sample size is ' + sampleMin)
            AddPrintMessage('The minimum populated area is ' + popAreaMin)
            AddPrintMessage('The percent is ' + percent)
            AddPrintMessage('The output directory is ' + out_dir)
            
            # Derived variables...
            #add the right extension according to directory type 
            #(regular directory vs. gdb)
            fcSuffix, tblSuffix, rastSuffix = setSuffixes(out_dir)
            popRaster = os.path.join(out_dir, "PopRaster" + rastSuffix)
            popWorkTable = os.path.join(out_dir, "PopTable" + tblSuffix)
            dasyRaster = os.path.join(out_dir, "DasyRaster" + rastSuffix)
            dasyWorkTable = os.path.join(out_dir, "DasyWorkTable" + tblSuffix)
            
            #Get ancillary raster details
            ancRastDesc = arcpy.Describe(ancRaster)
            outCoordSys = ancRastDesc.SpatialReference
            AddPrintMessage("The output coordinate system is: " 
                            + outCoordSys.Name ,0)
            outCellSize = ancRastDesc.MeanCellWidth
            AddPrintMessage("The output cell size is: " + str(outCellSize) ,0)
            
            '''
            Save current environment variables so they can be reset after 
            the process
            '''
            tempCoordSys = arcpy.env.outputCoordinateSystem
            tempExtent = arcpy.env.extent
            
            arcpy.env.outputCoordinateSystem = outCoordSys
            arcpy.env.extent = ancRastDesc.extent
            #arcpy.env.snapRaster = ancRaster
            
            # Process: Polygon to Raster...
            AddPrintMessage("Converting polygons to raster...",0)
            arcpy.PolygonToRaster_conversion(popFeatures, popKeyField, 
                                             popRaster, "CELL_CENTER", 
                                             "NONE", outCellSize)
        
            ##Build attribute table for popRaster
            AddPrintMessage("Conversion complete, calculating statistics and building attribute table...",0)
            arcpy.CalculateStatistics_management(popRaster,"1","1","#")
            arcpy.BuildRasterAttributeTable_management(popRaster, "Overwrite")
            
            '''
            Create table views for joining the census population counts to the 
            popRaster table view.
            '''
            popRasterTableView = arcpy.MakeTableView_management(
            popRaster, "popRasterView"
                    )
            popFeatureTableView = arcpy.MakeTableView_management(
                    popFeatures, "popFeatureView"
                    )
            arcpy.JoinField_management(
                    popRasterTableView, "Value", popFeatureTableView, 
                    popKeyField, popCountField
                    )
            '''
            Assign new name to popCountField incase the user provides a joined 
            census table
            '''
            popCountField = arcpy.ListFields(popRasterTableView)[-1].name

            #Process uninhabited polygons and update ancRaster
            if uninhab_user:
                AddPrintMessage("Removing uninhabited areas...",0)
                uninhabRaster = os.path.join(out_dir, "UninhabRaster" 
                                             + rastSuffix)
                uninhab_landcover = os.path.join(out_dir, "uninhab_landcover" 
                                                 + rastSuffix)
                uninhabFeatDesc = arcpy.Describe(uninhab_user)
                uninhabvalue = uninhabFeatDesc.OIDFieldName
                #Convert uninhabited polygons to raster
                arcpy.PolygonToRaster_conversion(uninhab_user, uninhabvalue, 
                                                 uninhabRaster, "CELL_CENTER", 
                                                 "NONE", outCellSize)            
                uninhab_reclass = arcpy.sa.IsNull(uninhabRaster) 
                uninhab_landcoverTemp = ancRaster * uninhab_reclass
                uninhab_landcoverTemp.save(uninhab_landcover)
                ancRaster = uninhab_landcover
                arcpy.Delete_management(uninhab_reclass)
                arcpy.Delete_management(uninhabRaster)
        
            # Return environment variables to previous values
            arcpy.env.outputCoordinateSystem = tempCoordSys
            arcpy.env.extent = tempExtent
            
            #Combine popRaster and ancRaster
            AddPrintMessage("Combining rasters...", 0)
            outCombine = arcpy.sa.Combine([popRaster,ancRaster])

            AddPrintMessage("Saving combined rasters...", 0)
            outCombine.save(dasyRaster)
            
            AddPrintMessage("Creating the standalone working tables",0)
            '''
            Get list of fields to include in population output table and import 
            popRasterTableView as a Pandas DataFrame.
            '''
            fields = ['Value', 'Count', popCountField]
            pop_df = pd.DataFrame(
                    arcpy.da.TableToNumPyArray(popRasterTableView, fields)
                    )
            '''
            Change the index for pop_df to polygon OID or "Value" from 
            polygon's raster
            '''
            pop_df.index = pop_df["Value"]
            
            #Import the dasymetric raster's attribute table as a DataFrame.
            dasy_df = pd.DataFrame(
                    arcpy.da.TableToNumPyArray(
                            dasyRaster, [
                                    field.name for field in arcpy.ListFields(dasyRaster)
                                    ]
                            )
                    )
            
            '''
            Clean up the in-memory views to avoid collisions if the tool is re-run.
            '''
            
            arcpy.Delete_management("popRasterView")
            arcpy.Delete_management("popFeatureView")
            
            arcpy.env.overwriteOutput = True
          
            #Derive ID fields from dasy_df to use later in dasymetric calculations.
            popIDField = dasy_df.columns[-2] 
            # Should always be the second-to-last field
            ancCatName = dasy_df.columns[-1] 
            # Should always be the last field
                
            #Set more varialbles for dasymetric calculations
            dasyAreaField = 'Count' 
            #The name of the field in dasy_df containing raster cell count
           
            AddPrintMessage("Collecting unique ancillary categories...",0)
            #all ancillary categories in study area
            inAncCatList = list(np.unique(dasy_df[ancCatName]).astype(int))
            
            '''
            This list will be populated with ancillary categories that are not 
            sampled and do not have preset class densities.
            '''
            unSampledList = []
            
            #Preset class densities from config.json file
            presetData = json.load(open(presetTable))
            
            '''
            Uninhabited classes: ancially classes where people can't live. 
            Classes with a preset class density of 0
            '''
            unInhabList = [
                    int(presetCat) for presetCat,presetVal 
                    in presetData.items() if float(presetVal) == 0]

            #Ancillary classes where people can live
            InhabList = [cat for cat in inAncCatList if cat not in unInhabList]
            
            '''
            Join the census population counts to the dasymetric DataFrame and 
            calculate population density for the polygon. 
            '''
            AddPrintMessage("Calculating populated area...",0)
            
            '''
            Join population counts to dasy_df and rename field in dasy_df to 
            "POP_COUNT"
            '''
            dasy_df = dasy_df.join(
                    pop_df[popCountField], on = popIDField).rename(
                            columns = {popCountField: "POP_COUNT"}
                            )
            
            '''
            Group the dasymetric units that are associated with inhabitable 
            classes by the census polygon ID and take the sum of the dasymetric 
            area in each group. Rename the column as "POP_AREA".
            #POP_AREA = sum(pixels) for inhabitable classes
            '''
            popAreaSum = dasy_df[
                    dasy_df[ancCatName].isin(InhabList)
                    ].groupby(popIDField)[dasyAreaField].sum().rename("POP_AREA")

            '''
            Transfer "POP_AREA" from popAreaSum to the dasymetric DataFrame 
            and the population DataFrame.
            '''
            dasy_df["POP_AREA"] = dasy_df.join(popAreaSum, 
                   on = popIDField)["POP_AREA"]
            pop_df = pop_df.join(popAreaSum).fillna(0) 
            
            '''
            Calculate population density for census polygons where poulated 
            area is greater than 0 
            '''
            AddPrintMessage("Calculating population density...", 0) 
            pop_densMask = pop_df["POP_AREA"] > 0
            pop_df.loc[pop_densMask, "POP_DENS"] = pop_df.loc[
                    pop_densMask, popCountField
                    ] / pop_df.loc[
                            pop_densMask, "POP_AREA"
                            ]
            #replace NaN with 0
            pop_df = pop_df.fillna(0)
            
            '''
            Calculate representative population density for ancillary classes 
            that have enough representative samples in the study area.
            '''
            AddPrintMessage("Selecting representative source units...",0) 
            '''
            Create column in the population DataFrame for storing the ancillary 
            class that a polygon is representative of
            '''
            pop_df["REP_CAT"] = 0
            
            for inAncCat in InhabList:
                repUnits_mask = (
                        dasy_df["POP_AREA"] > float(popAreaMin)
                        ) & (
                                dasy_df[ancCatName] == inAncCat
                                )
                repUnits = dasy_df.loc[
                        repUnits_mask, [
                                dasyAreaField, popIDField, ancCatName, "POP_AREA"
                                ]
                        ]
                repUnits["PERCENT"] = repUnits[dasyAreaField] / repUnits["POP_AREA"]                
                repUnits = list(
                        repUnits[repUnits["PERCENT"] >= float(percent)][popIDField]
                        )
                
                if len(repUnits) >= float(sampleMin):
                    pop_df.loc[pop_df["Value"].isin(repUnits), "REP_CAT"] = inAncCat
                    AddPrintMessage("Class " 
                                    + str(inAncCat) 
                                    + " was sufficiently sampled with " 
                                    + str(len(repUnits)) 
                                    + " representative source units.",0)

                elif str(inAncCat) not in list(presetData):
                    unSampledList.append(int(inAncCat))
                    AddPrintMessage("Class " 
                                    + str(inAncCat) 
                                    + " was not sufficiently sampled with only " 
                                    + str(len(repUnits)) 
                                    + " representative source units.",0)
            
            #Calculate statistics and make sampling summary table
            AddPrintMessage("Calculating representative population density for selected classes...",0)
            
            '''
            Create a mask for rows in the dasymetric DataFrame where \
            REP_CAT =! 0. We only want to create summaries for these \
            dasymetric rows because they are associated with representative \
            polygons.
            '''
            rep_mask = pop_df["REP_CAT"] != 0
            
            '''
            Calculate sum of census population counts and sum of populated 
            area for each sampled ancillary class
            '''
            classDens_df = pop_df[rep_mask].groupby("REP_CAT")[
                    [popCountField, 'POP_AREA']
                    ].sum().rename(
                    columns = {popCountField: "SUM_" + popCountField, 
                               "POP_AREA": "SUM_POP_AREA"}
                    )
            
            #Calculate sample density for sampled classes
            classDens_df["SAMPLEDENS"] = classDens_df[
                    "SUM_" + popCountField
                    ] / classDens_df[
                            "SUM_POP_AREA"
                            ]
            classDens_df["METHOD"] = "Sampled"
            classDens_df["CLASSDENS"] = classDens_df["SAMPLEDENS"]

            #Add preset densities to summary table
            if presetTable:
                AddPrintMessage("Adding preset values to the summary table...", 0)
                for preset_cat in list(presetData):
                    classDens_df.loc[int(preset_cat), "CLASSDENS"] = presetData[preset_cat]
                    classDens_df.loc[int(preset_cat), "METHOD"] = 'Preset'
                        
            # For all sampled and preset classes, calculate a population estimate.
            AddPrintMessage("Calculating first population estimate for \
                            sampled and preset classes...", 0)            
            #Get representative population densities from class density DataFrame.
            dasy_df = dasy_df.join(classDens_df['CLASSDENS'], 
                                   on = ancCatName).fillna(0)
            '''
            Set mask for dasy_df that will limit ancillary categories to \
            those in the class density DataFrame.
            '''
            popEst_mask = dasy_df[ancCatName].isin(classDens_df.index)

            dasy_df["POP_EST"] = 0
            dasy_df.loc[popEst_mask, "POP_EST"] = dasy_df.loc[
                    popEst_mask, dasyAreaField
                    ] * dasy_df.loc[
                            popEst_mask, 'CLASSDENS'
                            ]
            
            # Intelligent areal weighting for unsampled classes 
            AddPrintMessage("Performing intelligent areal weighting for unsampled classes...",0)
            if unSampledList:
                '''
                Calculate representative population densities for unsampled 
                ancillary classes using IAW    
                '''
                '''
                Create a mask that limits dasy_df to dasymetric units 
                associated with unsampled ancillary classes.
                '''
                unsampled_mask = dasy_df[ancCatName].isin(unSampledList) 
                '''
                #Populate remainining area of each dasymetric unit as the area 
                of dasymetric units associated with unsampled classes and 
                0 everywhere else.
                '''
                dasy_df["REM_AREA"] = 0
                dasy_df.loc[unsampled_mask, "REM_AREA"] = dasy_df.loc[
                        unsampled_mask, dasyAreaField
                        ]
                
                '''
                For each polygon, sum the remaining area and sum the population 
                that has already been estimated for sampled/preset classes.
                '''
                popEstSum = dasy_df.groupby(popIDField)[
                        ["POP_EST", "REM_AREA"]
                        ].sum()
                '''
                Join popEstSum to dasy_df to transfer the sum of population 
                estimates and the sum of remaining area to the 
                dasymetric DataFrame.
                '''
                dasy_df = dasy_df.join(popEstSum["POP_EST"], 
                                       on = popIDField, rsuffix = "poly")
                dasy_df = dasy_df.join(popEstSum["REM_AREA"], 
                                       on = popIDField, rsuffix = "poly")
                
                '''
                Calcualte a population difference between the census population 
                and the population estimated for sampled/preset ancillary classes.
                '''
                dasy_df["POP_DIFF"] = dasy_df["POP_COUNT"] - dasy_df["POP_ESTpoly"]
                
                '''
                Calculate an initial population estimate for dasymetric units 
                associated with unsampled ancillary classes and polygons where 
                the sampled/preset population estimates did not exceed the 
                census population. Also, remove dasymetric units associated 
                with polygons where the entire populated area is covered by 
                sampled/preset ancillary classes.
                Update - set clip(0) for POP_DIFF i.e., Eq. 3
                '''
                #Set mask
                diff_mask = (
                        (dasy_df[ancCatName].isin(unSampledList)) &
                        (dasy_df['REM_AREApoly'] != 0)
                        )
                                        
                dasy_df.loc[diff_mask, "POP_EST"] = (
                    dasy_df.loc[diff_mask, "POP_DIFF"].clip(0) *
                    dasy_df.loc[diff_mask, "REM_AREA"] /
                    dasy_df.loc[diff_mask, "REM_AREApoly"])
                
                '''
                Sum total initial population estimates and remaining area for 
                dasymetric units used to calculate initial population estimates 
                for unsampled ancillary classes.
                '''
                ancCat_sum = dasy_df[diff_mask].groupby(ancCatName)[
                        ["POP_EST" , "REM_AREA"]
                        ].sum()
                
                '''
                Calculate the representative population density for unsampled 
                classes using ancCat_sum and update the class density DataFrame.
                '''
                for cat in ancCat_sum.index:
                    #CLASSDENS = Sum of initial population estimates/ Sum of remaining area
                    classDens_df.loc[cat, "CLASSDENS"] = ancCat_sum.loc[
                            cat, "POP_EST"
                            ] / ancCat_sum.loc[
                                    cat, "REM_AREA"
                                    ]
                    classDens_df.loc[cat, "METHOD"] = "IAW"
                
                '''
                Add representative population densities for unsampled classes 
                in the dasymetric DataFrame.
                '''
                dasy_df.loc[unsampled_mask, 'CLASSDENS'] = dasy_df.loc[
                        unsampled_mask
                        ].join(
                        classDens_df.loc[ancCat_sum.index, 'CLASSDENS'], 
                        on = ancCatName, 
                        rsuffix = "_classDens")['CLASSDENS_classDens']
                '''
                Calculate new population estimates using representative 
                population densities for unsampled classes.
                POP_EST = dasymetric area * class density
                '''
                dasy_df.loc[unsampled_mask, "POP_EST"] = dasy_df.loc[
                        unsampled_mask, dasyAreaField
                        ] * dasy_df.loc[
                                unsampled_mask, 'CLASSDENS'
                                ]    
            # End of intelligent areal weighting
             
            # Perform final calculations to ensure pycnophylactic integrity
            AddPrintMessage("Performing final calculations to ensure pycnophylactic integrity...",0)
            '''
            For each dasymetric unit, use the ratio of the estimated population 
            to the total population estimated for the polygon associated with 
            the dasymetric unit to redistribute the census population.
            '''

            '''
	    if the sum of population densities within the source unit is equal to 0
	    set the POP_EST for those to 1 (i.e., area weighting (Eq. 5))
	    '''
            idx = (dasy_df
		    .groupby(popIDField)
                    .filter(
                    lambda s: s['POP_EST'].sum() == 0 and
                    s['POP_COUNT'].sum() > 0
		    ).index
                )

            dasy_df.loc[idx, 'POP_EST'] = 1
			
            #Sum population estimates by polygon.
            popEstsum = dasy_df.groupby(popIDField)["POP_EST"].sum()
            
            '''
            Calculate total fraction and redistribute census population to 
            calculate new population and new density.
            '''
            dasy_df["TOTALFRACT"] = dasy_df["POP_EST"] / dasy_df.join(popEstsum, 
                   on = popIDField, 
                   rsuffix = "SUM")["POP_ESTSUM"]
            dasy_df["NEW_POP"] = dasy_df["TOTALFRACT"] * dasy_df["POP_COUNT"]
            dasy_df["NEWDENSITY"] = dasy_df["NEW_POP"] / dasy_df[dasyAreaField]

            #export dasy_df
            #Fill NA
            dasy_df = dasy_df.fillna(0)
            #Get the OID field from the raster
            oid = arcpy.Describe(dasyRaster).OIDFieldName
            arcpy.da.NumPyArrayToTable(
                    dasy_df.drop(columns = oid).to_records(index = False), 
                    dasyWorkTable
                    )
             
            #export pop_df
            arcpy.da.NumPyArrayToTable(
                    pop_df.fillna(0).to_records(index = False), popWorkTable
                    )
            
            #export classDens_df to sampling summary table
            temp_samp = os.path.join(out_dir,"temp_samp.csv")
            classDens_df.fillna(0).reset_index().to_csv(temp_samp, 
                               header = True, index = False)
            arcpy.TableToTable_conversion(temp_samp, out_dir, 
                                          "SamplingSummaryTable" + tblSuffix)
            os.remove(temp_samp)

            #Create final population density raster.
            AddPrintMessage("Creating population density raster...",0)
            densRaster = os.path.join(out_dir, 'DensityRaster' + rastSuffix)
            #Make raster layer and join fields from dasymetric table
            arcpy.MakeRasterLayer_management(dasyRaster, "DRL")
            arcpy.AddJoin_management("DRL", "Value", dasyWorkTable, "Value", "KEEP_COMMON") 
            
            #Can't use lookup on joined field so make a temp raster
            dasyoutrast = os.path.join(out_dir, 'temp_dens' + rastSuffix)
            joinedRaster = arcpy.CopyRaster_management("DRL", dasyoutrast)
            
            arcpy.Lookup_3d(joinedRaster, 'NEWDENSITY', densRaster)
            
            #Delete temporary rasters
            arcpy.Delete_management("DRL")
            arcpy.Delete_management(dasyoutrast)
            
            '''
            Get NoData value from the dasymetric raster to set as NoData value 
            for the density array that gets created below.
            '''
            '''
            dasy_nd = arcpy.Raster(dasyRaster).noDataValue
            dasy_arr = arcpy.RasterToNumPyArray(dasyRaster)
            
            dasy_lut = dasy_df[['Value', 'NEWDENSITY']].set_index('Value')
            #Fill in NoData value for the NoData value from dasy_arr
            dasy_lut.loc[dasy_nd, 'NEWDENSITY'] = dasy_nd 
            dens_df = pd.DataFrame(np.ravel(dasy_arr)).join(dasy_lut, on = 0)
            dens_ar = np.array(
                    dens_df['NEWDENSITY']
                    ).reshape(
                            (dasy_arr.shape[0], dasy_arr.shape[1])
                            )
            
            #Write array to population density raster.
            densRaster = os.path.join(out_dir, 'DensityRaster' + rastSuffix)
            #Get lower left corner coordinates of ancillary raster
            llc = arcpy.Point(ancRastDesc.extent.XMin, ancRastDesc.extent.YMin)
            dens_rast = arcpy.NumPyArrayToRaster(
                    dens_ar, llc, outCellSize, 
                    outCellSize, value_to_nodata = dasy_nd
                    )
            dens_rast.save(densRaster)
            arcpy.DefineProjection_management(densRaster, outCoordSys)
            '''   
            #Check in extensions
            arcpy.CheckInExtension("3D")
            arcpy.CheckInExtension("spatial")
            
        # Geoprocessing Errors will be caught here
        except Exception as e:
            print (e.message)
            messages.AddErrorMessage(e.message)
        
        # other errors caught here
        except:
            # Cycle through Geoprocessing tool specific errors
            for msg in range(0, arcpy.GetMessageCount()):
                if arcpy.GetSeverity(msg) == 2:
                    arcpy.AddReturnMessage(msg)
                    
            # Return Python specific errors
            tb = sys.exc_info()[2]
            tbinfo = traceback.format_tb(tb)[0]
            pymsg = "PYTHON ERRORS:\nTraceback Info:\n" + tbinfo + "\nError Info:\n    " + \
                    str(sys.exc_type)+ ": " + str(sys.exc_value) + "\n"
            AddPrintMessage(pymsg, 2)
