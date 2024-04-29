# Intelligent Dasymetric Toolbox for ArcGIS Pro

[<img src="https://enviroatlas.epa.gov/enviroatlas/interactivemap/images/logo.png"     title="EnviroAtlas" width=400 >](https://www.epa.gov/enviroatlas)


Following the methods described in [Baynes, J., Neale, A., & Hultgren, T. (2022)](https://doi.org/10.5194/essd-14-2833-2022), EPA developed the Intelligent Dasymetric Mapping (IDM) [toolbox](https://github.com/USEPA/Dasymetric-Toolbox-ArcGISPro/tree/master) for ArcGIS Pro and a corresponding [toolbox](https://github.com/USEPA/Dasymetric-Toolbox-OpenSource) that uses open source GIS packages. 

## Overview

 
The US Census Bureau aggregates population counts into various units (e.g., blocks, block groups, tracts) that are bounded by both visible features such as roads and streams, as well as invisible boundaries such as county or state limits. While this aggregation is practical for the purposes of the Census, it is difficult to determine how many individuals within a census block live near roads, in floodplains, or other potential risk exposures using these boundaries. This is particularly true in sparsely populated areas with large census blocks.

Dasymetric mapping is a geospatial technique that uses information such as land cover to distribute population counts within selected boundaries like census blocks. EPA researchers use dasymetric population data to calculate the distribution of ecosystem services, model viewsheds, estimate resource use, and measure exposure potential.


<figure>
  <img src="https://www.epa.gov/sites/default/files/2015-07/dasymetric_728x210.jpg" alt="Dasymetric example image"/>
  <figcaption><sup>The image on the left shows a map of the population by block group based solely on the census data. The image on the right shows the dasymetric population allocation for several block groups in Tampa, Fla.</sup></figcaption>  
</figure>
<br>

IDM uses a representative population density for each ancillary class (e.g., land cover type) to distribute population counts from source units (e.g., census blocks). The representative population density of an ancillary class is the number of people per grid cell that are expected to reside in the ancillary class throughout the study area. IDM uses three methods to determine the representative population density of an ancillary class. 
1. Preset density - A preset density is a representative population density for an ancillary class that is determined by the user and provided in a configuration file. Any class and density value can be set using this method, but it is commonly used to identify uninhabited ancillary classes (e.g., open water as 0). 
2. Sampling - A sampled density is a representative population density for an ancillary class that is determined by collecting representative source units of the ancillary class. A representative source unit for an ancillary class is a source unit that is 1) of sufficient size 2) sufficiently composed of the ancillary class (i.e., homogenous). Finally, there must be 3) a sufficient number of representative source units for an ancillary class to be sampled. These three parameters are adjustable by the user in the IDM toolbox.   
3. Intelligent Areal Weighting - Representative population densities that are not preset or sampled are determined using intelligent areal weighting (IAW). 

Finally, to ensure that the population estimated for a source unit is equal to the original population count of the source unit, a distribution ratio is applied.

_**NOTE:** Source units that are too small or irregularly shaped to be represented in a raster matching the resolution of the ancillary raster are **ignored** by the IDM toolbox. For the EnviroAtlas dasymetric model, population counts in these blocks were identified and merged into neighboring blocks as a preprocessing step._

_**NOTE:** Simple area weighting is used for population counts within a source unit made up entirely of ancillary classes with representative population densities estimated at or preset to zero._

