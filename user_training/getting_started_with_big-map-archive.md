# Getting started with BIG-MAP Archive

For this exercise, select a demo instance of BIG-MAP Archive that allows you to try available features and command-line commands without affecting the main data repository.

## Manual data sharing and preservation using a web browser

### Log into the demo instance

- Navigate to the homepage of the demo instance by either entering the url in a web browser 
(e.g., [https://big-map-archive-demo.materialscloud.org/](https://big-map-archive-demo.materialscloud.org/)) 
or clicking the button labeled "Test on demo" on the homepage of the [main repository](https://archive.big-map.eu/).
- Click "Log in", then "Forgot password?".
- Enter your email address and click "Reset password". 
If you receive an error message such as "Invalid email address", contact us at  big-map-archive@materialscloud.org.
- Follow the instructions. At some point, you will be invited to choose a new password that must be at least 6 characters long. After your password reset, you are automatically logged in.

### Create (a first version of) an entry

- Click "New record" in the header.
- Select the files that you wish to upload and link to the record. Drag and drop them in the drop zone (light gray region). 
Note that you are limited to 100 files and a total file size of 100 GB. 
For this exercise, we recommend choosing two small files (total size ≤ 1 MB) containing dummy data.
- Fill in the record’s metadata:
  - A resource type. This field is compulsory and describes the overall nature of your data files’ contents.
  - A title (compulsory).
  - Authors (compulsory). Note that adding another archive user as an author does not make him a co-owner of the record.
  - A description (optional).
  - A license (optional). The recommended license is the BIG-MAP license which allows re-distribution and re-use of work within the BIG-MAP community.
  - Keywords (optional). Make sure that your keywords are entered one by one: there should be a small cross on the right side of each of them. You are allowed to create your own keywords. For instance, if you split a large dataset over multiple records, you may want to tag these records with the same 15 digit random number to help humans and machines retrieve the whole dataset easily using the built-in search engine. You can also use an autocomplete feature that suggests keywords based on input. Type, e.g., "wp".
  - References to external documents (optional).
- Click "Save" to create (the first version of) an entry. At this stage, it remains private and is visible to you only.

### Share the first version

BIG-MAP Archive is a private data repository, where access to shared records is restricted to authenticated users. 

- Click "My records" in the header
- Check that your newly created entry appears in your records’ list and click its title.
- Modify your record if needed.
- Click "Share on archive" to save and make your record visible to all authenticated users. By sharing records, owners give read and download permissions.
- Click "Shared records" in the header to check that your record appears in the shared records’ list.
- Click the record’s title and click "Download" to start downloading one of the linked files. 

### Update the first version

At this stage, we assume that you wish to update your entry without creating a new version. 
There may be a typo in the title of the first version, a missing keyword, etc.

- Go to "My records" and click the record’s title.
- Click "Edit". 
- Make a few changes in the metadata: change the title, add a keyword, etc. You are not allowed to add, modify or delete file links.
- Click "Share on archive" to save your changes.
- Navigate to "Shared records" and check that your modifications appear as expected.

### Create a second version and share it

In this section, you will update your entry by creating a second version. There may be a missing file, a typo in the title, etc. 

- Go to "My records" and click the record’s title.
- Click "New version" and "Import files". The file links from the first version get imported into the second one.
- Make a few changes: add a file, remove a file, change the title, etc.
- Click "Share on archive".
- Navigate to "Shared records" and check that the new version appears in the shared records’ list. By default, only the latest shared version of an entry appears in this list. 
- Switch the toggle on the left side of the web page to display both versions of the entry. 
- Click any of the two versions. Find the card entitled "Versions" on the right side of the web page. You should be able to easily navigate from one version to the other by clicking the appropriate link.

### [Optional] Ask a collaborator to create and share a third version of the entry

- Click "My records".
- Click the title of the second version of the entry.
- Click "Collaborate" and "Get a link" to generate a URL that you will copy and send to another user of the archive. 

Equipped with this URL, he is granted the rights to edit the second version, create a third version, and share it with the other authenticated users. 

### [Optional] Search for a shared record using the archive’s built-in search engine

- Click "Shared records".
- Type "+LNO +WP9" into the search box to find all shared records whose metadata contains "LNO" and "WP9". Depending on the contents of the database, you may get zero, one, or more hits. 

Read the search guide, if you wish to make more advanced queries, such as searching for all shared records where the title contains "LNO".

### Get an API token

To access endpoints of the data repository's API from a client application, you should supply a valid access token on each request. 

- To create a token, click "API access tokens" in the header’s drop-down menu on the right side of the page.
- Click "New token" and follow the displayed instructions. 

Note that the access token is shown only once and has an unlimited lifetime (unless you delete it). 
Treat it like a password: keep in a safe storage and do not to share with anyone else.

## Towards automated data sharing and preservation using a command line client

We have developed a CLI tool to help users automate record management for data sharing and preservation on the BIG-MAP-Archive data repository. 
Commands to create, update, and retrieve records can be executed at a terminal prompt and even called from custom applications. 
More commands can be built upon those to meet special needs.

### Install the CLI app on your machine, configure, and prepare input files

Follow the [Quick start](https://github.com/materialscloud-org/big-map-archive-api-client#quick-start) section to get started with the CLI app. Note that an API token is required. 
Make sure that the command `bma record --help` is available in your working directory. If not, you may need to activate the virtual environment where the package `big-map-archive-api_client` is installed.

### Create and share (a first version of) an entry

- Check that your current directory contains a `metadata.yaml` file located in `data/input` and the data files to be uploaded and linked to the future entry in `data/input/upload`.
- Execute the command with the following options:
```bash
bma record create --config-file=$PWD/bma_config.yaml --metadata-file=$PWD/data/input/metadata.yaml --data-files=$PWD/data/input/upload --publish
```
- Click the link printed in the terminal to access the record's web page.
- Extract the record's id from the url of the web page (e.g., 816ne-zvh93)

### Update the first version

Let us update your entry without creating a new version.

- Update the contents of `metadata.yaml` located in `data/input` (e.g., modify the title).
- Execute this command with these options, after replacing `<record_id>` with the previously obtained record's id:
```bash
bma record update --config-file=$PWD/bma_config.yaml --metadata-file=$PWD/data/input/metadata.yaml --data-files=$PWD/data/input/upload --record-id=<record_id> --update-only
```
- Navigate to "Shared records" and check that your modifications appear as expected.

### Create a second version and share it

This time, let us update your entry by creating a second version.

- Update the contents of `metadata.yaml` located in `data/input` (e.g., modify the title).
- Update the data files in `data/input/upload` (e.g., modify the contents of a file while keeping its name unchanged, add a file, and remove a file).
- Execute this command with these options, after replacing `<record_id>` with the id of the first version:
```bash
bma record update --config-file=$PWD/bma_config.yaml --metadata-file=$PWD/data/input/metadata.yaml --data-files=$PWD/data/input/upload --record-id=<record_id> --link-all-files-from-previous --publish
```
- Navigate to "Shared records" and check the new version. In addition to file links for all files in `data/input/upload`, you may find file links that were imported from the first version.
Note that, if a data file remains unchanged from one version to the next, the file is uploaded only once. However, the corresponding file link appears in the two entry versions. This saves storage space and reduces command execution time.

### Retrieve shared records

Retrieving shared records is straightforward. 

- For a single record, execute this command with these options, after replacing `<record_id>` with the sought-after record's id:
```bash
bma record get --config-file=$PWD/bma_config.yaml --output-file=$PWD/data/output/metadata.json --record-id=<record_id>
```
- For the latest shared version of each entry, execute this command with these options:
```bash
bma record get-all --config-file=$PWD/bma_config.yaml --output-file=$PWD/data/output/metadata.json
```
- For all shared versions of each entry:
```bash
bma record get-all --config-file=$PWD/bma_config.yaml --output-file=$PWD/data/output/metadata.json --all-versions
```
