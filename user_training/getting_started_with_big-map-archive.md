# Getting started with BIG-MAP Archive

## What you will accomplish using a web browser

### Log into the demo archive
- Navigate to the homepage of the demo archive 
by clicking this url [https://big-map-archive-demo.materialscloud.org/](https://big-map-archive-demo.materialscloud.org/) 
or clicking the button labeled "Test on demo" on the homepage of the [main archive](https://archive.big-map.eu/).
- Click "Log in", then "Forgot password?".
- Enter your email address and click "Reset password". 
If you receive an error message such as "Invalid email address", contact us at  big-map-archive@materialscloud.org.
- Follow the instructions. At some point, you will be invited to choose a new password that must be at least 6 characters long. After your password reset, you are automatically logged in.

### Create and share a record
- Click "New record" in the header.
- Select the files that you wish to attach to the record. Drag and drop them in the drop zone (light gray region). Note that you are limited to 100 files and a total file size of 100 GB. For this exercise, we recommend choosing two small files (total size ≤ 1 MB) containing dummy data.
- Fill in the record’s metadata:
  - A resource type. This field is compulsory and describes the overall nature of your data files’ contents.
  - A title (compulsory).
  - Authors (compulsory). Note that adding another archive user as an author does not make him a co-owner of the record.
  - A description (optional).
  - A license (optional). The recommended license is the BIG-MAP license which allows re-distribution and re-use of work within the BIG-MAP community.
  - Keywords (optional). Make sure that your keywords are entered one by one: there should be a small cross on the right side of each of them. You are allowed to create your own keywords. For instance, if you split a large dataset over multiple records, you may want to tag these records with the same 15 digit random number to help humans and machines retrieve the whole dataset easily using the built-in search engine. You can also use an autocomplete feature that suggests keywords based on input. Type, e.g., "wp".
  - References to external documents (optional).
- Click "Share on archive" to save and make your record visible to all authenticated users.
- Click "Shared records" in the header to check that your record appears in the shared records’ list. 
- Click the record’s title and click "Download" to start downloading one of the uploaded files to your local machine.

### Create and share a second version of your record
- At this stage, we assume that you wish to update your record. There may be a typo in the title, a missing file, etc. Go to "My records" and click the record’s title.
- Click "New version" and "Import files".
- Make a few changes: change the title, add a file, remove a file, etc.
- Once you are satisfied with your changes, click "Share on archive".
- Navigate to "Shared records" and check that your record appears in the shared records’ list.
- Switch the toggle on the left side of the web page to display both versions of the record. Note that the toggle switch is off by default, thus only the latest record's version is displayed.
- Click any of its two versions. Find the card entitled "Versions" on the right side of the web page. You should be able to easily navigate from one version to the other by clicking the appropriate link.

### Ask a collaborator to create and share a third version of your record
- Click "My records".
- Find the latest version of your record and click its title. 
- Click "Collaborate" and "Get a link" to generate a URL that you will copy and send to another user of the archive. Equipped with this URL, he should be able to create a third version of the record.
- You can also ask him for the URL of one of his shared records so that you can create an extra version of that record.

### Search for a shared record using the archive’s built-in search engine
- Click "Shared records".
- Type "+Liot +WP9" into the search box to find all shared records whose metadata contains "Liot" and "WP9". Depending on the contents of the database, you may get zero, one, or more hits. If you wish to make more advanced queries (e.g., you wish to find all shared records where a specific field contains a specific value, read the search guide.

### Get an API access token
- To access endpoints of the archive’s web API from a client application, you should supply a valid access token on each request. To create a token, click "API access tokens" in the header’s drop-down menu on the right side of the page.
- Click "New token" and follow the displayed instructions. Note that the access token is shown only once and has an unlimited lifetime (unless you delete it). We recommend to keep it in a safe storage and not to share with anyone else.

## What you will accomplish using a client Python script

### Create and share a record via the API
- Clone the source code repository named [big-map-archive-api-examples](https://github.com/materialscloud-org/big-map-archive-api-examples) on GitHub.
- Follow the instructions in the `README.md` file.