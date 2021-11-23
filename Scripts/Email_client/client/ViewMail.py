import imaplib
import email
from email.header import decode_header
import webbrowser
import os

def getMail(id,mailBox):
    imap.select(mailBox)
    msg=imap.fetch(str(id),"(RFC822)")[1]
    for r in msg:
        if(isinstance(r,tuple)):
            c=email.message_from_bytes(r[1])
            s=decode_header(c["Subject"])[0][0]   #Subject o Email
            f=c["From"]                       #Sender Name n Email
            print(s)
            print(f,"\n#########\n")
            if c.is_multipart() :
                for p in c.walk():
                    ct=p.get_content_type()
                    cd=str(p.get("Content-Disposition"))
                    try:
                        b=p.get_payload(decode=True).decode()
                    except:
                        pass
                    if ct == "text/plain" and "attachment" not in cd:
                        print(b)

def getSubjects(total,page):
    subjectList=[]
    on1page=10
    start=total-((page-1)*on1page)
    end=start-10
    while(start>end and start>0):
        for i in imap.fetch(str(start),"(RFC822)")[1]:
            if isinstance(i,tuple):
                c=email.message_from_bytes(i[1])
                s=decode_header(c["Subject"])[0][0]
                subjectList.append(s)
        start-=1
    return subjectList


def clearBox(a):
    return a.split("/")[1].strip("\" ")

# account credentials
#username = "abhishek.test@zohomail.in"
#password = "Abhishek@113"

# create an IMAP4 class with SSL
#imap = imaplib.IMAP4_SSL("imap.zoho.in",port=993)
# authenticate
#imap.login(username, password)

def getMailBoxes():
    mailBoxes=[]
    for i in imap.list()[1]:
        mailBoxes.append(clearBox(i.decode("utf-8")))
    return mailBoxes

#selected=0

#print(imap.select(mailBoxes[selected]),"\n\n")

#status, messages = imap.select("INBOX")
# number of top emails to fetch
#N = 3
# total number of emails
#messages = int(messages[0])
'''msg=imap.fetch("2","(RFC822)")[1]'''

'''for r in msg:
    if(isinstance(r,tuple)):
        c=email.message_from_bytes(r[1])
        s=decode_header(c["Subject"])[0][0]   #Subject o Email
        f=c["From"]                       #Sender Name n Email
        print(s)
        print(f,"\n#########\n")
        if c.is_multipart() :
            for p in c.walk():
                ct=p.get_content_type()
                cd=str(p.get("Content-Disposition"))
                try:
                    b=p.get_payload(decode=True).decode()
                except:
                    pass
                if ct == "text/plain" and "attachment" not in cd:
                    print(b)

print(getSubjects(2,1))
'''
'''for i in range(messages, messages-N, -1):
    # fetch the email message by ID
    res, msg = imap.fetch(str(i), "(RFC822)")
    for response in msg:
        if isinstance(response, tuple):
            # parse a bytes email into a message object
            msg = email.message_from_bytes(response[1])
            # decode the email subject
            subject = decode_header(msg["Subject"])[0][0]
            if isinstance(subject, bytes):
                # if it's a bytes, decode to str
                subject = subject.decode()
            # email sender
            from_ = msg.get("From")
            print("Subject:", subject)
            print("From:", from_)
            # if the email message is multipart
            if msg.is_multipart():
                # iterate over email parts
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
                        # print text/plain emails and skip attachments
                        print(body)
                    elif "attachment" in content_disposition:
                        # download attachment
                        filename = part.get_filename()
                        if filename:
                            if not os.path.isdir(subject):
                                # make a folder for this email (named after the subject)
                                os.mkdir(subject)
                            filepath = os.path.join(subject, filename)
                            # download attachment and save it
                            open(filepath, "wb").write(part.get_payload(decode=True))
            else:
                # extract content type of email
                content_type = msg.get_content_type()
                # get the email body
                body = msg.get_payload(decode=True).decode()
                if content_type == "text/plain":
                    # print only text email parts
                    print(body)
            print("="*100)
'''
#imap.close()
#imap.logout()
