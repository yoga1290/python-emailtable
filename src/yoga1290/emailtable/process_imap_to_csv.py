def messageHandler(responseMsg, OUTPUT_DIR='.'):
    # see https://thepythoncode.com/article/reading-emails-in-python
    import os
    import email
    from email.header import decode_header
    # from datetime import datetime
    
    response = responseMsg

    msgId, msgRef, msgDate, From, subject, files = None, None, None, None, None, []

    def clean(msgDate, text):
        # clean text for creating a folder
        # ex: Wed, 5 Mar 2025 17:12:30 -0800
        msgDate = msgDate.replace(',', '').replace(':', '-').replace(' ', '_')
        if len(msgDate) > 0:
            msgDate  =  msgDate + '___'
        # datee = datetime.strptime(msgDate, '%a %b %d %Y').strftime('%d-%m-%Y')
        return msgDate + (''.join(c if c.isalnum() else "_" for c in text))
        
    def processMessage(OUTPUT_DIR=OUTPUT_DIR,
                                msgDate='',
                                subject='',
                                files=[],
                                file_content=None,
                                filename=None,
                                content_type='text/plain'):
            folder_name = OUTPUT_DIR + "/attachments/" + clean('', subject)
            if not os.path.isdir(folder_name):
                # make a folder for this email (named after the subject)
                os.makedirs(folder_name)
            ext = 'txt' if content_type == 'text/plain' else ''
            ext = 'html' if content_type == 'text/html' else ext
            ext = 'pdf' if content_type == 'application/pdf' else ext
            mode = "w" if content_type in ['text/plain', 'text/html'] else "wb" 
            filename = "index" if not filename else filename;
            filename = clean(msgDate, filename)+ '.' + ext;
            filepath = os.path.join(folder_name, filename)
            # write the file
            try:
                open(filepath, mode).write(file_content)
            except Exception as ex:
                filepath = f'Exception while writing {filename}: {ex}'
            files.append(filepath)
    
    if isinstance(response, tuple):
        # parse a bytes email into a message object
        msg = email.message_from_bytes(response[1])

        # print(f'message keys: {list(msg.keys())}')
        
        # decode the email Date
        msgDate, encoding = decode_header(msg["Date"])[0]
        if isinstance(msgDate, bytes):
            # if it's a bytes, decode to str
            msgDate = msgDate.decode(encoding)
        
        # decode the email subject
        subject, encoding = decode_header(msg["Subject"])[0]
        if isinstance(subject, bytes):
            # if it's a bytes, decode to str
            subject = subject.decode(encoding)
            
        # decode email sender
        From, encoding = decode_header(msg.get("From"))[0]
        if isinstance(From, bytes):
            From = f'{From}' if encoding is None else From.decode(encoding)
            
        # print("Date:", msgDate)
        # print("Subject:", subject)
        # print("From:", From)
        msgId = msg.get('Message-ID')
        msgRef = msg.get("References", "")
        
        # if the email message is multipart
        if msg.is_multipart():
            # iterate over email parts
            partCount = 1
            for part in msg.walk():
                # extract content type of email
                content_type = part.get_content_type()
                content_disposition = str(part.get("Content-Disposition"))
                try:
                    # get the email body
                    body = part.get_payload(decode=True).decode()
                except:
                    pass
                if content_type == "text/plain" and "attachment" not in content_disposition:
                    processMessage(OUTPUT_DIR=OUTPUT_DIR, msgDate=msgDate, subject=subject, files=files, file_content=body, filename='body', content_type=content_type)

                    
                elif "attachment" in content_disposition:
                    # download attachment
                    filename = part.get_filename()
                    filename = clean(f'{msgDate}-{partCount}', filename)
                    partCount = partCount + 1
                    # print(f'has attachment: {filename}')
                    if filename:
                        processMessage(OUTPUT_DIR=OUTPUT_DIR, msgDate=msgDate, subject=subject, files=files, file_content=part.get_payload(decode=True), filename=clean(f'{msgDate}-{partCount}', filename), content_type=content_type)

                        
        else:
            # extract content type of email
            content_type = msg.get_content_type()
            # get the email body
            body = msg.get_payload(decode=True).decode()
            if content_type == "text/plain":
                processMessage(OUTPUT_DIR=OUTPUT_DIR, msgDate=msgDate, subject=subject, files=files, file_content=body, filename=None, content_type=content_type)

                
        if content_type == "text/html":
            processMessage(OUTPUT_DIR=OUTPUT_DIR, msgDate=msgDate, subject=subject, files=files, file_content=body, filename=None, content_type=content_type)

            
            # open in the default browser
            #webbrowser.open(filepath)
        # print("="*100)


        # print(f'From:{From}')
        # print(f'subject:{subject}')
        # print(f'files:{files}')
        # print('=======================')
        
        return {'msgId':msgId,
                'msgRef': msgRef,
                'date':msgDate,
                'from': From,
                'subject': subject,
                'files': files }


