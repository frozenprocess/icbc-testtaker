import imaplib
import re
import time
import config

def checkGmail():
    mail = imaplib.IMAP4_SSL(config.email_imap_address,config.email_imap_port)
    mail.login(config.email_username,config.email_password)
    mail.select('inbox')

    matched = []
    while len(matched) == 0:
        data = mail.search(None,"FROM","roadtests-donotreply@icbc.com")
        if data[1][0].decode("utf-8") != '':
            lastmail = data[1][0].decode("utf-8").split()[-1]
            data=mail.fetch(lastmail,'(RFC822)')[1][0][1].decode("utf-8")

            matched = re.findall(">([0-9]{6})<",data,re.MULTILINE)
        else:
            print("trying ...\n")
            time.sleep(10)
            # can not find the pin refresh the Inbox
            mail.recent()

    return matched[0]
