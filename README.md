# XXX

## XX

# Constructing a property model

Giving tailored advice to homeowners starts with a solid understanding of their property, its layout, and neighboring community. As such, this repo builds a model of each california property based on three distinct, layered sources. 

***USGS 3DEP elevation*** is a public map of ground elevation with 1m granularity. It enables drawing a hillshade of the properties surrounding area. This terrain info can inform risk patterns related to slope.

***Overture*** traces the outline of every property that is aggregated from four sources (OpenStreetMap, MS ML Buildings, Google Open Buildings, Esri Community Maps) and published monthly. For every building, Overture covers the building class, area, perimeter, height, and others.

***USGS 3DEP lidar tiles*** comprises digital elevation models that include surface objects, including vegetation, thus allowing to derive canopy heights on the property, fuel density, and more. 

Together, these three layers construct a model comprising of ground elevation, property layout and vegetation.