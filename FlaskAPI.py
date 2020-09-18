import os, requests
from flask import Flask, json, render_template, request
import mysql.connector
from flask_restful import Api, Resource
from bs4 import BeautifulSoup


my_json = {"veriler": []}
db = mysql.connector.connect(user='root', password="123456",host='127.0.0.1', database='deneme_shema')
api = Flask(__name__,template_folder='templates')

#Anasayfa
@api.route('/',methods=['GET'])
def home():
    return render_template('homepage.html')


#Verileri çek.
@api.route('/scrapnews', methods=['GET'])
def scrap_news():
    firstReq = requests.get("https://news.google.com/topics/CAAqJggKIiBDQkFTRWdvSUwyMHZNRGx1YlY4U0FuUnlHZ0pVVWlnQVAB?hl=tr&gl=TR&ceid=TR%3Atr")
    firstSoup = BeautifulSoup(firstReq.text, 'html.parser')
    my_json = {"veriler": []}
    currentDocs = []
    with open('dailynews.json', 'r', encoding='utf-8') as file: data = json.load(file)
    for item in data["veriler"]:
        try:currentDocs.append(item["News Url"])
        except:pass


    articles = firstSoup.find_all('article', class_='MQsxIb xTewfe R7GTQ keNKEd j7vNaf Cc0Z5d EjqUne')[:6]
    for data in articles:
        if str(data.find('a')['href']).replace('.', 'https://news.google.com') in currentDocs:
            return "<h4>Mevcut veri zaten var.</h4>"
        else:
            #NewsContent = data.find('div', class_='Da10Tb Rai5ob').text
            #NewsContent = data.find('h4',class_='ipQwMb ekueJc RD0gLb').text
            NewsContent = data.find('a', class_='DY5T1d').text
            NewsTitle = data.find('h3', class_='ipQwMb ekueJc RD0gLb').text
            NewsUrl = str(data.find('a')['href']).replace('.', 'https://news.google.com')

            newsImg = firstSoup.find_all('img', class_='tvs3Id QwxBBf')
            global NewsIMG
            for imgs in newsImg:
                NewsIMG = imgs['src']

            data_to_json = {
                    "News Title": NewsTitle,
                    "News Content": NewsContent,
                    "News Url": NewsUrl,
                    "News IMG": NewsIMG}

            my_json["veriler"].append(data_to_json)

    with open('dailynews.json','w+',encoding='UTF-8') as file:
        json.dump(my_json, file, indent=4, ensure_ascii=False, sort_keys = True, separators = (',', ': '))


    return json.dumps(my_json["veriler"], ensure_ascii=False, indent=4)

@api.route('/scraptechnews', methods=['GET'])
def scrap_technews():
    firstReq = requests.get("https://news.google.com/topics/CAAqKAgKIiJDQkFTRXdvSkwyMHZNR1ptZHpWbUVnSjBjaG9DVkZJb0FBUAE?hl=tr&gl=TR&ceid=TR:tr")
    firstSoup = BeautifulSoup(firstReq.text, 'html.parser')
    my_json = {"veriler": []}
    currentDocs = []
    with open('technews.json', 'r', encoding='utf-8') as file: data = json.load(file)

    for item in data["veriler"]:
        try:currentDocs.append(item["News Url"])
        except:pass

    articles = firstSoup.find_all('article', class_='MQsxIb xTewfe R7GTQ keNKEd j7vNaf Cc0Z5d EjqUne')[:5]
    for data in articles:
        if str(data.find('a')['href']).replace('.', 'https://news.google.com') in currentDocs:
            return "<h4>Bu verileri daha önce kayıt etmiştik.</h4>"
        else:
            NewsContent = data.find('div', class_='Da10Tb Rai5ob').text
            NewsTitle = data.find('h3', class_='ipQwMb ekueJc RD0gLb').text
            NewsUrl = str(data.find('a')['href']).replace('.', 'https://news.google.com')

            newsImg = firstSoup.find_all('img', class_='tvs3Id QwxBBf')
            global NewsIMG
            for imgs in newsImg:
                NewsIMG = imgs['src']

            data_to_json = {
                "News Title": NewsTitle,
                "News Content": NewsContent,
                "News Url": NewsUrl,
                "News IMG": NewsIMG
            }

            my_json["veriler"].append(data_to_json)

    with open('technews.json', 'w+', encoding='UTF-8') as file:
        json.dump(my_json, file, indent=4, ensure_ascii=False, sort_keys=True, separators=(',', ': '))

    return json.dumps(my_json["veriler"], ensure_ascii=False, indent=4)

