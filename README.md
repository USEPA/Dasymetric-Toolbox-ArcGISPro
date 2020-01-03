# Intelligent Dasymetric Toolbox for ArcGIS Pro

[<img src="https://enviroatlas.epa.gov/enviroatlas/interactivemap/images/logo.png"     title="EnviroAtlas" width=400 >](https://www.epa.gov/enviroatlas)

## Overview
 
Dasymetric mapping is a geospatial technique that uses information such as land cover types to more accurately distribute data within selected boundaries like census blocks.

The Intelligent Dasymetric Mapping (IDM) Toolbox is available for ArcGIS Pro. An additional [version](https://github.com/USEPA/Dasymetric-Toolbox-OpenSource) is available that uses open source GIS libraries. 


<figure>
  <img src="https://www.epa.gov/sites/production/files/styles/large/public/2015-07/dasymetric_728x210.jpg" alt="my alt text"/>
  <figcaption><sup>The image on the left shows a map of the population by block group based solely on the census data. The image on the right shows the dasymetric population allocation for several block groups in Tampa, Fla.</sup></figcaption>  
</figure>
<br>

-   EnviroAtlas researchers use the dasymetric data to calculate the distribution of ecosystem services, and other metrics including walking distances, viewsheds, resource use, and exposure potential.
-   For more information on the Dasymetric data created for EnviroAtlas, see our [website](https://www.epa.gov/enviroatlas/dasymetric-toolbox) or  [Dasymetric Allocation of Population Fact Sheet](https://enviroatlas.epa.gov/enviroatlas/DataFactSheets/pdf/Supplemental/DasymetricAllocationofPopulation.pdf).



## Installation
[https://pro.arcgis.com/en/pro-app/help/analysis/geoprocessing/basics/use-a-custom-geoprocessing-tool.htm](https://pro.arcgis.com/en/pro-app/help/analysis/geoprocessing/basics/use-a-custom-geoprocessing-tool.htm)

## Usage
#### Requirements
The Intelligent Dasymetric Toolbox was developed for ArcGIS Pro. The Spatial Analyst and 3D Analyst extensions are required. 

Use of this tool may require increasing the maximum number of unique values the 'Combine Tool' can produce.

You can increase this number by changing a setting in  ArcGIS Pro. On the  **Project**  tab, select  **Options**  and select the  **Raster and Imagery**  choice. In the dialog box, select the  **Raster Dataset**  choice and enter an appropriate value for the  **Maximum number of unique values to display**.  
[https://pro.arcgis.com/en/pro-app/tool-reference/spatial-analyst/combine.htm](https://pro.arcgis.com/en/pro-app/tool-reference/spatial-analyst/combine.htm)

#### Uninhabited areas
The user can provide an optional uninhabited feature class. This feature class should contain polygons where no population are expected to reside. The polygons of the feature class are classified as an uninhabited ancillary class and the representative population density for this class is preset to 0 people per pixel.

#### Preset Densities
The user can set a population density for any ancillary class using their own domain knowledge by modifying the 'config.json' file in the toolbox's root directory. 

The preset densities for the following land cover classes from the 2011 National Land Cover Database (NLCD) are set to 0 people per pixel:

* 11, Open Water
* 12, Perennial Ice/Snow
* 95, Emergent Herbaceous Wetlands


#### Tool parameters
|Parameter|  Description|
|--|--|
|Population Features|  The source units with population counts and a unique identifier to be converted to a raster.|
| Population Count Field | The field in Population Features that stores the population counts.|
 |Population Key Field|The field in the Population Features that stores the unique identifier for the source unit.|
|Ancillary Raster | The ancillary raster dataset to be used to redistribute population. The cell size and spatial reference from the ancillary raster are used for all output rasters from this tool. Land-use or land-cover are the most frequently used ancillary datasets, but any dataset that has classes of relatively homogenous population density could be used here. |
|Uninhabited File (optional) | A feature class containing the uninhabited areas in the study area. |
|Minimum Sample | This is the minimum threshold of representative source units required for an ancillary class to be considered sampled. We found that if only a small number (1-3) were sampled, those units were not often truly representative of others in that ancillary class, and the Intelligent Areal Weighting (IAW) method provided better results. Any class that is not preset or sufficiently sampled will be assigned a density using the IAW method. **The default is 3**. |
|Minimum Sampling Area | The minimum number of raster cells that may be considered "representative" of a source area. Increasing this number may eliminate some very small areas that might be considered anomalous outliers that could skew the class average. **The default is 1**.|
|Percent | The script will calculate the percent area that each ancillary class covers in each source unit, and any source unit with an ancillary class above the percent area threshold will be considered representative of that class. Please specify the percent threshold value in decimal notation. **The default is 0.95**.|
|Output Directory | The directory where all outputs from the tool will be saved. |



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
[https://www.epa.gov/enviroatlas/forms/contact-us-about-enviroatlas](https://www.epa.gov/enviroatlas/forms/contact-us-about-enviroatlas)


## Credits
The Intelligent Dasymetric Toolbox for ArcGIS Pro was developed for [EnviroAtlas](https://www.epa.gov/enviroatlas). EnviroAtlas is a collaborative effort led by U.S. EPA that provides geospatial data, easy-to-use tools, and other resources related to ecosystem services, their stressors, and human health. 

The dasymetric  toolbox was updated for ArcGIS Pro in January 2020 by **Anam Khan**<sup>1</sup> and **Jeremy Baynes**<sup>2</sup>. This release also introduced optional functionality to mask known uninhabited areas.

The toolbox was originally developed for ArcMap 10 by **Torrin Hultgren**<sup>3</sup> 

The dasymetric toolbox follows the the methods by **Mennis and Hultgren (2006)**<sup>4</sup>. 


<sub><sup>1</sup> Oak Ridge Associated Universities, National Student Services Contractor at the U.S. EPA</sub>  
<sub><sup>2</sup> U.S. EPA</sub>  
<sub><sup>3</sup> National Geospatial Support Team at U.S. EPA</sub>  
<sub><sup>4</sup> Mennis, Jeremy & Hultgren, Torrin. (2006).  Intelligent Dasymetric Mapping and Its Application to Areal Interpolation. Cartography and Geographic Information Science. 33. 179-194.</sub>



## License
MIT License

Copyright (c) 2019 U.S. Federal Government (in countries where recognized)

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

## EPA Disclaimer
*The United States Environmental Protection Agency (EPA) GitHub project code is provided on an "as is" basis and the user assumes responsibility for its use.  EPA has relinquished control of the information and no longer has responsibility to protect the integrity , confidentiality, or availability of the information.  Any reference to specific commercial products, processes, or services by service mark, trademark, manufacturer, or otherwise, does not constitute or imply their endorsement, recommendation or favoring by EPA.  The EPA seal and logo shall not be used in any manner to imply endorsement of any commercial product or activity by EPA or the United States Government.*
