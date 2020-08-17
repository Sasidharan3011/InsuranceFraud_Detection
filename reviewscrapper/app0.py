# -*- coding: utf-8 -*-
"""
Created on Sat Mar 28 18:56:34 2020

@author: ELCOT
"""

from flask import Flask,render_template,request,jsonify
import requests
from bs4 import BeautifulSoup as bs
import pymongo

app=Flask(__name__)

@app.route('/',methods=(['POST','GET']))

def index():
    if request.method=='POST':
        searchstring=request.form['content'].replace(" ","")
        
        dbConn = pymongo.MongoClient("mongodb://localhost:27017/")
        db=dbConn['review_scrapperDB']
        reviews=db['searchstring'].find({})
        if reviews.count()>0:
            return render_template('results.html',reviews=reviews)
        else:
            flipkart_url = "https://www.flipkart.com/search?q=" + searchstring
            reqcon=requests.get(flipkart_url)
            bes=bs(reqcon.content,'html.parser')
            allreviews=bes.find_all('div', {"class": "_1HmYoV _35HD7C"})
            alllink=[]
            for i in allreviews:
                alllink.append(i.find("a").get("href"))
            prodlink=str(alllink[1])
            produrl="https://www.flipkart.com"+prodlink
            con=requests.get(produrl)
            review_soup=bs(con.content,'html.parser')
            #all_review = review_soup.find_all('a', {'href': 'col _39LH-M'})
            url=review_soup.find("div", {"class": "swINJg _3nrCtb"})
            data=str(url.find_parent().get("href"))
            baseurl="https://www.flipkart.com"
            url2=baseurl+data
            prodres=requests.get(url2)
            prodsoup=bs(prodres.content,'html.parser')
            prodreviews=prodsoup.find_all('div', {"class": "ooJZfD _2oZ8XT col-9-12"})
            table = db[searchstring]
            reviews=[]
            for review in prodreviews:
                try:
                    name=review.find_all("p",{"class":"_3LYOAd _3sxSiS"})
                    name=[e.get_text() for e in name]
                except:
                    name="no name"
                try:
                    rating=review.find_all("div",{"class":"hGSR34 E_uFuv"})
                    rating=[e.get_text() for e in rating]
                except :
                    rating="no rating"
                try:
                    head=review.find_all("p",{"class":"_2xg6Ul"})
                    head=[e.get_text() for e in head]
                except:
                    head="no head comment"
                try:
                    comment=review.find_all("div",{"class":"qwjRop"})
                    comment=[e.get_text() for e in comment]
                except :
                    comment="no comment "
                for i in range(len(name)):
                    
                    mydict = {"Product":searchstring,"Name":name[i],"Rating":rating[i],"CommentHead":head[i],"Comment":comment[i]}
                    x = table.insert_one(mydict)
                    reviews.append(mydict)
            return render_template('results.html', reviews=reviews)
    else:
        return render_template('index.html')
if __name__=="__main__":
    app.run(port=9999,debug=True)
                    
                