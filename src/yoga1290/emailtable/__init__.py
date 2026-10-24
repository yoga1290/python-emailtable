import os

def processIMAPToCSV(
    USERNAME= os.getenv('USERNAME', 'USERNAME-REQUIRED@gmail.com'),
    APP_PASSWORD= os.getenv('APP_PASSWORD', 'APP-PASSWORD'),
    IMAP_SERVER= os.getenv('IMAP_SERVER', 'imap.gmail.com'),
    IMAP_PORT= int(os.getenv('IMAP_PORT', 993)),
    IMAP_MAILBOX= os.getenv('IMAP_MAILBOX', 'INBOX'),
    IMAP_N_COUNT= os.getenv('IMAP_N_COUNT', '5'),

    IMAP_FROM_EMAIL=os.getenv('IMAP_FROM_EMAIL', None), # example: '<username>+<filter>@gmail.com'
    IMAP_TO_EMAIL=os.getenv('IMAP_TO_EMAIL', None), # example: '<username>+<filter>@gmail.com'
    IMAP_OUTPUT_DIR=os.getenv('IMAP_OUTPUT_DIR', './data'),
    IMAP_CSV_COL_MESSAGE_ID=os.getenv('IMAP_CSV_COL_MESSAGE_ID', 'msgId'),
    IMAP_CSV_COL_MESSAGE_REF=os.getenv('IMAP_CSV_COL_MESSAGE_REF', 'msgRef'),
    IMAP_CSV_COL_DATE=os.getenv('IMAP_CSV_COL_DATE', 'date'),
    IMAP_CSV_COL_FROM=os.getenv('IMAP_CSV_COL_FROM', 'from'),
    IMAP_CSV_COL_SUBJECT=os.getenv('IMAP_CSV_COL_SUBJECT', 'subject'),
    IMAP_CSV_COL_ATTACHMENT_PATH=os.getenv('IMAP_CSV_COL_ATTACHMENT_PATH', 'attachment'),
):
    import pandas as pd
    from . import process_imap_to_csv as imap2csv

    if IMAP_OUTPUT_DIR:
        data = imap2csv.processIMAPToCSV(USERNAME, APP_PASSWORD, IMAP_SERVER,
                                imap_port=IMAP_PORT,
                                mailbox=IMAP_MAILBOX,
                                most_recent_messages_count=int(IMAP_N_COUNT),
                                subject=None,
                                fromEmail=IMAP_FROM_EMAIL,
                                toEmail=IMAP_TO_EMAIL,
                                OUTPUT_DIR=IMAP_OUTPUT_DIR,
                                IMAP_CSV_COL_MESSAGE_ID=IMAP_CSV_COL_MESSAGE_ID,
                                IMAP_CSV_COL_MESSAGE_REF=IMAP_CSV_COL_MESSAGE_REF,
                                IMAP_CSV_COL_DATE=IMAP_CSV_COL_DATE,
                                IMAP_CSV_COL_FROM=IMAP_CSV_COL_FROM,
                                IMAP_CSV_COL_SUBJECT=IMAP_CSV_COL_SUBJECT,
                                IMAP_CSV_COL_ATTACHMENT_PATH=IMAP_CSV_COL_ATTACHMENT_PATH,)
        dataFrame = pd.DataFrame(data)
        dataFrame.to_csv(f'{IMAP_OUTPUT_DIR}/output.csv')


