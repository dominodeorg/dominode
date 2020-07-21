# README

This is the readme for a qgis-project data directory.

It has special considerations for the management and workflows of project data due to the requirements for the manual management of conflicts within QGIS project files.

## Collaboration and publication process

Due to the difficulty in preventing conflicts when modifying QGIS project files and geodata, a custodian should be designated who is responsible for the publication of map projects.

If a user wishes to contribute changes to the map project, the intent should be communicated to the custodian so that further work can be halted. Once the custodian confirms that contributions may be completed and that the latest update has been published for them to utilise as a base for modifications.

The updated data may then be forwarded to the custodian for publication, or the custodian may remove the project lock to allow users to push changes to the repository.

If this process is not followed, the responsibility for attempting to merge modifications may fall to the user or they may have their contributions excluded.

## Custodians

The following table indicates the custodians for map projects within this repository.

|Project|Role|Name|Mail|GitHub|
|---|---|---|---|---|
|Default|Primary Custodian|Charles Dixon-Paver|charles@kartoza.com|zacharlie|

## Map Projects

The following table indicates available map projects and their relevant custodians.

|Project|Custodian|Description|
|---|---|---|
|dominode-topomaps.qgs|Default|Primary map project for toposheet production|

When creating a new map project, please ensure that this table is maintained with the relevant details.

The naming convention for maps and associated files is to use hypen-separated, or kebab-case, styling.

> Map projects should be saved and stored as *qgs* documents (xml) **wherever possible** and not *qgz* documents (zipped archives, which are binary).

## Geodata descriptions

The following sections detail the relevant sources and file structures for geodata that are utilised within the projects in this directory.

### Quickstart

Download the relevant project data sources, usually indicated by a *./data* source in the following table. Remote sources should be available within map projects directly (assuming the relevant connections have been configured correctly within QGIS). Local data sources are stored within the repository.

Once the data has been downloaded to the local system, create a symbolic link at ```qgis-projects/data``` which may redirect to the relevant filepath. Symbolic links can be relative or absolute.

Linux and Mac users can create a symbolic link using the ```ln``` command, e.g. ```ln -s /home/user/data/project ./data```

Windows users may use the ```mklink``` function from *cmd*, e.g. ```mklink /D ../../../data ./data```.

### Project data

The following table outlines data sources used in projects.

|Data|Description|Source|
|---|---|---|
|./data/dominode_data.gpkg|local copy of all data directly copied from remote staging database|It is recommended that this is copied directly from the Dominode staging environment database. Simply connect to the database, create a local geopackage named dominode_data.gpkg and select all features, then drag and drop them onto the gpkg within the QGIS Browser.|
|./data/auxillary_data.gpkg|Additional data required but not present in core database. This data should be accounted for in the remote data source later on.|https://drive.google.com/file/d/1lH3dr4Ic3EZmHfmmZXPCjM-vbp6V6epN/view?usp=sharing|
|./local/COMPASS_ROSE.geojson|Feature generated with the Magnetic Declination QGIS plugin|local|

> Note that the *data* directory is intended to be a symbolic link to a local data directory separate from the project repository.

### Remote data

Wherever possible, geodata should be stored in remote systems (such as a database). For PostGIS, this should be a pg_service file, however it should not be stored within this repository.

### Local data

Local data may be stored within the VCS repository, however it should meet the following requirements:

* Data should be relatively small in size. Git limits files to 100MB in size so the data source should not be able to grow beyond that size.
* Data should have relatively few records. It is likely that another data format is more suitable for data which contains many thousands of records.
* Data should be text based wherever possible. This makes GeoJSON and WKT geodata suitable for inclusion as local data, provided that the data repository is reasonable in size and scope.

Git and other VCS systems utilise deltas extensively to monitor and track each commit, making it very difficult to remove unwanted data. Because differential versioning is difficult with binary files, it is not recommended that they are used for local data sources.

There are instances where binary objects may be stored (e.g. GeoPackage) or larger files (e.g. SQL dumps) may be allowed for inclusion, however this is the exception rather than the rule and should only be used where no other reasonable alternatives are available.

