# Geodata descriptions

|source|comment|
|---|---|
|./data/dominode_data.gpkg|local copy of all data directly copied from remote staging database|
|./data/auxillary_data.gpkg|Additional data required but ot present in core database. This data should be accounted for in the remote data source|
|./local/COMPASS_ROSE.geojson|Feature generated with the Magnetic Declination QGIS plugin|

> Note that the data directory is intended to be a symbolic link to a local data directory. Linux and Mac users can create a symbolic link using the ```ln``` command, e.g. ```ln -s ../../../data ./data``` whilst windows users may use the ```mklink``` function from cmd e.g. ```mklink /D ../../../data ./data```.