def processIMAPToCSV(
        username,
        password,
        imap_server,
        imap_port=None,
        mailbox="INBOX",
        most_recent_messages_count=2,
        subject=None,
        fromEmail=None,
        toEmail=None,
        OUTPUT_DIR='.',
        IMAP_CSV_COL_MESSAGE_ID='msgId',
        IMAP_CSV_COL_MESSAGE_REF='msgRef',
        IMAP_CSV_COL_DATE='date',
        IMAP_CSV_COL_FROM='from',
        IMAP_CSV_COL_SUBJECT='subject',
        IMAP_CSV_COL_ATTACHMENT_PATH='attachment',
        ):
    
    import imaplib
    import email
    from email.header import decode_header
    # import webbrowser
    import os
    
    # create an IMAP4 class with SSL 
    if imap_port:
        imap = imaplib.IMAP4_SSL(imap_server, imap_port)
    else:
        imap = imaplib.IMAP4_SSL(imap_server)
    # authenticate
    imap.login(username, password)
    
    status, messages = imap.select(mailbox)
    
    # number of top emails to fetch
    N = most_recent_messages_count
        
    # total number of emails
    messages = int(messages[0])

    # see https://stackoverflow.com/a/2230571
    # see https://docs.python.org/3/library/imaplib.html#imaplib.IMAP4.search
    hasNoQuery = subject is None and fromEmail is None and toEmail is None
    messageIds = []
    criterion=[]
    if subject:
        criterion.append('SUBJECT "%s"' % subject)
        # typ, data = imap.search(None,'(SUBJECT "%s")' % subject)
        # messageIds.extend(data[0].split())
        # print('messageIds (subject)', messageIds)
    if fromEmail:
        criterion.append('FROM "%s"' % fromEmail)
        # typ, data = imap.search(None,'(FROM "%s")' % fromEmail)
        # messageIds.extend(data[0].split())
        # print('messageIds (domain)', messageIds)
    if toEmail:
        criterion.append('TO "%s"' % toEmail)
        # typ, data = imap.search(None,'(TO "%s")' % toEmail)
        # messageIds.extend(data[0].split())
        # print('messageIds (domain)', messageIds)
    if hasNoQuery:
        messageIds = [str(i) for i in range(messages, messages-N, -1)]
    else:
        typ, data = imap.search(None, f'({' '.join(criterion)})')
        messageIds.extend(data[0].split())

    msgIds, msgRefs, datesSent, FromEmails, files, subjects = [], [], [], [], [], []
    
    for i in messageIds:
        # fetch the email message by ID
        # res, msg = imap.fetch(str(i), "(RFC822)")
        res, msg = imap.fetch(i, "(RFC822)")
        for response in msg:
            try:
                messageHandlerData = messageHandler(response, OUTPUT_DIR)
                
                
                if messageHandlerData:
                    msgId, msgRef, From, subject, attachmentFilepaths, dateSent = messageHandlerData['msgId'], messageHandlerData['msgRef'], messageHandlerData['from'], messageHandlerData['subject'], messageHandlerData['files'], messageHandlerData['date']

                    
                    for filepath in attachmentFilepaths:
                        FromEmails.append(From)
                        subjects.append(subject)
                        files.append(filepath)
                        datesSent.append(dateSent)
                        msgIds.append(msgId)
                        msgRefs.append(msgRef)
            except Exception as e:
                print(f'Error: msgId: {i}. Exception: {e}')
    # close the connection and logout
    imap.close()
    imap.logout()
    return {f'{IMAP_CSV_COL_MESSAGE_ID}':msgIds,
            f'{IMAP_CSV_COL_MESSAGE_REF}':msgRefs,
            f'{IMAP_CSV_COL_DATE}':datesSent,
            f'{IMAP_CSV_COL_FROM}': FromEmails,
            f'{IMAP_CSV_COL_SUBJECT}': subjects,
            f'{IMAP_CSV_COL_ATTACHMENT_PATH}': files }