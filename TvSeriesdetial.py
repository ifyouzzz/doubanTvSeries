import pymongo
import requests
from pyquery import PyQuery as pq
import re
import config
from bson.objectid import ObjectId
import time

client = pymongo.MongoClient(host='localhost', port=27017)
db = client[config.mongodbName]
collection = db[config.dbTableName]
headers = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.92 Safari/537.36'
}


def getTvSeriesDetial(urlForDetial, nameForDetial, scoreForDetial):
    try:
        time.sleep(0.5)
        request = requests.get(urlForDetial, headers=headers)
        if request.status_code == 200:
            html = request.text
            doc = pq(html)
            year = re.findall(r"\((.*?)\)", doc('.year').text())
            type = re.findall('''<span property="v:genre">(.*?)</span>''', str(doc))
            totalPeople = doc('#interest_sectl div div.rating_self.clearfix div div.rating_sum a span').text()
            info = doc('#info > span.actor').text()
            ac_info = re.findall(': (.*)', info)
            print(nameForDetial, ac_info, year, totalPeople, type, scoreForDetial)
            if type is not None:
                condition = {'name': nameForDetial, 'score': scoreForDetial}
                before = collection.find_one(condition)
                before['voteNumber'] = totalPeople
                before['year'] = year[0]
                before['type'] = type
                before['actor_info'] = ac_info
                collection.update(condition, before)
    except ConnectionError as e:
        print(e)


if __name__ == '__main__':
    count = collection.find().count()
    data = collection.find_one({'name': '延禧攻略'})
    urls = []
    names = []
    scores = []
    print(count)
    count_num = 0
    for i in range(count):
        _id = data['_id']
        urls.append(data['url'])
        names.append(data['name'])
        scores.append(data['score'])
        data = collection.find_one({'_id': {'$gt': ObjectId(str(_id))}})
    for url, name, score in zip(urls, names, scores):
        print('正在存储第', count_num, '条数据')
        getTvSeriesDetial(urlForDetial=url, nameForDetial=name, scoreForDetial=score)
        count_num += 1