For more information on the dasymetric data created for EnviroAtlas, see our [website](https://www.epa.gov/enviroatlas/dasymetric-toolbox), [factsheet](https://enviroatlas.epa.gov/enviroatlas/DataFactSheets/pdf/Supplemental/DasymetricAllocationofPopulation.pdf), or [journal article](https://doi.org/10.5194/essd-14-2833-2022).

## Requirements
The IDM Toolbox was developed for ArcGIS Pro 2.2.4. It has been tested on versions up to 3.2

The Spatial Analyst or 3D Analyst extensions are required. 

Use of the IDM toolbox may require increasing the maximum number of unique values the 'Combine Tool' can produce.

You can increase this number by changing a setting in  ArcGIS Pro. On the  **Project**  tab, select  **Options**  and select the  **Raster and Imagery**  choice. In the dialog box, select the  **Raster Dataset**  choice and enter an appropriate value for the  **Maximum number of unique values to display**.  
[https://pro.arcgis.com/en/pro-app/tool-reference/spatial-analyst/combine.htm](https://pro.arcgis.com/en/pro-app/tool-reference/spatial-analyst/combine.htm)

## Installation
The IDM Toolbox for ArcGIS Pro can be added to a new or existing ArcGIS Pro project.

[https://pro.arcgis.com/en/pro-app/help/analysis/geoprocessing/basics/use-a-custom-geoprocessing-tool.htm](https://pro.arcgis.com/en/pro-app/help/analysis/geoprocessing/basics/use-a-custom-geoprocessing-tool.htm)

## Usage

### Preset Densities
The user can set a population density for any ancillary class using their own domain knowledge by modifying the **'config.json'** file in the toolbox's root directory. Any class and density value can be provided using this method, but it is commonly used to identify uninhabited ancillary classes (e.g., open water as 0). 

The preset densities for the following ancillary classes from the National Land Cover Database (NLCD) are set to 0 people per pixel:

* 11, Open Water
* 12, Perennial Ice/Snow
* 95, Emergent Herbaceous Wetlands

The config.json file is a data dictionary with ancillary raster value as the key (string data type) and preset density as the value (float / integer data type). 

For example: 

{
"11":0,
"12":0,
"95":0,
"0":0
}


### Tool parameters
|Parameter|  Description| Data Type
|--|--|--|
|Population Features|  The source units with population counts and a unique identifier to be converted to a raster. Common source units are census polygons.| Feature Class |
|Population Count Field | The field in Population Features that stores the population counts.| Field|
|Population Key Field|The field in the Population Features that stores the **unique** identifier for the source unit. | Field <br><br><ul><li>ObjectID</li><li>Short integer</li><li>Long integer</li><li>Text</li><li>Double</li></ul>|
|Ancillary Raster | The ancillary raster is a categorical raster dataset with classes that will be used to redistribute population. Land-use or land-cover are frequently used ancillary datasets, but any dataset that has classes of relatively homogenous population density could be used here. <br><br>_**NOTE:** The cell size and spatial reference from the ancillary raster are used for all output rasters from this tool._ | Raster Dataset |
|Uninhabited File (optional) | An optional feature class containing polygons where no population is expected to reside. The ancillary raster values that overlay the areas within the provided feature class are reclassified as an uninhabited ancillary class (i.e., class "0") and the representative population density for this class is preset to 0 people per pixel.| Feature Class|
|Minimum Sample | This is the minimum number of representative source units required for an ancillary class to be considered sampled. A source unit is considered representative of an ancillary class if the ancillary class makes up a certain percent of the source unit’s populated area. Any class that is not preset or sufficiently sampled will be assigned a density using the IAW method. <br><br>**The default is 3**. | Long |
|Minimum Sampling Area | The minimum size of a representative source unit (in number of ancillary raster cells). Any source unit with a populated area smaller than this parameter will not be considered a representative source unit. Increasing this number may eliminate small areas that might be outliers that could skew the class average. <br><br>**The default is 1**.| Long |
|Percent | A source unit is considered representative of an ancillary class if the ancillary class makes up a certain percent of the source unit’s populated area. This parameter is the minimum percent area of a source unit that a single ancillary class must cover for that source unit to be a representative source unit. This value is in decimal notation. <br><br>**The default is 0.95**.| Double |
|Output Directory | The directory where all outputs from the tool will be saved. <br><br> _**NOTE:** Must be a folder location, geodatabases are not supported with this tool._ | Workspace


### Outputs

|Filename | Description |
|--|--|
|**DensityRaster.tif** | **The final population density raster for the study area.**|
|DasyRaster.tif | The dasymetric raster represents the spatial intersection of the population source units and the ancillary raster. Each value represents a unique combination of source unit and ancillary raster. These are also known as 'target units'.|
|PopRaster.tif | The population features provided by the user are converted to a raster using the population key field as the values of the raster.|
|uninhab_landcover.tif| If the user provides an optional uninhabited file, this raster will be provided in the output directory. This is a copy of the ancillary raster where areas covered by the uninhabited areas are classified as an uninhabited ancillary class (i.e., class 0).|
|PopTable.dbf | The population working table consists of the following information for each source unit in the population features <br><br><ul><li>Value - The unique identifier of the source unit provided by the population key field. This is also the value in the population raster for the source unit.</li><li>Count - The number of pixels in the population raster for this source unit. This is the total area of a source unit including all uninhabited areas.</li><li>_Population count field_ - The population count of the source unit. The field name will be the same name as the corresponding field in the population features.</li><li>POP_AREA - The number of habitable pixels in the source unit. This represents the total area of all habitable ancillary classes in the source unit.</li><li>POP_DENS - The population count of the source unit divided by the populated area of the source unit.</li><li>REP_CAT - The ancillary class for which the source unit is considered representative. A value of 0 indicates the source unit is not a representative source unit</li></ul>|
|DasyWorkTable.dbf | The dasymetric working table for each target unit:<br><br><ul><li>Value - A unique identifier for the target unit and the raster value for the target unit in DasyRaster.tif.</li><li>Count - The number of pixels in the dasymetric raster for the target unit.</li><li>_Polygon ID_ - This field stores the unique identifier for the source unit associated with the target unit. The unique identifier is the value of the source unit in the population raster. The name of this field will be the first 9 characters of the population raster’s base name.</li><li>_Ancillary ID_ - This field stores the value of the ancillary class associated with the target unit. The name of this field will be the first 9 characters of the ancillary raster’s base name.</li><li>POP_COUNT - The population count for the source unit associated with the target unit.</li><li>POP_AREA - The populated area of the source unit associated with the target unit.</li><li>CLASSDENS - The representative population density for the ancillary class associated with the target unit.</li><li>POP_EST - The population estimated for the target unit before the distribution ratio is calculated.</li><li>REM_AREA - The remaining area of a target unit after population has been estimated for areas covered by sampled or preset classes in the source unit associated with the target unit.</li><li>POP_DIFF - The remaining population of the source unit associated with the target unit. It is the difference between the population estimated by sampled and preset densities and the original population count for the source unit.</li><li>TOTALFRACT - The distribution ratio for the target unit. It is the ratio of the target unit’s population estimate to the total population estimated for the source unit associated with the target unit.</li><li>NEW_POP: The final population estimated for the target unit.</li><li>NEWDENSITY - The final population density estimated for the target unit.</li></ul>|
|SamplingSummaryTable.dbf | Information about how the representative population density for each ancillary class was determined. <br><br><ul><li>REP_CAT - The ancillary class for which the representative population density was calculated.</li><li>SUM_ _population count_: This field stores the sum of the population counts of all representative source units for a sampled class. The field name is a concatenation of ‘SUM_’ and the name of the population count field provided by the user.</li><li>SUM_POP_AR - This field stores the sum of the populated area of all representative source units of a sampled class.</li><li>SAMPLEDENS - The sampled density of a sampled class is the sum of population count divided by the ‘SUM_POP_AR’ of the sampled class.</li><li>METHOD - The method used to determine the representative population density for the ancillary class. The three available methods are: Sampled, Preset, or IAW.</li><li>CLASSDENS - The representative population density for the ancillary class. For classes that are sampled and do not have a preset density, the CLASSDENS will be the same as SAMPLEDENS.</li></ul>|


### Example
[Example data](data) are provided.  

|Parameter|  Value|
|--|--|
|Population Features |2010_blocks_DE.shp|
|Population Count Field | POP10 |
|Population Key Field | polyID |
|Ancillary Raster | nlcd_2011_DE.tif |
|Uninhabited File | uninhab_DE.shp |
|Minimum Sample | 3 |
|Minimum Sampling Area | 1 |
|Percent | 0.95|
|Output Directory | |

## Contact

U.S. Environmental Protection Agency  
Office of Research and Development  
Durham, NC 27709  
[https://ecomments.epa.gov/enviroatlas/](https://ecomments.epa.gov/enviroatlas/)


## Credits
The Intelligent Dasymetric Toolbox for ArcGIS Pro was developed for [EnviroAtlas](https://www.epa.gov/enviroatlas). EnviroAtlas is a collaborative effort led by U.S. EPA that provides geospatial data, easy-to-use tools, and other resources related to ecosystem services, their stressors, and human health. 

The dasymetric toolbox was updated for ArcGIS Pro in January 2020 by **Anam Khan**<sup>2</sup> and **Jeremy Baynes**<sup>3</sup> and described in Baynes, et al., 2022<sup>1</sup>. This release introduced optional functionality to mask known uninhabited areas.

The toolbox was originally developed for ArcMap 10 by **Torrin Hultgren**<sup>4</sup> following the methods of **Mennis and Hultgren (2006)**<sup>5</sup>. 

<sub><sup>1</sup> Baynes, J., Neale, A., & Hultgren, T. (2022). Improving intelligent dasymetric mapping population density estimates at 30 m resolution for the conterminous United States by excluding uninhabited areas. Earth system science data, 14(6), 2833.</sub>  
<sub><sup>2</sup> Oak Ridge Associated Universities, National Student Services Contractor at the U.S. EPA</sub>  
<sub><sup>3</sup> U.S. EPA Office of Research and Development</sub>  
<sub><sup>4</sup> National Geospatial Support Team at U.S. EPA</sub>  
<sub><sup>5</sup> Mennis, Jeremy & Hultgren, Torrin. (2006).  Intelligent Dasymetric Mapping and Its Application to Areal Interpolation. Cartography and Geographic Information Science. 33. 179-194.</sub>


## License
MIT License

Copyright (c) 2024 U.S. Federal Government (in countries where recognized)

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

## EPA Disclaimer
*The United States Environmental Protection Agency (EPA) GitHub project code is provided on an "as is" basis and the user assumes responsibility for its use.  EPA has relinquished control of the information and no longer has responsibility to protect the integrity, confidentiality, or availability of the information.  Any reference to specific commercial products, processes, or services by service mark, trademark, manufacturer, or otherwise, does not constitute or imply their endorsement, recommendation or favoring by EPA.  The EPA seal and logo shall not be used in any manner to imply endorsement of any commercial product or activity by EPA or the United States Government.*
