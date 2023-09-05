# Getting started with BIG-MAP Archive

This is a beginner-friendly exercise that takes you through the process of creating, sharing, updating, and retrieving records for BIG-MAP Archive. Before you start this tutorial, you should have a user account on a demo instance of the data repository (e.g., [https://big-map-archive-demo.materialscloud.org/](https://big-map-archive-demo.materialscloud.org/)), which enables you to try available features and commands without affecting the [main instance](https://archive.big-map.eu/). If this is not the case, email us big-map-archive@materialscloud.org.

## Manual data sharing and preservation

In this section, users interact with the data repository through a web browser.

### Log in to the demo instance

- Navigate to the homepage.
- Click "Log in" and enter your account credentials. If you receive an error message such as "Invalid email address", contact us.
- In case of unknown or forgotten password:
  - Click "Forgot password?". 
  - Enter your email address and click "Reset password".
  - Follow the instructions. At some point, choose a new password that must be at least 6 characters long.
- Upon successful login, you are automatically redirected to the shared records' first page.

### Create (a first version of) an entry

- Click "New record" in the header.
- Select the files to upload and link to the future record. Drag and drop them in the drop zone (light gray region). 
Note that you are limited to 100 files and a total file size of 100 GB. 
For this exercise, we recommend choosing small files (file size ≤ 1 MB) containing dummy data.
- Fill in the record’s metadata:
  - A resource type. This field is compulsory and describes the overall nature of your data files’ contents.
  - A title (compulsory).
  - Authors (compulsory). Note that adding another user as an author does not make him or her a record's co-owner.
  - A description (optional).
  - A license (optional). The recommended license is the BIG-MAP license which allows re-distribution and re-use of work within the BIG-MAP community.
  - Keywords (optional). Any keyword is allowed. However, each keyword should be entered separately: there should be a small cross on the right side of each of them. You also benefit from an autocomplete feature that suggests keywords based on input. Type, e.g., "wp". Recommendation: if you split a large dataset over multiple entries, you may want to tag the first version of each entry with the same random number. This helps humans and machines retrieve the whole dataset easily using the built-in search engine. 
  - References to external documents (optional).
- Click "Save" to create (the first version of) the entry. It remains visible only to you (owner).

### Share the first version

- Go to "My records" and click the record’s title.
- Click "Share on archive" to make your record appear in the shared records' list. By sharing the record, you automatically give all authenticated users permission to read the record's metadata and download its linked files.  

### Update the first version (metadata only)

- Go to "My records" and click the record’s title.
- Click "Edit" to update the record's metadata. Note that adding, modifying, or deleting file links are not allowed at this stage.
- Add a keyword, an author, etc.
- Click "Share on archive" to save your changes.
- Navigate to "Shared records" and click the record’s title. Your modifications should be visible to authenticated users.

### Create and share a second version

- Go to "My records" and click the record’s title.
- Click "New version" to create a second version of the entry.
- Click "Import files" to import all file links from the first version into the second one.
- Remove a file link, upload a file, change the title, etc.
- Click "Share on archive" to make the second version visible to authenticated users. 
- Navigate to "Shared records". The second version should appear in the shared records’ list, contrary to the first version, which is now missing. This is due to the fact that only the latest shared version of an entry is displayed by default. 
- Switch the toggle on the left side of the web page to show both versions. 
- Click any of the two versions. Find the card entitled "Versions" on the right side of the web page. You should be able to easily navigate from one version to the other by clicking the appropriate link.

### Collaborate with others (entry co-ownership)

- Go to "My records" and click the record’s title.
- Click "Collaborate" and "Get a link" to generate a URL to be sent to collaborators. Equipped with this URL, they can become co-owners of the entry.
- Ask one of them to create a third version (without sharing).
- Visit "My records". You should be able to see and edit the newly created draft.

### Search through shared records' metadata

- Click "Shared records".
- Type "+LNO +WP9" into the search box to search for all shared records whose metadata contains LNO and WP9. Depending on the contents of the database, the built-in search engine returns zero or more hits. For more advanced queries, such as searching through specific fields in the metadata (e.g., the title), read the provided search guide.

## Towards automated data sharing and preservation

In this section, users interact with the data repository through a command-line interface (CLI) application, which is installed on their machine. Commands to create, update, and retrieve records can be executed at terminal prompts and even invoked from custom applications. Note that more complex commands can be built upon those presented below to meet special user needs.

### Get an API token

- Click "API access tokens" in the header’s drop-down menu on the right side of the web page.
- Click "New token" and follow the instructions to create an API token with unlimited lifetime. Keep it private and in a safe storage. You will use it to access API endpoints of the data repository.

### Get started with the CLI app

- Follow the [Quick start guide](https://github.com/materialscloud-org/big-map-archive-api-client#quick-start) to
  - install the CLI app on your machine
  - prepare a YAML configuration file named `bma_config.yaml` that specifies the domain name and your API token for the data repository
  - prepare a YAML file named `metadata.yaml` that contains your future record's metadata (its title, its list of authors, etc).
- Activate the virtual environment where the package `big-map-archive-api-client` is installed.
- Test that the following command is available:
  ```bash
  bma record --help
  ```
  
### Create and share (a first version of) an entry

- Move `metadata.yaml` to the `data/input` directory.
- Put the data files to be uploaded and linked to the future record in the `data/input/upload` directory.
- Execute the following command:
```bash
bma record create --config-file=$PWD/bma_config.yaml --metadata-file=$PWD/data/input/metadata.yaml --data-files=$PWD/data/input/upload --publish
```
- Once this is done, access the record's web page by simply clicking the generated hyperlink in the terminal.
- Store the record's id.

### Update the first version (metadata only)

- Update the contents of `metadata.yaml` (e.g., the title).
- Execute the following command, after replacing `<record_id>` with the id of the first version:
```bash
bma record update --config-file=$PWD/bma_config.yaml --metadata-file=$PWD/data/input/metadata.yaml --data-files=$PWD/data/input/upload --record-id=<record_id> --update-only
```
- Check that your modifications appear as expected in the record's web page.

### Create and share a second version

- Update the contents of the `metadata.yaml` file and the `upload` directory:
  - Modify the description.
  - Change the contents of a file.
  - Remove a file.
  - Add a new file.
- Execute this command, after replacing `<record_id>` with the id of the first version:
```bash
bma record update --config-file=$PWD/bma_config.yaml --metadata-file=$PWD/data/input/metadata.yaml --data-files=$PWD/data/input/upload --record-id=<record_id> --link-all-files-from-previous --publish
```
Note that, if a data file remains unchanged from one version to the next, it is linked to both versions but uploaded only once. This saves storage space and avoids unnecessary use of bandwidth.
- Navigate to "Shared records" and click the record's title. Observe the links imported from the first version, in addition to the links for the files in `data/input/upload`. The `--link-all-files-from-previous` flag is responsible for these extra links.

### Retrieve shared records' metadata

- To retrieve the metadata of a specific shared record, execute this command, after replacing `<record_id>` with the sought-after record's id:
```bash
bma record get --config-file=$PWD/bma_config.yaml --output-file=$PWD/data/output/metadata.json --record-id=<record_id>
```
- To retrieve the metadata of the latest shared version of each entry, execute this command:
```bash
bma record get-all --config-file=$PWD/bma_config.yaml --output-file=$PWD/data/output/metadata.json
```
- For all shared versions of each entry:
```bash
bma record get-all --config-file=$PWD/bma_config.yaml --output-file=$PWD/data/output/metadata.json --all-versions
```