def processSMTP(
    USERNAME= os.getenv('USERNAME', 'USERNAME-REQUIRED@gmail.com'),
    APP_PASSWORD= os.getenv('APP_PASSWORD', 'APP-PASSWORD'),
    SMTP_SERVER= os.getenv('SMTP_SERVER', 'smtp.gmail.com'),
    SMTP_PORT= int(os.getenv('SMTP_PORT', '587')),
    
    SMTP_CSV_PATH=os.getenv('SMTP_CSV_PATH', None),
    SMTP_CSV_FILE_COLUMN=os.getenv('SMTP_CSV_FILE_COLUMN', None),
    SMTP_CSV_TO_EMAIL_COLUMN=os.getenv('SMTP_CSV_TO_EMAIL_COLUMN', None),
    SMTP_CSV_SUBJECT_COLUMN=os.getenv('SMTP_CSV_SUBJECT_COLUMN', None)
):
    import pandas as pd
    from . import process_csv_to_smtp
    
    if SMTP_CSV_PATH:
        outboxDF = pd.read_csv(SMTP_CSV_PATH)
        data = []
        for record in outboxDF.iloc:
            bodyFilepath = record[SMTP_CSV_FILE_COLUMN]
            toEmail = record[SMTP_CSV_TO_EMAIL_COLUMN]
            subject = record[SMTP_CSV_SUBJECT_COLUMN]
            status = ''
            try:
                bodyFilepath = record[SMTP_CSV_FILE_COLUMN]
                toEmail = record[SMTP_CSV_TO_EMAIL_COLUMN]
                subject = record[SMTP_CSV_SUBJECT_COLUMN]
                with open(bodyFilepath, 'r') as f:
                    bodyContent = f.read()
                    process_csv_to_smtp.sendmail(
                                username=USERNAME,
                                password=APP_PASSWORD,
                                smtp_server=SMTP_SERVER,
                                smtp_port=SMTP_PORT,
                                fromEmail=USERNAME,
                                toEmail=toEmail,
                                subject=subject,
                                body=bodyContent)
                    status = 'OK'
            except Exception as ex:
                status = ex
                print(f'Exception: {ex} while processing record {toEmail}, {subject}, {bodyFilepath}')
            data.append({
                    f'{SMTP_CSV_TO_EMAIL_COLUMN}':toEmail,
                    f'{SMTP_CSV_SUBJECT_COLUMN}':subject,
                    f'{SMTP_CSV_FILE_COLUMN}':bodyFilepath,
                    "Status":status})
            
        dataFrame = pd.DataFrame(data)
        dataFrame.to_csv(SMTP_CSV_PATH)


def proccessCSVDrafts(
    USERNAME=os.getenv("USERNAME", "USERNAME-REQUIRED@gmail.com"),
    APP_PASSWORD=os.getenv("APP_PASSWORD", "APP-PASSWORD"),
    IMAP_SERVER=os.getenv("IMAP_SERVER", "imap.gmail.com"),
    IMAP_PORT=os.getenv("IMAP_PORT", "993"),
    FROM_EMAIL=os.getenv("FROM_EMAIL", None),
    
    DRAFT_CSV_PATH=os.getenv("DRAFT_CSV_PATH", None),
    DRAFT_CSV_FILE_COLUMN=os.getenv("DRAFT_CSV_FILE_COLUMN", None),
    DRAFT_CSV_EMAIL_COLUMN=os.getenv("DRAFT_CSV_EMAIL_COLUMN", None),
    DRAFT_CSV_MESSAGE_ID_COLUMN=os.getenv(
        "DRAFT_CSV_MESSAGE_ID_COLUMN", None
    ),
    DRAFT_CSV_REFERENCES_COLUMN=os.getenv(
        "DRAFT_CSV_REFERENCES_COLUMN", None
    ),
    DRAFT_CSV_SUBJECT_COLUMN=os.getenv("DRAFT_CSV_SUBJECT_COLUMN", None),
    DRAFT_FOLDER=os.getenv("DRAFTS_FOLDER", "[Gmail]/Drafts"),
):
    from . import process_email_draft
    process_email_draft.proccessCSVDrafts(
        USERNAME=USERNAME,
        APP_PASSWORD=APP_PASSWORD,
        IMAP_SERVER=IMAP_SERVER,
        IMAP_PORT=IMAP_PORT,
        FROM_EMAIL=FROM_EMAIL,
        DRAFT_CSV_PATH=DRAFT_CSV_PATH,
        DRAFT_CSV_FILE_COLUMN=DRAFT_CSV_FILE_COLUMN,
        DRAFT_CSV_EMAIL_COLUMN=DRAFT_CSV_EMAIL_COLUMN,
        DRAFT_CSV_MESSAGE_ID_COLUMN=DRAFT_CSV_MESSAGE_ID_COLUMN,
        DRAFT_CSV_REFERENCES_COLUMN=DRAFT_CSV_REFERENCES_COLUMN,
        DRAFT_CSV_SUBJECT_COLUMN=DRAFT_CSV_SUBJECT_COLUMN,
        DRAFT_FOLDER=DRAFT_FOLDER,
    )