from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from math import ceil

import imaplib
import email
from email.header import decode_header
import webbrowser
import os

import smtplib
from email import encoders
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from bs4 import BeautifulSoup as bs

imap = None

def first(request):
    global imap
    if 'user_email' in request.session:
        ee=request.session.get('user_email')
        pe=request.session.get('user_pass')
        imap = imaplib.IMAP4_SSL("imap.zoho.in",port=993)
        imap.login(ee, pe)
        return HttpResponseRedirect('/mailBox/0/0')
    return HttpResponseRedirect('login')

def getMail(request,mbn,mid):
    boxes=getMailBoxes()
    imap.select(boxes[mbn])
    msg=imap.fetch(str(mid),"(RFC822)")[1]
    attachments = getattachment(mid,boxes[mbn])
    if (len(attachments)==0):
        attachments=False
    for r in msg:
        if(isinstance(r,tuple)):
            c=email.message_from_bytes(r[1])
            s=decode_header(c["Subject"])[0][0]   #Subject o Email
            f=c["From"]                       #Sender Name n Email
            n=""
            e=""
            if(len(f.split("<"))>1):
                n=f.split("<")[0].strip("\" ")
                e=f.split("<")[1].strip("\" >")
            else:
                e=f.strip("\" >")
            d=c["Date"]
            if c.is_multipart() :
                for p in c.walk():
                    ct=p.get_content_type()
                    cd=str(p.get("Content-Disposition"))
                    try:
                        b=p.get_payload(decode=True).decode()
                    except:
                        pass
                    if ct == "text/html" and "attachment" not in cd:
                        return render(request,"client/MailView.html",{"sub":s,"from":f,"con":b,"name":n,"fmail":e,"date":d,"boxes":boxes,"boxnum":mbn,"mid":mid,"atlist":attachments})
            else:
                ct = c.get_content_type()
                b = c.get_payload(decode=True).decode()
                if ct == "text/plain":
                    return render(request,"client/MailView.html",{"sub":s,"from":f,"con":b,"boxes":boxes,"boxnum":mbn,"mid":mid,"atlist":attachments})

def getSubjects(total,page,search=False,searchList=None):
    subjectList={}
    if search:
        if searchList!=None:
            for i in searchList:
                flag=False
                response=imap.fetch(str(i),'(FLAGS)')[1][0]
                response=response.decode()
                if('Flagged' in response):
                    flag=True
                response=imap.fetch(str(i),"(RFC822)")[1][0]
                msg=email.message_from_bytes(response[1])
                s=decode_header(msg["Subject"])[0][0]
                if isinstance(s,bytes):
                    s=s.decode()
                f=msg["From"]
                #n=f.split("<")[0].strip("\" ")
                d=msg["Date"][:16]
                subjectList[(s,f,d,flag)]=i
            return subjectList
    on1page=10
    start=total-((page-1)*on1page)
    end=start-10
    while(start>end and start>0):
        flag=False
        response=imap.fetch(str(start),'(FLAGS)')[1][0]
        response=response.decode()
        if('Flagged' in response):
            flag=True
        response=imap.fetch(str(start),"(RFC822)")[1][0]
        msg=email.message_from_bytes(response[1])
        s=decode_header(msg["Subject"])[0][0]
        if isinstance(s,bytes):
            s=s.decode()
        f=msg["From"]
        #n=f.split("<")[0].strip("\" ")
        d=msg["Date"][:16]
        subjectList[(s,f,d,flag)]=start
        start-=1
    return subjectList


def clearBox(a):
    return a.split("/")[1].strip("\" ")


def getMailBoxes():
    global imap
    mailBoxes=[]
    for i in imap.list()[1]:
        mailBoxes.append(clearBox(i.decode("utf-8")))
    return mailBoxes


def login(request):
    return render(request,"client/Login.html")


def logchecker(request):
    global imap
    ee=request.POST['email']
    pe=request.POST['pass']
    request.session['user_email']=ee
    request.session['user_pass']=pe
    imap = imaplib.IMAP4_SSL("imap.zoho.in",port=993)
    imap.login(ee, pe)
    selected=0
    page=0
    return HttpResponseRedirect("/mailBox/"+str(selected)+"/"+str(page))

