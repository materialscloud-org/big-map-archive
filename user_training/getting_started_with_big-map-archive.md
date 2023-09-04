# Getting started with BIG-MAP Archive

This is a beginner-friendly exercise that takes you through the process of creating, sharing, updating, and retrieving records for BIG-MAP Archive. Before you start this tutorial, you should have access to a demo instance of the data repository (e.g., [https://big-map-archive-demo.materialscloud.org/](https://big-map-archive-demo.materialscloud.org/)), which enables you to try available features and commands without affecting the [main instance](https://archive.big-map.eu/). 

## Manual data sharing and preservation

In this section, users interact with the data repository through a web browser.

### Log in to the demo instance

- Navigate to the homepage.
- Click "Log in", then "Forgot password?".
- Enter your email address and click "Reset password". 
If you receive an error message such as "Invalid email address", contact us at big-map-archive@materialscloud.org.
- Follow the instructions. At some point, choose a new password that must be at least 6 characters long. After your password reset, you are automatically logged in.

### Create (a first version of) an entry

- Click "New record" in the header.
- Select the files to upload and link to the record. Drag and drop them in the drop zone (light gray region). 
Note that you are limited to 100 files and a total file size of 100 GB. 
For this exercise, we recommend choosing small files (file size ≤ 1 MB) containing dummy data.
- Fill in the record’s metadata:
  - A resource type. This field is compulsory and describes the overall nature of your data files’ contents.
  - A title (compulsory).
  - Authors (compulsory). Note that adding another user as an author does not make him a co-owner of the record.
  - A description (optional).
  - A license (optional). The recommended license is the BIG-MAP license which allows re-distribution and re-use of work within the BIG-MAP community.
  - Keywords (optional). Any keyword is allowed. However, each keyword should be entered separately: there should be a small cross on the right side of each of them. You can also benefit from an autocomplete feature that suggests keywords based on input. Type, e.g., "wp". Recommendation: if you split a large dataset over multiple entries, you may want to tag the first version of each entry with the same random number. This helps humans and machines retrieve the whole dataset easily using the built-in search engine. 
  - References to external documents (optional).
- Click "Save" to create (the first version of) the entry. The draft is visible only to its owner.

### Share the first version

- Go to "My records" and click the record’s title.
- Click "Share on archive" to make your record visible to all authenticated users. By sharing the record, you automatically give all authenticated users permission to read its metadata and download its linked files. Your record should now appear in the shared records' list. 

### Update the first version (metadata only)

- Go to "My records" and click the record’s title.
- Click "Edit" to update the record's metadata. Note that adding, modifying, or deleting file links are not allowed at this stage.
- Add a keyword, an author, etc.
- Click "Share on archive" to save your changes.
- Navigate to "Shared records" and click the record’s title. Your modifications should be visible to all authenticated users.

### Create and share a second version

- Go to "My records" and click the record’s title.
- Click "New version" to create a second version of the entry.
- Click "Import files" to import all file links from the first version into the second one.
- Remove a file link, upload a file, change the title, etc.
- Click "Share on archive" to make the second version visible to all authenticated users. 
- Navigate to "Shared records". The second version should appear in the shared records’ list, contrary to the first version, which is now missing. This is due to the fact that only the latest shared version of an entry is displayed by default. 
- Switch the toggle on the left side of the web page to show both versions. 
- Click any of the two versions. Find the card entitled "Versions" on the right side of the web page. You should be able to easily navigate from one version to the other by clicking the appropriate link.

### Ask a collaborator to create and share a third version

- Go to "My records" and click the record’s title.
- Click "Collaborate" and "Get a link" to generate a URL to be sent to one of your collaborators. Equipped with this URL, he/she should be able to update your entry (e.g., create new versions) after login.

### Search for shared records using the built-in search engine

- Click "Shared records".
- Type "+LNO +WP9" into the search box to find all shared records whose metadata contains LNO and WP9. Depending on the contents of the database, you may get zero, one, or more hits. For more advanced queries, such as searching for all shared records where the title contains LNO and WP9, read the provided search guide.

## Towards automated data sharing and preservation

In this section, users interact with the data repository through a command-line interface (CLI) application, which is installed on their machine. Commands to create, update, and retrieve records can be executed at terminal prompts and even called from custom applications. Note that more complex commands can be built upon those presented below to meet special user needs.

### Get an API token

- Click "API access tokens" in the header’s drop-down menu on the right side of the web page.
- Click "New token" and follow the instructions to create an API token with unlimited lifetime. Keep your token in a safe storage and do not to share with anyone else. It will give you access to API endpoints of the data repository. 

### Get started with the CLI app

- Follow the [Quick start guide](https://github.com/materialscloud-org/big-map-archive-api-client#quick-start) to
  - install the CLI app on your machine
  - prepare a YAML configuration file that specifies the domain name and your API token for the data repository - filename: `bma_config.yaml`
  - prepare a YAML file that contains metadata (a title, a list of authors, etc) for future records - filename: `metadata.yaml`.
- Test whether the command `bma record --help` is available from your working directory. If not, you may need to activate the virtual environment where the package `big-map-archive-api-client` is installed.

### Create and share (a first version of) an entry

- Put the `metadata.yaml` file in the `data/input` directory.
- Put the data files to be uploaded and linked to the future record in the `data/input/upload` directory.
- Execute this command:
```bash
bma record create --config-file=$PWD/bma_config.yaml --metadata-file=$PWD/data/input/metadata.yaml --data-files=$PWD/data/input/upload --publish
```
- Once the execution is completed, copy the record's id and click the link that is printed in the terminal to access the record's web page.

### Update the first version (metadata only)

- Update the contents of the `metadata.yaml` file (e.g., the title).
- Execute the following command, after replacing `<record_id>` with the id of the first version:
```bash
bma record update --config-file=$PWD/bma_config.yaml --metadata-file=$PWD/data/input/metadata.yaml --data-files=$PWD/data/input/upload --record-id=<record_id> --update-only
```
- Check that your modifications appear as expected in the record's web page.

### Create and share a second version

- Update the contents of the `metadata.yaml` file (e.g., the description).
- Change the files in the `upload` directory:
  - Modify the contents of a file but keep its name unchanged.
  - Add a file.
  - Remove a file.
- Execute this command, after replacing `<record_id>` with the id of the first version:
```bash
bma record update --config-file=$PWD/bma_config.yaml --metadata-file=$PWD/data/input/metadata.yaml --data-files=$PWD/data/input/upload --record-id=<record_id> --link-all-files-from-previous --publish
```
- Navigate to "Shared records" and click the record's title. In addition to a link for each file in `data/input/upload`, you may find all of the links from the first version. This is an effect of the flag `--link-all-files-from-previous`.

### Retrieve shared records

- For a single record, execute this command, after replacing `<record_id>` with the sought-after record's id:
```bash
bma record get --config-file=$PWD/bma_config.yaml --output-file=$PWD/data/output/metadata.json --record-id=<record_id>
```
- For the latest shared version of each entry, execute this command:
```bash
bma record get-all --config-file=$PWD/bma_config.yaml --output-file=$PWD/data/output/metadata.json
```
- For all shared versions of each entry:
```bash
bma record get-all --config-file=$PWD/bma_config.yaml --output-file=$PWD/data/output/metadata.json --all-versions
```