### Blob Storage

Geodata for projects is typically stored as blob/ binary data and is not suitable for storage in a version control system such as git. In these instances, data should be shared by alternative data storage means.

The simplest way to maintain consistency across projects is to promote the utilisation of symbolic links to blob storage directories.

Git LFS (Large File Storage) provides support for these items by including "pointers" to file objects which are pushed to large file storage. Clones download these files from the large file storage (hardlinks), removing the requirement for manually creating symbolic links to data sources.

There are additional limitations on the usage of the Git LFS with hosted git systems, so this functionality is not recommended for general use and should only be implemented on a case by case basis where it is required or warranted, only undertaken under explicit instruction from the relevant project decision making bodies.

> Note that certain LFS functionality (which is supported OOTB within GitHub) include the ability to "lock" files, which is utilised as a document management system for QGIS projects. This functionality is implemented by the Git LFS client and should not impact the usage of LFS functionality on hosted repositories.

## File locks

File locking is performed by using the Git LFS client, installed from [git-lfs.github.com](https://git-lfs.github.com). As the name suggests, this is a client side application and should not require any server side configuration when utilised with repositories hosted on GitHub.

By default, once created, files should be locked by the relevant project custodian. Locking a file should prevent any merges which contain changes to the locked file.

In order to lock a specified file, custodians may utilise the following git command.

```text
git lfs lock qgis-projects/project-name.qgs
```

Conversely, to unlock a file, similar syntax is used.

```text
git lfs lock qgis-projects/project-name.qgs
```

> Files which are intended to be locked should be specified using a relevant pattern in the project .gitattributes file. By default, a pattern for matching all child items for the qgis-projects directory of tpe qgs/ qgz should be included, as outlined in the directory structure section below.

## Merge conflicts

Due to the system of locking files with LFS, it is expected that some errors in merging may occur, as users may inadvertently modify the QGIS project files without realising.

Users may be required to manually review their commits and drop changes associated with a locked file before a commit may be performed.

As this feature is largely experimental, no further advice may be given on resolving these errors at this time.

### File permissions

Git LFS does modify file permissions, however at this time it is not known exactly how this mechanism functions or where issues might be introduced into the workflow. By default, locked files are *expected* to be read-only, however this may or may not be the case in practice and users are expected to set QGIS project files to read only in cloned repositories if they are not read only by default. Setting file permissions may enable users to prevent he inadvertent editing of locked file data which may result in commit errors.

## Directory structure

The following lines should be added to ```.gitignore``` in the *Project Root*.

```text
qgis-projects/data
qgis-projects/**/*.qgs~
qgis-projects/**/*.qgz~
```

This prevents git from interfering with the symbolic link to the data directory, which is likely to differ between users and operating systems. It also prevents the inclusion of QGIS autogenerated "backup" files, which are largely unnecessary when utilising a distributed VCS such as git.

The following lines should be added to ```.gitattributes``` in the *Project Root*.

```text
qgis-projects/**/*.qgs lockable
qgis-projects/**/*.qgz lockable
```

This ensures that QGIS project files are made available for *locking* by the Git LFS system.

There are a number of directories which (note that not all directories may be present until the relevant data is available) as outlined by the following table.

|Item|Description|
|---|---|
|README.md|This readme document in markdown format.|
|assets|Multimedia assets directory. This may include images used in this readme document, corporate stationary objects or assets for use in the cartographic process, such as svg libraries.|
|atlas|Default output directory for atlas items. Storing this directory within the project repository should be used with caution, as atlas outputs are often large binary data.|
|data|Symbolic link to large file storage|
|docs|Additional documents and addenda|
|local|Directory or local data sources|
|qml|Directory for QGIS QML style files|
|qpt|Directory for qpt print layout template documents|
|scripts|Processing tools and script utility directory|
|sld|Directory SLD format style files, often saved for interoperability purposes|
|*.qgs|QGIS project files|
