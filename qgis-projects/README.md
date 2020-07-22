# QGIS Projects

- dominode-topomaps.qgs
  - Custodian: charles@kartoza.com
  - Description: Primary map project for toposheet production

## Project data

Adding data should be done directly by primary project custodians wherever possible. Adding of features or layers to existing data sources (remote/ gpkg etc) should be distributed in the same manner as the original data source (republished) or have their source details modified in the following section.

---

- File: ./data/data.gpkg
- Custodian: Default
- Description: Local copy of utilised data copied from remote staging database as well as additional features sourced from public internet sources.
- Source: [Download from google drive](https://drive.google.com/file/d/1B3o7bPx1iQH5qMXUGWQO-BwLkeJYlYP7/view?usp=sharing).

> Note that the *data* directory is intended to be a symbolic link to a local data directory separate from the project repository.

## Directory structure

Primary custodians for the qgis-projects directory should be indicated in the ```CODEOWNERS``` in the *Project Root*.

```text
qgis-projects/    @user01 @user02
```

Additional ownership can be added to the ```CODEOWNERS``` file where relevant.

```text
qgis-projects/file-name.qgs    @user03
```

There are a number of directories utilised within a qis-projects directory (note that not all directories may be present until the relevant data is available). Common directories, their naming conventions and their functions are outlined by the following list.

- README.md: This readme document in markdown format.
- assets: Multimedia assets directory. This may include images used in this readme document, corporate stationary objects or assets for use in the cartographic process, such as svg libraries.
- atlas: Default output directory for atlas items. Storing this directory within the project repository should be used with caution, as atlas outputs are often large binary data. Should be added to .gitignore by default.
- data: Symbolic link to large file storage
- qpt: Directory for qpt print layout template documents
- sld: Directory SLD format style files, often saved for interoperability purposes
- qml: Directory for QGIS QML style files
- scripts: Processing tools and script utility directory
- *.qgs: QGIS project files

> Additional documents and addenda should be stored with the parent project (project root, i.e. ```../docs```)