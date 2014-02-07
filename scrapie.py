from bs4 import BeautifulSoup
import time
import datetime
import requests
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
import smtplib
import pickle

def get_soup(url):
    r = requests.get(url)
    data = r.text
    return BeautifulSoup(data)

def get_page_links(url, soup, words):
    page_links = []
    for link in soup.find_all('a'):
        #print(link.text)
        for word in words:
            if  word in link.text.lower():
                link_dic = grab_link(url, link)
                if link_dic:
                    page_links.append(link_dic) 
                    break
                else:
                    pass
            else:
                pass
    return page_links

def grab_link(url, link):
    if "reddit" in url:
        parent_links = link.parent.parent.find_all('a', class_="comments")
        if parent_links:
            comment = parent_links[0].get('href')
            content = {"title": link.text.encode('ascii', 'ignore'), "link": comment, "source": url}
        else:
            return {}
    elif "http" in link.get('href'):
        content = {"title": link.text, "link": link.get('href'), "source": url}
    else:
        content = {"title" : link.text, "link" : url + link.get('href'), "source": url}
    return content

def crawler(sources, words):                                                        
    total_links = []                                                                 
    for url in sources:                                                             
        page_links = []
        soup = get_soup(url)
        page_links = get_page_links(url, soup, words)
        total_links = total_links + page_links
    return total_links

def sendmail(fromaddr, toaddrlist, messagelist, password, subject = "3D printing post(s)", smtpserver = "smtp.gmail.com:587"):
    print"Got inside function"
    header = "From: %s\n" % fromaddr
    header += "To: %s\n" % ",".join(toaddrlist)
    header += "Subject: %s\n\n" % subject
    content = ""
    for m in messagelist:
        content += "Site: %s\n" % m['source']
        content += "Title: %s\n" % m['title']
        content += "Link: %s\n\n" % m['link']
    message = header + content
    print(message)
    server = smtplib.SMTP(smtpserver)
    print("started server")
    server.starttls()
    print("got before login")
    server.login(fromaddr, password)
    problems = server.sendmail(fromaddr, toaddrlist, message)
    print(problems)
    server.quit()

fromaddr = ""
toaddr = []
pas = ""
sites_to_monitor = []
words_to_look_for = []


try:
    has_seen_list = pickle.load( open( "has_seen_list.p", "rb" ))
except (IOError, EOFError):
    has_seen_list = []

count = 0 
while True:
    print("This is count %d. At %s" % (count, datetime.datetime.now().time()))
    this_pass_list = []
    msg = []
    crawler_dic_list = crawler(sites_to_monitor, words_to_look_for)
    for dic in crawler_dic_list:
        if dic['link'] in has_seen_list:
            pass
        else:
            print "=============="
            msg.append(dic)
            print(dic['source'])
            print(dic['title'])
            print(dic['link'])
            this_pass_list.append(dic['link'])
    if len(this_pass_list):
        has_seen_list += this_pass_list
        sendmail(fromaddr, toaddr, msg, pas)
        pickle.dump( has_seen_list, open("has_seen_list.p", "w"))
    else:
        pass
    time.sleep(1)
    count += 1