#Verileri kayıt et.
@api.route('/savetech', methods=['GET'])
def savetech_db():
    file = os.path.abspath('technews.json')
    json_data = open(file,encoding="utf-8", errors='ignore').read()
    json_obj = json.loads(json_data)
    sql_select = "select * from googletechnews"
    cursor = db.cursor()
    cursor.execute(sql_select)
    saved_data = cursor.fetchall()
    currentDocs = []

    with open('technews.json', 'r', encoding='utf-8') as file: data = json.load(file)
    for item in data["veriler"]:
        try:currentDocs.append(item["News Url"])
        except: pass

    if not saved_data:
        for ord in json_obj["veriler"]:
            cursor.execute(
                "INSERT INTO googletechnews (NewsURL, NewsTitle, NewsContent, NewsIMG) VALUES (%s,%s,%s, %s)",
                (ord["News Url"], str(ord["News Title"]).encode('ascii', 'ignore'),
                 str(ord["News Content"]).encode('ascii', 'ignore'), ord["News IMG"]))

        db.commit()
        cursor.close()
        return "<h4>Veriler başarı bir şekilde googletechnews tablosuna aktarıldı.</h4>"

    for data in saved_data:
        if data[1] in currentDocs:
            return "<h4>Bu veriler halihazırda veri tabanında mevcut.</h4>"
        else:
            for ord in json_obj["veriler"]:
                cursor.execute("INSERT INTO googletechnews (NewsURL, NewsTitle, NewsContent, NewsIMG) VALUES (%s,%s,%s, %s)",
                               (ord["News Url"], str(ord["News Title"]).encode('ascii','ignore'), str(ord["News Content"]).encode('ascii','ignore'), ord["News IMG"]))


            db.commit()
            cursor.close()
            return "<h4>Veriler başarı ile googletechnews tablosuna aktarıldı.</h4>"

@api.route('/savenews', methods=['GET'])
def savenews_db():
    file = os.path.abspath('dailynews.json')
    json_data = open(file,encoding="utf-8", errors='ignore').read()
    json_obj = json.loads(json_data)

    cursor = db.cursor()
    sql_select = "select * from googlenews"
    cursor.execute(sql_select)
    saved_data = cursor.fetchall()
    currentDocs = []
    with open('dailynews.json', 'r', encoding='utf-8') as file:
        data = json.load(file)

    for item in data["veriler"]:
        try:currentDocs.append(item["News Url"])
        except:pass

    if not saved_data:
        for ord in json_obj["veriler"]:
            cursor.execute("INSERT INTO googlenews (NewsURL, NewsTitle, NewsContent, NewsIMG) VALUES (%s,%s,%s, %s)",
                           (ord["News Url"], ord["News Title"],
                            ord["News Content"], ord["News IMG"]))

        db.commit()
        cursor.close()
        return "<h4>Veriler başarı ile googlenews tablosuna aktarıldı.</h4>"

    for data in saved_data:
        if data[1] in currentDocs:
            return "<h4>Bu veriler halihazırda veri tabanında mevcut.</h4>"
        else:
            for ord in json_obj["veriler"]:
                cursor.execute("INSERT INTO googlenews (NewsURL, NewsTitle, NewsContent, NewsIMG) VALUES (%s,%s,%s, %s)",
                               (ord["News Url"], ord["News Title"],
                               ord["News Content"], ord["News IMG"]))

            db.commit()
            cursor.close()
            return "<h4>Veriler başarı ile googlenews tablosuna aktarıldı.</h4>"

#Verileri göster.
@api.route('/news', methods=['GET', 'POST'])
def get_news():
    sql_select = "select * from googlenews"
    cursor = db.cursor()
    cursor.execute(sql_select)
    records = cursor.fetchall()

    if len(records) == 0:
        return "<h4>googletechnews tablosunda henüz kayıtlı bir veri yok.</h4>"

    elif request.method == 'POST':
        if request.form.get("data"):
            id_no = request.form.get("data")
            query = "DELETE FROM `googlenews` WHERE id = %s"
            cursor.execute(query, (int(id_no),))
            db.commit()
            return render_template('veriler.html', veri=records)
    else:
        return render_template('veriler.html', veri=records)

@api.route('/technews', methods=['GET'])
def get_techNews():
    sql_select = "select * from googletechnews"
    cursor = db.cursor()
    cursor.execute(sql_select)
    records = cursor.fetchall()
    if len(records) == 0:
        return "<h4>googletechnews tablosunda henüz kayıtlı bir veri yok.</h4>"
    else:
        return render_template('veriler.html', veri=records)

#Verileri sil.
@api.route('/delnews', methods=['GET'])
def delnews():
    cursor = db.cursor()
    Delete_all_rows = """truncate table googlenews """
    cursor.execute(Delete_all_rows)
    db.commit()
    return "<h4>googlenews tablosundaki tüm bilgiler silindi."

@api.route('/deltechnews', methods=['GET'])
def deltech_news():
    cursor = db.cursor()
    Delete_all_rows = """truncate table googletechnews """
    cursor.execute(Delete_all_rows)
    db.commit()
    return "<h4>googletechnews tablosundaki tüm bilgiler silindi."


#Veritabanında Arama
@api.route('/search', methods=['GET','POST'])
def search_data():
    if request.method == 'POST':
        data = request.form['aranan']
        cursor = db.cursor()
        cursor.execute(" SELECT * from googlenews where NewsTitle LIKE \'%"+str(data)+"%\'  UNION SELECT * from googletechnews where NewsTitle LIKE \'%"+str(data)+"%\' ")

        myresult = cursor.fetchall()
        return render_template('search.html',veri=myresult)
    else:
        return render_template('search.html')

if __name__ == '__main__':
    api.run(debug=True)
