# BIG-MAP Archive

## Main archive

The [BIG-MAP Archive](https://archive.big-map.eu/) is fully online and waiting for your submissions!

It is a research data repository to enable data sharing within the BIG-MAP community.

The data uploaded in the BIG-MAP Archive remains private within BIG-MAP, and accessible by all registered BIG-MAP members.

The focus is on data, raw and/or processed, that you already curated and want to share within BIG-MAP (but you don't want to share it publicly yet: e.g., to allow its use in BIG-MAP before publication of the corresponding paper). Currently, the maximum total file size is limited to 100 GB per record.

## Demo archive and tutorial

In addition to the main production archive (with daily backups), a [demo archive](https://big-map-archive-demo.materialscloud.org/) is available so that you can practice creating and managing records via the graphical user interface (GUI) and the application programming interface (API). 

A [tutorial](https://github.com/materialscloud-org/big-map-archive/blob/master/user_training/getting_started_with_big-map-archive.md) walks you through the very basic steps to help you getting started. Please experiment on the demo archive, as you are not allowed to delete shared records on the main archive.

## User accounts

The main archive and the demo archive are independent systems. If you are a registered BIG-MAP member, two accounts (one per archive) should have been created for you by the BIG-MAP Archive team. 

Prior to your first login to an archive, you should reset your password, as explained in the tutorial.

## Support

If you have any comments or questions, please send your emails to big-map-archive@materialscloud.org.

## Issues

If you find a bug, please create an issue directly into [GitHub](https://github.com/materialscloud-org/big-map-archive/issues). If possible, give enough details so that the BIG-MAP Archive team is able to reproduce the encountered problem. Thank you!

## [For devops] Files and folders

Following is an overview of the generated files and folders:

| Name | Description |
|---|---|
| ``Dockerfile`` | Dockerfile used to build your application image. |
| ``Pipfile`` | Python requirements installed via [pipenv](https://pipenv.pypa.io) |
| ``Pipfile.lock`` | Locked requirements (generated on first install). |
| ``app_data`` | Application data such as vocabularies. |
| ``assets`` | Web assets (CSS, JavaScript, LESS, JSX templates) used in the Webpack build. |
| ``docker`` | Example configuration for NGINX and uWSGI. |
| ``docker-compose.full.yml`` | Example of a full infrastructure stack. |
| ``docker-compose.yml`` | Backend services needed for local development. |
| ``docker-services.yml`` | Common services for the Docker Compose files. |
| ``invenio.cfg`` | The Invenio application configuration. |
| ``logs`` | Log files. |
| ``static`` | Static files that need to be served as-is (e.g. images). |
| ``templates`` | Folder for your Jinja templates. |
| ``.invenio`` | Common file used by Invenio-CLI to be version controlled. |
| ``.invenio.private`` | Private file used by Invenio-CLI *not* to be version controlled. |

## [For devops] InvenioRDM documentation

BIG-MAP Archive is based on [InvenioRDM](https://inveniordm.docs.cern.ch/).

## Acknowledgements

This project has received funding from the European Union’s [Horizon 2020 research and innovation programme](https://ec.europa.eu/programmes/horizon2020/en) under grant agreement [No 957189](https://cordis.europa.eu/project/id/957189). The project is part of BATTERY 2030+, the large-scale European research initiative for inventing the sustainable batteries of the future.

