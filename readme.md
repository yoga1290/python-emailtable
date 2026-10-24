# Table-Based Email Automation

### Outline

- [**📥 Pull Emails (IMAP)**](#%EF%B8%8F-pull-emails-imap)
- [**📝️ Draft emails**](#%EF%B8%8F-draft-emails)
- [**📤️ Send Emails (SMTP)**](#%EF%B8%8F-send-emails-smtp)
- [**📦️ Run in Docker Containers**](#%EF%B8%8F-run-in-docker-containers)

# 📥️ Pull Emails (IMAP)

A good practice is to read inputs that are coming from Envirnoment Variables.
This will help passing down configurations from (Docker) Containers and/or Kubernetes to my actual running code.

Here are the **Environment Variables** needed:
```shell
USERNAME=email@gmail.com
APP_PASSWORD=app-password
IMAP_SERVER=imap.gmail.com
IMAP_PORT=993
IMAP_OUTPUT_DIR=./data #Optional; flags for inbox process
IMAP_FROM_EMAIL=email<+filter>@gmail.com
IMAP_TO_EMAIL=email<+filter>@gmail.com
######################
# OPTIONAL VARIABLES #
######################
IMAP_N_COUNT=1
IMAP_MAILBOX=INBOX
IMAP_CSV_COL_MESSAGE_ID=msgId
IMAP_CSV_COL_MESSAGE_REF=msgRef
IMAP_CSV_COL_DATE=date
IMAP_CSV_COL_FROM=email
IMAP_CSV_COL_SUBJECT=subject
IMAP_CSV_COL_ATTACHMENT_PATH=attachment
```


```python
!source .env # load ENV variables from file; if needed
!pip install yoga1290.emailtable

from yoga1290.emailtable import processIMAPToCSV
processIMAPToCSV(
    # USERNAME= os.getenv('USERNAME', 'USERNAME-REQUIRED@gmail.com'),
    # APP_PASSWORD= os.getenv('APP_PASSWORD', 'APP-PASSWORD'),
    # IMAP_SERVER= os.getenv('IMAP_SERVER', 'imap.gmail.com'),
    # IMAP_PORT= int(os.getenv('IMAP_PORT', 993)),
    # IMAP_MAILBOX= os.getenv('IMAP_MAILBOX', 'INBOX'),
    # IMAP_N_COUNT= os.getenv('IMAP_N_COUNT', '5'),

    # IMAP_FROM_EMAIL=os.getenv('IMAP_FROM_EMAIL', None), # example: '<username>+<filter>@gmail.com'
    # IMAP_TO_EMAIL=os.getenv('IMAP_TO_EMAIL', None), # example: '<username>+<filter>@gmail.com'
    # IMAP_OUTPUT_DIR=os.getenv('IMAP_OUTPUT_DIR', './data'),
    # IMAP_CSV_COL_MESSAGE_ID=os.getenv('IMAP_CSV_COL_MESSAGE_ID', 'msgId'),
    # IMAP_CSV_COL_MESSAGE_REF=os.getenv('IMAP_CSV_COL_MESSAGE_REF', 'msgRef'),
    # IMAP_CSV_COL_DATE=os.getenv('IMAP_CSV_COL_DATE', 'date'),
    # IMAP_CSV_COL_FROM=os.getenv('IMAP_CSV_COL_FROM', 'from'),
    # IMAP_CSV_COL_SUBJECT=os.getenv('IMAP_CSV_COL_SUBJECT', 'subject'),
    # IMAP_CSV_COL_ATTACHMENT_PATH=os.getenv('IMAP_CSV_COL_ATTACHMENT_PATH', 'attachment'),
)
```


```python
import pandas as pd
import os

IMAP_OUTPUT_DIR=os.getenv("IMAP_OUTPUT_DIR", None)
outboxDF = pd.read_csv(f'{IMAP_OUTPUT_DIR}/output.csv')
outboxDF.head(5)
```




<div>

<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>msgId</th>
      <th>msgRef</th>
      <th>date</th>
      <th>email</th>
      <th>subject</th>
      <th>content_path</th>
    </tr>
  </thead>
  <tbody>
  </tbody>
</table>
</div>



# 📝️ Draft emails

The **Environment Variables** passed as parameters:
```shell
USERNAME=email@gmail.com
APP_PASSWORD=app-password
IMAP_SERVER=imap.gmail.com
IMAP_PORT=993
DRAFT_CSV_PATH=./data/output.csv
DRAFT_CSV_EMAIL_COLUMN=email
DRAFT_CSV_MESSAGE_ID_COLUMN=msgId
DRAFT_CSV_REFERENCES_COLUMN=msgRef
DRAFT_CSV_SUBJECT_COLUMN=subject
DRAFT_CSV_FILE_COLUMN=content_path
DRAFTS_FOLDER="[Gmail]/Drafts"
```


```python
!source .env # load ENV variables from file; if needed
!pip install yoga1290.emailtable

from yoga1290.emailtable import proccessCSVDrafts
proccessCSVDrafts(
    # USERNAME=os.getenv("USERNAME", "USERNAME-REQUIRED@gmail.com"),
    # APP_PASSWORD=os.getenv("APP_PASSWORD", "APP-PASSWORD"),
    # IMAP_SERVER=os.getenv("IMAP_SERVER", "imap.gmail.com"),
    # IMAP_PORT=os.getenv("IMAP_PORT", "993"),
    # FROM_EMAIL=os.getenv("FROM_EMAIL", None),
    
    # DRAFT_CSV_PATH=os.getenv("DRAFT_CSV_PATH", None),
    # DRAFT_CSV_FILE_COLUMN=os.getenv("DRAFT_CSV_FILE_COLUMN", None),
    # DRAFT_CSV_EMAIL_COLUMN=os.getenv("DRAFT_CSV_EMAIL_COLUMN", None),
    # DRAFT_CSV_MESSAGE_ID_COLUMN=os.getenv(
    #     "DRAFT_CSV_MESSAGE_ID_COLUMN", None
    # ),
    # DRAFT_CSV_REFERENCES_COLUMN=os.getenv(
    #     "DRAFT_CSV_REFERENCES_COLUMN", None
    # ),
    # DRAFT_CSV_SUBJECT_COLUMN=os.getenv("DRAFT_CSV_SUBJECT_COLUMN", None),
    # DRAFT_FOLDER=os.getenv("DRAFTS_FOLDER", "[Gmail]/Drafts"),
)
```


```python
import pandas as pd
import os

DRAFT_CSV_PATH=os.getenv("DRAFT_CSV_PATH", None)
outboxDF = pd.read_csv(f'{DRAFT_CSV_PATH}')
outboxDF.head(5)
```




<div>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>msgId</th>
      <th>msgRef</th>
      <th>date</th>
      <th>email</th>
      <th>subject</th>
      <th>content_path</th>
      <th>Status</th>
    </tr>
  </thead>
  <tbody>
  </tbody>
</table>
</div>



# 📤️ Send Emails (SMTP)


```python
!source .env # load ENV variables from file; if needed
!pip install yoga1290.emailtable

from yoga1290.emailtable import processSMTP
processSMTP(
    # USERNAME= os.getenv('USERNAME', 'USERNAME-REQUIRED@gmail.com'),
    # APP_PASSWORD= os.getenv('APP_PASSWORD', 'APP-PASSWORD'),
    # SMTP_SERVER= os.getenv('SMTP_SERVER', 'smtp.gmail.com'),
    # SMTP_PORT= int(os.getenv('SMTP_PORT', '587')),
    
    # SMTP_CSV_PATH=os.getenv('SMTP_CSV_PATH', None),
    # SMTP_CSV_FILE_COLUMN=os.getenv('SMTP_CSV_FILE_COLUMN', None),
    # SMTP_CSV_EMAIL_COLUMN=os.getenv('SMTP_CSV_EMAIL_COLUMN', None),
    # SMTP_CSV_SUBJECT_COLUMN=os.getenv('SMTP_CSV_SUBJECT_COLUMN', None),
)
```


```python
import pandas as pd
import os

SMTP_CSV_PATH=os.getenv('SMTP_CSV_PATH', None)
pd.read_csv(SMTP_CSV_PATH).head(5)
```




<div>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>msgId</th>
      <th>msgRef</th>
      <th>date</th>
      <th>email</th>
      <th>subject</th>
      <th>content_path</th>
    </tr>
  </thead>
  <tbody>
  </tbody>
</table>
</div>



# 📦️ Run in Docker Containers

One way I use it, I trigger it as part of chain of jobs, each runs on seperate docker container; running one by one, example: `emailtable-job2` following `emailtable-job1`, so my `docker-compose.yml` would look like the following:

```yaml
# docker-compose.yml

emailtable-job2:
    env_file:
      - .env
    depends_on:
      emailtable-job1:
        condition: service_completed_successfully
    image: ghcr.io/yoga1290/python-emailtable:26.10
    # my docker image here is just based on python:3.13-alpine with my package pre-installed; saves network over time.
    working_dir: /app
    volumes:
      - .:/app
    command:
      - python
      - -c
      - |
        from yoga1290.emailtable import (
                        proccessCSVDrafts,
                        processIMAPToCSV,
                        processSMTP )
        # proccessCSVDrafts() #...
```
```shell
$ > docker compose up emailtable-job2
```