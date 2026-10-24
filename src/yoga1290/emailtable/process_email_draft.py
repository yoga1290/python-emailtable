import imaplib
import email
from email.message import EmailMessage
from email.policy import default
from email.utils import parseaddr
from datetime import datetime, timezone
import os


def _save_draft(
    imap,
    reply: EmailMessage,
    drafts_folder: str,
) -> EmailMessage:
    """Save an email to the IMAP Drafts folder."""

    status, response = imap.append(
        drafts_folder,
        r"(\Draft)",
        imaplib.Time2Internaldate(datetime.now(timezone.utc)),
        reply.as_bytes(policy=default),
    )

    if status != "OK":
        raise RuntimeError(f"Failed to save draft: {response}")

    return reply

import html
from email.message import EmailMessage


def _set_email_body(
    message: EmailMessage,
    body: str,
    is_html: bool = True,
) -> None:
    """Set an email body as HTML with a plain-text fallback."""

    if is_html:
        # Escape text to prevent accidental HTML interpretation.
        # Convert line breaks to HTML breaks while preserving paragraphs.
        escaped_body = body #html.escape(body).replace("\n", "<br>\n")
        html_body = (
            '<html><body>'
            '<div style="font-family: Arial, sans-serif; '
            'font-size: 14px; line-height: 1.6;">'
            + escaped_body
            + '</div></body></html>'
        )

        # Plain-text version first.
        message.set_content(body)

        # HTML alternative.
        message.add_alternative(
            html_body,
            subtype="html",
        )
    else:
        message.set_content(body)

def draft_email(
    imap,
    to_email: str,
    subject: str,
    reply_body: str,
    sender_email: str,
    drafts_folder: str = None,
) -> EmailMessage:
    """Create a new email draft and save it to Drafts."""

    drafts_folder = (
        drafts_folder
        or os.getenv("DRAFTS_FOLDER", "[Gmail]/Drafts")
    )

    recipient = parseaddr(to_email)[1]

    if not recipient:
        raise ValueError(f"Invalid recipient email: {to_email}")

    message = EmailMessage()
    message["From"] = sender_email
    message["To"] = recipient
    message["Subject"] = subject

    # message.set_content(reply_body)
    _set_email_body(message, reply_body)

    return _save_draft(imap, message, drafts_folder)


def draft_reply(
    imap,
    original_from: str,
    original_subject: str,
    original_message_id: str,
    original_references: str,
    reply_body: str,
    sender_email: str,
    drafts_folder: str = os.getenv("DRAFTS_FOLDER", "[Gmail]/Drafts"),
) -> EmailMessage:
    """Create a reply to an existing email and save it to Drafts."""

    recipient = parseaddr(original_from)[1]

    if not recipient:
        raise ValueError("The original email has no valid sender address.")

    message = EmailMessage()
    message["From"] = sender_email
    message["To"] = recipient

    subject = original_subject or ""

    if subject.lower().startswith("re:"):
        message["Subject"] = subject
    else:
        message["Subject"] = f"Re: {subject}"

    # Preserve email conversation threading.
    if original_message_id:
        message["In-Reply-To"] = original_message_id

    references = " ".join(
        value.strip()
        for value in (original_references, original_message_id)
        if value and value.strip()
    )

    if references:
        message["References"] = references

    # message.set_content(reply_body)
    _set_email_body(message, reply_body)


    return _save_draft(imap, message, drafts_folder)

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
    import os
    import imaplib
    import pandas as pd

    if not DRAFT_CSV_PATH:
        raise ValueError("DRAFT_CSV_PATH must be configured.")
    
    df = pd.DataFrame({
        f'{DRAFT_CSV_FILE_COLUMN}':[],
        f'{DRAFT_CSV_EMAIL_COLUMN}':[],
        f'{DRAFT_CSV_MESSAGE_ID_COLUMN}':[],
        f'{DRAFT_CSV_REFERENCES_COLUMN}':[],
        f'{DRAFT_CSV_SUBJECT_COLUMN}':[],
    })
    if os.path.exists(DRAFT_CSV_PATH):    
        df = pd.read_csv(DRAFT_CSV_PATH)

    sender_email = FROM_EMAIL or USERNAME
    results = []

    try:
        # Establish one IMAP connection for all records.
        with imaplib.IMAP4_SSL(
            IMAP_SERVER,
            int(IMAP_PORT),
        ) as imap:

            imap.login(USERNAME, APP_PASSWORD)

            for _, record in df.iterrows():
                body_filepath = record[DRAFT_CSV_FILE_COLUMN]
                to_email = record[DRAFT_CSV_EMAIL_COLUMN]
                subject = record[DRAFT_CSV_SUBJECT_COLUMN]

                try:
                    # Validate the body file path.
                    if pd.isna(body_filepath) or not str(body_filepath).strip():
                        raise ValueError("Email body filepath is empty.")

                    with open(
                        body_filepath,
                        "r",
                        encoding="utf-8",
                    ) as file:
                        body_content = file.read()

                    # Read threading headers from the CSV.
                    message_id = record[
                        DRAFT_CSV_MESSAGE_ID_COLUMN
                    ]

                    references = record[
                        DRAFT_CSV_REFERENCES_COLUMN
                    ]

                    message_id = (
                        "" if pd.isna(message_id)
                        else str(message_id).strip()
                    )

                    references = (
                        "" if pd.isna(references)
                        else str(references).strip()
                    )

                    # Create and save the reply draft.
                    draft_reply(
                        imap=imap,
                        original_from=to_email,
                        original_subject=subject,
                        original_message_id=message_id,
                        original_references=references,
                        reply_body=body_content,
                        sender_email=sender_email,
                        drafts_folder=DRAFT_FOLDER,
                    )

                    record_status = "OK"

                except Exception as ex:
                    record_status = f"ERROR: {ex}"

                    print(
                        f"Exception while processing record "
                        f"{to_email}, {subject}, {body_filepath}: {ex}"
                    )

                results.append(record_status)

    finally:
        # Ensure every processed record receives a status.
        df["Status"] = results + ["NOT PROCESSED"] * (
            len(df) - len(results)
        )

        df.to_csv(DRAFT_CSV_PATH, index=False)

    return df
