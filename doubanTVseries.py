from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
import time
import pandas as pd
import pymongo
import config

browser = webdriver.Chrome()
wait = WebDriverWait(browser, 10)
url = 'https://movie.douban.com/tag/#/?sort=T&range=0,10&tags=%E7%94%B5%E8%A7%86%E5%89%A7,%E4%B8%AD%E5%9B%BD%E5%A4%A7%E9%99%86'
browser.get(url)
browser.switch_to.window(browser.window_handles[0])
client = pymongo.MongoClient(host='localhost', port=27017)
db = client[config.mongodbName]
collection = db[config.dbTableName]


def save_to_mongo(name, score, url):
    item = {
        'name': name,
        'score': score,
        'url': url
    }
    result = collection.insert(item)
    if result:
        print('成功保存Mongodb!')
    else:
        print('保存失败!')


for i in range(40):
    js = 'var q=document.documentElement.scrollTop=10000000'
    browser.execute_script(js)
    moreButton = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '#app div div.article > a.more')))
    moreButton.click()
    time.sleep(2)


names = [k.text for k in browser.find_elements_by_class_name('title')]
scores = [k.text for k in browser.find_elements_by_class_name('rate')]
urls = [k.get_attribute('href') for k in browser.find_elements_by_class_name('item')]
pd.DataFrame({'name': names,
              'score': scores,
              'url': urls}).to_csv('电视剧.csv')
for name, score, url in zip(names, scores, urls):
    save_to_mongo(name, score, url)
