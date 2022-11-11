"""users.json file generator

This script allows users to generate a file called users.json in the app_data folder
from an Excel file called users.xlsx also located in the app_data folder.

The input file users.xlsx is expected to have a column called E-mail in sheet 1.
The contents of the output file users.json is structured as follows:
`[
  {
    "email": "aaa@bbb.cc",
    "BIGMAP": True
  },
  {
    "email": "ddd@eee.ff",
    "BIGMAP": True
  },
    ...
]`.

Note that:
- None of these two files should be pushed to a GitHub repository (secrets).
- This script requires that pandas and openpyxl be installed within the virtual environment you are running this script in.
- The script register_users.py creates user accounts from users.json.
"""

import pandas as pd
import os
import json
import errno

if __name__ == '__main__':

    input_file = '../app_data/users.xlsx'
    sheet_name = 'Sheet1'
    output_file = '../app_data/users.json'

    try:
        # get list of emails from input file
        df = pd.read_excel(input_file, sheet_name=sheet_name)
        emails = df["E-mail"].tolist()

        # remove file if already exists
        if os.path.exists(output_file):
            os.remove(output_file)

        # create empty output file
        f = open(output_file, "x")

        # create a list of users
        users = []
        for email in emails:
            user = {'email': email, 'BIG-MAP': True}
            users.append(user)

        # dump list of users into output file
        with open(output_file, mode='w', encoding='utf-8') as f:
            json.dump(users, f)
    except Exception as e:
        print(e)

