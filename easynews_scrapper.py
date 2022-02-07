#!/usr/bin/env python

"""easynews_scrapper.py: """

__author__      = "Indra"
__copyright__   = "Copyright 2022, Planet Earth"


from encodings import utf_8
import requests
from bs4 import BeautifulSoup
import json
            
def brmarking_to_list(markinginput):
    lbody = list()
    for c in markinginput.children:
        if str(c) != '<br/>':
            lbody.append(c)
    return lbody

def scrapper(inurl=str()):
    '''
    Return: 
    {
        title:<title>
        datetime_tag:date time
        datetime:date time
        summary: <summary>
        contentdata : [
            { bodytitle: [<body title>], bodytext:[<paragraph1>,<paragraph2>...<paragraphn>] },
            { bodytitle: [<body title>], bodytext:[<paragraph1>,<paragraph2>...<paragraphn>] }            
        ]
    }
    '''
    retdata = {}
    htmltxt = requests.get(inurl)
    htmltxt.encoding = htmltxt.apparent_encoding
    soup = BeautifulSoup(htmltxt.text,"html.parser")
    article = soup.find("section",class_ ="module--detail-content")
    if article == None:
        return None
        # raise Exception("Except",inurl)
    title = article.find("div",class_="content--detail-title")
    retdata['title']=title.h1.span.text
    retdata['datetime']=title.p.time.text
    retdata['datetime_tag']=title.p.time['datetime']

    mainbody = article.find("div",class_="content--detail-body")
    summary = mainbody.find(class_="content--summary")
    if summary is not None : retdata['summary'] = summary.text
    else : retdata['summary'] = ""

    detail = mainbody.find(class_= "content--detail-more")
    contentbodies = detail.find_all(class_="content--body")
    if contentbodies != []:
        contentlist = list()
        for contentbody in contentbodies:
            bodytitle = contentbody.find("h2", class_="body-title")
            bodytext = contentbody.find("div", class_="body-text")
            bodydict = {}
            if bodytitle !=None : bodydict['bodytitle'] = bodytitle.string
            else: bodydict['bodytitle'] = ""
            if bodytext !=None : bodydict['bodytext'] = brmarking_to_list(bodytext)
            else: bodydict['bodytext'] = ""
            contentlist.append(bodydict)
        retdata['contentdata'] = contentlist
    else:
        bodytexts = detail.find(class_="body-text")
        if bodytexts != None : retdata ['contentdata'] = [{'bodytitle':"",'bodytext':brmarking_to_list(bodytexts)}]

    contentsummarymore = detail.find(class_= "content--summary-more")
    if contentsummarymore != None: retdata ['summarymore'] = [{'bodytitle':"",'bodytext':brmarking_to_list(contentsummarymore)}]
    return retdata



def newslist():
    """
    [
        {news_id: "k10013457141000" , news_web_url: "https://www3.nhk.or.jp/n…130/k10013457141000.html" },
        {news_id: "k10013462211000" , news_web_url: "https://www3.nhk.or.jp/n…202/k10013462211000.html" }
    ]
    """
    resp = requests.get("https://www3.nhk.or.jp/news/easy/news-list.json")
    resp.encoding = resp.apparent_encoding
    datas = json.loads(resp.text)
    lsdates = list(datas[0])
    lsurl = list()
    for date in lsdates:
        lsnews = datas[0][date]
        for new in lsnews:
            lsurl.append({'news_id': new['news_id'],'news_web_url':new['news_web_url']})
    return lsurl
 

def extract_to_file(foutput,contentdata):
    for content in contentdata:
        if content['bodytitle'] != "":
            foutput.write("Body-Title: " + content['bodytitle']+'\n')
        bodytexts = content['bodytext']
        if bodytexts != []: foutput.write("Body-Text: \n")
        for texts in bodytexts:
            foutput.write(texts+'\n\n')


def scrapping_news():
    listnews = newslist()
    for news in listnews:
        data = scrapper(news['news_web_url'])
        if data == None : continue
        with open(news['news_id']+".txt","w+",encoding="utf_8") as foutput:
            foutput.write("News URL: "+news['news_web_url']+'\n')
            foutput.write("Title "+'\n')
            foutput.write(data['title']+'\n\n')
            foutput.write("Date and Time "+'\n')
            foutput.write(data['datetime']+'\n\n')
            foutput.write("Summary " +'\n')
            foutput.write(data['summary']+'\n\n')
            if 'summarymore' in data:
                foutput.write("Summary-More\n")
                extract_to_file(foutput,data['summarymore'])
                foutput.write("\n\n")                
            if 'contentdata' in data:
                foutput.write("Content-Data\n")                
                extract_to_file(foutput,data['contentdata'])


def mainapp():
    scrapping_news()


if __name__ == '__main__':
    mainapp()