def mailBox(request,mn,page,searchEnb=None):
    boxes=getMailBoxes()
    imap.select(boxes[mn])

    search=False
    searchList=None

    if (searchEnb!=None):
        typ,msgno = imap.search(None, 'FROM', searchEnb)
        searchList = [int(x) for x in msgno[0].split()]
        search=True

    total = int(imap.select(boxes[mn])[1][0])
    subjects=getSubjects(total,page+1,search,searchList)
    totalpages=ceil(total/10)-1
    ms=total-(page*10)
    me=ms-10
    if me<0:
        me=0
    return render(request,"client/InboxView.html",{"Box":boxes,"Sub":subjects,"currBox":mn,
"currPage":page,"Totpage":totalpages,"startmail":ms,"endMail":me})

def logout(request):
    del request.session['user_email']
    del request.session['user_pass']
    imap.logout()
    return HttpResponseRedirect("/")

def composeMail(request):
    return render(request,"client/ComposeMail.html")

def packmsg(from1,to,subject,body,cc):
    msg = MIMEMultipart("alternative")
    msg["From"] = from1
    msg["To"] = to
    msg['Cc']=cc
    msg["Subject"] = subject

    html = "<div>"+body+"</div>"

    text = bs(html, "html.parser").text

    text_part = MIMEText(text, "plain")
    html_part = MIMEText(html, "html")

    msg.attach(text_part)
    msg.attach(html_part)
    return msg

def mailfunction(email,password,FROM,TO,CC,msg):
    server = smtplib.SMTP_SSL("smtp.zoho.in", 465)
    server.login(email, password)
    server.sendmail(FROM, (TO+CC) , msg.as_string())
    server.quit()

def getlist(a):
    g=[]
    for i in a.split(","):
        g.append(i.strip(" "))
    return ((", ".join(g)),g)

def sendMail(request):
    to=request.POST['sendto']
    sub=request.POST['subject']
    cc=request.POST['cc']
    body=request.POST['mailBody']

    reclist=getlist(to)
    cclist=getlist(cc)

    ue=request.session['user_email']
    up=request.session['user_pass']

    msg=packmsg(ue,reclist[0],sub,body,cclist[0])
    mailfunction(ue,up,ue,reclist[1],cclist[1],msg)

    return HttpResponseRedirect("/")

def deletethis(dl):
    for curr in dl:
        imap.store(str(curr), '+FLAGS', '\Deleted')
        imap.expunge()

def deleteMail(request):
    dl=request.POST.getlist('checks')
    deletethis(dl)
    return HttpResponseRedirect("/")

def createnewbox(a):
    imap.create(a)
    return

def createbox(request):
    newbox=request.POST['newbox']
    createnewbox(newbox)
    return HttpResponseRedirect("/")

def flagmail(request,mid):
    imap.store(str(mid),'+FLAGS','\\Flagged')
    return HttpResponseRedirect("/")

def removeflag(request,mid):
    imap.store(str(mid),'-FLAGS','\\Flagged')
    return HttpResponseRedirect("/")

def movemail(request,mbn,mid,box):
    boxes=getMailBoxes()

    result = imap.copy(str(mid),boxes[box])
    deletethis([mid])

    return HttpResponseRedirect("/")

def getattachment(mailno,box):
    res, msg = imap.fetch(str(mailno), "(RFC822)")
    response = msg[0]
    msg = email.message_from_bytes(response[1])
    attach = []

    for part in msg.walk():
        if 'attachment' in str(part.get("Content-Disposition")):
            filename = part.get_filename()
            if filename:
                attach.append(filename)
    return attach

def downloadAttached(request, mid):
    res, msg = imap.fetch(str(mid), "(RFC822)")
    response = msg[0]
    msg = email.message_from_bytes(response[1])
    for part in msg.walk():
        if 'attachment' in str(part.get("Content-Disposition")):
            filename = part.get_filename()
            if filename:
                print('attachment_found : ',filename)
                if not os.path.isdir(str(mid)):
                    os.mkdir(str(mid))
                filepath = os.path.join(str(mid), filename)
                open(filepath, "wb").write(part.get_payload(decode=True))
    return HttpResponseRedirect('#')

#def

def searchThis(request):
    q=request.POST['query']
    return mailBox(request,0,0,q)

def Feedback(request):
    return render(request,"client/help.html")
